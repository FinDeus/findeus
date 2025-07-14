# FinDeus - Netlify Deployment Guide

This guide will help you deploy the FinDeus Financial Intelligence Platform to Netlify.

## Prerequisites

1. **Netlify Account**: Sign up at [netlify.com](https://netlify.com)
2. **GitHub Repository**: Your code is now in the FinDeus/findeus repository
3. **API Keys**: You'll need these API keys for environment variables

## Deployment Steps

### 1. Connect to Netlify
1. Go to [netlify.com](https://netlify.com) and log in
2. Click **"New site from Git"**
3. Choose **GitHub** as your Git provider
4. Select the **`FinDeus/findeus`** repository
5. Configure the build settings (should auto-detect from netlify.toml):
   - **Build command**: `pip install -r requirements.txt`
   - **Publish directory**: `static`
   - **Functions directory**: `netlify/functions`

### 2. Set Environment Variables
In your Netlify dashboard, go to **Site settings** → **Environment variables** and add:

```
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=gcp-starter
FLASK_ENV=production
FLASK_DEBUG=False
```

### 3. Deploy
Click **"Deploy site"** and Netlify will build and deploy your application.

## Features Available

- **AI Query Engine** - OpenAI and Anthropic integration
- **Real-time Market Data** - Yahoo Finance integration
- **Document Processing** - OpenAI embeddings
- **Health Monitoring** - Service status checks

## API Endpoints

- `/api/health` - Health check
- `/api/ai/query` - AI queries
- `/api/market/realtime/<symbol>` - Real-time market data
- `/api/embeddings/generate` - Document embeddings

## Troubleshooting

1. **Build Fails**: Check that all dependencies are in `requirements.txt`
2. **API Errors**: Verify environment variables are set correctly
3. **Function Timeout**: Netlify functions have a 10-second timeout limit

Your FinDeus platform will be live at your Netlify URL! 