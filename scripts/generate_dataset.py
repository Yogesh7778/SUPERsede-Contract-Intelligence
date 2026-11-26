from __future__ import annotations
import argparse
import json
import random
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "dataset" / "synthetic"

SCENARIOS = [
    "matching_invoice",
    "valid_amended_invoice",
    "stale_invoice_after_amendment",
    "explicit_supersession",
    "future_effective_amendment",
    "unsigned_amendment",
    "separate_project_scopes",
    "incorrect_purchase_order",
    "separate_sow_obligation",
    "conflicting_delivery_dates",
    "ambiguous_precedence",
    "ambiguous_effective_date",
]

COMPANIES = [
    ("Aster Systems Pvt Ltd", "Bluepeak Technologies Pvt Ltd"),
    ("Northstar Solutions Ltd", "Cedar Labs Pvt Ltd"),
    ("Orion Digital Services Ltd", "Maple Retail Pvt Ltd"),
    ("Vertex Consulting Pvt Ltd", "Silverline Industries Ltd"),
    ("Summit Software Ltd", "Greenfield Logistics Pvt Ltd"),
]

CURRENCIES = ["INR", "USD", "EUR"]


def make_doc(pack_id, doc_id, doc_type, title, party_a, party_b,
             clause_id, subject, clause_text, effective_date,
             signed_status="SIGNED", scope="General services",
             amount=None, currency=None, expiry_date=None,
             related_to=None):
    return {
        "document_id": doc_id,
        "pack_id": pack_id,
        "document_type": doc_type,
        "title": title,
        "party_a": party_a,
        "party_b": party_b,
        "signed_status": signed_status,
        "effective_date": effective_date,
        "expiry_date": expiry_date,
        "scope": scope,
        "clause_id": clause_id,
        "subject": subject,
        "amount": amount,
        "currency": currency,
        "source_page": 1,
        "source_clause_text": clause_text,
        "related_to": related_to or [],
    }


