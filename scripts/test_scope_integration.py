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

    common_scope = {
        "contract_id": "contract-001",
        "project_id": "project-alpha",
        "parties": ["Company A", "Company B"],
        "service_scope": "Software development"
    }

    test_cases = [
        {
            "name": "Same scope",
            "scope_a": common_scope,
            "scope_b": common_scope.copy(),
            "expected_scope": "SAME_SCOPE",
            "expected_conflict": True,
            "expected_review": False
        },
        {
            "name": "Different scope",
            "scope_a": common_scope,
            "scope_b": {
                "contract_id": "contract-001",
                "project_id": "project-beta",
                "parties": ["Company A", "Company B"],
                "service_scope": "Software development"
            },
            "expected_scope": "DIFFERENT_SCOPE",
            "expected_conflict": False,
            "expected_review": False
        },
        {
            "name": "Incomplete scope",
            "scope_a": common_scope,
            "scope_b": {
                "contract_id": "contract-001",
                "project_id": None,
                "parties": ["Company A", "Company B"],
                "service_scope": "Software development"
            },
            "expected_scope": "UNCERTAIN_SCOPE",
            "expected_conflict": False,
            "expected_review": True
        }
    ]

    passed = 0

    for test in test_cases:

        print("\n" + "=" * 60)
        print("TEST:", test["name"])

        result = detector.compare_clauses(
            clause_a=clause_a,
            clause_b=clause_b,
            scope_a=test["scope_a"],
            scope_b=test["scope_b"]
        )

        checks = [
            result["scope_status"] == test["expected_scope"],
            result["potential_conflict"] == test["expected_conflict"],
            result["requires_review"] == test["expected_review"]
        ]

        print("Scope status:", result["scope_status"])
        print("NLI label:", result["nli_label"])
        print("Potential conflict:", result["potential_conflict"])
        print("Requires review:", result["requires_review"])
        print("Reason:", result["reason"])

        if all(checks):
            print("Result: PASS")
            passed += 1
        else:
            print("Result: FAIL")
            print("Expected scope:", test["expected_scope"])
            print("Expected conflict:", test["expected_conflict"])
            print("Expected review:", test["expected_review"])

    print("\nFinal result:", passed, "/", len(test_cases), "tests passed")


if __name__ == "__main__":
    main()
