"""Create a transparent comparison and error-analysis report from saved evaluation JSON."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def read(name):
    return json.loads((ROOT / "reports/evaluation" / name).read_text())

def error_summary(report):
    pairs = Counter((item["label"], item["prediction"]) for item in report["misclassified"])
    return [{"actual": actual, "predicted": predicted, "count_in_saved_first_100_errors": count} for (actual, predicted), count in pairs.most_common()]

def main():
    baseline = read("pretrained_test_full.json")
    fine_tuned = read("finetuned_test_full.json")
    comparison = {
        "task": "ContractNLI document-level evaluation with evidence-aware windows",
        "test_split": "untouched predefined test split",
        "records": fine_tuned["records"],
        "methodology": fine_tuned["protocol"],
        "baseline": baseline["metrics"],
        "fine_tuned": fine_tuned["metrics"],
        "delta": {key: fine_tuned["metrics"][key] - baseline["metrics"][key] for key in ["accuracy", "macro_precision", "macro_recall", "macro_f1", "weighted_f1"]},
        "error_analysis": {
            "baseline": error_summary(baseline),
            "fine_tuned": error_summary(fine_tuned),
            "interpretation": "The fine-tuned checkpoint improves recall for Contradiction but has low contradiction precision; it still over-flags contradictions for some NotMentioned documents. Review the saved misclassified IDs with source data before legal use.",
        },
        "limitations": [
            "Fine-tuning used a small, balanced 96-document CPU/MPS-safe subset, not the full training split.",
            "No test labels were used in selection or training.",
            "Evidence contexts and multiple-instance pooling are an approximation to original whole-contract ContractNLI evaluation.",
        ],
    }
    output = ROOT / "reports/evaluation/contractnli_model_comparison.json"
    output.write_text(json.dumps(comparison, indent=2), encoding="utf-8")
    print(json.dumps({"baseline_macro_f1": comparison["baseline"]["macro_f1"], "fine_tuned_macro_f1": comparison["fine_tuned"]["macro_f1"], "delta": comparison["delta"]}, indent=2))

if __name__ == "__main__":
    main()
