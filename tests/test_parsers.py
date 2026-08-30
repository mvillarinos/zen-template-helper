"""
Tests for the template type parser registry and each parser module.

Covers:
- Registry dispatch (get_parser)
- Terminology: template_type replaces client_type in AppointmentsParser
- CSV alias/column compatibility for all three parsers
- parse_csv_rows behavior for Appointments, Customers, Surveys
- Adding a new template type to the registry
"""
import sys
import os
import pytest

# Ensure the project root is on the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.parsers import get_parser, REGISTRY
from src.parsers import AppointmentsParser, CustomersParser, SurveysParser


# ---------------------------------------------------------------------------
# Registry tests
# ---------------------------------------------------------------------------

class TestRegistry:
    def test_known_types_are_registered(self):
        for key in ("Appointments", "Customers", "Surveys"):
            assert key in REGISTRY

    def test_get_parser_returns_correct_module(self):
        assert get_parser("Appointments") is AppointmentsParser
        assert get_parser("Customers") is CustomersParser
        assert get_parser("Surveys") is SurveysParser

    def test_get_parser_raises_for_unknown_type(self):
        with pytest.raises(KeyError, match="Unknown template type"):
            get_parser("NonExistent")

    def test_new_template_type_can_be_added(self):
        """Registering a new type should not require modifying any other file."""
        import types
        dummy = types.ModuleType("DummyParser")
        dummy.REQUIRED_CSV_COLUMNS = {"col"}
        dummy.parse_csv_rows = lambda rows: rows
        dummy.generate_text = lambda *a, **kw: "dummy"
        dummy.render_ui_groups = lambda app: None
        dummy.needs_location = lambda: False

        # Register the new type
        REGISTRY["Dummy"] = dummy
        assert get_parser("Dummy") is dummy

        # Clean up so other tests are not affected
        del REGISTRY["Dummy"]


# ---------------------------------------------------------------------------
# AppointmentsParser tests
# ---------------------------------------------------------------------------

class TestAppointmentsParser:
    def _standalone_row(self):
        return {
            "Customer Name": "Jane Doe",
            "Type": "Standalone",
            "Treatment Name": "Massage",
            "Appointment On": "Jan 15, 2025 10:00 AM",
            "Customer Mobile Phone": "555-1234",
            "Customer Home Phone": "",
            "Group ID": "",
        }

    def test_parse_csv_rows_standalone(self):
        rows = [self._standalone_row()]
        clients = AppointmentsParser.parse_csv_rows(rows)
        assert len(clients) == 1
        c = clients[0]
        assert c.name == "Jane Doe"
        assert c.template_type == "Standalone"
        assert len(c.services) == 1
        assert c.services[0]["service"] == "Massage"

    def test_template_type_attribute_not_client_type(self):
        """Ensure the canonical attribute is template_type, not client_type."""
        rows = [self._standalone_row()]
        client = AppointmentsParser.parse_csv_rows(rows)[0]
        assert hasattr(client, "template_type")
        assert not hasattr(client, "client_type")

    def test_parse_csv_rows_linked_groups_services(self):
        rows = [
            {"Customer Name": "Jane", "Type": "Linked", "Treatment Name": "Massage",
             "Appointment On": "Jan 15, 2025 10:00 AM", "Customer Mobile Phone": "", "Customer Home Phone": "", "Group ID": ""},
            {"Customer Name": "Jane", "Type": "Linked", "Treatment Name": "Facial",
             "Appointment On": "Jan 15, 2025 11:00 AM", "Customer Mobile Phone": "", "Customer Home Phone": "", "Group ID": ""},
        ]
        clients = AppointmentsParser.parse_csv_rows(rows)
        assert len(clients) == 1
        assert len(clients[0].services) == 2

    def test_parse_csv_rows_group(self):
        rows = [
            {"Customer Name": "Alice", "Type": "Group", "Treatment Name": "Massage",
             "Appointment On": "Jan 15, 2025 10:00 AM", "Customer Mobile Phone": "", "Customer Home Phone": "", "Group ID": "G1"},
            {"Customer Name": "Bob", "Type": "Group", "Treatment Name": "Massage",
             "Appointment On": "Jan 15, 2025 10:00 AM", "Customer Mobile Phone": "", "Customer Home Phone": "", "Group ID": "G1"},
        ]
        clients = AppointmentsParser.parse_csv_rows(rows)
        assert len(clients) == 1  # same group
        assert clients[0].get_clients_count() == 2

    def test_required_csv_columns(self):
        assert {"Customer Name", "Type", "Treatment Name"}.issubset(AppointmentsParser.REQUIRED_CSV_COLUMNS)

    def test_header_skip_lines(self):
        assert AppointmentsParser.HEADER_SKIP_LINES == 0

    def test_needs_location(self):
        assert AppointmentsParser.needs_location() is True

    def test_phone_fallback_to_home(self):
        row = {
            "Customer Name": "Jane", "Type": "Standalone", "Treatment Name": "Massage",
            "Appointment On": "Jan 15, 2025 10:00 AM",
            "Customer Mobile Phone": "",
            "Customer Home Phone": "555-9999",
            "Group ID": "",
        }
        clients = AppointmentsParser.parse_csv_rows([row])
        assert clients[0].phone == "555-9999"


# ---------------------------------------------------------------------------
# CustomersParser tests
# ---------------------------------------------------------------------------

class TestCustomersParser:
    def _row(self):
        return {
            "First Name": "Maria",
            "Last Name": "Garcia",
            "Location": "Miami",
            "Primary Phone": "555-0001",
        }

    def test_parse_csv_rows(self):
        clients = CustomersParser.parse_csv_rows([self._row()])
        assert len(clients) == 1
        c = clients[0]
        assert c.name == "Maria"
        assert c.location == "Miami"
        assert c.phone == "555-0001"

    def test_required_csv_columns(self):
        assert {"First Name", "Location"}.issubset(CustomersParser.REQUIRED_CSV_COLUMNS)

    def test_header_skip_lines(self):
        assert CustomersParser.HEADER_SKIP_LINES == 0

    def test_needs_location(self):
        assert CustomersParser.needs_location() is False


# ---------------------------------------------------------------------------
# SurveysParser tests
# ---------------------------------------------------------------------------

class TestSurveysParser:
    def _row(self, phone="555-2222", email=""):
        return {"CustomerName": "Laura", "Phone": phone, "Email": email}

    def test_parse_csv_rows(self):
        clients = SurveysParser.parse_csv_rows([self._row()])
        assert len(clients) == 1
        c = clients[0]
        assert c.name == "Laura"
        assert c.phone == "555-2222"

    def test_phone_fallback_to_email(self):
        clients = SurveysParser.parse_csv_rows([self._row(phone="", email="laura@example.com")])
        assert clients[0].phone == "laura@example.com"

    def test_required_csv_columns(self):
        assert {"CustomerName", "Phone"}.issubset(SurveysParser.REQUIRED_CSV_COLUMNS)

    def test_header_skip_lines(self):
        assert SurveysParser.HEADER_SKIP_LINES == 3

    def test_needs_location(self):
        assert SurveysParser.needs_location() is True
