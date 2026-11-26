"""Memory-conscious, document-level MIL fine tuning on ContractNLI."""
import argparse, json, random, sys, platform
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from transformers import AutoModelForSequenceClassification, AutoTokenizer, get_linear_schedule_with_warmup

from src.evaluation.contractnli import LABEL_TO_ID, load_split, prepare_examples, select_stratified_records, validate_evidence


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def select_device(requested):
    if requested == "auto":
        requested = "mps" if torch.backends.mps.is_available() else "cpu"
    if requested == "mps" and not torch.backends.mps.is_available():
        raise RuntimeError("MPS was requested but is unavailable")
    return torch.device(requested)


def make_documents(records):
    """One target per document; NotMentioned windows are never separately labelled."""
    return [{"example_id": r["example_id"], "label": LABEL_TO_ID[r["label"]], "contexts": prepare_examples(r)} for r in records]


def collate(tokenizer, documents, max_length):
    flat, owners = [], []
    for doc_index, document in enumerate(documents):
        for context in document["contexts"]:
            flat.append(context)
            owners.append(doc_index)
    encoded = tokenizer(
        [item["context"] for item in flat],
        [item["hypothesis"] for item in flat],
        truncation=True, max_length=max_length, padding=True, return_tensors="pt",
    )
    return encoded, torch.tensor(owners), torch.tensor([item["label"] for item in documents])


def document_logits(window_logits, owners, count):
    """Max-pool per-class window evidence into one differentiable document prediction."""
    result = torch.full((count, window_logits.shape[1]), -float("inf"), device=window_logits.device)
    return result.scatter_reduce(0, owners[:, None].expand_as(window_logits), window_logits, reduce="amax", include_self=True)


def run_epoch(model, loader, optimizer, scheduler, target_device, accumulation=1):
    training = optimizer is not None
    model.train(training)
    loss_sum, batches = 0.0, 0
    if training:
        optimizer.zero_grad()
    for step, (encoded, owners, labels) in enumerate(loader, 1):
        encoded = {key: value.to(target_device) for key, value in encoded.items()}
        owners, labels = owners.to(target_device), labels.to(target_device)
        with torch.set_grad_enabled(training):
            logits = document_logits(model(**encoded).logits, owners, len(labels))
            loss = F.cross_entropy(logits, labels)
            if training:
                (loss / accumulation).backward()
                if step % accumulation == 0 or step == len(loader):
                    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                    optimizer.step()
                    scheduler.step()
                    optimizer.zero_grad()
        loss_sum += loss.item()
        batches += 1
    return loss_sum / max(batches, 1)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="cross-encoder/nli-deberta-v3-small")
    parser.add_argument("--output", default="models/checkpoints/contractnli-deberta")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--grad-accumulation", type=int, default=8)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--device", choices=["auto", "cpu", "mps"], default="auto")
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--train-per-class", type=int, help="Balanced document-level cap per label.")
    parser.add_argument("--dev-per-class", type=int, help="Optional validation cap for smoke tests only.")
    args = parser.parse_args()
    seed_everything(args.seed)

    train_records = load_split("dataset/unified/contractnli_unified.jsonl", "train")
    dev_records = load_split("dataset/unified/contractnli_unified.jsonl", "dev")
    if validate_evidence(train_records + dev_records):
        raise ValueError("Evidence integrity validation failed")
    train_records = select_stratified_records(train_records, args.train_per_class, args.seed)
    dev_records = select_stratified_records(dev_records, args.dev_per_class, args.seed)
    train, dev = make_documents(train_records), make_documents(dev_records)

    tokenizer = AutoTokenizer.from_pretrained(args.model)
    target_device = select_device(args.device)
    if target_device.type == "mps" and args.batch_size > 1:
        raise ValueError("Use --batch-size 1 on 8 GB MPS hardware; increase gradient accumulation instead.")
    model = AutoModelForSequenceClassification.from_pretrained(args.model).to(target_device)
    expected_mapping = {0: "contradiction", 1: "entailment", 2: "neutral"}
    if model.config.id2label != expected_mapping:
        raise ValueError(f"Unexpected model label mapping: {model.config.id2label}")
    collator = lambda values: collate(tokenizer, values, args.max_length)
    train_loader = DataLoader(train, batch_size=args.batch_size, shuffle=True, collate_fn=collator)
    dev_loader = DataLoader(dev, batch_size=args.batch_size, collate_fn=collator)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.learning_rate)
    total_steps = max(1, (len(train_loader) * args.epochs + args.grad_accumulation - 1) // args.grad_accumulation)
    scheduler = get_linear_schedule_with_warmup(optimizer, 0, total_steps)

    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    best_loss, history, patience = float("inf"), [], 0
    for epoch in range(args.epochs):
        train_loss = run_epoch(model, train_loader, optimizer, scheduler, target_device, args.grad_accumulation)
        dev_loss = run_epoch(model, dev_loader, None, None, target_device)
        record = {"epoch": epoch + 1, "train_loss": train_loss, "dev_loss": dev_loss}
        history.append(record)
        print(record, flush=True)
        if dev_loss < best_loss:
            best_loss, patience = dev_loss, 0
            model.save_pretrained(out)
            tokenizer.save_pretrained(out)
        else:
            patience += 1
            if patience >= 2:
                break
    metadata = {
        "arguments": vars(args), "device": str(target_device),
        "mps_available": torch.backends.mps.is_available(), "platform": platform.platform(),
        "label_to_id": LABEL_TO_ID, "train_documents": len(train), "dev_documents": len(dev),
        "train_label_distribution": Counter(record["label"] for record in train_records),
        "dev_label_distribution": Counter(record["label"] for record in dev_records),
        "history": history, "best_dev_loss": best_loss,
        "methodology": "Positive labels use verified evidence contexts. NotMentioned uses multi-window document-level max pooling; chunks have no independent labels.",
    }
    (out / "training_history.json").write_text(json.dumps(metadata, indent=2, default=dict), encoding="utf-8")


if __name__ == "__main__":
    main()
