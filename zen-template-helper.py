import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
import json

class TemplateFiller(tk.Tk):
    def __init__(self, root):
        self.root = root
        self.root.title("Template Filler")
        self.root.geometry("800x720")
        
        self.users = []
        self.templates = {}
        self.services = []
        self.time_intervals = [
            "09:00", "09:15", "09:30", "09:45",
            "10:00", "10:15", "10:30", "10:45",
            "11:00", "11:15", "11:30", "11:45",
            "12:00", "12:15", "12:30", "12:45",
            "13:00", "13:15", "13:30", "13:45",
            "14:00", "14:15", "14:30", "14:45",
            "15:00", "15:15", "15:30", "15:45",
            "16:00", "16:15", "16:30", "16:45",
            "17:00"
        ]

        self.selected_user = None

        self.create_widgets()

        # Automatically load templates after widgets are created
        try:
            self.load_templates("data/zen-templates.json")
            # self.load_templates_button.configure(style="Success.TButton")
            self.load_templates_button.configure(text="⟳")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load templates on start: {str(e)}")
            self.load_templates_button.configure(style="Default.TButton")

        # Automatically load services after widgets are created
        try:
            self.load_services("data/zen-services.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load templates on start: {str(e)}")
        
    def create_widgets(self):
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        self.header = ttk.Frame(self.main_frame)
        self.header.pack(fill=tk.X, pady=[0,5])       

        ttk.Button(self.header, text="Load CSV Data", command=self.load_csv_dialog).pack(side=tk.LEFT) 

        ttk.Button(self.header, text="Change Theme", command=self.change_theme).pack(side=tk.RIGHT)
        
        # Left and right frames
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=[5, 0])
        
        # Template group
        self.template_group = ttk.Frame(self.left_frame)
        self.template_group.pack(fill=tk.X)

        ttk.Label(self.template_group, text="Select Template:").pack(side=tk.TOP, fill=tk.X)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(self.template_group, textvariable=self.template_var, state="readonly")
        self.template_combo.pack(side=tk.LEFT, fill=tk.X, pady=5, expand=True)
        self.load_templates_button = ttk.Button(self.template_group, text="Load Templates", command=self.load_templates_dialog)
        self.load_templates_button.pack(side=tk.RIGHT, padx=[5, 0])

        ttk.Label(self.left_frame, text="Select User:").pack(anchor=tk.W)
        self.user_listbox = tk.Listbox(self.left_frame, width=40, height=10, selectmode=tk.SINGLE)
        self.user_listbox.pack(fill=tk.BOTH, expand=True, pady=[5,0])
        self.user_listbox.bind("<<ListboxSelect>>", self.handleSelectClient)
        
        ttk.Label(self.right_frame, text="Select Services:").pack(anchor=tk.W)
        # Layout
        self.services_frame = ttk.Frame(self.right_frame)
        self.services_frame.pack(fill=tk.X)
        self.services_left_frame = ttk.Frame(self.services_frame)
        self.services_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.services_right_frame = ttk.Frame(self.services_frame, width=40)
        self.services_right_frame.pack(side=tk.RIGHT, fill=tk.Y, expand=False, padx=[5, 0])
        self.service1_var = tk.StringVar()
        self.service1_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service1_var, state="readonly")
        self.service1_combo.pack(fill=tk.X, pady=5)
        self.service2_var = tk.StringVar()
        self.service2_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service2_var, state="readonly")
        self.service2_combo.pack(fill=tk.X, pady=5)
        self.service3_var = tk.StringVar()
        self.service3_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service3_var, state="readonly")
        self.service3_combo.pack(fill=tk.X, pady=5)
        self.service4_var = tk.StringVar()
        self.service4_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service4_var, state="readonly")
        self.service4_combo.pack(fill=tk.X, pady=5)
        self.service5_var = tk.StringVar()
        self.service5_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service5_var, state="readonly")
        self.service5_combo.pack(fill=tk.X, pady=5)
        self.hour1_var = tk.StringVar()
        self.hour1_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour1_var, state="readonly")
        self.hour1_combo.pack(pady=5)
        self.hour2_var = tk.StringVar()
        self.hour2_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour2_var, state="readonly")
        self.hour2_combo.pack(pady=5)
        self.hour3_var = tk.StringVar()
        self.hour3_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour3_var, state="readonly")
        self.hour3_combo.pack(pady=5)
        self.hour4_var = tk.StringVar()
        self.hour4_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour4_var, state="readonly")
        self.hour4_combo.pack(pady=5)
        self.hour5_var = tk.StringVar()
        self.hour5_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour5_var, state="readonly")
        self.hour5_combo.pack(pady=5)
        self.hour1_combo['values'] = list(self.time_intervals)
        self.hour2_combo['values'] = list(self.time_intervals)
        self.hour3_combo['values'] = list(self.time_intervals)
        self.hour4_combo['values'] = list(self.time_intervals)
        self.hour5_combo['values'] = list(self.time_intervals)
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

        self.clear_services_button = ttk.Button(self.right_frame, text="Clear services", command=self.clear_services)
        self.clear_services_button.pack(fill=tk.X, pady=5)

        ttk.Label(self.right_frame, text="Generated Text:").pack(anchor=tk.W)
        self.result_text = tk.Text(self.right_frame, wrap=tk.WORD, width=40, height=15, state="disabled")
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Button(self.right_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(pady=[5,0], fill=tk.BOTH, expand=True)
    
    def load_csv_dialog(self):
        filename = filedialog.askopenfilename(title="Select CSV File", filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if filename:
            try:
                self.load_csv(filename)
                messagebox.showinfo("Success", "CSV file loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
    
    def load_templates_dialog(self):
        filename = filedialog.askopenfilename(title="Select Templates JSON File", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
        if filename:
            try:
                self.load_templates(filename)
                messagebox.showinfo("Success", "Templates loaded successfully!")
                # self.load_templates_button.configure(style="Success.TButton")
                self.load_templates_button.configure(text="Refresh Templates")
                # self.load_templates_button.configure(style="Accent.TButton")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load templates: {str(e)}")
                self.load_templates_button.configure(style="Default.TButton")
    
    def load_csv(self, filename):
        self.users = []
        try:
            with open(filename, 'r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if 'First Name' in row and 'Location' in row:
                        self.users.append(row)
                    else:
                        raise KeyError("Missing required columns in CSV")
            
            self.user_listbox.delete(0, tk.END)
            for user in self.users:
                self.user_listbox.insert(tk.END, f"{user['First Name']} {user['Last Name']} ({user['Location']})")
                
        except Exception as e:
            raise Exception(f"Error reading CSV: {str(e)}")
    
    def load_templates(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.templates = json.load(file)
        
        self.template_combo['values'] = list(self.templates.keys())
        if self.templates:
            self.template_combo.set(list(self.templates.keys())[0])

    def load_services(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.services = json.load(file).get('services')

        servicesTitles = [service['title'] for service in self.services]
        self.service1_combo['values'] = list(servicesTitles)
        self.service2_combo['values'] = list(servicesTitles)
        self.service3_combo['values'] = list(servicesTitles)
        self.service4_combo['values'] = list(servicesTitles)
        self.service5_combo['values'] = list(servicesTitles)
    
    def handleSelectClient(self, event=None):
        selection = self.user_listbox.curselection()
        if not selection:
            return
        
        self.selected_user = self.users[selection[0]]
        self.copy_phone_to_clipboard()
        self.generate_text()

    def handleRefreshTimes(self, index, event):
        for i in range(index, 5):
            if i == 1:
                selected_service = next((s for s in self.services if s["title"] == self.service1_var.get()), None)
                if selected_service and self.hour1_var.get() != "":
                    duration = selected_service.get("duration", 0)
                    self.hour2_var.set(self.add_minutes_to_time(self.hour1_var.get(), duration))
            elif i == 2:
                selected_service = next((s for s in self.services if s["title"] == self.service2_var.get()), None)
                if selected_service and self.hour2_var.get() != "":
                    duration = selected_service.get("duration", 0)
                    self.hour3_var.set(self.add_minutes_to_time(self.hour2_var.get(), duration))
            elif i == 3:
                selected_service = next((s for s in self.services if s["title"] == self.service3_var.get()), None)
                if selected_service and self.hour3_var.get() != "":
                    duration = selected_service.get("duration", 0)
                    self.hour4_var.set(self.add_minutes_to_time(self.hour3_var.get(), duration))
            elif i == 4:
                selected_service = next((s for s in self.services if s["title"] == self.service4_var.get()), None)
                if selected_service and self.hour4_var.get() != "":
                    duration = selected_service.get("duration", 0)
                    self.hour5_var.set(self.add_minutes_to_time(self.hour4_var.get(), duration))
        self.generate_text()

    def generate_text(self):
        
        template_name = self.template_var.get()
        
        if not template_name or template_name not in self.templates:
            messagebox.showwarning("Warning", "Please select a valid template")
            return
        
        if not self.selected_user:
            return
        
        template = self.templates[template_name]

        selected_services = self.formatSelectedServices()
        try:
            result = template.format(FirstName=self.selected_user['First Name'], Location=self.selected_user['Location'], Services=selected_services)
            self.result_text.config(state="normal")
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result)
            self.result_text.config(state="disabled")
        except KeyError as e:
            messagebox.showerror("Error", f"Template field {e} not found in user data")

    def change_theme(self):
        if self.root.tk.call("ttk::style", "theme", "use") == "azure-dark":
            # Set light theme
            self.root.tk.call("set_theme", "light")
        else:
            # Set dark theme
            self.root.tk.call("set_theme", "dark")

    def clear_services(self):
        self.service1_var.set("")
        self.service2_var.set("")
        self.service3_var.set("")
        self.service4_var.set("")
        self.service5_var.set("")
        self.hour1_var.set("")
        self.hour2_var.set("")
        self.hour3_var.set("")
        self.hour4_var.set("")
        self.hour5_var.set("")
    
    def copy_to_clipboard(self):
        # self.generate_text()
        text = self.result_text.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def copy_phone_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.selected_user['Primary Phone'])

    def formatSelectedServices(self):
        selected_services = ""
        for i in range(1, 6):
            service_var = getattr(self, f'service{i}_var')
            hour_var = getattr(self, f'hour{i}_var')
            service_name = service_var.get()
            hour_time = hour_var.get()
            if service_name and hour_time:
                selected_services = selected_services + f"\n🕒 {hour_time} - {service_name}"
        return selected_services

    def add_minutes_to_time(self, time_str, minutes):
        try:
            # Parse the time string into a datetime object
            time_obj = datetime.strptime(time_str, "%H:%M")
            # Add the minutes
            new_time = time_obj + timedelta(minutes=minutes)
            # Format the new time back to HH:MM
            return new_time.strftime("%H:%M")
        except ValueError as e:
            raise ValueError(f"Invalid time format: {time_str}. Expected HH:MM.") from e

def main():
    root = tk.Tk()
    
    # Set the theme
    root.tk.call('source', 'themes/Azure/azure.tcl')
    root.tk.call('set_theme', 'dark')
    # root.tk.call('set_theme', 'light')

    # Create a style object
    style = ttk.Style()
    style.configure("Success.TButton",  foreground="green")
    style.configure("Default.TButton",  foreground="black")
    
    app = TemplateFiller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
