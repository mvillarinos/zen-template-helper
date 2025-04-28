import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
import json

class TemplateFiller:
    def __init__(self, root):
        self.root = root
        self.root.title("Template Filler")
        self.root.geometry("800x600")
        
        self.users = []
        self.templates = {}
        self.services = []
        self.time_intervals = [
            "09:00", "09:30", "10:00", "10:30", "11:00", "11:30",
            "12:00", "12:30", "13:00", "13:30", "14:00", "14:30",
            "15:00", "15:30", "16:00", "16:30", "17:00"
        ]

        self.selected_user = None

        self.create_widgets()

        # Automatically load templates after widgets are created
        try:
            self.load_templates("data/zen-templates.json")
            self.load_templates_button.configure(style="Success.TButton")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load templates on start: {str(e)}")
            self.load_templates_button.configure(style="Default.TButton")

        # Automatically load services after widgets are created
        try:
            self.load_services("data/zen-services.json")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load templates on start: {str(e)}")
        
    def create_widgets(self):
        self.top_frame = ttk.Frame(self.root, padding="10")
        self.top_frame.pack(fill=tk.X)
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create the "Load Templates" button and store it as an instance variable
        self.load_templates_button = ttk.Button(self.top_frame, text="Load Templates", command=self.load_templates_dialog)
        self.load_templates_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.top_frame, text="Load CSV Data", command=self.load_csv_dialog).pack(side=tk.LEFT, padx=5)
        
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        ttk.Label(self.left_frame, text="Select Template:").pack(anchor=tk.W)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(self.left_frame, textvariable=self.template_var)
        self.template_combo.pack(fill=tk.X, pady=5)

        ttk.Label(self.left_frame, text="Select User:").pack(anchor=tk.W)
        self.user_listbox = tk.Listbox(self.left_frame, width=40, height=10)
        self.user_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        self.user_listbox.bind("<<ListboxSelect>>", self.handleSelectClient)
        
        # ttk.Label(self.right_frame, text="Generated Text:").pack(anchor=tk.W)
        # self.result_text = tk.Text(self.right_frame, wrap=tk.WORD, width=40, height=15)
        # self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        ttk.Label(self.right_frame, text="Select Services:").pack(anchor=tk.W)
        # Layout
        self.services_frame = ttk.Frame(self.right_frame)
        self.services_frame.pack(fill=tk.X)
        self.services_left_frame = ttk.Frame(self.services_frame)
        self.services_left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.services_right_frame = ttk.Frame(self.services_frame, width=40)
        self.services_right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.service1_var = tk.StringVar()
        self.service1_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service1_var)
        self.service1_combo.pack(fill=tk.X, pady=5)
        self.service2_var = tk.StringVar()
        self.service2_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service2_var)
        self.service2_combo.pack(fill=tk.X, pady=5)
        self.service3_var = tk.StringVar()
        self.service3_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service3_var)
        self.service3_combo.pack(fill=tk.X, pady=5)
        self.service4_var = tk.StringVar()
        self.service4_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service4_var)
        self.service4_combo.pack(fill=tk.X, pady=5)
        self.service5_var = tk.StringVar()
        self.service5_combo = ttk.Combobox(self.services_left_frame, textvariable=self.service5_var)
        self.service5_combo.pack(fill=tk.X, pady=5)
        self.hour1_var = tk.StringVar()
        self.hour1_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour1_var)
        self.hour1_combo.pack(pady=5)
        self.hour2_var = tk.StringVar()
        self.hour2_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour2_var)
        self.hour2_combo.pack(pady=5)
        self.hour3_var = tk.StringVar()
        self.hour3_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour3_var)
        self.hour3_combo.pack(pady=5)
        self.hour4_var = tk.StringVar()
        self.hour4_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour4_var)
        self.hour4_combo.pack(pady=5)
        self.hour5_var = tk.StringVar()
        self.hour5_combo = ttk.Combobox(self.services_right_frame, textvariable=self.hour5_var)
        self.hour5_combo.pack(pady=5)
        
        ttk.Button(self.right_frame, text="Copy to Clipboard", command=self.copy_to_clipboard).pack(pady=5, fill=tk.BOTH, expand=True)
    
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
                self.load_templates_button.configure(style="Success.TButton")
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
        
        self.service1_combo['values'] = list(self.services)
        self.service2_combo['values'] = list(self.services)
        self.service3_combo['values'] = list(self.services)
        self.service4_combo['values'] = list(self.services)
        self.service5_combo['values'] = list(self.services)
    
    def handleSelectClient(self, event=None):
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        self.selected_user = self.users[selection[0]]
        self.copy_phone_to_clipboard()

    def generate_text(self):
        
        template_name = self.template_var.get()
        
        if not template_name or template_name not in self.templates:
            messagebox.showwarning("Warning", "Please select a valid template")
            return
        
        template = self.templates[template_name]
        try:
            result = template.format(FirstName=self.selected_user['First Name'], Location=self.selected_user['Location'])
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result)
        except KeyError as e:
            messagebox.showerror("Error", f"Template field {e} not found in user data")
    
    def copy_to_clipboard(self):
        text = self.result_text.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def copy_phone_to_clipboard(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.selected_user['Primary Phone'])

    def add_minutes_to_time(time_str, minutes):
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
    
    # Create a style object
    style = ttk.Style()
    style.configure("Success.TButton",  foreground="green")
    style.configure("Default.TButton",  foreground="black")
    
    app = TemplateFiller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
