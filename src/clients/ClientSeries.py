class ClientSeries:
    def __init__(self, name, last_name, phone):
        self.name = name.strip()
        self.last_name = last_name.strip()
        self.phone = phone

    def __repr__(self):
        return f"{self.name} {self.last_name}"
