# Deploying Zen Template Helper to Google Cloud Free Tier

This guide shows you how to deploy the Zen Template Helper web application to Google Cloud Platform (GCP) using the free tier resources.

## What's Included

This repository now includes:
- `web_app.py` - Flask web application that provides a web interface for the template functionality
- `app.yaml` - Google App Engine configuration file
- `requirements.txt` - Python dependencies
- `templates/` - HTML templates for the web interface
- `static/` - CSS and JavaScript files
- Original desktop application (`zen-template-helper.py`) remains unchanged

## Prerequisites

1. **Google Cloud Account**: Create a free account at [cloud.google.com](https://cloud.google.com)
2. **Google Cloud SDK**: Install the gcloud CLI tool
3. **Python 3.9+**: Required for the application

## Google Cloud Free Tier Resources

The free tier includes:
- **App Engine**: 28 frontend instance hours per day
- **Cloud Storage**: 5 GB storage
- **Cloud Functions**: 2 million invocations per month
- **Firestore**: 1 GB storage, 50K reads, 20K writes per day

## Step-by-Step Deployment

### 1. Set up Google Cloud Project

```bash
# Install Google Cloud SDK (if not already installed)
# Visit: https://cloud.google.com/sdk/docs/install

# Create a new project (replace PROJECT_ID with your desired project name)
gcloud projects create zen-template-helper-demo --name="Zen Template Helper Demo"

# Set the project as default
gcloud config set project zen-template-helper-demo

# Enable required APIs
gcloud services enable appengine.googleapis.com
```

### 2. Initialize App Engine

```bash
# Initialize App Engine (choose a region when prompted)
gcloud app create

# Note: Choose a region close to your users. Popular free tier regions:
# - us-central1 (Iowa)
# - us-east1 (South Carolina)
# - europe-west1 (Belgium)
```

### 3. Deploy the Application

```bash
# Clone this repository (if not already done)
git clone https://github.com/mvillarinos/zen-template-helper.git
cd zen-template-helper

# Deploy to App Engine
gcloud app deploy app.yaml

# When prompted, type 'Y' to continue
```

### 4. Access Your Application

```bash
# Open your deployed application
gcloud app browse
```

Your application will be available at: `https://PROJECT_ID.uc.r.appspot.com`

## Configuration Files Explained

### `app.yaml`
```yaml
runtime: python39          # Python runtime version
handlers:
- url: /static             # Serve static files (CSS, JS, images)
  static_dir: static
- url: /.*                 # Route all other requests to the Flask app
  script: auto
automatic_scaling:
  min_instances: 0         # Scale to zero when not in use (free tier friendly)
  max_instances: 1         # Limit to 1 instance (free tier limit)
```

### `requirements.txt`
```
Flask==2.3.3              # Web framework
Werkzeug==2.3.7           # WSGI toolkit
```

## Features Available in Web Demo

✅ **Template Selection**: Choose from available message templates
✅ **Multi-language Support**: Spanish and English templates
✅ **Client Data Input**: Enter customer information
✅ **Service Selection**: Choose from available spa services
✅ **Template Generation**: Generate personalized messages
✅ **Copy to Clipboard**: Easy copying of generated templates

## Cost Considerations

**Free Tier Limits:**
- App Engine: 28 frontend instance hours/day (about 1.17 hours when running continuously)
- With `min_instances: 0`, your app will scale to zero when not in use
- Perfect for demo/testing purposes

**Staying Within Free Limits:**
- The app automatically scales to zero when not in use
- Each visit starts an instance that runs for a few minutes
- Sufficient for demo purposes and low-traffic testing

## Monitoring Usage

```bash
# Check your current usage
gcloud app logs tail -s default

# View App Engine quotas
gcloud app regions list
```

## Local Development

To run locally for testing:

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python web_app.py

# Access at http://localhost:8080
```

## Updating the Application

```bash
# Make your changes, then redeploy
gcloud app deploy app.yaml

# View logs
gcloud app logs tail -s default
```

## Security Considerations

For production use, consider:
- Adding authentication
- Implementing rate limiting
- Using HTTPS (automatically provided by App Engine)
- Securing sensitive data

## Troubleshooting

**Common Issues:**

1. **Billing Account Required**: Even for free tier, you need to add a billing account
2. **Region Selection**: Choose your region carefully (cannot be changed later)
3. **Quotas Exceeded**: Monitor your usage in the Cloud Console

**Getting Help:**
- Google Cloud Console: [console.cloud.google.com](https://console.cloud.google.com)
- App Engine Documentation: [cloud.google.com/appengine/docs](https://cloud.google.com/appengine/docs)

## Next Steps

Once deployed, you can:
- Share the URL with users for testing
- Monitor usage in Google Cloud Console
- Customize the interface further
- Add more features as needed

Your Zen Template Helper is now running on Google Cloud's free tier! 🎉