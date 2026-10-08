import unicodedata
from datetime import datetime

MONTHS_ES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio',
             'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']


class ClientSeries:
    def __init__(self, name, last_name, phone, series_name, expiration_date):
        self.name = name.strip()
        self.last_name = last_name.strip()
        self.phone = phone
        # NFKC convierte letras decorativas (p. ej. negritas Unicode) en texto normal
        self.series_name = ' '.join(unicodedata.normalize('NFKC', series_name).split())
        self.expiration_date = expiration_date.strip()

    def get_expiration_text(self):
        try:
            date = datetime.strptime(self.expiration_date, '%m/%d/%Y')
        except ValueError:
            return self.expiration_date
        return f"{date.day} de {MONTHS_ES[date.month - 1]} de {date.year}"

    def __repr__(self):
        return f"{self.name} {self.last_name} - {self.series_name} (vence {self.expiration_date})"
