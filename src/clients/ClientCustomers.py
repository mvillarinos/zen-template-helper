class ClientCustomers:
    def __init__(self, name, last_name, location, phone):
        self.name = name
        self.last_name = last_name
        self.location = location
        self.phone = phone

    def __repr__(self):
        # Return a string representation of the ClientCustomers object.
        location = f" ({self.location})" if self.location else ""
        return f"{self.name} {self.last_name}{location}"