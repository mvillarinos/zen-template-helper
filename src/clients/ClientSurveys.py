class ClientSurveys:
    def __init__(self, name, phone):
        self.name = name
        self.phone = phone

    def __repr__(self):
        # Return a string representation of the ClientSurveys object.
        return f"{self.name} ({self.phone})"