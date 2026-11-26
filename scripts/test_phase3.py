from pathlib import Path

from src.document_processing.document_processor import DocumentProcessor
from src.models.semantic_matcher import SemanticMatcher
from src.models.nli_classifier import NLIClassifier

from src.reasoning.temporal_reasoner import TemporalReasoner
from src.reasoning.scope_reasoner import ScopeReasoner
from src.reasoning.precedence_reasoner import PrecedenceReasoner
from src.reasoning.conflict_detector import ConflictDetector
from src.reasoning.document_comparison_pipeline import DocumentComparisonPipeline


def check(name, condition):
    status = "PASS" if condition else "FAIL"
    print(f"{status}: {name}")
    return condition


def main():

    print("\n====================================")
    print("SUPERSede PHASE 3 VALIDATION")
    print("====================================")

    passed = 0
    failed = 0

    # Initialize document processor.
    processor = DocumentProcessor()

    # Initialize deep-learning models.
    print("\nLoading deep-learning models...")

    semantic_matcher = SemanticMatcher()
    nli_classifier = NLIClassifier()

    # Initialize reasoning components.
    temporal_reasoner = TemporalReasoner()
    scope_reasoner = ScopeReasoner()
    precedence_reasoner = PrecedenceReasoner()

    detector = ConflictDetector(
        semantic_matcher,
        nli_classifier,
        temporal_reasoner,
        scope_reasoner,
        precedence_reasoner
    )

    pipeline = DocumentComparisonPipeline(detector)

    # -------------------------------------------------
    # TEST 1: Scope reasoning - same scope
    # -------------------------------------------------

    print("\nTEST 1: SAME SCOPE")

    same_scope = {
        "contract_id": "CTR-001",
        "project_id": "PROJ-101",
        "parties": ["ABC Technologies", "XYZ Solutions"],
        "service_scope": "Software Development"
    }

    scope_result = scope_reasoner.compare_scope(
        same_scope,
        same_scope.copy()
    )

    result = check(
        "Same scope identified",
        scope_result["overall"] == "SAME_SCOPE"
    )
    passed += result
    failed += not result

    # -------------------------------------------------
    # TEST 2: Different scope
    # -------------------------------------------------

    print("\nTEST 2: DIFFERENT SCOPE")

    different_scope = {
        "contract_id": "CTR-002",
        "project_id": "PROJ-202",
        "parties": ["ABC Technologies", "XYZ Solutions"],
        "service_scope": "Cloud Infrastructure"
    }

    scope_result = scope_reasoner.compare_scope(
        same_scope,
        different_scope
    )

    result = check(
        "Different scope identified",
        scope_result["overall"] == "DIFFERENT_SCOPE"
    )
    passed += result
    failed += not result

    # -------------------------------------------------
    # TEST 3: Incomplete scope
    # -------------------------------------------------

    print("\nTEST 3: INCOMPLETE SCOPE")

    incomplete_scope = {
        "contract_id": "CTR-001",
        "project_id": None,
        "parties": ["ABC Technologies", "XYZ Solutions"],
        "service_scope": None
    }

    scope_result = scope_reasoner.compare_scope(
        same_scope,
        incomplete_scope
    )

    result = check(
        "Incomplete scope identified",
        scope_result["overall"] == "UNCERTAIN_SCOPE"
    )
    passed += result
    failed += not result

    # -------------------------------------------------
    # TEST 4: Pack-level classification
    # -------------------------------------------------

    print("\nTEST 4: PACK-LEVEL CLASSIFICATION")

    classification_tests = [
        (
            "Conflict classification",
            [
                {
                    "potential_conflict": True,
                    "requires_review": False,
                    "nli_label": "contradiction",
                    "scope_status": "SAME_SCOPE",
                    "precedence_status": "INSUFFICIENT_INFORMATION"
                }
            ],
            "CONFLICT"
        ),
        (
            "Superseded candidate classification",
            [
                {
                    "potential_conflict": False,
                    "requires_review": True,
                    "nli_label": "contradiction",
                    "scope_status": "SAME_SCOPE",
                    "precedence_status": "PRECEDENCE_ESTABLISHED"
                }
            ],
            "SUPERSEDED"
        ),
        (
            "Consistent classification",
            [
                {
                    "potential_conflict": False,
                    "requires_review": False,
                    "nli_label": "entailment",
                    "scope_status": "SAME_SCOPE",
                    "precedence_status": "INSUFFICIENT_INFORMATION"
                }
            ],
            "CONSISTENT"
        ),
        (
            "Uncertain classification",
            [
                {
                    "potential_conflict": False,
                    "requires_review": True,
                    "nli_label": "neutral",
                    "scope_status": "UNCERTAIN_SCOPE",
                    "precedence_status": "INSUFFICIENT_INFORMATION"
                }
            ],
            "UNCERTAIN"
        )
    ]

    for name, comparisons, expected in classification_tests:

        classification = pipeline.classify_document_pair(
            comparisons
        )

        result = check(
            name,
            classification["label"] == expected
        )

        passed += result
        failed += not result

    # -------------------------------------------------
    # TEST 5: End-to-end document comparison
    # -------------------------------------------------

    print("\nTEST 5: END-TO-END DOCUMENT COMPARISON")

    original_file = Path("scripts/original_test.txt")
    amendment_file = Path("scripts/amendment_test.txt")

    original_text = """
SERVICE AGREEMENT

Agreement ID: AGR-001
Contract ID: CTR-001
Project ID: PROJ-101
Service Scope: Software Development

First Party: ABC Technologies
Second Party: XYZ Solutions

Effective Date: 2026-01-01
Expiry Date: 2026-12-31
Status: Signed

1. Definitions
This agreement establishes the terms between the parties.

2. Payment Terms
The customer shall pay INR 50,000 every month.

3. Confidentiality
Both parties shall maintain confidentiality of all shared information.
"""

    amendment_text = """
AMENDMENT AGREEMENT

Agreement ID: AGR-001
Contract ID: CTR-001
Project ID: PROJ-101
Service Scope: Software Development
Amends Agreement: AGR-001

First Party: ABC Technologies
Second Party: XYZ Solutions

Effective Date: 2026-06-01
Status: Signed

1. Definitions
This amendment modifies the original service agreement.

2. Payment Terms
The customer shall pay INR 60,000 every month.

3. Confidentiality
Both parties shall maintain confidentiality of all shared information.
"""

    original_file.write_text(original_text, encoding="utf-8")
    amendment_file.write_text(amendment_text, encoding="utf-8")

    original_document = processor.process_document(
        original_file,
        "AGR-001",
        "original"
    )

    amendment_document = processor.process_document(
        amendment_file,
        "amendment-001",
        "amendment"
    )

    result = check(
        "Original contract metadata extracted",
        original_document["metadata"]["contract_id"] == "CTR-001"
    )
    passed += result
    failed += not result

    result = check(
        "Amendment relationship extracted",
        amendment_document["metadata"]["explicitly_amends"] == "AGR-001"
    )
    passed += result
    failed += not result

    comparison = pipeline.compare_documents(
        original_document,
        amendment_document,
        evaluation_date="2026-07-01",
        similarity_threshold=0.50
    )

    result = check(
        "All 9 clause comparisons completed",
        comparison["total_comparisons"] == 9
    )
    passed += result
    failed += not result

    result = check(
        "Payment contradiction detected with precedence review",
        any(
            item["comparison"].get("nli_label") == "contradiction"
            and item["comparison"].get("precedence_status")
            == "PRECEDENCE_ESTABLISHED"
            for item in comparison["results"]
        )
    )
    passed += result
    failed += not result

    result = check(
        "Overall classification generated",
        comparison["classification"]["label"] in (
            "CONFLICT",
            "SUPERSEDED",
            "CONSISTENT",
            "UNCERTAIN"
        )
    )
    passed += result
    failed += not result

    print("\nDOCUMENT PAIR CLASSIFICATION")
    print(comparison["classification"])

    # -------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------

    print("\n====================================")
    print("PHASE 3 VALIDATION SUMMARY")
    print("====================================")

    print("Passed:", passed)
    print("Failed:", failed)
    print("Total:", passed + failed)

    if failed == 0:
        print("\nALL PHASE 3 VALIDATION TESTS PASSED!")
    else:
        print("\nSOME TESTS FAILED. REVIEW THE OUTPUT.")


if __name__ == "__main__":
    main()
