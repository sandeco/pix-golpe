# -*- coding: utf-8 -*-
"""Transforma a captura bruta de uma corrida (JSONL) nas tabelas e figuras do artigo.

Uso:
    python paper/analyze.py paper/results/run-2026-09-22-burst.jsonl

Saída, na pasta paper/results/<nome-da-captura>/:
    decisions.csv     uma linha por mensagem e por lado (veredito, probabilidade, latência, tokens, custo)
    traces.csv        uma linha por rastreio (latência, tamanho do subgrafo, acertos contra a verdade)
    summary.csv/.tex  métricas agregadas por lado, com IC 95% bootstrap para as medianas
    confusion.csv     matriz de confusão 2x3 por lado (real x veredito)
    agreement.csv     concordância entre os dois lados (kappa de Cohen, rastreios idênticos)
    latency_cdf.png   CDF da latência de decisão e de rastreio
    latency_box.png   boxplot das latências
"""
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

SIDES = ("rust", "python")
NAMES = {"rust": "Rust + Jev", "python": "Python + DeepSeek"}
RNG = np.random.default_rng(42)


def bootstrap_ci(values, stat=np.median, n=10_000, alpha=0.05):
    arr = np.asarray(values, dtype=float)
    if arr.size == 0:
        return (float("nan"), float("nan"))
    idx = RNG.integers(0, arr.size, size=(n, arr.size))
    stats = stat(arr[idx], axis=1)
    return (float(np.quantile(stats, alpha / 2)), float(np.quantile(stats, 1 - alpha / 2)))


def load(path: Path):
    events = [json.loads(l) for l in path.open(encoding="utf-8")]
    meta = next(e for e in events if e["type"] == "capture")
    run = next(e for e in events if e["type"] == "run")
    decisions = defaultdict(dict)
    traces = defaultdict(dict)
    done, errors, report = {}, [], None
    for e in events:
        t, side = e.get("type"), e.get("side")
        if t == "decision":
            decisions[side][e["id"]] = e
        elif t == "trace":
            traces[side][e["id"]] = e
        elif t == "done":
            done[side] = e["totals"]
        elif t == "error":
            errors.append(e)
        elif t == "report":
            report = e
    return meta, run, decisions, traces, done, errors, report


def load_truth(data_dir: Path):
    truth = {}
    for l in (data_dir / "mensagens.jsonl").open(encoding="utf-8"):
        m = json.loads(l)
        truth[m["id"]] = m
    return truth


def binary(real: bool, verdict: str):
    """Classe binária: só GOLPE conta como positivo; SUSPEITA e OK contam como negativo."""
    pred = verdict == "golpe"
    if real and pred:
        return "TP"
    if real and not pred:
        return "FN"
    if not real and pred:
        return "FP"
    return "TN"


def kappa(a, b, labels):
    ids = sorted(set(a) & set(b))
    n = len(ids)
    if n == 0:
        return float("nan"), 0
    agree = sum(a[i] == b[i] for i in ids) / n
    pa = Counter(a[i] for i in ids)
    pb = Counter(b[i] for i in ids)
    expected = sum(pa[l] / n * pb[l] / n for l in labels)
    return ((agree - expected) / (1 - expected) if expected < 1 else 1.0), n


