import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import json
import string

class TemplateFiller:
    def __init__(self, root):
        self.root = root
        self.root.title("Template Filler")
        self.root.geometry("800x600")
        
        # Data storage
        self.users = []
        self.templates = {}
        
        self.create_widgets()
        
    def create_widgets(self):
        # Create main frames
        self.top_frame = ttk.Frame(self.root, padding="10")
        self.top_frame.pack(fill=tk.X)
        
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File loading buttons in top frame
        ttk.Button(self.top_frame, 
                  text="Load CSV Data", 
                  command=self.load_csv_dialog).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.top_frame, 
                  text="Load Templates", 
                  command=self.load_templates_dialog).pack(side=tk.LEFT, padx=5)
        
        # Split main frame into left and right
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # User selection section
        ttk.Label(self.left_frame, text="Select User:").pack(anchor=tk.W)
        self.user_listbox = tk.Listbox(self.left_frame, width=40, height=10)
        self.user_listbox.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Template selection section
        ttk.Label(self.left_frame, text="Select Template:").pack(anchor=tk.W)
        self.template_var = tk.StringVar()
        self.template_combo = ttk.Combobox(self.left_frame, 
                                         textvariable=self.template_var)
        self.template_combo.pack(fill=tk.X, pady=5)
        
        # Generate button
        ttk.Button(self.left_frame, 
                  text="Generate Text", 
                  command=self.generate_text).pack(pady=10)
        
        # Result section
        ttk.Label(self.right_frame, text="Generated Text:").pack(anchor=tk.W)
        self.result_text = tk.Text(self.right_frame, wrap=tk.WORD, width=40, height=15)
        self.result_text.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Copy button
        ttk.Button(self.right_frame, 
                  text="Copy to Clipboard", 
                  command=self.copy_to_clipboard).pack(pady=5)
    
    def load_csv_dialog(self):
        filename = filedialog.askopenfilename(
            title="Select CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.load_csv(filename)
                messagebox.showinfo("Success", "CSV file loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load CSV: {str(e)}")
    
    def load_templates_dialog(self):
        filename = filedialog.askopenfilename(
            title="Select Templates JSON File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.load_templates(filename)
                messagebox.showinfo("Success", "Templates loaded successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load templates: {str(e)}")
    
    def load_csv(self, filename):
        self.users = []
        with open(filename, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                self.users.append(row)
        
        # Update listbox
        self.user_listbox.delete(0, tk.END)
        for user in self.users:
            # Assuming 'Location' field exists
            display_name = user.get('Location', str(user))
            self.user_listbox.insert(tk.END, display_name)
    
    def load_templates(self, filename):
        with open(filename, 'r', encoding='utf-8') as file:
            self.templates = json.load(file)
        
        # Update template dropdown
        self.template_combo['values'] = list(self.templates.keys())
        if self.templates:
            self.template_combo.set(list(self.templates.keys())[0])
    
    def generate_text(self):
        # Get selected user and template
        selection = self.user_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a user")
            return
        
        user = self.users[selection[0]]
        template_name = self.template_var.get()
        
        if not template_name:
            messagebox.showwarning("Warning", "Please select a template")
            return
        
        if not self.templates:
            messagebox.showwarning("Warning", "No templates loaded")
            return
        
        # Generate text
        template = self.templates[template_name]
        try:
            result = template.format(**user)
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(1.0, result)
        except KeyError as e:
            messagebox.showerror("Error", f"Template field {e} not found in user data")
    
    def copy_to_clipboard(self):
        text = self.result_text.get(1.0, tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        messagebox.showinfo("Success", "Text copied to clipboard!")

def main():
    root = tk.Tk()
    app = TemplateFiller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