def build_pack(index, scenario, rng):
    pack_id = f"PACK_{index:03d}"
    party_a, party_b = rng.choice(COMPANIES)
    currency = rng.choice(CURRENCIES)
    base = rng.choice([40000, 50000, 65000, 80000])
    updated = base + rng.choice([5000, 10000, 15000])
    month = rng.choice([1, 2, 3, 4, 5, 6])
    start = date(2026, month, 1)
    amendment_date = date(2026, 10, 1)
    invoice_date = date(2026, 10, 15)
    docs = []
    pairs = []

    def add(doc):
        docs.append(doc)
        return doc

    def pair(left, right, label, explanation):
        pairs.append({
            "document_ids": [left["document_id"], right["document_id"]],
            "clause_ids": [left["clause_id"], right["clause_id"]],
            "expected_label": label,
            "explanation": explanation,
            "evidence": [
                {
                    "document_id": left["document_id"],
                    "clause_id": left["clause_id"],
                    "text": left["source_clause_text"],
                },
                {
                    "document_id": right["document_id"],
                    "clause_id": right["clause_id"],
                    "text": right["source_clause_text"],
                },
            ],
        })

    agreement_text = (
        f"The monthly service fee payable by {party_b} to {party_a} "
        f"shall be {currency} {base:,}, effective from {start.isoformat()}."
    )
    agreement = add(make_doc(
        pack_id, f"{pack_id}_DOC_01", "AGREEMENT",
        "Master Services Agreement", party_a, party_b,
        "AGR-FEE-01", "monthly_service_fee", agreement_text,
        start.isoformat(), amount=base, currency=currency,
        scope="General services",
    ))

    if scenario in ("matching_invoice", "valid_amended_invoice",
                    "stale_invoice_after_amendment",
                    "future_effective_amendment",
                    "unsigned_amendment", "ambiguous_effective_date"):
        if scenario != "matching_invoice":
            if scenario == "future_effective_amendment":
                effective = "2026-12-01"
            elif scenario == "ambiguous_effective_date":
                effective = "To be agreed by the parties"
            else:
                effective = "2026-10-01"

            signed = "UNSIGNED" if scenario == "unsigned_amendment" else "SIGNED"
            amendment_text = (
                f"With effect from {effective}, the monthly service fee "
                f"shall change to {currency} {updated:,}. "
                "All other terms remain unchanged."
            )
            amendment = add(make_doc(
                pack_id, f"{pack_id}_DOC_02", "AMENDMENT",
                "Amendment to Master Services Agreement", party_a, party_b,
                "AMD-FEE-01", "monthly_service_fee", amendment_text,
                effective, signed_status=signed, amount=updated,
                currency=currency, scope="General services",
                related_to=[agreement["document_id"]],
            ))

        if scenario == "valid_amended_invoice":
            invoice_amount = updated
            label = "CONSISTENT"
            explanation = "The signed amendment changes the fee and the invoice uses the amended amount."
        elif scenario == "stale_invoice_after_amendment":
            invoice_amount = base
            label = "CONFLICT"
            explanation = "The invoice uses the former fee after the signed amendment's effective date."
        elif scenario == "future_effective_amendment":
            invoice_amount = base
            label = "CONSISTENT"
            explanation = "The invoice predates the amendment's future effective date."
        elif scenario == "unsigned_amendment":
            invoice_amount = updated
            label = "UNCERTAIN"
            explanation = "The invoice uses the proposed amended amount, but the amendment is unsigned."
        elif scenario == "ambiguous_effective_date":
            invoice_amount = updated
            label = "UNCERTAIN"
            explanation = "The amendment does not provide a definite effective date."
        else:
            invoice_amount = base
            label = "CONSISTENT"
            explanation = "The invoice matches the fee stated in the agreement."

        invoice_text = (
            f"Invoice dated {invoice_date.isoformat()} charges "
            f"{currency} {invoice_amount:,} for monthly services."
        )
        invoice = add(make_doc(
            pack_id, f"{pack_id}_DOC_{len(docs)+1:02d}", "INVOICE",
            "Monthly Services Invoice", party_a, party_b,
            "INV-FEE-01", "monthly_service_fee", invoice_text,
            invoice_date.isoformat(), amount=invoice_amount,
            currency=currency, scope="General services",
            related_to=[agreement["document_id"]],
        ))
        comparison_doc = docs[1] if len(docs) > 2 else agreement
        pair(comparison_doc, invoice, label, explanation)

    elif scenario == "explicit_supersession":
        amendment_text = (
            f"This signed amendment expressly replaces Clause AGR-FEE-01. "
            f"The monthly fee shall be {currency} {updated:,} from 2026-10-01."
        )
        amendment = add(make_doc(
            pack_id, f"{pack_id}_DOC_02", "AMENDMENT",
            "Express Supersession Amendment", party_a, party_b,
            "AMD-FEE-01", "monthly_service_fee", amendment_text,
            "2026-10-01", amount=updated, currency=currency,
            related_to=[agreement["document_id"]],
        ))
        pair(agreement, amendment, "SUPERSEDED",
             "The signed amendment explicitly replaces the original fee clause.")

    elif scenario == "separate_project_scopes":
        sow_text = (
            f"For Project Delta only, the parties agree to a separate project "
            f"fee of {currency} {updated:,}. This fee applies only to Project Delta."
        )
        sow = add(make_doc(
            pack_id, f"{pack_id}_DOC_02", "SOW", "Project Delta Statement of Work",
            party_a, party_b, "SOW-FEE-01", "project_fee", sow_text,
            "2026-07-01", amount=updated, currency=currency,
            scope="Project Delta only",
            related_to=[agreement["document_id"]],
        ))
        pair(agreement, sow, "CONSISTENT",
             "The amounts apply to different scopes: general services and Project Delta.")

    elif scenario == "incorrect_purchase_order":
        po_amount = updated
        po_text = (
            f"Purchase order for general services authorizes a monthly amount "
            f"of {currency} {po_amount:,}."
        )
        po = add(make_doc(
            pack_id, f"{pack_id}_DOC_02", "PURCHASE_ORDER",
            "Purchase Order", party_a, party_b, "PO-FEE-01",
            "monthly_service_fee", po_text, "2026-07-01",
            amount=po_amount, currency=currency,
            related_to=[agreement["document_id"]],
        ))
        pair(agreement, po, "CONFLICT",
             "The purchase order amount differs from the agreement for the same scope and period.")

    elif scenario == "separate_sow_obligation":
        sow_text = (
            "The supplier shall provide a quarterly security assessment "
            "and submit a written report within ten business days."
        )
        sow = add(make_doc(
            pack_id, f"{pack_id}_DOC_02", "SOW",
            "Security Assessment Statement of Work", party_a, party_b,
            "SOW-OBL-01", "security_assessment",
            sow_text, "2026-07-01", scope="Security assessment project",
            related_to=[agreement["document_id"]],
        ))
        pair(agreement, sow, "CONSISTENT",
             "The SOW adds a separate obligation and does not contradict the fee clause.")

    elif scenario == "conflicting_delivery_dates":
        sow_text = "The final project deliverable must be submitted by 2026-09-15."
        po_text = "The final project deliverable is required by 2026-09-30."
        sow = add(make_doc(
            pack_id, f"{pack_id}_DOC_02", "SOW", "Project Delivery SOW",
            party_a, party_b, "SOW-DATE-01", "delivery_deadline",
            sow_text, "2026-07-01", scope="Project Delta",
            related_to=[agreement["document_id"]],
        ))
        po = add(make_doc(
            pack_id, f"{pack_id}_DOC_03", "PURCHASE_ORDER",
            "Project Purchase Order", party_a, party_b,
            "PO-DATE-01", "delivery_deadline", po_text,
            "2026-07-02", scope="Project Delta",
            related_to=[sow["document_id"]],
        ))
        pair(sow, po, "CONFLICT",
             "The SOW and purchase order state different delivery deadlines for the same project.")

    elif scenario == "ambiguous_precedence":
        amendment_text = (
            f"The monthly fee is {currency} {updated:,}. "
            "This document does not state whether it replaces the earlier fee clause."
        )
        amendment = add(make_doc(
            pack_id, f"{pack_id}_DOC_02", "AMENDMENT",
            "Unclear Fee Amendment", party_a, party_b,
            "AMD-FEE-01", "monthly_service_fee", amendment_text,
            "2026-10-01", signed_status="UNKNOWN",
            amount=updated, currency=currency,
            related_to=[agreement["document_id"]],
        ))
        pair(agreement, amendment, "UNCERTAIN",
             "The later document differs in amount but its authority and replacement effect are unclear.")

    return {
        "pack_id": pack_id,
        "scenario": scenario,
        "document_ids": [d["document_id"] for d in docs],
        "documents": docs,
        "comparisons": pairs,
        "pack_label": pairs[0]["expected_label"] if pairs else "UNCERTAIN",
    }


