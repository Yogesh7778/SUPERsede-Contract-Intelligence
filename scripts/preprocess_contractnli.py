import json
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]

SOURCE_DIR = ROOT / "dataset" / "public" / "contract-nli"
OUTPUT_DIR = ROOT / "dataset" / "processed" / "contractnli"


def load_json(path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def process_split(split_name):
    source_path = SOURCE_DIR / f"{split_name}.json"

    if not source_path.exists():
        raise FileNotFoundError(f"Missing file: {source_path}")

    raw_data = load_json(source_path)

    documents = raw_data["documents"]
    hypotheses = raw_data["labels"]

    processed_records = []
    label_counts = Counter()
    evidence_count = 0
    skipped_count = 0

    for document in documents:
        document_id = document["id"]
        document_text = document["text"]
        spans = document["spans"]

        for annotation_set in document["annotation_sets"]:
            annotations = annotation_set["annotations"]

            for hypothesis_id, annotation in annotations.items():

                if hypothesis_id not in hypotheses:
                    skipped_count += 1
                    continue

                choice = annotation["choice"]
                evidence_indices = annotation.get("spans", [])

                evidence = []

                for span_index in evidence_indices:
                    if not isinstance(span_index, int):
                        continue

                    if span_index < 0 or span_index >= len(spans):
                        continue

                    start, end = spans[span_index]

                    if start < 0 or end > len(document_text) or start > end:
                        continue

                    evidence_text = document_text[start:end]

                    evidence.append({
                        "span_index": span_index,
                        "start": start,
                        "end": end,
                        "text": evidence_text
                    })

                if evidence:
                    evidence_count += len(evidence)

                processed_records.append({
                    "document_id": document_id,
                    "file_name": document["file_name"],
                    "document_type": document.get("document_type"),
                    "document_url": document.get("url"),
                    "hypothesis_id": hypothesis_id,
                    "hypothesis_description":
                        hypotheses[hypothesis_id]["short_description"],
                    "hypothesis": hypotheses[hypothesis_id]["hypothesis"],
                    "contract_text": document_text,
                    "label": choice,
                    "evidence": evidence
                })

                label_counts[choice] += 1

    output_path = OUTPUT_DIR / f"{split_name}_processed.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            processed_records,
            file,
            indent=2,
            ensure_ascii=False
        )

    print(f"\n{split_name.upper()} SPLIT")
    print("-" * 40)
    print("Documents:", len(documents))
    print("Processed records:", len(processed_records))
    print("Label distribution:", dict(label_counts))
    print("Evidence spans:", evidence_count)
    print("Skipped annotations:", skipped_count)
    print("Saved:", output_path)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for split in ["train", "dev", "test"]:
        process_split(split)

    print("\nContractNLI preprocessing completed!")


if __name__ == "__main__":
    main()
