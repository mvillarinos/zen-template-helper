# CSV column aliases → canonical names. Existing column names are kept as primary keys
# for backward compatibility with existing Booker survey CSV exports.
CSV_ALIASES = {
    "CustomerName": "name",
    "Phone": "phone",
    "Email": "email",
}

# Required CSV columns (original names) for validation
REQUIRED_CSV_COLUMNS = {"CustomerName", "Phone"}

# Number of header lines to skip in survey CSVs (Booker adds question headers)
HEADER_SKIP_LINES = 3


class SurveysParser:
    """
    Represents a parsed survey respondent record.

    CSV inputs use the original Booker column names (CustomerName, Phone, Email).
    """

    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def __repr__(self):
        return f"{self.name} ({self.phone})"


def parse_csv_rows(rows):
    """Parse a list of raw CSV row dicts into SurveysParser instances."""
    return [
        SurveysParser(
            name=row['CustomerName'],
            phone=row['Phone'] if row.get('Phone') else row.get('Email', '')
        )
        for row in rows
    ]


def generate_text(client, template, language, operator, location=None):
    """Generate the filled template text for a Surveys client."""
    return template['template'][language].format(
        FirstName=client.name,
        Location=location['text'][language] if location else '',
        Operator=operator
    )


def render_ui_groups(app):
    """Render the UI dynamic groups required for the Surveys template type."""
    app.render_operator_group()
    app.render_location_group()


def needs_location():
    return True
