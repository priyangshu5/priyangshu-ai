# Priyangshu AI

A ChatGPT-like AI website featuring advanced text chat and image generation capabilities.

## Features

- 💬 Advanced text chat with multiple AI models
- 🎨 Smart image generation with automatic model selection
- 🌍 Multi-language support (English, Assamese, Hindi, Spanish, French)
- 🎯 Automatic prompt enhancement for better image results
- 💾 Chat history preservation
- 🌙 Dark/Light mode toggle
- 📱 Responsive design for all devices

## Setup Instructions

### For GitHub Pages (Static Frontend):

1. **Create a GitHub repository** named `priyangshu-ai`
2. **Upload these files to your repository:**
   - `index.html`
   - `style.css`
   - `script.js`
   - `assets/` folder with your logo and favicon

3. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Select "Deploy from a branch" → main branch
   - Your website will be available at `https://yourusername.github.io/priyangshu-ai`

### For Backend (Optional - if you want live AI functionality):

The website currently uses a mock backend. To enable real AI functionality:

1. **Deploy the Flask backend:**
   - You can use Heroku, Render, or PythonAnywhere
   - Upload the `api/app.py` file
   - Update the `apiBaseUrl` in `script.js`

2. **Environment variables:**
   - Set your API key as an environment variable
   - The backend will handle all AI requests

## File Structure
