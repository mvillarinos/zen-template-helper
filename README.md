# zen-template-helper

A desktop and web application for generating personalized spa appointment and customer communication templates.

## Overview

This application helps spa businesses create personalized messages for their customers using pre-defined templates. It supports multiple languages (Spanish and English) and can handle various types of communications including appointment confirmations, birthday messages, and service availability notifications.

## Features

- **Template Management**: Pre-built templates for different communication types
- **Multi-language Support**: Spanish and English templates
- **Client Management**: Handle appointments and customer data
- **Service Integration**: Include spa services in communications
- **Desktop Application**: Full-featured Tkinter GUI application
- **Web Demo**: Browser-based version for cloud deployment

## Applications Included

### 1. Desktop Application (`zen-template-helper.py`)
- Full-featured GUI using Tkinter
- Complete client and appointment management
- Template editing and customization
- Local data storage

### 2. Web Demo (`web_app.py`)
- Browser-based interface
- Template generation functionality
- Designed for Google Cloud Free Tier deployment
- Responsive design with Bootstrap

## Getting Started

### Desktop Application
```bash
# Run the desktop application
python zen-template-helper.py
```

### Web Demo
```bash
# Install dependencies
pip install -r requirements.txt

# Run the web application
python web_app.py

# Access at http://localhost:8080
```

## Cloud Deployment

The web demo can be deployed to Google Cloud Platform's free tier. See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions on how to deploy to Google App Engine.

## Data Files

The application uses JSON files in the `data/` directory:
- `zen-templates.json` - Message templates
- `zen-services.json` - Available spa services
- `zen-operators.json` - Staff operators
- `zen-locations.json` - Spa locations

## Project Structure

```
zen-template-helper/
├── zen-template-helper.py    # Desktop application
├── web_app.py               # Web demo application
├── app.yaml                 # Google App Engine configuration
├── requirements.txt         # Python dependencies
├── DEPLOYMENT.md           # Cloud deployment guide
├── data/                   # JSON data files
├── src/                    # Source modules
│   ├── clients/           # Client management classes
│   ├── ui/               # UI components
│   └── themes/           # GUI themes
├── templates/            # HTML templates (web demo)
└── static/              # CSS/JS files (web demo)
```

## License

MIT License - see the LICENSE file for details.