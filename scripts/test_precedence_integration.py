from src.models.semantic_matcher import SemanticMatcher
from src.models.nli_classifier import NLIClassifier

from src.reasoning.temporal_reasoner import TemporalReasoner
from src.reasoning.scope_reasoner import ScopeReasoner
from src.reasoning.precedence_reasoner import PrecedenceReasoner
from src.reasoning.conflict_detector import ConflictDetector


def main():

    detector = ConflictDetector(
        semantic_matcher=SemanticMatcher(),
        nli_classifier=NLIClassifier(),
        temporal_reasoner=TemporalReasoner(),
        scope_reasoner=ScopeReasoner(),
        precedence_reasoner=PrecedenceReasoner()
    )

    clause_a = "The monthly service fee shall be INR 50,000."
    clause_b = "The monthly service fee shall be INR 60,000."

    original = {
        "document_id": "original-agreement",
        "explicitly_amends": [],
        "signed": True
    }

    signed_amendment = {
        "document_id": "amendment-001",
        "explicitly_amends": ["original-agreement"],
        "signed": True
    }

    unsigned_amendment = {
        "document_id": "amendment-002",
        "explicitly_amends": ["original-agreement"],
        "signed": False
    }

    test_cases = [
        {
            "name": "Signed amendment",
            "document_a": original,
            "document_b": signed_amendment,
            "expected": "PRECEDENCE_ESTABLISHED",
            "expected_conflict": False,
            "expected_review": True
        },
        {
            "name": "Unsigned amendment",
            "document_a": original,
            "document_b": unsigned_amendment,
            "expected": "INSUFFICIENT_INFORMATION",
            "expected_conflict": True,
            "expected_review": False
        }
    ]

    passed = 0

    for test in test_cases:

        print("\n" + "=" * 60)
        print("TEST:", test["name"])

        result = detector.compare_clauses(
            clause_a=clause_a,
            clause_b=clause_b,
            document_a=test["document_a"],
            document_b=test["document_b"]
        )

        print("Precedence:", result["precedence_status"])
        print("NLI:", result["nli_label"])
        print("Potential conflict:", result["potential_conflict"])
        print("Requires review:", result["requires_review"])
        print("Reason:", result["reason"])

        checks = [
            result["precedence_status"] == test["expected"],
            result["potential_conflict"] == test["expected_conflict"],
            result["requires_review"] == test["expected_review"]
        ]

        if all(checks):
            print("Result: PASS")
            passed += 1
        else:
            print("Result: FAIL")

    print("\nFinal result:", passed, "/", len(test_cases), "tests passed")


if __name__ == "__main__":
    main()
