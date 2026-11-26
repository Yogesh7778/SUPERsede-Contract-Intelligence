from src.reasoning.temporal_reasoner import TemporalReasoner

def main():
    reasoner = TemporalReasoner()

    terms = [
        {
            "document_id": "original-agreement",
            "amount": 50000,
            "effective_date": "2026-01-01",
            "expiry_date": "2026-09-30"
        },
        {
            "document_id": "amendment-1",
            "amount": 60000,
            "effective_date": "2026-10-01",
            "expiry_date": None
        }
    ]

    test_dates = [
        "2026-09-15",
        "2026-10-15"
    ]

    for evaluation_date in test_dates:
        print("\nEvaluation date:", evaluation_date)

        applicable = reasoner.get_applicable_terms(
            terms,
            evaluation_date
        )

        for term in applicable:
            print(
                term["document_id"],
                "| Monthly fee: INR",
                term["amount"]
            )

        print("Applicable terms found:", len(applicable))


if __name__ == "__main__":
    main()
