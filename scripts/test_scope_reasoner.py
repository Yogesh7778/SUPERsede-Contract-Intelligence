from src.reasoning.scope_reasoner import ScopeReasoner


def main():
    reasoner = ScopeReasoner()

    original_clause = {
        "contract_id": "CON-001",
        "project_id": "PROJECT-A",
        "parties": ["Company A", "Company B"],
        "service_scope": "Cloud hosting"
    }

    same_scope_clause = {
        "contract_id": "CON-001",
        "project_id": "PROJECT-A",
        "parties": ["Company A", "Company B"],
        "service_scope": "Cloud hosting"
    }

    different_scope_clause = {
        "contract_id": "CON-001",
        "project_id": "PROJECT-B",
        "parties": ["Company A", "Company B"],
        "service_scope": "Software development"
    }

    incomplete_scope_clause = {
        "contract_id": "CON-001",
        "project_id": None,
        "parties": ["Company A", "Company B"],
        "service_scope": "Cloud hosting"
    }

    test_cases = [
        ("Same scope", original_clause, same_scope_clause, "SAME_SCOPE"),
        ("Different scope", original_clause, different_scope_clause, "DIFFERENT_SCOPE"),
        ("Incomplete scope", original_clause, incomplete_scope_clause, "UNCERTAIN_SCOPE")
    ]

    passed = 0

    for name, clause_a, clause_b, expected in test_cases:
        result = reasoner.compare_scope(clause_a, clause_b)

        status = "PASS" if result["overall"] == expected else "FAIL"

        print(f"\n{name}: {status}")
        print("Expected:", expected)
        print("Actual:", result["overall"])
        print("Details:", result["details"])

        if result["overall"] == expected:
            passed += 1

    print(f"\nFinal result: {passed}/{len(test_cases)} tests passed.")


if __name__ == "__main__":
    main()
