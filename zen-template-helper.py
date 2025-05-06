import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
import json
import os
import subprocess
import sys
from data.autosuggest_combobox import AutoSuggestCombobox

class TemplateFiller(tk.Tk):
    def __init__(self, root):
        self.root = root
        self.root.title("Zen Template Filler")
        self.root.geometry("800x720")
        self.root.iconbitmap("data/zen-icon.ico")
        
        self.users = []
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
        self.selected_user = None

        # Automatically load templates and services
        try:
            self.load_templates("data/zen-templates.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load templates on start: {str(e)}")
        try:
            self.load_services("data/zen-services.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load templates on start: {str(e)}")

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

        self.theme_button = ttk.Button(self.header, text="☽", command=self.change_theme, width="2")
        self.theme_button.pack(side=tk.RIGHT)
        ttk.Button(self.header, text="Get update", command=self.get_update).pack(side=tk.RIGHT, padx=5)
        
        # Left and right frames with resizable layout
        self.resizable_frame = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.resizable_frame.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(self.resizable_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = ttk.Frame(self.resizable_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=[5, 0])

        self.resizable_frame.add(self.left_frame, weight=3)
        self.resizable_frame.add(self.right_frame, weight=1)
        
        # Template group
        self.template_group = ttk.Frame(self.left_frame)
        self.template_group.pack(fill=tk.X)

        ttk.Label(self.template_group, text="Select Template:").pack(side=tk.TOP, fill=tk.X)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(self.template_group, textvariable=self.template_var, values=list(self.templates.keys()), state="readonly")
        self.template_combo.pack(side=tk.LEFT, fill=tk.X, pady=5, expand=True)
        self.template_combo.set(list(self.templates.keys())[0])
        self.load_templates_button = ttk.Button(self.template_group, text="📁", command=self.load_templates_dialog, width="3")
        self.load_templates_button.pack(side=tk.RIGHT, padx=[5, 0])

        # User listbox
        ttk.Label(self.left_frame, text="Select User:").pack(anchor=tk.W)
        self.user_listbox = tk.Listbox(self.left_frame, width=40, height=10, selectmode=tk.SINGLE)
        self.user_listbox.pack(fill=tk.BOTH, expand=True, pady=[5,0])
        self.user_listbox.bind("<<ListboxSelect>>", self.handleSelectClient)
        
        # Services group
        ttk.Label(self.right_frame, text="Select Services:").pack(anchor=tk.W)

        self.services_frame = ttk.Frame(self.right_frame)
        self.services_frame.pack(fill=tk.X)

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

        self.clear_services_button = ttk.Button(self.right_frame, text="Clear services", command=self.clear_services)
        self.clear_services_button.pack(fill=tk.X, pady=5)

        # Result text area
        ttk.Label(self.right_frame, text="Generated Text:").pack(anchor=tk.W)
        self.result_text = tk.Text(self.right_frame, wrap=tk.WORD, width=40, height=15, state="disabled")
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Button(self.right_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(pady=[5,0], fill=tk.BOTH, expand=True, side=tk.BOTTOM)
    
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
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load templates: {str(e)}")
    
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

    def load_services(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.services = json.load(file).get('services')
    
    def handleSelectClient(self, event=None):
        selection = self.user_listbox.curselection()
        if not selection:
            return
        
        self.selected_user = self.users[selection[0]]
        self.copy_phone_to_clipboard()
        self.generate_text()

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
            self.root.tk.call("set_theme", "light")
            self.theme_button.config(text="☀")
        else:
            self.root.tk.call("set_theme", "dark")
            self.theme_button.config(text="☽")

    def clear_services(self):
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
    
    def copy_to_clipboard(self):
        text = self.result_text.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def copy_phone_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.selected_user['Primary Phone'])
    
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

def main():
    root = tk.Tk()
    
    # Set the theme
    root.tk.call('source', 'themes/Azure/azure.tcl')
    root.tk.call('set_theme', 'dark')
    
    app = TemplateFiller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
