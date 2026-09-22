#!/usr/bin/env python3
"""
Spec Scorer — Avalia a qualidade de uma spec de feature
Baseado na rubrica em references/evaluation_rubric.md

Uso:
    python scripts/spec_scorer.py --spec caminho/para/spec.md
    python scripts/spec_scorer.py --spec spec.md --json   # saída em JSON
"""

import argparse
import json
import re
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


# ─── Estruturas de dados ────────────────────────────────────────────────────

@dataclass
class DimensionScore:
    name: str
    weight: float          # peso relativo (soma = 1.0)
    raw_score: float       # 0–100 dentro da dimensão
    max_raw: float         # máximo possível
    issues: list[str] = field(default_factory=list)
    positives: list[str] = field(default_factory=list)

    @property
    def weighted_score(self) -> float:
        return (self.raw_score / self.max_raw) * self.weight * 100


@dataclass
class SpecReport:
    file: str
    total_score: float
    classification: str
    dimensions: list[DimensionScore]
    critical_gaps: list[str]
    suggestions: list[str]
    raw_text: str


# ─── Helpers de análise ─────────────────────────────────────────────────────

def load_spec(path: str) -> str:
    p = Path(path)
    if not p.exists():
        print(f"❌ Arquivo não encontrado: {path}", file=sys.stderr)
        sys.exit(1)
    return p.read_text(encoding="utf-8")


def has_section(text: str, section_pattern: str) -> bool:
    return bool(re.search(section_pattern, text, re.IGNORECASE | re.MULTILINE))


def section_content(text: str, section_pattern: str) -> str:
    """Extrai conteúdo da seção até a próxima seção de mesmo nível."""
    match = re.search(section_pattern, text, re.IGNORECASE | re.MULTILINE)
    if not match:
        return ""
    start = match.end()
    next_section = re.search(r'^#{1,2}\s+\d+\.', text[start:], re.MULTILINE)
    end = start + next_section.start() if next_section else len(text)
    return text[start:end].strip()


def count_pattern(text: str, pattern: str) -> int:
    return len(re.findall(pattern, text, re.IGNORECASE | re.MULTILINE))


def has_content(text: str, min_words: int = 10) -> bool:
    words = re.findall(r'\b\w+\b', text)
    return len(words) >= min_words


def count_rf_items(text: str) -> int:
    return count_pattern(text, r'\bRF-\d+\b')


def count_nf_items(text: str) -> int:
    return count_pattern(text, r'\bNG-\d+\b')


def count_ec_items(text: str) -> int:
    return count_pattern(text, r'\bEC-\d+\b')


def count_unfilled_placeholders(text: str) -> int:
    return count_pattern(text, r'\[[A-Z][^\]]{3,60}\]')


def has_numeric_metric(text: str) -> bool:
    # Busca padrões como "< 200ms", "≥ 25%", "99,9%", "< 2min"
    return bool(re.search(r'[<>≤≥]\s*\d+|=\s*\d+\s*%|\d+\s*(ms|min|h|%|dias?|days?)', text))


def has_vague_terms(text: str) -> list[str]:
    vague = ["rapidamente", "logo", "brevemente", "alguns", "muitos",
             "de forma eficiente", "de forma intuitiva", "fácil de usar",
             "user-friendly", "performático", "ser bonito", "ser rápido",
             "ser bom", "quickly", "easily", "fast", "nice"]
    found = []
    for term in vague:
        if re.search(r'\b' + re.escape(term) + r'\b', text, re.IGNORECASE):
            found.append(term)
    return found


def has_contradictions_signal(text: str) -> bool:
    # Heurística simples: presença de "mas" / "porém" / "entretanto" depois de requisito
    return bool(re.search(r'RF-\d+.*?\b(mas|porém|entretanto|however|but)\b', text,
                           re.IGNORECASE | re.DOTALL))


# ─── Avaliadores por dimensão ────────────────────────────────────────────────

