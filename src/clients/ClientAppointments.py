from datetime import datetime

month_mapping = {
            "es": {
                "Jan": "enero", "Feb": "febrero", "Mar": "marzo",
                "Apr": "abril", "May": "mayo", "Jun": "junio",
                "Jul": "julio", "Aug": "agosto", "Sep": "septiembre",
                "Oct": "octubre", "Nov": "noviembre", "Dec": "diciembre"
            },
            "en": {
                "Jan": "January", "Feb": "February", "Mar": "March",
                "Apr": "April", "May": "May", "Jun": "June",
                "Jul": "July", "Aug": "August", "Sep": "September",
                "Oct": "October", "Nov": "November", "Dec": "December"
            }
        }
day_mapping = {
            "1": "1st", "2": "2nd", "3": "3rd", "4": "4th", "5": "5th",
            "6": "6th", "7": "7th", "8": "8th", "9": "9th", "10": "10th",
            "11": "11th", "12": "12th", "13": "13th", "14": "14th", "15": "15th",
            "16": "16th", "17": "17th", "18": "18th", "19": "19th", "20": "20th",
            "21": "21st", "22": "22nd", "23": "23rd", "24": "24th", "25": "25th",
            "26": "26th", "27": "27th", "28": "28th", "29": "29th", "30": "30th",
            "31": "31st"
        }

def extract_time(appointment_on):
    return " ".join(appointment_on.split()[-2:]).upper()

def extract_first_name(name):
    if name == None: return name
    return name.split()[0]

def format_plural(count, lang):
    if lang == 'es':
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
    elif lang == 'en':
        if count == 2:
            return "both"
        if count == 3:
            return "the three of you"
        if count == 4:
            return "the four of you"
        if count == 5:
            return "the five of you"
        if count == 6:
            return "the six of you"
        if count == 7:
            return "the seven of you"
        if count == 8:
            return "the eight of you"

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

    def get_date(self, lang='es'):
        date_obj = datetime.strptime(self.services[0]['time'], "%b %d, %Y %I:%M %p")
        day = str(int(date_obj.strftime("%d")))
        month = month_mapping[lang][date_obj.strftime("%b")]
        if lang =='es':
            return f"{day} de {month}"
        else:
            return f"{month} {day_mapping[day]}"
    
    def get_formatted_services(self, lang="es"):
        selected_services = ""
        if self.client_type == "Standalone":
            selected_services = f"\n🕒 {extract_time(self.services[0]['time'])} - {self.services[0]['service']}"
        elif self.client_type == "Group":
            groups = []
            for service in self.services:
                if service['time'] not in groups:
                    groups.append(service['time'])
            grouped_services = {time: [] for time in groups}
            for service in self.services:
                grouped_services[service['time']].append(service)
            sorted_grouped_services = sorted(grouped_services.items(), key=lambda x: datetime.strptime(x[0], "%b %d, %Y %I:%M %p"))
            for time, services in sorted_grouped_services:
                selected_services += f"\n🕒 {extract_time(time)} - "
                all_same_service = all(s['service'] == services[0]['service'] for s in services)
                if all_same_service and len(services) > 1:
                    if lang == 'es':
                        selected_services += f"{services[0]['service']} para {format_plural(len(services),lang)}"
                    elif lang == 'en':
                        selected_services += f"{services[0]['service']} for {format_plural(len(services),lang)}"   
                else:
                    for service in services:
                        if lang == 'es':
                            selected_services += f"{service['service']} para {extract_first_name(service['client'])}, "
                        elif lang== 'en':
                            selected_services += f"{service['service']} for {extract_first_name(service['client'])}, "
                    selected_services = selected_services[:-2]  # Remove the last comma and space
        elif self.client_type == "Linked" or self.client_type == "Package":
            ordered_services = ordered_services = sorted(self.services,key=lambda x: datetime.strptime(x['time'], "%b %d, %Y %I:%M %p"))
            for service in ordered_services:
                selected_services += f"\n🕒 {extract_time(service['time'])} - {service['service']}"
        return selected_services

    def __repr__(self):
        # Return a string representation of the ClientAppointments object.
        return f"{self.name}, {self.client_type}, services={self.services}"