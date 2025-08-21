#!/usr/bin/env python3
"""
Web-based demo version of Zen Template Helper
Designed for deployment on Google Cloud App Engine Free Tier
"""

import json
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify

# Import the core classes from the desktop app
from src.clients.ClientAppointments import ClientAppointments
from src.clients.ClientCustomers import ClientCustomers

app = Flask(__name__)

class WebTemplateFiller:
    def __init__(self):
        self.templates = {}
        self.services = []
        self.operators = []
        self.locations = []
        self.load_data()
    
    def load_data(self):
        """Load all the JSON data files"""
        try:
            with open('data/zen-templates.json', 'r', encoding='utf-8') as f:
                self.templates = json.load(f)
        except FileNotFoundError:
            self.templates = []
            
        try:
            with open('data/zen-services.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.services = data.get('services', [])
        except FileNotFoundError:
            self.services = []
            
        try:
            with open('data/zen-operators.json', 'r', encoding='utf-8') as f:
                self.operators = json.load(f)
        except FileNotFoundError:
            self.operators = []
            
        try:
            with open('data/zen-locations.json', 'r', encoding='utf-8') as f:
                self.locations = json.load(f)
        except FileNotFoundError:
            self.locations = []
    
    def get_templates_by_type(self, template_type):
        """Get templates filtered by type"""
        return [t for t in self.templates if t.get('type') == template_type]
    
    def fill_template(self, template_text, client_data, language='es'):
        """Fill template with client data"""
        # Basic template filling - replace placeholders
        filled = template_text
        
        # Replace basic placeholders
        filled = filled.replace('{FirstName}', client_data.get('first_name', ''))
        filled = filled.replace('{Date}', client_data.get('date', ''))
        filled = filled.replace('{Location}', client_data.get('location', ''))
        filled = filled.replace('{Services}', client_data.get('services', ''))
        filled = filled.replace('{Operator}', client_data.get('operator', ''))
        filled = filled.replace('{Plural}', client_data.get('plural', ''))
        
        return filled

# Initialize the web template filler
web_filler = WebTemplateFiller()

@app.route('/')
def index():
    """Main page showing the template filler interface"""
    # Extract location titles for the dropdown
    location_names = [loc.get('title', loc) if isinstance(loc, dict) else loc for loc in web_filler.locations]
    
    return render_template('index.html', 
                         templates=web_filler.templates,
                         services=web_filler.services[:20],  # Limit for demo
                         operators=web_filler.operators,
                         locations=location_names)

@app.route('/api/templates/<template_type>')
def get_templates(template_type):
    """API endpoint to get templates by type"""
    templates = web_filler.get_templates_by_type(template_type)
    return jsonify(templates)

@app.route('/api/fill-template', methods=['POST'])
def fill_template():
    """API endpoint to fill a template with provided data"""
    data = request.json
    
    template_text = data.get('template', '')
    client_data = data.get('client_data', {})
    language = data.get('language', 'es')
    
    filled_template = web_filler.fill_template(template_text, client_data, language)
    
    return jsonify({
        'filled_template': filled_template,
        'success': True
    })

@app.route('/demo')
def demo():
    """Demo page showing the application functionality"""
    return render_template('demo.html',
                         templates=web_filler.templates,
                         services=web_filler.services[:10])

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=8080)