def score_completude(text: str) -> DimensionScore:
    dim = DimensionScore(name="Completude", weight=0.30, raw_score=0, max_raw=30)
    score = 0

    # Seções essenciais (1–6) presentes e com conteúdo
    required_sections = [
        (r'^#{1,2}\s+1[\.\s]+Resum', "Seção 1 (Resumo)"),
        (r'^#{1,2}\s+2[\.\s]+Contexto', "Seção 2 (Contexto)"),
        (r'^#{1,2}\s+3[\.\s]+Goals', "Seção 3 (Goals)"),
        (r'^#{1,2}\s+4[\.\s]+Non.Goals', "Seção 4 (Non-Goals)"),
        (r'^#{1,2}\s+5[\.\s]+Usuári', "Seção 5 (Usuários)"),
        (r'^#{1,2}\s+6[\.\s]+Requisitos', "Seção 6 (Requisitos)"),
    ]
    present = 0
    for pattern, name in required_sections:
        if has_section(text, pattern):
            content = section_content(text, pattern)
            if has_content(content, 8):
                present += 1
                dim.positives.append(f"✅ {name} presente e preenchida")
            else:
                dim.issues.append(f"⚠️ {name} presente mas com conteúdo insuficiente")
        else:
            dim.issues.append(f"❌ {name} ausente")
    score += (present / len(required_sections)) * 10

    # Requisitos com IDs
    rf_count = count_rf_items(text)
    if rf_count >= 5:
        score += 8
        dim.positives.append(f"✅ {rf_count} requisitos RF numerados")
    elif rf_count >= 3:
        score += 5
        dim.issues.append(f"⚠️ Apenas {rf_count} requisitos RF — recomendado mínimo 5")
    elif rf_count > 0:
        score += 2
        dim.issues.append(f"❌ Poucos requisitos RF ({rf_count}) — spec incompleta")
    else:
        dim.issues.append("❌ Nenhum requisito RF numerado — impossível rastrear")

    # Non-goals
    ng_count = count_nf_items(text)
    if ng_count >= 3:
        score += 7
        dim.positives.append(f"✅ {ng_count} non-goals definidos")
    elif ng_count >= 1:
        score += 4
        dim.issues.append(f"⚠️ Apenas {ng_count} non-goal(s) — adicione mais para clareza")
    else:
        dim.issues.append("❌ Non-goals ausentes — risco de scope creep")

    # Placeholders não preenchidos
    placeholders = count_unfilled_placeholders(text)
    if placeholders == 0:
        score += 5
        dim.positives.append("✅ Nenhum placeholder [colchete] não preenchido")
    else:
        penalty = min(placeholders * 2, 10)
        score = max(0, score - penalty)
        dim.issues.append(f"❌ {placeholders} placeholder(s) não preenchido(s) — spec incompleta")

    dim.raw_score = min(score, dim.max_raw)
    return dim


def score_testabilidade(text: str) -> DimensionScore:
    dim = DimensionScore(name="Testabilidade", weight=0.25, raw_score=0, max_raw=25)
    score = 0

    # Verbos concretos — heurística: ausência de termos vagos em requisitos
    vague = has_vague_terms(text)
    if not vague:
        score += 10
        dim.positives.append("✅ Ausência de termos vagos nos requisitos")
    else:
        penalty = min(len(vague) * 3, 10)
        score += max(0, 10 - penalty)
        dim.issues.append(f"⚠️ Termos vagos encontrados: {', '.join(vague[:5])}")

    # Fluxo principal (happy path)
    has_happy_path = has_section(text, r'Fluxo Principal|Happy Path|6\.2')
    if has_happy_path:
        # Verifica se tem pelo menos 3 passos numerados
        happy_content = section_content(text, r'Fluxo Principal|Happy Path|6\.2')
        steps = count_pattern(happy_content, r'^\s*\d+\.')
        if steps >= 3:
            score += 8
            dim.positives.append(f"✅ Fluxo principal com {steps} passos")
        else:
            score += 4
            dim.issues.append("⚠️ Fluxo principal incompleto (< 3 passos)")
    else:
        dim.issues.append("❌ Fluxo principal (happy path) ausente — essencial para testes")

    # Métricas numéricas nos goals
    goals_content = section_content(text, r'^#{1,2}\s+3[\.\s]+Goals')
    if has_numeric_metric(goals_content) or has_numeric_metric(text[:2000]):
        score += 7
        dim.positives.append("✅ Métricas de sucesso numéricas presentes")
    else:
        dim.issues.append("⚠️ Métricas de sucesso sem valores numéricos — dificulta validação")

    dim.raw_score = min(score, dim.max_raw)
    return dim


