document.addEventListener('DOMContentLoaded', function() {
    const templateSelect = document.getElementById('templateSelect');
    const languageSelect = document.getElementById('languageSelect');
    const firstName = document.getElementById('firstName');
    const date = document.getElementById('date');
    const location = document.getElementById('location');
    const operator = document.getElementById('operator');
    const services = document.getElementById('services');
    const generateBtn = document.getElementById('generateBtn');
    const clearBtn = document.getElementById('clearBtn');
    const result = document.getElementById('result');
    const generatedTemplate = document.getElementById('generatedTemplate');
    const copyBtn = document.getElementById('copyBtn');
    const serviceItems = document.querySelectorAll('.service-item');

    // Set default date to today
    const today = new Date().toISOString().split('T')[0];
    date.value = today;

    // Service selection
    serviceItems.forEach(item => {
        item.addEventListener('click', function() {
            const serviceName = this.dataset.service;
            const currentServices = services.value;
            
            if (currentServices) {
                services.value = currentServices + '\n' + serviceName;
            } else {
                services.value = serviceName;
            }
            
            // Visual feedback
            this.classList.toggle('selected');
        });
    });

    // Generate template
    generateBtn.addEventListener('click', function() {
        const selectedTemplateIndex = templateSelect.value;
        const language = languageSelect.value;
        
        if (!selectedTemplateIndex) {
            alert('Please select a template');
            return;
        }
        
        if (!firstName.value) {
            alert('Please enter a first name');
            return;
        }

        const template = window.templates[selectedTemplateIndex];
        const templateText = template.template[language] || template.template.es;
        
        const clientData = {
            first_name: firstName.value,
            date: formatDate(date.value, language),
            location: location.value || 'Zen Spa',
            services: formatServices(services.value),
            operator: operator.value || 'Spa Concierge',
            plural: '' // Simplified for demo
        };

        // Call API to fill template
        fetch('/api/fill-template', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                template: templateText,
                client_data: clientData,
                language: language
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                generatedTemplate.textContent = data.filled_template;
                result.style.display = 'block';
                result.scrollIntoView({ behavior: 'smooth' });
            } else {
                alert('Error generating template');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error generating template');
        });
    });

    // Clear form
    clearBtn.addEventListener('click', function() {
        document.getElementById('templateForm').reset();
        result.style.display = 'none';
        serviceItems.forEach(item => item.classList.remove('selected'));
        date.value = today;
    });

    // Copy to clipboard
    copyBtn.addEventListener('click', function() {
        navigator.clipboard.writeText(generatedTemplate.textContent)
            .then(() => {
                const originalText = copyBtn.textContent;
                copyBtn.textContent = 'Copied!';
                copyBtn.classList.add('btn-success');
                copyBtn.classList.remove('btn-outline-primary');
                
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                    copyBtn.classList.remove('btn-success');
                    copyBtn.classList.add('btn-outline-primary');
                }, 2000);
            })
            .catch(err => {
                console.error('Failed to copy: ', err);
                alert('Failed to copy to clipboard');
            });
    });

    function formatDate(dateString, language) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        const options = { 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        };
        
        if (language === 'es') {
            return date.toLocaleDateString('es-ES', options);
        } else {
            return date.toLocaleDateString('en-US', options);
        }
    }

    function formatServices(servicesText) {
        if (!servicesText) return '';
        
        const lines = servicesText.split('\n').filter(line => line.trim());
        return lines.map(line => `• ${line.trim()}`).join('\n');
    }
});