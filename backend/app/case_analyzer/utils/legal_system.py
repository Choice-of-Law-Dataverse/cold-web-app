"""Shared predicates for legal-system-dependent analysis branches."""


def requires_common_law_steps(legal_system: str | None, jurisdiction: str | None) -> bool:
    """Whether obiter dicta and dissenting opinions steps apply to this decision."""
    if legal_system and legal_system.strip().lower() == "common-law jurisdiction":
        return True
    if jurisdiction and jurisdiction.strip().lower() == "india":
        return True
    return False