def score_clareza(text: str) -> DimensionScore:
    dim = DimensionScore(name="Clareza", weight=0.20, raw_score=0, max_raw=20)
    score = 0

    # Open questions sinalizadas
    open_questions = count_pattern(text, r'⚠️\s*ABERTO:|OQ-\d+')
    ambiguities_hidden = count_pattern(text, r'\?.*\?')  # múltiplas interrogações — sinal de dúvida
    if open_questions > 0:
        score += 6
        dim.positives.append(f"✅ {open_questions} open question(s) sinalizadas explicitamente")
    elif ambiguities_hidden > 3:
        dim.issues.append("⚠️ Possíveis ambiguidades não sinalizadas (use ⚠️ ABERTO: ou seção 14)")

    # Sujeito claro nos requisitos
    rf_section = section_content(text, r'^#{1,2}\s+6[\.\s]+Requisitos')
    subjects = count_pattern(rf_section, r'\b(o sistema|o usuário|a plataforma|the system|the user)\b')
    rf_count = count_rf_items(rf_section)
    if rf_count > 0 and subjects >= rf_count * 0.5:
        score += 6
        dim.positives.append("✅ Requisitos com sujeito claro (sistema/usuário)")
    elif rf_count > 0:
        dim.issues.append("⚠️ Alguns requisitos sem sujeito explícito — quem faz o quê?")

    # Contradições
    if has_contradictions_signal(text):
        score = max(0, score - 5)
        dim.issues.append("⚠️ Possível contradição entre requisitos — revisar")

    # Linguagem técnica sem definição (heurística)
    vague = has_vague_terms(text)
    if not vague:
        score += 8
        dim.positives.append("✅ Linguagem precisa e sem termos vagos")
    else:
        score += max(0, 8 - len(vague) * 2)

    dim.raw_score = min(score, dim.max_raw)
    return dim


def score_escopo(text: str) -> DimensionScore:
    dim = DimensionScore(name="Escopo", weight=0.15, raw_score=0, max_raw=15)
    score = 0

    # Non-goals úteis
    ng_section = section_content(text, r'^#{1,2}\s+4[\.\s]+Non.Goals')
    ng_count = count_nf_items(text)
    if ng_count >= 3 and has_content(ng_section, 15):
        score += 7
        dim.positives.append(f"✅ Non-goals claros e específicos ({ng_count} itens)")
    elif ng_count >= 1:
        score += 4
        dim.issues.append("⚠️ Non-goals presentes mas podem ser mais específicos")
    else:
        dim.issues.append("❌ Non-goals ausentes")

    # Dependências mapeadas
    has_deps = has_section(text, r'10[\.\s]+Integra|Dependências|Dependencies')
    if has_deps:
        deps_content = section_content(text, r'10[\.\s]+Integra|Dependências')
        if has_content(deps_content, 5):
            score += 5
            dim.positives.append("✅ Dependências e integrações mapeadas")
        else:
            score += 2
            dim.issues.append("⚠️ Seção de dependências presente mas vazia")
    else:
        dim.issues.append("⚠️ Dependências externas não mapeadas (seção 10)")

    # Plano de rollout
    has_rollout = has_section(text, r'Rollout|Plano de Lançamento|13[\.\s]+')
    if has_rollout:
        score += 3
        dim.positives.append("✅ Plano de rollout/rollback presente")
    else:
        dim.issues.append("⚠️ Plano de rollout/rollback ausente (seção 13)")

    dim.raw_score = min(score, dim.max_raw)
    return dim


def score_edge_cases(text: str) -> DimensionScore:
    dim = DimensionScore(name="Edge Cases", weight=0.10, raw_score=0, max_raw=10)
    score = 0

    ec_count = count_ec_items(text)
    ec_section = section_content(text, r'^#{1,2}\s+11[\.\s]+Edge|Edge Cases')

    if ec_count == 0:
        dim.issues.append("❌ CRÍTICO: Nenhum edge case definido — a implementação não saberá como tratar erros")
        dim.raw_score = 0
        return dim

    if ec_count >= 4:
        score += 5
        dim.positives.append(f"✅ {ec_count} edge cases cobertos")
    elif ec_count >= 2:
        score += 3
        dim.issues.append(f"⚠️ Apenas {ec_count} edge case(s) — adicione casos de falha externa e inputs inválidos")
    else:
        score += 1
        dim.issues.append(f"❌ Apenas {ec_count} edge case — muito insuficiente")

    # Edge cases com comportamento definido
    has_behavior = count_pattern(ec_section, r'\|[^|]{5,}')
    if has_behavior >= ec_count * 2:  # pelo menos trigger + comportamento
        score += 3
        dim.positives.append("✅ Edge cases com comportamento esperado definido")
    else:
        dim.issues.append("⚠️ Edge cases sem comportamento definido — são apenas perguntas, não spec")

    # Cobertura de falhas externas
    covers_external = bool(re.search(
        r'(timeout|indisponível|fora do ar|falha|erro\s+\d{3}|retry|fallback)',
        ec_section, re.IGNORECASE
    ))
    if covers_external:
        score += 2
        dim.positives.append("✅ Cobre falhas de dependências externas")
    else:
        dim.issues.append("⚠️ Não cobre falhas de sistemas externos (timeouts, indisponibilidade)")

    dim.raw_score = min(score, dim.max_raw)
    return dim