def main(path: Path):
    root = path.parent.parent
    meta, run, decisions, traces, done, errors, report = load(path)
    truth = load_truth(root.parent / "data")
    out = path.parent / path.stem
    out.mkdir(parents=True, exist_ok=True)

    # decisions.csv
    rows = []
    for side in SIDES:
        for mid, d in sorted(decisions[side].items()):
            m = truth[mid]
            rows.append({
                "side": side, "id": mid, "golpe_real": int(m["golpe_real"]), "golpe_prob": d.get("golpe"),
                "verdict": d["verdict"], "classe_binaria": binary(m["golpe_real"], d["verdict"]),
                "tipo": d.get("tipo"), "urgencia": d.get("urgencia"), "pede_pix": d.get("pede_pix"),
                "latency_ms": d["latency_ms"], "tokens_in": d.get("tokens_in"), "tokens_out": d.get("tokens_out"),
                "cost_usd": d.get("cost_usd"), "model": d.get("model"), "recv_s": d.get("_recv_s"),
            })
    with (out / "decisions.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # traces.csv
    trows = []
    for side in SIDES:
        for mid, t in sorted(traces[side].items()):
            tr = t.get("truth", {})
            trows.append({
                "side": side, "id": mid, "chave": t.get("chave"), "latency_ms": t["latency_ms"],
                "visitados": t.get("visitados"), "arestas_sub": t.get("arestas_sub"),
                "n_laranjas": len(t.get("laranjas", [])), "n_saque": len(t.get("saque", [])),
                "laranjas_reais": tr.get("laranjas_reais"), "laranjas_acertadas": tr.get("laranjas_acertadas"),
                "saque_reais": tr.get("saque_reais"), "saque_acertadas": tr.get("saque_acertadas"),
            })
    with (out / "traces.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(trows[0].keys()))
        w.writeheader()
        w.writerows(trows)

    # summary + confusion
    summary, confusion = [], []
    for side in SIDES:
        ds = decisions[side]
        lat = np.array([d["latency_ms"] for d in ds.values()])
        tlat = np.array([t["latency_ms"] for t in traces[side].values()])
        cls = Counter(binary(truth[i]["golpe_real"], d["verdict"]) for i, d in ds.items())
        tp, fp, fn, tn = cls["TP"], cls["FP"], cls["FN"], cls["TN"]
        n = tp + fp + fn + tn
        prec = tp / (tp + fp) if tp + fp else float("nan")
        rec = tp / (tp + fn) if tp + fn else float("nan")
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else float("nan")
        lo, hi = bootstrap_ci(lat)
        tlo, thi = bootstrap_ci(tlat)
        lar_real = sum(t.get("truth", {}).get("laranjas_reais", 0) for t in traces[side].values())
        lar_hit = sum(t.get("truth", {}).get("laranjas_acertadas", 0) for t in traces[side].values())
        saq_real = sum(t.get("truth", {}).get("saque_reais", 0) for t in traces[side].values())
        saq_hit = sum(t.get("truth", {}).get("saque_acertadas", 0) for t in traces[side].values())
        totals = done.get(side, {})
        summary.append({
            "side": side, "nome": NAMES[side], "modelo": Counter(d.get("model") for d in ds.values()).most_common(1)[0][0],
            "mensagens": n, "erros": sum(1 for e in errors if e.get("side") == side),
            "tempo_total_s": round(totals.get("total_ms", float("nan")) / 1000, 1),
            "decisao_p50_ms": round(float(np.median(lat)), 1), "decisao_p50_ic95": f"[{lo:.1f}, {hi:.1f}]",
            "decisao_p95_ms": round(float(np.quantile(lat, 0.95)), 1), "decisao_media_ms": round(float(lat.mean()), 1),
            "decisao_dp_ms": round(float(lat.std(ddof=1)), 1),
            "rastreios": len(tlat), "rastreio_p50_ms": round(float(np.median(tlat)), 1) if tlat.size else None,
            "rastreio_p50_ic95": f"[{tlo:.1f}, {thi:.1f}]", "rastreio_p95_ms": round(float(np.quantile(tlat, 0.95)), 1) if tlat.size else None,
            "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "acuracia": round((tp + tn) / n, 4), "precisao": round(prec, 4), "recall": round(rec, 4), "f1": round(f1, 4),
            "suspeita_em_golpe_real": sum(1 for i, d in ds.items() if truth[i]["golpe_real"] and d["verdict"] == "revisar"),
            "suspeita_em_normal": sum(1 for i, d in ds.items() if not truth[i]["golpe_real"] and d["verdict"] == "revisar"),
            "laranjas_recall": round(lar_hit / lar_real, 4) if lar_real else None,
            "saque_recall": round(saq_hit / saq_real, 4) if saq_real else None,
            "tokens_in": sum(d.get("tokens_in") or 0 for d in ds.values()),
            "tokens_out": sum(d.get("tokens_out") or 0 for d in ds.values()),
            "custo_usd": round(sum(d.get("cost_usd") or 0 for d in ds.values()), 6),
            "custo_usd_por_1000": round(sum(d.get("cost_usd") or 0 for d in ds.values()) / n * 1000, 4),
        })
        for real in (True, False):
            c = Counter(d["verdict"] for i, d in ds.items() if truth[i]["golpe_real"] == real)
            confusion.append({"side": side, "real": "golpe" if real else "normal",
                              "GOLPE": c["golpe"], "SUSPEITA": c["revisar"], "OK": c["ok"]})
    with (out / "summary.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(summary[0].keys()))
        w.writeheader()
        w.writerows(summary)
    with (out / "confusion.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(confusion[0].keys()))
        w.writeheader()
        w.writerows(confusion)

    # agreement between arms
    va = {i: d["verdict"] for i, d in decisions["rust"].items()}
    vb = {i: d["verdict"] for i, d in decisions["python"].items()}
    k, n_common = kappa(va, vb, ("golpe", "revisar", "ok"))
    common_traces = set(traces["rust"]) & set(traces["python"])
    identical = sum(1 for i in common_traces
                    if sorted(traces["rust"][i].get("laranjas", [])) == sorted(traces["python"][i].get("laranjas", []))
                    and sorted(traces["rust"][i].get("saque", [])) == sorted(traces["python"][i].get("saque", [])))
    with (out / "agreement.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["metrica", "valor"])
        w.writerow(["mensagens_em_comum", n_common])
        w.writerow(["vereditos_iguais", sum(va[i] == vb[i] for i in va if i in vb)])
        w.writerow(["kappa_cohen_veredito", round(k, 4)])
        w.writerow(["rastreios_em_comum", len(common_traces)])
        w.writerow(["rastreios_identicos_laranjas_e_saque", identical])

    # summary.tex
    s = {r["side"]: r for r in summary}
    lines = [
        r"\begin{tabular}{lrr}", r"\toprule",
        r"Métrica & " + NAMES["rust"] + " & " + NAMES["python"] + r" \\", r"\midrule",
        f"Mensagens avaliadas & {s['rust']['mensagens']} & {s['python']['mensagens']} \\\\",
        f"Tempo total (s) & {s['rust']['tempo_total_s']} & {s['python']['tempo_total_s']} \\\\",
        f"Decisão p50 (ms) [IC 95\\%] & {s['rust']['decisao_p50_ms']} {s['rust']['decisao_p50_ic95']} & {s['python']['decisao_p50_ms']} {s['python']['decisao_p50_ic95']} \\\\",
        f"Decisão p95 (ms) & {s['rust']['decisao_p95_ms']} & {s['python']['decisao_p95_ms']} \\\\",
        f"Rastreio p50 (ms) [IC 95\\%] & {s['rust']['rastreio_p50_ms']} {s['rust']['rastreio_p50_ic95']} & {s['python']['rastreio_p50_ms']} {s['python']['rastreio_p50_ic95']} \\\\",
        f"Rastreio p95 (ms) & {s['rust']['rastreio_p95_ms']} & {s['python']['rastreio_p95_ms']} \\\\",
        f"TP / FP / FN / TN & {s['rust']['TP']} / {s['rust']['FP']} / {s['rust']['FN']} / {s['rust']['TN']} & {s['python']['TP']} / {s['python']['FP']} / {s['python']['FN']} / {s['python']['TN']} \\\\",
        f"Acurácia & {s['rust']['acuracia']:.4f} & {s['python']['acuracia']:.4f} \\\\",
        f"Precisão & {s['rust']['precisao']:.4f} & {s['python']['precisao']:.4f} \\\\",
        f"Recall & {s['rust']['recall']:.4f} & {s['python']['recall']:.4f} \\\\",
        f"F1 & {s['rust']['f1']:.4f} & {s['python']['f1']:.4f} \\\\",
        f"Recall de laranjas no rastreio & {s['rust']['laranjas_recall']} & {s['python']['laranjas_recall']} \\\\",
        f"Tokens de entrada / saída & {s['rust']['tokens_in']} / {s['rust']['tokens_out']} & {s['python']['tokens_in']} / {s['python']['tokens_out']} \\\\",
        f"Custo (USD) & {s['rust']['custo_usd']:.4f} & {s['python']['custo_usd']:.4f} \\\\",
        r"\bottomrule", r"\end{tabular}",
    ]
    (out / "summary.tex").write_text("\n".join(lines) + "\n", encoding="utf-8")

    # figures
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, kind, source in ((axes[0], "Decisão", decisions), (axes[1], "Rastreio", traces)):
        for side in SIDES:
            v = np.sort([e["latency_ms"] for e in source[side].values()])
            if v.size:
                ax.step(v, np.arange(1, v.size + 1) / v.size, where="post", label=NAMES[side])
        ax.set_xscale("log")
        ax.set_xlabel("latência (ms, escala log)")
        ax.set_ylabel("fração acumulada")
        ax.set_title(f"CDF da latência de {kind.lower()}")
        ax.grid(True, which="both", alpha=0.3)
        ax.legend()
    fig.tight_layout()
    fig.savefig(out / "latency_cdf.png", dpi=150)

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, kind, source in ((axes[0], "Decisão", decisions), (axes[1], "Rastreio", traces)):
        data = [[e["latency_ms"] for e in source[side].values()] for side in SIDES]
        ax.boxplot(data, tick_labels=[NAMES[s] for s in SIDES], showfliers=True)
        ax.set_yscale("log")
        ax.set_ylabel("latência (ms, escala log)")
        ax.set_title(f"Latência de {kind.lower()}")
        ax.grid(True, axis="y", which="both", alpha=0.3)
    fig.tight_layout()
    fig.savefig(out / "latency_box.png", dpi=150)

    # run metadata
    (out / "run_meta.json").write_text(json.dumps({
        "captura": meta, "run": run, "done": done, "erros": errors,
        "report_servidor": report, "n_decisoes": {s: len(decisions[s]) for s in SIDES},
        "n_rastreios": {s: len(traces[s]) for s in SIDES},
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    for r in summary:
        print(f"{r['nome']}: {r['mensagens']} msgs, {r['tempo_total_s']} s, decisão p50 {r['decisao_p50_ms']} ms, "
              f"rastreio p50 {r['rastreio_p50_ms']} ms, acurácia {r['acuracia']}, recall {r['recall']}, custo US$ {r['custo_usd']}")
    print(f"kappa entre lados: {k:.4f} em {n_common} mensagens; rastreios idênticos: {identical}/{len(common_traces)}")
    print("saída em", out)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
