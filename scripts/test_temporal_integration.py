from src.models.semantic_matcher import SemanticMatcher
from src.models.nli_classifier import NLIClassifier

from src.reasoning.temporal_reasoner import TemporalReasoner
from src.reasoning.scope_reasoner import ScopeReasoner
from src.reasoning.precedence_reasoner import PrecedenceReasoner
from src.reasoning.conflict_detector import ConflictDetector


def main():

    print("Loading components...")

    detector = ConflictDetector(
        semantic_matcher=SemanticMatcher(),
        nli_classifier=NLIClassifier(),
        temporal_reasoner=TemporalReasoner(),
        scope_reasoner=ScopeReasoner(),
        precedence_reasoner=PrecedenceReasoner()
    )

    clause_a = "The monthly service fee shall be INR 50,000."
    clause_b = "The monthly service fee shall be INR 60,000."

    test_cases = [
        {
            "name": "Both terms applicable",
            "evaluation_date": "2026-10-15",
            "term_a": {
                "document_id": "original-agreement",
                "effective_date": "2026-01-01",
                "expiry_date": None
            },
            "term_b": {
                "document_id": "amendment-001",
                "effective_date": "2026-10-01",
                "expiry_date": None
            },
            "expected": "BOTH_APPLICABLE"
        },
        {
            "name": "Only one term applicable",
            "evaluation_date": "2026-10-15",
            "term_a": {
                "document_id": "original-agreement",
                "effective_date": "2026-01-01",
                "expiry_date": "2026-09-30"
            },
            "term_b": {
                "document_id": "amendment-001",
                "effective_date": "2026-10-01",
                "expiry_date": None
            },
            "expected": "ONLY_ONE_APPLICABLE"
        },
        {
            "name": "Neither term applicable",
            "evaluation_date": "2025-12-15",
            "term_a": {
                "document_id": "original-agreement",
                "effective_date": "2026-01-01",
                "expiry_date": None
            },
            "term_b": {
                "document_id": "amendment-001",
                "effective_date": "2026-10-01",
                "expiry_date": None
            },
            "expected": "NEITHER_APPLICABLE"
        }
    ]

    passed = 0

    for test in test_cases:

        print("\n" + "=" * 60)
        print("TEST:", test["name"])

        result = detector.compare_clauses(
            clause_a=clause_a,
            clause_b=clause_b,
            term_a=test["term_a"],
            term_b=test["term_b"],
            evaluation_date=test["evaluation_date"]
        )

        print("Expected:", test["expected"])
        print("Actual:", result["temporal_status"])
        print("NLI label:", result["nli_label"])
        print("Potential conflict:", result["potential_conflict"])
        print("Reason:", result["reason"])

        if result["temporal_status"] == test["expected"]:
            print("Result: PASS")
            passed += 1
        else:
            print("Result: FAIL")

    print("\nFinal result:", passed, "/", len(test_cases), "tests passed")


if __name__ == "__main__":
    main()
