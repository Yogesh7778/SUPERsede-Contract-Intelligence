import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

CONTRACTNLI_DIR = ROOT / "dataset" / "processed" / "contractnli"
SYNTHETIC_FILE = (
    ROOT / "dataset" / "synthetic" / "annotations" / "ground_truth.json"
)
OUTPUT_DIR = ROOT / "dataset" / "unified"

CONTRACTNLI_OUTPUT = OUTPUT_DIR / "contractnli_unified.jsonl"
SUPERSede_OUTPUT = OUTPUT_DIR / "supersede_unified.jsonl"
SUMMARY_OUTPUT = OUTPUT_DIR / "dataset_summary.json"

SYNTHETIC_SPLIT_SEED = 123


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_jsonl(path, records):
    with open(path, "w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def process_contractnli():
    records = []

    for split in ["train", "dev", "test"]:
        source = CONTRACTNLI_DIR / f"{split}_processed.json"
        data = load_json(source)

        for item in data:
            records.append({
                "example_id": (
                    f"contractnli_{split}_"
                    f"{item['document_id']}_{item['hypothesis_id']}"
                ),
                "dataset": "ContractNLI",
                "task_type": "clause_level_nli",
                "split": split,
                "document_id": item["document_id"],
                "document_type": item.get("document_type"),
                "hypothesis_id": item["hypothesis_id"],
                "hypothesis": item["hypothesis"],
                "hypothesis_description": item["hypothesis_description"],
                "contract_text": item["contract_text"],
                "label": item["label"],
                "evidence": item["evidence"],
                "document_url": item.get("document_url")
            })

    write_jsonl(CONTRACTNLI_OUTPUT, records)
    return records


def assign_synthetic_splits(packs):
    """
    Split by complete document pack so comparisons from the same
    pack cannot leak across train, validation and test.
    """
    import random

    shuffled = list(packs)
    random.Random(SYNTHETIC_SPLIT_SEED).shuffle(shuffled)

    total = len(shuffled)
    train_end = int(total * 0.70)
    dev_end = int(total * 0.85)

    split_map = {}

    for pack in shuffled[:train_end]:
        split_map[pack["pack_id"]] = "train"

    for pack in shuffled[train_end:dev_end]:
        split_map[pack["pack_id"]] = "dev"

    for pack in shuffled[dev_end:]:
        split_map[pack["pack_id"]] = "test"

    return split_map


def process_synthetic():
    data = load_json(SYNTHETIC_FILE)
    packs = data["packs"]

    split_map = assign_synthetic_splits(packs)
    records = []

    for pack in packs:
        pack_id = pack["pack_id"]
        split = split_map[pack_id]

        for comparison_index, comparison in enumerate(
            pack.get("comparisons", [])
        ):
            records.append({
                "example_id": (
                    f"supersede_{pack_id}_{comparison_index + 1}"
                ),
                "dataset": "SUPERSede_Synthetic",
                "task_type": "cross_document_reasoning",
                "split": split,
                "pack_id": pack_id,
                "scenario": pack["scenario"],
                "pack_label": pack["expected_label"],
                "document_ids": comparison["document_ids"],
                "clause_ids": comparison["clause_ids"],
                "label": comparison["expected_label"],
                "explanation": comparison["explanation"],
                "evidence": comparison["evidence"]
            })

    write_jsonl(SUPERSede_OUTPUT, records)
    return records


def build_summary(contract_records, synthetic_records):
    summary = {
        "project": "SUPERSede",
        "version": "1.0",
        "synthetic_split_seed": SYNTHETIC_SPLIT_SEED,
        "datasets": {}
    }

    for name, records in [
        ("ContractNLI", contract_records),
        ("SUPERSede_Synthetic", synthetic_records)
    ]:
        label_counts = Counter(
            record["label"] for record in records
        )
        split_counts = Counter(
            record["split"] for record in records
        )

        summary["datasets"][name] = {
            "total_records": len(records),
            "label_distribution": dict(label_counts),
            "split_distribution": dict(split_counts)
        }

    summary["total_records"] = (
        len(contract_records) + len(synthetic_records)
    )

    with open(SUMMARY_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    return summary


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("Building unified SUPERSede dataset...\n")

    contract_records = process_contractnli()
    synthetic_records = process_synthetic()

    summary = build_summary(
        contract_records,
        synthetic_records
    )

    print("Dataset generation completed!")
    print("-" * 45)
    print("ContractNLI records:", len(contract_records))
    print("Synthetic records:", len(synthetic_records))
    print("Total records:", summary["total_records"])

    print("\nOutput files:")
    print(CONTRACTNLI_OUTPUT)
    print(SUPERSede_OUTPUT)
    print(SUMMARY_OUTPUT)

    print("\nSummary:")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
