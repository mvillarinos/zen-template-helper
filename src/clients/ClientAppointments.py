from datetime import datetime

def extract_time(appointment_on):
    return " ".join(appointment_on.split()[-2:]).upper()

def extract_first_name(name):
        return name.split()[0]

def format_plural(count):
    if count == 2:
        return "ambas"
    if count == 3:
        return "las tres"
    if count == 4:
        return "las cuatro"
    if count == 5:
        return "las cinco"
    if count == 6:
        return "las seis"
    if count == 7:
        return "las siete"
    if count == 8:
        return "las ocho"

class ClientAppointments:
    def __init__(self, name, client_type, group_id = None):
        self.name = name
        self.client_type = client_type
        self.group_id = group_id
        self.services = []

    def add_service(self, service_name, service_time, client = None):
        self.services.append({
            "service": service_name,
            "time": service_time,
            "client": client
        })

    def get_first_name(self):
        return extract_first_name(self.name)

    def get_date(self):
        month_mapping = {
            "January": "enero", "February": "febrero", "March": "marzo",
            "April": "abril", "May": "mayo", "June": "junio",
            "July": "julio", "August": "agosto", "September": "septiembre",
            "October": "octubre", "November": "noviembre", "December": "diciembre"
        }
        date_obj = datetime.strptime(self.services[0]['time'], "%B %d, %Y %I:%M %p")
        # Format the date and replace the month with its Spanish equivalent
        day = str(int(date_obj.strftime("%d")))
        month = month_mapping[date_obj.strftime("%B")]
        return f"{day} de {month}"
    
    def get_formatted_services(self):
        selected_services = ""
        if self.client_type == "Standalone":
            selected_services = f"\n🕒 {extract_time(self.services[0].service_time)} - {self.services[0].service}"
        elif self.client_type == "Group":
            groups = []
            for service in self.services:
                if service['time'] not in groups:
                    groups.append(service['time'])
            grouped_services = {time: [] for time in groups}
            for service in self.services:
                grouped_services[service['time']].append(service)
            sorted_grouped_services = sorted(grouped_services.items(), key=lambda x: datetime.strptime(x[0], "%B %d, %Y %I:%M %p"))
            for time, services in sorted_grouped_services:
                selected_services += f"\n🕒 {extract_time(time)} - "
                all_same_service = all(s['service'] == services[0]['service'] for s in services)
                if all_same_service and len(services) > 1:
                    selected_services += f"{services[0]['service']} para {format_plural(len(services))}"
                else:
                    for service in services:
                        selected_services += f"{service['service']} para {extract_first_name(service['client'])}, "
                    selected_services = selected_services[:-2]  # Remove the last comma and space
        elif self.client_type == "Linked" or self.client_type == "Package":
            ordered_services = ordered_services = sorted(self.services,key=lambda x: datetime.strptime(x['time'], "%B %d, %Y %I:%M %p"))
            for service in ordered_services:
                selected_services += f"\n🕒 {extract_time(service['time'])} - {service['service']}"
        return selected_services

    def __repr__(self):
        # Return a string representation of the ClientAppointments object.
        return f"{self.name}, {self.client_type}, services={self.services}"