import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
import json
import os
import subprocess
import sys
# Custom components
from src.ui.AutoSuggestCombobox import AutoSuggestCombobox
from src.ui.ToastService import ToastService
# System classes
from src.clients.ClientAppointments import ClientAppointments
from src.clients.ClientCustomers import ClientCustomers
from src.clients.ClientSurveys import ClientSurveys

class TemplateFiller(tk.Tk):
    def __init__(self, root, style):
        self.root = root
        self.root.title("Zen Template Filler")
        self.root.geometry("800x720")
        self.root.iconbitmap("data/zen-icon.ico")
        
        self.language = 'es'
        self.templates = {}
        self.services = []
        self.time_intervals = [
            "9 AM", "9:15 AM", "9:30 AM", "9:45 AM",
            "10 AM", "10:15 AM", "10:30 AM", "10:45 AM",
            "11 AM", "11:15 AM", "11:30 AM", "11:45 AM",
            "12 PM", "12:15 PM", "12:30 PM", "12:45 PM",
            "1 PM", "1:15 PM", "1:30 PM", "1:45 PM",
            "2 PM", "2:15 PM", "2:30 PM", "2:45 PM",
            "3 PM", "3:15 PM", "3:30 PM", "3:45 PM",
            "4 PM", "4:15 PM", "4:30 PM", "4:45 PM",
            "5 PM"
        ]
        self.operators = []
        self.locations = []
        self.clients = []
        self.client_selected = None
        self.client_types = ''

        # Automatically load templates, services and locations
        try:
            self.load_templates("data/zen-templates.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load templates on start: {str(e)}")
        try:
            self.load_services("data/zen-services.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load services on start: {str(e)}")
        try:
            self.load_locations("data/zen-locations.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load locations on start: {str(e)}")
        try:
            self.load_operators("data/zen-operators.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load operators on start: {str(e)}")

        # Initialize toast service
        self.toast_service = ToastService(self.root, style)

        # Create the widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        self.header = ttk.Frame(self.main_frame)
        self.header.pack(fill=tk.X, pady=[0,5])       

        ttk.Button(self.header, text="Load CSV Data", command=self.load_csv_dialog).pack(side=tk.LEFT) 

        self.language_button = ttk.Button(self.header, text=self.language.upper(), command=self.change_language, width="3")
        self.language_button.pack(side=tk.RIGHT)
        self.theme_button = ttk.Button(self.header, text="☽", command=self.change_theme, width="2")
        self.theme_button.pack(side=tk.RIGHT, padx=5)
        ttk.Button(self.header, text="Get update", command=self.get_update).pack(side=tk.RIGHT)
        
        # Left and right frames with resizable layout
        self.resizable_frame = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.resizable_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.resizable_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = ttk.Frame(self.resizable_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=[5, 0])

        self.resizable_frame.add(self.left_frame, weight=3)
        self.resizable_frame.add(self.right_frame, weight=1)
        
        # LEFT COLUMN
        # Template group
        self.template_group = ttk.Frame(self.left_frame)
        self.template_group.pack(fill=tk.X)

        ttk.Label(self.template_group, text="Select Template:").pack(side=tk.TOP, fill=tk.X)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(self.template_group, textvariable=self.template_var, values=[template["title"] for template in self.templates], state="readonly")
        self.template_combo.pack(side=tk.LEFT, fill=tk.X, pady=5, expand=True)
        self.template_combo.bind("<<ComboboxSelected>>",  self.handleSelectTemplate)
        
        self.load_templates_button = ttk.Button(self.template_group, text="📁", command=self.load_templates_dialog, width="3")
        self.load_templates_button.pack(side=tk.RIGHT, padx=[5, 0])

        # Client listbox
        ttk.Label(self.left_frame, text="Select Client:").pack(anchor=tk.W)
        self.client_listbox = tk.Listbox(self.left_frame, width=40, height=10, selectmode=tk.SINGLE, exportselection=0)
        self.client_listbox.pack(fill=tk.BOTH, expand=True, pady=[5,0])
        self.client_listbox.bind("<<ListboxSelect>>", self.handleSelectClient)
        
        # RIGHT COLUMN
        # Dynamic group
        self.dynamic_group = ttk.Frame(self.right_frame)
        self.dynamic_group.pack(fill=tk.X)

        # Result text area
        ttk.Label(self.right_frame, text="Generated Text:").pack(anchor=tk.W)
        self.result_text = tk.Text(self.right_frame, wrap=tk.WORD, width=40, height=15, state="disabled")
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Button(self.right_frame, text="Copy to Clipboard", command=self.copy_result_text_to_clipboard).pack(pady=[5,0], fill=tk.BOTH, expand=True, side=tk.BOTTOM)

        # Autoselect first template and render dynamic groups accordingly
        self.template_combo.current(0)
        self.handleSelectTemplate()

    def render_dynamic_groups(self):
        self.group_clear(self.dynamic_group)
        if self.client_types == 'Appointments':
            self.render_operator_group()
            self.render_location_group()
        elif self.client_types == 'Customers':
            self.render_operator_group()
            # self.render_services_group()
        elif self.client_types == 'Surveys':
            self.render_operator_group()
            self.render_location_group()

    def render_operator_group(self):
        ttk.Label(self.dynamic_group, text="Operator:").pack(anchor=tk.W)
        self.operator_var = tk.StringVar()
        self.operator_combo = ttk.Combobox(self.dynamic_group, textvariable=self.operator_var, values=self.operators, width="8", state="readonly")
        self.operator_combo.pack(fill=tk.X, pady=5)
        self.operator_combo.bind("<<ComboboxSelected>>", self.generate_text)

    def render_services_group(self):
        self.services_frame = ttk.Frame(self.dynamic_group)
        self.services_frame.pack(fill=tk.X)

        ttk.Label(self.services_frame, text="Select Services:").pack(anchor=tk.W)

        self.services_left_frame = ttk.Frame(self.services_frame)
        self.services_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.services_right_frame = ttk.Frame(self.services_frame)
        self.services_right_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=[5, 0])

        servicesTitles = list([service['title'] for service in self.services])
        self.service1_combo = AutoSuggestCombobox(self.services_left_frame)
        self.service1_combo.set_completion_list(servicesTitles)
        self.service1_combo.pack(fill=tk.X, pady=5)
        self.service2_combo = AutoSuggestCombobox(self.services_left_frame)
        self.service2_combo.set_completion_list(servicesTitles)
        self.service2_combo.pack(fill=tk.X, pady=5)
        self.service3_combo = AutoSuggestCombobox(self.services_left_frame)
        self.service3_combo.set_completion_list(servicesTitles)
        self.service3_combo.pack(fill=tk.X, pady=5)
        self.service4_combo = AutoSuggestCombobox(self.services_left_frame)
        self.service4_combo.set_completion_list(servicesTitles)
        self.service4_combo.pack(fill=tk.X, pady=5)
        self.service5_combo = AutoSuggestCombobox(self.services_left_frame)
        self.service5_combo.set_completion_list(servicesTitles)
        self.service5_combo.pack(fill=tk.X, pady=5)
        self.hour1_combo = ttk.Combobox(self.services_right_frame, values=self.time_intervals, width="8", state="readonly")
        self.hour1_combo.pack(pady=5)
        self.hour2_combo = ttk.Combobox(self.services_right_frame, values=self.time_intervals, width="8", state="readonly")
        self.hour2_combo.pack(pady=5)
        self.hour3_combo = ttk.Combobox(self.services_right_frame, values=self.time_intervals, width="8", state="readonly")
        self.hour3_combo.pack(pady=5)
        self.hour4_combo = ttk.Combobox(self.services_right_frame, values=self.time_intervals, width="8", state="readonly")
        self.hour4_combo.pack(pady=5)
        self.hour5_combo = ttk.Combobox(self.services_right_frame, values=self.time_intervals, width="8", state="readonly")
        self.hour5_combo.pack(pady=5)
        self.service1_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(1, event))
        self.service2_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(2, event))
        self.service3_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(3, event))
        self.service4_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(4, event))
        self.service5_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(5, event))
        self.hour1_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(1, event))
        self.hour2_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(2, event))
        self.hour3_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(3, event))
        self.hour4_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(4, event))
        self.hour5_combo.bind("<<ComboboxSelected>>", lambda event: self.handleRefreshTimes(5, event))

        self.clear_services_button = ttk.Button(self.dynamic_group, text="Clear services", command=self.clear_services)
        self.clear_services_button.pack(fill=tk.X, pady=5)


    def render_location_group(self):
        self.location_frame = ttk.Frame(self.dynamic_group)
        self.location_frame.pack(fill=tk.X)
        ttk.Label(self.location_frame, text="Location:").pack(anchor=tk.W)
        self.location_var = tk.StringVar()
        self.location_combo = ttk.Combobox(self.location_frame, textvariable=self.location_var, values=[location["title"] for location in self.locations], state="readonly" )
        self.location_combo.pack(fill=tk.X, pady=5)
        self.location_combo.bind("<<ComboboxSelected>>", self.generate_text)

    def load_csv_dialog(self):
        filename = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            try:
                self.load_csv(filename)
                self.toast_service.show_toast('CSV file loaded successfully!','Success')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
    
    def load_templates_dialog(self):
        filename = filedialog.askopenfilename(title="Select Templates JSON File", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            try:
                self.load_templates(filename)
                self.toast_service.show_toast('Templates loaded successfully!','Success')
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load templates: {str(e)}")
    
    def load_csv(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                if self.client_types == 'Surveys':
                    # Skip the first 3 lines (survey question header)
                    for _ in range(3):
                        next(file, None)
                    reader = csv.DictReader(file)
                else:
                    reader = csv.DictReader(file)
                if self.client_types == 'Appointments':
                    if 'Customer Name' in reader.fieldnames and 'Type' in reader.fieldnames and 'Treatment Name' in reader.fieldnames:
                        new_clients = []
                        for row in reader:
                            new_clients.append(row)
                        self.clients = self.formatClients(new_clients)
                    else:
                        raise KeyError("Missing required columns in CSV")
                elif self.client_types == 'Customers':
                    if 'First Name' in reader.fieldnames and 'Location' in reader.fieldnames:
                        new_clients = []
                        for row in reader:
                            new_clients.append(row)
                        self.clients = self.formatClients(new_clients)
                    else:
                        raise KeyError("Missing required columns in CSV")
                elif self.client_types == 'Surveys':
                    if 'CustomerName' in reader.fieldnames and 'Phone' in reader.fieldnames:
                        new_clients = []
                        for row in reader:
                            new_clients.append(row)
                        self.clients = self.formatClients(new_clients)
                    else:
                        print(reader.fieldnames)
                        raise KeyError("Missing required columns in CSV")
                    
                self.client_listbox.delete(0, tk.END)
                for client in self.clients:
                    self.client_listbox.insert(tk.END, repr(client))
        except Exception as e:
            raise Exception(f"Error reading CSV: {str(e)}")
    
    def load_templates(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.templates = json.load(file)

    def load_services(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.services = json.load(file).get('services')
    
    def load_locations(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.locations = json.load(file)

    def load_operators(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.operators = json.load(file)
    
    def handleSelectClient(self, event=None):
        selection = self.client_listbox.curselection()
        if not selection:
            return
        self.client_selected = self.clients[selection[0]]
        self.copy_phone_to_clipboard()
        self.generate_text()

    def handleSelectTemplate(self, event=None):
        selection = self.template_combo.current()
        if selection == -1:
            return
        template = self.templates[selection]
        self.client_types = template['type']
        self.clear_all_values()
        self.render_dynamic_groups()

    def handleRefreshTimes(self, index, event):
        for i in range(index, 5):
            service_combo = getattr(self, f'service{i}_combo')
            hour_combo = getattr(self, f'hour{i}_combo')
            selected_service = next((s for s in self.services if s["title"] == service_combo.get()), None)
            if selected_service and hour_combo.get() != "":
                duration = selected_service.get("duration", 0)
                if i < 5:
                    next_hour_combo = getattr(self, f'hour{i+1}_combo')
                    next_hour_combo.set(self.add_minutes_to_time(hour_combo.get(), duration))
        self.generate_text()

    def generate_text(self, event=None):        
        if not self.client_selected:
            return
        template = next((template for template in self.templates if template["title"] == self.template_var.get()), None)
        if not self.operator_var.get():
            self.toast_service.show_toast('Please select an operator','Warning')
            return
        try:
            if self.client_types == 'Appointments':
                if not self.location_var.get():
                    self.toast_service.show_toast('Please select a location','Warning')
                    return
                location =  next((location for location in self.locations if location["title"] == self.location_var.get()), None)
                result = template['template'][self.language].format(
                    FirstName=self.client_selected.get_formatted_names(self.language),
                    Services=self.client_selected.get_formatted_services(self.language),
                    Date=self.client_selected.get_date(self.language),
                    Location=location['text'][self.language],
                    Operator=self.operator_var.get(),
                    Plural= 's' if self.language == 'es' and self.client_selected.get_clients_count() > 1 else ''
                )
            elif self.client_types == 'Customers':
                selected_services = self.formatSelectedServices()
                result = template['template'][self.language].format(
                    FirstName=self.client_selected.name,
                    Location=self.client_selected.location,
                    Services=selected_services,
                    Operator=self.operator_var.get()
                )
            elif self.client_types == 'Surveys':
                if not self.location_var.get():
                    self.toast_service.show_toast('Please select a location','Warning')
                    return
                location =  next((location for location in self.locations if location["title"] == self.location_var.get()), None)
                result = template['template'][self.language].format(
                    FirstName=self.client_selected.name,
                    Location=location['text'][self.language],
                    Operator=self.operator_var.get()
                )

            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result)
            self.result_text.config(state="disabled")
        except KeyError as e:
            messagebox.showerror("Error", f"Template field {e} not found in client data")

    def change_theme(self):
        if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
            self.root.tk.call("set_theme", "light")
            self.theme_button.config(text="☀")
        else:
            self.root.tk.call("set_theme", "dark")
            self.theme_button.config(text="☽")

    def change_language(self):
        if self.language == 'es':
            self.language = 'en'
            self.language_button.config(text='EN')
        else:
            self.language = 'es'
            self.language_button.config(text='ES')
        self.generate_text()

    def clear_all_values(self):
        self.clear_services()
        self.clear_locations()
        self.client_listbox.delete(0, tk.END)
        self.clients = []
        self.result_text.config(state="normal")
        self.result_text.delete(1.0, tk.END)

    def clear_services(self):
        if 'service1_combo' in globals():
            self.service1_combo.set("")
            self.service2_combo.set("")
            self.service3_combo.set("")
            self.service4_combo.set("")
            self.service5_combo.set("")
            self.hour1_combo.set("")
            self.hour2_combo.set("")
            self.hour3_combo.set("")
            self.hour4_combo.set("")
            self.hour5_combo.set("")

    def clear_locations(self):
        if 'location_combo' in globals():
            self.location_combo.current(-1)
    
    def copy_result_text_to_clipboard(self):
        text = self.result_text.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def copy_phone_to_clipboard(self):
        if hasattr(self.client_selected, "phone"):
            self.root.clipboard_clear()
            self.root.clipboard_append(self.client_selected.phone)
    
    def get_update(self):
        try:
            # Get the current directory and filepath of the script
            current_file = os.path.abspath(__file__)
            current_dir = os.path.dirname(current_file)
            
            # Run the "git pull" command in the current directory using Git Bash
            subprocess.run(["git", "pull"], cwd=current_dir, check=True, shell=True)
            
            # Relaunch the application
            pythonw = sys.executable.replace("python.exe", "pythonw.exe")
            os.execl(pythonw, pythonw, f'"{current_file}"', *sys.argv[1:])
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Failed to update repository: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")


    def formatSelectedServices(self):
        selected_services = ""
        for i in range(1, 5):
            service_var = getattr(self, f'service{i}_combo')
            hour_var = getattr(self, f'hour{i}_combo')
            service_name = service_var.get()
            hour_time = hour_var.get()
            if service_name and hour_time:
                selected_services = selected_services + f"\n🕒 {hour_time} - {service_name}"
        return selected_services

    def add_minutes_to_time(self, time_str, minutes):
        try:
            # Parse the time string into a datetime object
            time_obj = datetime.strptime(time_str, "%I:%M %p" if ":" in time_str else "%I %p")
            # Add the minutes
            new_time = time_obj + timedelta(minutes=minutes)
            # Format the new time back to 12-hour format with "AM"/"PM" and a space
            return new_time.strftime("%I:%M %p").lstrip("0").replace(":00", "")
        except ValueError as e:
            raise ValueError(f"Invalid time format: {time_str}. Expected 12-hour format with AM/PM.") from e

    def group_clear(self, group):
        for widget in group.winfo_children():
            widget.pack_forget()

    def formatClients(self, clients):
        local_clients = []
        if self.client_types == 'Appointments':
            for row in clients:
                phone = row['Customer Mobile Phone'] if 'Customer Mobile Phone' in row else row['Customer Home Phone'] if 'Customer Home Phone' in row else None
                if row['Type'] == 'Standalone':
                    new = ClientAppointments(name=row['Customer Name'], client_type=row['Type'], phone=phone)
                    new.add_service(row['Treatment Name'], row['Appointment On'])
                    local_clients.append(new)
                elif row['Type'] == 'Linked' or row['Type'] == 'Package':
                    linked = next((c for c in local_clients if c.name == row['Customer Name']), None)
                    if linked:
                        linked.add_service(row['Treatment Name'], row['Appointment On'])
                    else:
                        new = ClientAppointments(name=row['Customer Name'], client_type=row['Type'], phone=phone)
                        new.add_service(row['Treatment Name'], row['Appointment On'])
                        local_clients.append(new)
                elif row['Type'] == 'Group':
                    grouped = next((c for c in local_clients if c.group_id == row['Group ID']), None)
                    if grouped:
                        grouped.add_service(row['Treatment Name'], row['Appointment On'], row['Customer Name'])
                    else:
                        new = ClientAppointments(name=row['Customer Name'], client_type=row['Type'], group_id=row['Group ID'], phone=phone)
                        new.add_service(row['Treatment Name'], row['Appointment On'], row['Customer Name'])
                        local_clients.append(new)
        elif self.client_types == 'Customers':
            for row in clients:
                local_clients.append(ClientCustomers(name=row['First Name'], last_name=row['Last Name'], location=row['Location'], phone=row['Primary Phone']))
        elif self.client_types == 'Surveys':
            for row in clients:
                local_clients.append(ClientSurveys(name=row['CustomerName'], phone=row['Phone'] if row['Phone'] else row['Email']))

        return local_clients

def main():
    root = tk.Tk()
    
    # Set the theme
    root.tk.call('source', 'src/themes/Azure/azure.tcl')
    root.tk.call('set_theme', 'dark')
    style = ttk.Style()
    
    app = TemplateFiller(root, style)
    root.mainloop()

if __name__ == "__main__":
    main()
