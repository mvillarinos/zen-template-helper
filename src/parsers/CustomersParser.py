# CSV column aliases → canonical names. Existing column names are kept as primary keys
# for backward compatibility with existing CSV exports.
CSV_ALIASES = {
    "First Name": "name",
    "Last Name": "last_name",
    "Location": "location",
    "Primary Phone": "phone",
}

# Required CSV columns (original names) for validation
REQUIRED_CSV_COLUMNS = {"First Name", "Location"}


class CustomersParser:
    """
    Represents a parsed customer record.

    Internally uses canonical field names. CSV inputs that use legacy column names
    (see CSV_ALIASES) are accepted without any change to column names.
    """

    def __init__(self, name, last_name, location, phone):
        self.name = name
        self.last_name = last_name
        self.location = location
        self.phone = phone

    def __repr__(self):
        return f"{self.name} {self.last_name} ({self.location})"


def parse_csv_rows(rows):
    """Parse a list of raw CSV row dicts into CustomersParser instances."""
    return [
        CustomersParser(
            name=row['First Name'],
            last_name=row.get('Last Name', ''),
            location=row['Location'],
            phone=row.get('Primary Phone', '')
        )
        for row in rows
    ]


def generate_text(client, template, language, operator, location=None):
    """Generate the filled template text for a Customers client."""
    return template['template'][language].format(
        FirstName=client.name,
        Location=client.location,
        Services='',
        Operator=operator
    )


def render_ui_groups(app):
    """Render the UI dynamic groups required for the Customers template type."""
    app.render_operator_group()


def needs_location():
    return False