# ─── Score final e relatório ─────────────────────────────────────────────────

def classify(score: float) -> str:
    if score >= 90: return "⭐ Excelente — Pronta para implementação"
    if score >= 80: return "✅ Boa — Pronta com ajustes menores"
    if score >= 65: return "⚠️  Adequada — Implementável com riscos"
    if score >= 50: return "🔶 Incompleta — Revisar antes de implementar"
    return "❌ Insuficiente — Volta para entrevista/rascunho"


def build_report(spec_path: str) -> SpecReport:
    text = load_spec(spec_path)
    dims = [
        score_completude(text),
        score_testabilidade(text),
        score_clareza(text),
        score_escopo(text),
        score_edge_cases(text),
    ]
    total = sum(d.weighted_score for d in dims)

    critical_gaps = [
        issue for d in dims for issue in d.issues
        if issue.startswith("❌")
    ]
    suggestions = [
        issue for d in dims for issue in d.issues
        if issue.startswith("⚠️")
    ]

    return SpecReport(
        file=spec_path,
        total_score=round(total, 1),
        classification=classify(total),
        dimensions=dims,
        critical_gaps=critical_gaps,
        suggestions=suggestions,
        raw_text=text,
    )


# ─── Output ──────────────────────────────────────────────────────────────────

def print_report(report: SpecReport):
    print(f"\n{'='*60}")
    print(f"  SPEC QUALITY REPORT")
    print(f"  Arquivo: {report.file}")
    print(f"{'='*60}")
    print(f"\n  SCORE TOTAL: {report.total_score}/100  —  {report.classification}\n")

    print("  BREAKDOWN POR DIMENSÃO:")
    print(f"  {'Dimensão':<20} {'Score':<10} {'Peso':<8} {'Contribuição'}")
    print(f"  {'-'*50}")
    for d in report.dimensions:
        pct = round(d.raw_score / d.max_raw * 100)
        contrib = round(d.weighted_score, 1)
        print(f"  {d.name:<20} {pct:>3}%{'':<5} {int(d.weight*100):>3}%{'':<3} {contrib:>5}/pt")

    if report.critical_gaps:
        print(f"\n  ❌ GAPS CRÍTICOS ({len(report.critical_gaps)}):")
        for g in report.critical_gaps:
            print(f"     {g}")

    if report.suggestions:
        print(f"\n  ⚠️  MELHORIAS RECOMENDADAS ({len(report.suggestions)}):")
        for s in report.suggestions[:8]:  # top 8
            print(f"     {s}")
        if len(report.suggestions) > 8:
            print(f"     ... e mais {len(report.suggestions) - 8} sugestão(ões)")

    positives = [p for d in report.dimensions for p in d.positives]
    if positives:
        print(f"\n  ✅ PONTOS FORTES:")
        for p in positives[:5]:
            print(f"     {p}")

    print(f"\n{'='*60}\n")


def print_json(report: SpecReport):
    output = {
        "file": report.file,
        "total_score": report.total_score,
        "classification": report.classification,
        "dimensions": [
            {
                "name": d.name,
                "score_pct": round(d.raw_score / d.max_raw * 100),
                "weighted_contribution": round(d.weighted_score, 1),
                "issues": d.issues,
                "positives": d.positives,
            }
            for d in report.dimensions
        ],
        "critical_gaps": report.critical_gaps,
        "suggestions": report.suggestions,
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


# ─── Entry point ─────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Avalia a qualidade de uma spec de feature (0–100)"
    )
    parser.add_argument("--spec", required=True, help="Caminho para o arquivo .md da spec")
    parser.add_argument("--json", action="store_true", help="Saída em formato JSON")

    args = parser.parse_args()
    report = build_report(args.spec)

    if args.json:
        print_json(report)
    else:
        print_report(report)

    # Exit code não-zero se score < 65 (para uso em CI/CD)
    sys.exit(0 if report.total_score >= 65 else 1)


if __name__ == "__main__":
    main()
