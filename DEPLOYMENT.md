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

**Required API Keys:**
- `OPENAI_API_KEY` = `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`
- `ANTHROPIC_API_KEY` = `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`
- `PINECONE_API_KEY` = `pcsk_5pzSVC_LDozAkXeNkEKP48vhnVB2FQkEv5dPD9yJAWpWvyiTzbVB5PHj7fitXxQ4YGEy37`
- `PINECONE_ENVIRONMENT` = `gcp-starter`

**Flask Configuration:**
- `FLASK_ENV` = `production`
- `FLASK_DEBUG` = `False`

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
- ✅ Real AI chat functionality (OpenAI & Anthropic)
- ✅ Real-time market data
- ✅ Portfolio analysis
- ✅ Risk assessment
- ✅ Pinecone vector database integration
- ✅ Serverless functions for API endpoints
- ✅ Automatic HTTPS
- ✅ Global CDN distribution

## 🛠️ Troubleshooting
- If functions fail, check environment variables are set correctly
- Check function logs in Netlify dashboard
- Ensure all API keys are valid and have proper permissions
- Verify Pinecone environment is set correctly

## 📱 Access Your Live Site
Once deployed with the API keys, your FinDeus God of Finance platform will be live with full AI capabilities at your Netlify URL! 