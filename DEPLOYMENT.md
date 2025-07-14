# FinDeus Deployment Guide

## 🚀 Deploy to Netlify

### Prerequisites
- GitHub account with your FinDeus repository
- Netlify account (free tier available)

### Step 1: Connect to Netlify
1. Go to [netlify.com](https://netlify.com)
2. Sign up/Login with your GitHub account
3. Click "New site from Git"
4. Choose "GitHub" as your Git provider
5. Select your `findeus` repository

### Step 2: Configure Build Settings
- **Build command**: `echo 'No build required for static site'`
- **Publish directory**: `.` (root directory)
- **Functions directory**: `netlify/functions`

### Step 3: Environment Variables
In Netlify dashboard, go to Site settings → Environment variables and add:
- `OPENAI_API_KEY` = your OpenAI API key
- `ANTHROPIC_API_KEY` = your Anthropic API key (optional)

### Step 4: Deploy
- Click "Deploy site"
- Netlify will automatically build and deploy your site
- You'll get a random URL like `https://amazing-site-123456.netlify.app`

### Step 5: Custom Domain (Optional)
- In Site settings → Domain management
- Add your custom domain
- Follow DNS configuration instructions

## 🔧 Features Enabled
- ✅ Divine "God of Finance" interface
- ✅ AI chat functionality
- ✅ Real-time market data
- ✅ Portfolio analysis
- ✅ Risk assessment
- ✅ Serverless functions for API endpoints
- ✅ Automatic HTTPS
- ✅ Global CDN distribution

## 🛠️ Troubleshooting
- If functions fail, check environment variables are set
- Check function logs in Netlify dashboard
- Ensure all dependencies are in requirements.txt

## 📱 Access Your Live Site
Once deployed, your FinDeus God of Finance platform will be live at your Netlify URL! 