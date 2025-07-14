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
- **Build command**: `echo 'Building FinDeus God of Finance'`
- **Publish directory**: `.` (root directory)
- **Functions directory**: `netlify/functions`

### Step 3: Environment Variables
In Netlify dashboard, go to Site settings → Environment variables and add:

**Required API Keys:**
- `OPENAI_API_KEY` = `your-openai-api-key-here`
- `ANTHROPIC_API_KEY` = `your-anthropic-api-key-here`
- `PINECONE_API_KEY` = `your-pinecone-api-key-here`
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

## 🔑 Getting New API Keys

### OpenAI API Key
1. Go to [platform.openai.com](https://platform.openai.com)
2. Sign in or create an account
3. Navigate to API Keys section
4. Click "Create new secret key"
5. Copy the key and add it to Netlify environment variables

### Anthropic API Key
1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign in or create an account
3. Navigate to API Keys
4. Create a new key
5. Copy and add to Netlify environment variables

### Pinecone API Key
1. Go to [pinecone.io](https://pinecone.io)
2. Sign in or create an account
3. Navigate to API Keys
4. Create a new key
5. Copy and add to Netlify environment variables 