"""Cliente assincrono DeepSeek; CLI para testar uma mensagem real do dataset."""

from __future__ import annotations

import argparse
import asyncio
import json
import math
import os
from pathlib import Path
import sys
import time

import httpx

try:  # usa o repositorio de certificados do sistema (proxy/antivirus com CA propria)
    import ssl
    import truststore
    _SSL_CTX = truststore.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
except ImportError:  # pragma: no cover
    _SSL_CTX = True

# Custo estimado em USD por milhao de tokens.
INPUT_USD_PER_MILLION = 0.28
OUTPUT_USD_PER_MILLION = 0.42
API_URL = "https://api.deepseek.com/chat/completions"
MODEL = "deepseek-flash"
MAX_ATTEMPTS = 3  # Inclui a primeira tentativa.
SYSTEM_PROMPT = '''You classify a message in Brazilian Portuguese. Reply ONLY with a JSON object:
{"golpe": <probability 0..1 that this message is a scam or fraud attempt (impersonation, fake bill, fake bank alert, fake prize, pressure to pay)>,
 "tipo": <one of "troca_numero","boleto_falso","falsa_central","premio","pix_errado","cobranca_legitima","pessoal","outro">,
 "urgencia": <0 = no time pressure, 1 = some urgency, 2 = extreme urgency, threats or deadlines>,
 "pede_pix": <probability 0..1 that the message asks the reader to make a Pix transfer or payment>}
Meaning of tipo: troca_numero = relative with a new phone number asking for money; boleto_falso = fake bill or invoice; falsa_central = fake bank or support alert; premio = fake prize or giveaway; pix_errado = claims a Pix was sent by mistake and asks for refund; cobranca_legitima = legitimate charge or order confirmation; pessoal = ordinary personal message; outro = anything else.'''
TIPOS = {
    "troca_numero", "boleto_falso", "falsa_central", "premio", "pix_errado",
    "cobranca_legitima", "pessoal", "outro",
}


def load_api_key(start: Path | None = None) -> str:
    """Ambiente tem precedencia; busca manual de .env no cwd e nos pais."""
    existing = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if existing:
        return existing
    start = (start or Path.cwd()).resolve()
    for directory in (start, *start.parents):
        env_path = directory / ".env"
        if not env_path.is_file():
            continue
        for line in env_path.read_text(encoding="utf-8-sig").splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:].lstrip()
            name, separator, value = line.partition("=")
            if separator and name.strip() == "DEEPSEEK_API_KEY":
                value = value.strip()
                if value[:1] in ("'", '"'):
                    quote = value[0]
                    end = value.find(quote, 1)
                    if end < 0:
                        raise ValueError(f"DEEPSEEK_API_KEY: aspas abertas em {env_path}")
                    value = value[1:end]
                else:
                    value = value.split(" #", 1)[0].strip()
                if value:
                    return value
    raise ValueError("DEEPSEEK_API_KEY ausente no ambiente e nos .env do diretorio atual e pais")


def verdict(golpe: float) -> str:
    return "golpe" if golpe >= 0.6 else "ok" if golpe <= 0.4 else "revisar"


def cost_usd(tokens_in: int, tokens_out: int) -> float:
    return tokens_in * INPUT_USD_PER_MILLION / 1e6 + tokens_out * OUTPUT_USD_PER_MILLION / 1e6


def parse_response(payload: dict, latency_ms: float) -> dict:
    try:
        content = payload["choices"][0]["message"]["content"]
        usage = payload["usage"]
        tokens_in = usage["prompt_tokens"]
        tokens_out = usage["completion_tokens"]
        model = payload["model"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ValueError(f"DeepSeek: resposta sem campos obrigatorios: {exc}") from exc
    try:
        answer = json.loads(content)
    except (ValueError, TypeError) as exc:
        raise ValueError("DeepSeek: JSON invalido no conteudo do modelo") from exc
    if not isinstance(answer, dict):
        raise ValueError("DeepSeek: o conteudo do modelo deve ser um objeto JSON")
    missing = {"golpe", "tipo", "urgencia", "pede_pix"} - answer.keys()
    if missing:
        raise ValueError(f"DeepSeek: campos faltando no JSON: {', '.join(sorted(missing))}")
    result = {}
    for name, upper in (("golpe", 1.0), ("urgencia", 2.0), ("pede_pix", 1.0)):
        value = answer[name]
        if (isinstance(value, bool) or not isinstance(value, (int, float))
                or not math.isfinite(value) or not 0.0 <= value <= upper):
            raise ValueError(f"DeepSeek: {name} deve ser um numero entre 0 e {upper:g}")
        result[name] = float(value)
    if not isinstance(answer["tipo"], str) or answer["tipo"] not in TIPOS:
        raise ValueError("DeepSeek: tipo ausente dos criterios da SPEC")
    if not isinstance(model, str) or not model:
        raise ValueError("DeepSeek: campo model invalido")
    if any(type(n) is not int or n < 0 for n in (tokens_in, tokens_out)):
        raise ValueError("DeepSeek: contagem de tokens invalida")
    result.update(tipo=answer["tipo"], tokens_in=tokens_in, tokens_out=tokens_out,
                  model=model, latency_ms=latency_ms)
    return result


class DeepSeekClient:
    def __init__(self, api_key: str | None = None, *, transport=None):
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key or load_api_key()}"},
            timeout=httpx.Timeout(120.0, connect=20.0),
            limits=httpx.Limits(max_connections=8, max_keepalive_connections=8,
                               keepalive_expiry=60.0),
            transport=transport,
            verify=_SSL_CTX,
        )

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        await self.aclose()

    async def aclose(self) -> None:
        await self.client.aclose()

    async def classificar(self, remetente: str, texto: str) -> dict:
        body = {
            "model": MODEL, "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Remetente: {remetente}\nMensagem: {texto}"},
            ],
        }
        for attempt in range(MAX_ATTEMPTS):
            started = time.perf_counter()
            response = await self.client.post(API_URL, json=body)
            # Ida e volta da tentativa HTTP; espera de backoff nao e latencia HTTP.
            latency_ms = (time.perf_counter() - started) * 1000.0
            if (response.status_code == 429 or 500 <= response.status_code < 600):
                if attempt + 1 < MAX_ATTEMPTS:
                    await asyncio.sleep(2.0 ** attempt)
                    continue
            response.raise_for_status()
            try:
                payload = response.json()
            except ValueError as exc:
                raise ValueError("DeepSeek: resposta HTTP nao contem JSON valido") from exc
            return parse_response(payload, latency_ms)
        raise RuntimeError("DeepSeek: tentativas esgotadas")


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("texto", nargs="?", help="sem texto, usa a primeira mensagem real de golpe")
    parser.add_argument("--remetente", default="teste")
    args = parser.parse_args()
    if args.texto is None:
        path = Path(__file__).resolve().parent.parent / "data" / "mensagens.jsonl"
        with path.open(encoding="utf-8") as handle:
            message = next(m for line in handle if line.strip()
                           if (m := json.loads(line)).get("golpe_real"))
        # A verdade de referencia serve apenas para escolher o exemplo local.
        args.remetente, args.texto = message["remetente"], message["texto"]
    async with DeepSeekClient() as client:
        result = await client.classificar(args.remetente, args.texto)
    result["verdict"] = verdict(result["golpe"])
    result["cost_usd"] = cost_usd(result["tokens_in"], result["tokens_out"])
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (ValueError, httpx.HTTPError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)
