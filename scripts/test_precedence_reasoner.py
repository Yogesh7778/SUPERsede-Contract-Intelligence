from src.reasoning.precedence_reasoner import PrecedenceReasoner


def main():
    reasoner = PrecedenceReasoner()

    original_agreement = {
        "document_id": "agreement-001",
        "document_type": "agreement",
        "signed": True,
        "explicitly_amends": []
    }

    signed_amendment = {
        "document_id": "amendment-001",
        "document_type": "amendment",
        "signed": True,
        "explicitly_amends": ["agreement-001"]
    }

    unsigned_amendment = {
        "document_id": "amendment-002",
        "document_type": "amendment",
        "signed": False,
        "explicitly_amends": ["agreement-001"]
    }

    test_cases = [
        (
            "Signed amendment",
            original_agreement,
            signed_amendment,
            "amendment-001"
        ),
        (
            "Unsigned amendment",
            original_agreement,
            unsigned_amendment,
            None
        )
    ]

    passed = 0

    for name, document_a, document_b, expected in test_cases:

        result = reasoner.determine_precedence(
            document_a,
            document_b
        )

        actual = result["higher_priority"]

        status = "PASS" if actual == expected else "FAIL"

        print(f"\n{name}: {status}")
        print("Expected:", expected)
        print("Actual:", actual)
        print("Reason:", result["reason"])

        if actual == expected:
            passed += 1

    print(f"\nFinal result: {passed}/{len(test_cases)} tests passed.")


if __name__ == "__main__":
    main()
