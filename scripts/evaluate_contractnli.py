"""Evaluate a checkpoint or pretrained NLI model using document-level window aggregation."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.evaluation.contractnli import load_split, validate_evidence, prepare_examples, aggregate_window_predictions, metrics, select_stratified_records
from src.models.nli_classifier import NLIClassifier

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="cross-encoder/nli-deberta-v3-small")
    parser.add_argument("--split", default="test", choices=["dev", "test"])
    parser.add_argument("--limit", type=int)
    parser.add_argument("--per-class", type=int, help="Deterministic balanced document cap for development/smoke evaluation.")
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    parser.add_argument("--output", default="reports/evaluation/contractnli_metrics.json")
    args = parser.parse_args()
    records = load_split("dataset/unified/contractnli_unified.jsonl", args.split)
    if args.per_class:
        records = select_stratified_records(records, args.per_class)
    elif args.limit:
        records = records[:args.limit]
    errors = validate_evidence(records)
    if errors: raise ValueError(f"Invalid evidence offsets: {errors[:5]}")
    selected_device = None if args.device == "auto" else args.device
    model = NLIClassifier(args.model, device=selected_device, max_length=args.max_length)
    prepared = []
    for record in records:
        for item in prepare_examples(record):
            prepared.append((item, record["label"]))
    predictions = []
    for (item, target), result in zip(prepared, model.predict_batch([(item["context"], item["hypothesis"]) for item, _ in prepared], batch_size=args.batch_size)):
        predictions.append({"example_id": item["example_id"], "target_label": target, **result})
    final = aggregate_window_predictions(predictions)
    output = {"protocol": "Evidence spans center positive examples; no-evidence documents use coverage windows with conservative document aggregation. This is an approximation of document-level ContractNLI.", "model": args.model, "device": str(model.device), "max_length": args.max_length, "split": args.split, "records": len(records), "metrics": metrics([x["label"] for x in final], [x["prediction"] for x in final]), "misclassified": [x for x in final if x["label"] != x["prediction"]][:100]}
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    Path(args.output).write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output["metrics"], indent=2))
if __name__ == "__main__": main()