def validate(packs):
    errors = []
    seen = set()

    for pack in packs:
        for doc in pack["documents"]:
            doc_id = doc["document_id"]
            if doc_id in seen:
                errors.append(f"Duplicate document ID: {doc_id}")
            seen.add(doc_id)

            try:
                if doc["effective_date"] != "To be agreed by the parties":
                    date.fromisoformat(doc["effective_date"])
            except (TypeError, ValueError):
                errors.append(f"Invalid effective date in {doc_id}")

        for comparison in pack["comparisons"]:
            for evidence in comparison["evidence"]:
                if evidence["document_id"] not in pack["document_ids"]:
                    errors.append(f"Missing evidence document in {pack['pack_id']}")
                if not evidence["text"].strip():
                    errors.append(f"Empty evidence text in {pack['pack_id']}")

    return errors


def write_dataset(packs):
    for folder in ("agreements", "amendments", "sows",
                   "purchase_orders", "invoices", "metadata", "annotations"):
        (OUTPUT / folder).mkdir(parents=True, exist_ok=True)

    all_docs = []
    pack_metadata = []

    for pack in packs:
        pack_metadata.append({
            "pack_id": pack["pack_id"],
            "scenario": pack["scenario"],
            "document_ids": pack["document_ids"],
            "expected_label": pack["pack_label"],
        })

        for doc in pack["documents"]:
            all_docs.append(doc)
            folder = {
                "AGREEMENT": "agreements",
                "AMENDMENT": "amendments",
                "SOW": "sows",
                "PURCHASE_ORDER": "purchase_orders",
                "INVOICE": "invoices",
            }[doc["document_type"]]

            content = f"""# {doc['title']}

**SYNTHETIC DOCUMENT — NOT LEGAL ADVICE**

- Document ID: {doc['document_id']}
- Pack ID: {doc['pack_id']}
- Document type: {doc['document_type']}
- Party A: {doc['party_a']}
- Party B: {doc['party_b']}
- Status: {doc['signed_status']}
- Effective date: {doc['effective_date']}
- Expiry date: {doc['expiry_date'] or 'Not specified'}
- Scope: {doc['scope']}

## {doc['clause_id']} — {doc['subject']}

{doc['source_clause_text']}

"""
            (OUTPUT / folder / f"{doc['document_id']}.md").write_text(
                content, encoding="utf-8"
            )

    ground_truth = {
        "dataset_name": "SUPERSede Synthetic Commercial Document Packs",
        "version": "0.1",
        "labels": ["CONFLICT", "SUPERSEDED", "CONSISTENT", "UNCERTAIN"],
        "packs": [
            {
                "pack_id": p["pack_id"],
                "scenario": p["scenario"],
                "expected_label": p["pack_label"],
                "comparisons": p["comparisons"],
            }
            for p in packs
        ],
    }

    (OUTPUT / "metadata" / "document_packs.json").write_text(
        json.dumps({"packs": pack_metadata, "documents": all_docs}, indent=2),
        encoding="utf-8",
    )
    (OUTPUT / "annotations" / "ground_truth.json").write_text(
        json.dumps(ground_truth, indent=2), encoding="utf-8"
    )

    readme = """# SUPERSede Synthetic Dataset

Version: 0.1

This dataset contains generated commercial-document examples for developing
and testing the SUPERSede prototype. All organizations and document content
are fictional. These examples are not legal advice and are not real contracts.

## Contents
- agreements/: synthetic master agreements
- amendments/: synthetic amendments
- sows/: synthetic statements of work
- purchase_orders/: synthetic purchase orders
- invoices/: synthetic invoices
- metadata/document_packs.json: document and pack metadata
- annotations/ground_truth.json: expected pack and clause-pair labels

## Labels
- CONFLICT: provisions appear incompatible for the same scope and period.
- SUPERSEDED: a later provision expressly replaces an earlier provision.
- CONSISTENT: provisions can both apply without contradiction.
- UNCERTAIN: authority, applicability, or effective date is ambiguous.

## Generate
From the project root, run:

    python scripts/generate_dataset.py

To use a different seed:

    python scripts/generate_dataset.py --seed 123

## Limitations
This is a small synthetic development dataset, not a legal benchmark.
Its labels are generated from scenario templates and have not been
independently validated by legal professionals. Some legal questions,
including signature requirements and document hierarchy, depend on the
underlying contract and jurisdiction. Do not use these examples to make
real legal or payment decisions.
"""
    (OUTPUT / "README.md").write_text(readme, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Generate SUPERSede synthetic data.")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    packs = []
    index = 1

    for scenario in SCENARIOS:
        for _ in range(5):
            packs.append(build_pack(index, scenario, rng))
            index += 1

    errors = validate(packs)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(" -", error)
        raise SystemExit(1)

    write_dataset(packs)

    document_count = sum(len(p["documents"]) for p in packs)
    print("Dataset generated successfully.")
    print(f"Packs: {len(packs)}")
    print(f"Documents: {document_count}")
    print(f"Scenarios: {len(SCENARIOS)}")
    print(f"Output: {OUTPUT}")
    print("Validation: passed")


if __name__ == "__main__":
    main()