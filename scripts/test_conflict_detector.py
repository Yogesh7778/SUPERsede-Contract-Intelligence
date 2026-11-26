from src.models.semantic_matcher import SemanticMatcher
from src.models.nli_classifier import NLIClassifier

from src.reasoning.temporal_reasoner import TemporalReasoner
from src.reasoning.scope_reasoner import ScopeReasoner
from src.reasoning.precedence_reasoner import PrecedenceReasoner
from src.reasoning.conflict_detector import ConflictDetector


def main():

    print("Loading models and reasoning components...")

    semantic_matcher = SemanticMatcher()
    nli_classifier = NLIClassifier()

    temporal_reasoner = TemporalReasoner()
    scope_reasoner = ScopeReasoner()
    precedence_reasoner = PrecedenceReasoner()

    detector = ConflictDetector(
        semantic_matcher=semantic_matcher,
        nli_classifier=nli_classifier,
        temporal_reasoner=temporal_reasoner,
        scope_reasoner=scope_reasoner,
        precedence_reasoner=precedence_reasoner
    )

    test_cases = [
        {
            "name": "Potential Contradiction",
            "clause_a": "The monthly service fee shall be INR 50,000.",
            "clause_b": "The monthly service fee shall be INR 60,000."
        },
        {
            "name": "Entailment",
            "clause_a": "The customer shall pay INR 50,000 every month.",
            "clause_b": "The monthly service fee is INR 50,000."
        },
        {
            "name": "Unrelated Clauses",
            "clause_a": "The monthly service fee shall be INR 50,000.",
            "clause_b": "The agreement shall remain confidential."
        }
    ]

    for test in test_cases:

        print("\n" + "=" * 60)
        print("TEST:", test["name"])

        result = detector.compare_clauses(
            test["clause_a"],
            test["clause_b"]
        )

        for key, value in result.items():
            print(f"{key}: {value}")


if __name__ == "__main__":
    main()
