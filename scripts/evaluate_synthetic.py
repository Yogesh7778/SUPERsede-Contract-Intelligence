"""Evaluate hybrid reasoning conditional on the synthetic corpus's annotated evidence pairs.

This isolates reasoning/NLI from clause retrieval and is deliberately labelled a
gold-evidence evaluation; it does not measure real-world evidence localization.
"""
import argparse, json, re, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.evaluation.contractnli import metrics
from src.models.nli_classifier import NLIClassifier
from src.models.semantic_matcher import SemanticMatcher
from src.reasoning.conflict_detector import ConflictDetector
from src.reasoning.document_comparison_pipeline import DocumentComparisonPipeline
from src.reasoning.precedence_reasoner import PrecedenceReasoner
from src.reasoning.scope_reasoner import ScopeReasoner
from src.reasoning.temporal_reasoner import TemporalReasoner

ROOT = Path(__file__).resolve().parents[1]

def source_path(document_id):
    matches = list((ROOT / "dataset/synthetic").glob(f"**/{document_id}.md"))
    if not matches:
        raise FileNotFoundError(document_id)
    return matches[0]

def parse_document(document_id):
    path = source_path(document_id)
    text = path.read_text(encoding="utf-8")
    values = {key.lower(): value.strip() for key, value in re.findall(r"^- ([^:]+):\s*(.+)$", text, re.MULTILINE)}
    parties = [values.get("party a"), values.get("party b")]
    return {
        "document_id": document_id,
        "signed": values.get("status", "").upper() == "SIGNED",
        "effective_date": values.get("effective date"),
        "expiry_date": None if values.get("expiry date") == "Not specified" else values.get("expiry date"),
        "contract_id": values.get("pack id"),
        "project_id": values.get("pack id"),
        "parties": [party for party in parties if party],
        "service_scope": values.get("scope"),
        "text": text,
        "source_filename": path.name,
    }

def infer_amends(first, second):
    """Use an explicit synthetic replacement reference only to populate document relation metadata."""
    for amendment, other in ((first, second), (second, first)):
        if "AMENDMENT" not in amendment["text"].upper():
            continue
        if re.search(r"(?:expressly replaces|replaces clause)", amendment["text"], re.IGNORECASE):
            amendment["explicitly_amends"] = [other["document_id"]]
        else:
            amendment["explicitly_amends"] = []
    first.setdefault("explicitly_amends", [])
    second.setdefault("explicitly_amends", [])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="models/checkpoints/contractnli-deberta-mps-balanced-96")
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    parser.add_argument("--output", default="reports/evaluation/synthetic_hybrid_gold_evidence.json")
    args = parser.parse_args()
    model = NLIClassifier(args.model, device=None if args.device == "auto" else args.device, max_length=256)
    detector = ConflictDetector(SemanticMatcher(), model, TemporalReasoner(), ScopeReasoner(), PrecedenceReasoner())
    pipeline = DocumentComparisonPipeline(detector)
    annotations = json.loads((ROOT / "dataset/synthetic/annotations/ground_truth.json").read_text())
    outcomes = []
    for pack in annotations["packs"]:
        comparison = pack["comparisons"][0]
        left_evidence, right_evidence = comparison["evidence"]
        left, right = parse_document(left_evidence["document_id"]), parse_document(right_evidence["document_id"])
        infer_amends(left, right)
        result = detector.compare_clauses(
            left_evidence["text"], right_evidence["text"],
            term_a=left, term_b=right, evaluation_date="2026-10-15",
            scope_a=left, scope_b=right, document_a=left, document_b=right,
        )
        predicted = pipeline.classify_document_pair([result])["label"]
        outcomes.append({"pack_id": pack["pack_id"], "scenario": pack["scenario"], "actual": pack["expected_label"], "predicted": predicted, "comparison": result, "evidence": comparison["evidence"]})
    labels = ["CONFLICT", "SUPERSEDED", "CONSISTENT", "UNCERTAIN"]
    from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, accuracy_score
    actual, predicted = [x["actual"] for x in outcomes], [x["predicted"] for x in outcomes]
    p, r, f, support = precision_recall_fscore_support(actual, predicted, labels=labels, zero_division=0)
    report = {
        "protocol": "Gold-evidence synthetic reasoning evaluation. It uses annotation-provided evidence pairs, so it measures NLI/reasoning conditional on correct retrieval, not end-to-end clause localization.",
        "records": len(outcomes), "labels": labels,
        "accuracy": accuracy_score(actual, predicted), "macro_precision": float(p.mean()), "macro_recall": float(r.mean()), "macro_f1": float(f.mean()),
        "per_class": {label: {"precision": float(p[i]), "recall": float(r[i]), "f1": float(f[i]), "support": int(support[i])} for i, label in enumerate(labels)},
        "confusion_matrix": confusion_matrix(actual, predicted, labels=labels).tolist(),
        "classification_report": classification_report(actual, predicted, labels=labels, output_dict=True, zero_division=0),
        "errors": [x for x in outcomes if x["actual"] != x["predicted"]], "outcomes": outcomes,
        "limitations": ["Synthetic data has 60 packs and cannot establish real-world generalization.", "This protocol supplies annotated evidence, so retrieval performance is excluded."],
    }
    output = ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({key: report[key] for key in ["records", "accuracy", "macro_f1", "confusion_matrix"]}, indent=2))

if __name__ == "__main__":
    main()
