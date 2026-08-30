"""
Template type parser registry.

Each entry maps a template type name (matching the "type" field in zen-templates.json)
to a parser module that implements the following interface:

    REQUIRED_CSV_COLUMNS : set[str]
        CSV column names that must be present in the input file.

    HEADER_SKIP_LINES : int  (optional, default 0)
        Number of leading lines to skip before the CSV header row.

    parse_csv_rows(rows: list[dict]) -> list
        Convert raw CSV row dicts to parser model instances.

    generate_text(client, template, language, operator, location=None) -> str
        Render the filled template string for a given client.

    render_ui_groups(app) -> None
        Populate the dynamic UI panel with controls needed for this template type.

    needs_location() -> bool
        Whether this template type requires a location to be selected.

--- How to add a new template type ---
1. Create a new module in src/parsers/, e.g. src/parsers/MyTypeParser.py, implementing
   the interface above.
2. Import it here and add it to REGISTRY with a key matching the "type" value used in
   your zen-templates.json entries.
3. No changes to the main application file are needed.
"""

from src.parsers import AppointmentsParser, CustomersParser, SurveysParser

# Central registry: template_type (str) → parser module
REGISTRY = {
    "Appointments": AppointmentsParser,
    "Customers": CustomersParser,
    "Surveys": SurveysParser,
}


def get_parser(template_type: str):
    """
    Return the parser module for the given template type, or raise KeyError
    if the type is not registered.
    """
    if template_type not in REGISTRY:
        raise KeyError(f"Unknown template type: '{template_type}'. "
                       f"Registered types: {list(REGISTRY.keys())}")
    return REGISTRY[template_type]
