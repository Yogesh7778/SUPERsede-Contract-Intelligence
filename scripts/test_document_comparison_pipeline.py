from pathlib import Path
from src.document_processing.document_processor import DocumentProcessor
from src.models.semantic_matcher import SemanticMatcher
from src.models.nli_classifier import NLIClassifier
from src.reasoning.temporal_reasoner import TemporalReasoner
from src.reasoning.scope_reasoner import ScopeReasoner
from src.reasoning.precedence_reasoner import PrecedenceReasoner
from src.reasoning.conflict_detector import ConflictDetector
from src.reasoning.document_comparison_pipeline import DocumentComparisonPipeline

def main():

    print("Loading document processing and reasoning components...")

    # Step 1: Initialize document processor.
    processor = DocumentProcessor()

    # Step 2: Initialize deep learning models.
    semantic_matcher = SemanticMatcher()
    nli_classifier = NLIClassifier()

    # Step 3: Initialize reasoning components.
    temporal_reasoner = TemporalReasoner()
    scope_reasoner = ScopeReasoner()
    precedence_reasoner = PrecedenceReasoner()

    # Step 4: Initialize conflict detector.
    detector = ConflictDetector(
        semantic_matcher=semantic_matcher,
        nli_classifier=nli_classifier,
        temporal_reasoner=temporal_reasoner,
        scope_reasoner=scope_reasoner,
        precedence_reasoner=precedence_reasoner
    )

    # Step 5: Initialize document comparison pipeline.
    pipeline = DocumentComparisonPipeline(detector)

    # Step 6: Create original agreement.
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

    # Step 7: Create amendment.
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

    original_file = Path("scripts/original_test.txt")
    amendment_file = Path("scripts/amendment_test.txt")

    original_file.write_text(original_text, encoding="utf-8")
    amendment_file.write_text(amendment_text, encoding="utf-8")

    # Step 8: Process both documents.
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
    print("\nORIGINAL DOCUMENT METADATA")
    print(original_document["metadata"])

    print("\nAMENDMENT DOCUMENT METADATA")
    print(amendment_document["metadata"])

    # Step 9: Compare the two structured documents.
    results = pipeline.compare_documents(
        document_a=original_document,
        document_b=amendment_document,
        evaluation_date="2026-07-01",
        similarity_threshold=0.50
    )

    # Step 10: Display results.
    print("\nDOCUMENT COMPARISON RESULTS")
    print("===========================")

    print("Original:", results["document_a"])
    print("Amendment:", results["document_b"])
    print("Total comparisons:", results["total_comparisons"])

    for item in results["results"]:

        comparison = item["comparison"]

        print("\n-----------------------------")

        print(
            "Clause Pair:",
            item["clause_a_number"],
            "vs",
            item["clause_b_number"]
        )

        print("Similarity:", comparison.get("similarity"))
        print("Scope Status:", comparison.get("scope_status"))
        print("NLI Label:", comparison.get("nli_label"))
        print("Potential Conflict:", comparison.get("potential_conflict"))
        print("Requires Review:", comparison.get("requires_review"))
        print("Reason:", comparison.get("reason"))


if __name__ == "__main__":
    main()
