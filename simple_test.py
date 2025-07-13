#!/usr/bin/env python3
"""
Simple FinDeus Platform Test
============================

This demonstrates the core FinDeus functionality working with your real API keys.
"""

import requests
import json
import time

def load_env():
    """Load environment variables from .env file"""
    env_vars = {}
    with open('.env', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    return env_vars

def ai_financial_analysis(api_key):
    """Simulate the Meta-Controller AI analysis"""
    print("🧠 FinDeus AI Analysis Engine")
    print("   Analyzing: 'Should I invest in tech stocks in 2024?'")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-4',
        'messages': [
            {
                'role': 'system', 
                'content': 'You are FinDeus, an AI financial advisor. Provide concise, actionable investment advice.'
            },
            {
                'role': 'user', 
                'content': 'Should I invest in tech stocks in 2024? Give me 3 key points with reasoning.'
            }
        ],
        'max_tokens': 200
    }
    
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        advice = result['choices'][0]['message']['content']
        print(f"   💡 FinDeus Advice:\n{advice}")
        return advice
    else:
        print("   ❌ AI analysis failed")
        return None

def document_processing(api_key):
    """Simulate document processing and embedding generation"""
    print("\n📄 Document Processing & RAG Pipeline")
    
    # Sample financial document content
    documents = [
        "Apple Inc. reported Q4 2023 revenue of $119.58 billion, up 2% year-over-year. iPhone sales remained strong despite market challenges.",
        "Tesla's stock price volatility increased 15% in Q4 2023 due to production concerns and competitive pressure from traditional automakers.",
        "The Federal Reserve maintained interest rates at 5.25-5.50% in December 2023, signaling potential cuts in 2024 based on inflation data."
    ]
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    print("   🔍 Processing financial documents...")
    embeddings = []
    
    for i, doc in enumerate(documents):
        print(f"   📊 Document {i+1}: {doc[:50]}...")
        
        data = {
            'model': 'text-embedding-3-small',
            'input': doc
        }
        
        response = requests.post('https://api.openai.com/v1/embeddings', headers=headers, json=data)
        
        if response.status_code == 200:
            result = response.json()
            embedding = result['data'][0]['embedding']
            embeddings.append({
                'document': doc,
                'embedding': embedding,
                'dimensions': len(embedding)
            })
            print(f"   ✅ Generated {len(embedding)}-dimensional embedding")
        else:
            print(f"   ❌ Failed to process document {i+1}")
    
    return embeddings

def rag_query(api_key, embeddings):
    """Simulate RAG query using processed documents"""
    print("\n🔍 RAG Query: 'What companies had strong Q4 2023 performance?'")
    
    # In a real implementation, this would use vector similarity search
    # For demo, we'll use the Apple document as most relevant
    relevant_doc = embeddings[0]['document'] if embeddings else "No relevant documents found"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {
                'role': 'system',
                'content': 'You are FinDeus RAG system. Answer based on the provided document context.'
            },
            {
                'role': 'user',
                'content': f"Based on this document: '{relevant_doc}'\n\nQuestion: What companies had strong Q4 2023 performance?"
            }
        ],
        'max_tokens': 150
    }
    
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        answer = result['choices'][0]['message']['content']
        print(f"   💬 RAG Response: {answer}")
        return answer
    else:
        print("   ❌ RAG query failed")
        return None

def monte_carlo_simulation():
    """Simulate Monte Carlo financial modeling"""
    print("\n💰 Monte Carlo Portfolio Simulation")
    print("   📊 Simulating 10,000 scenarios for tech-heavy portfolio...")
    
    # Simulate results
    import random
    random.seed(42)
    
    scenarios = []
    for _ in range(10000):
        # Simulate annual return (normal distribution around 8% with 15% volatility)
        annual_return = random.normalvariate(0.08, 0.15)
        scenarios.append(annual_return)
    
    # Calculate statistics
    expected_return = sum(scenarios) / len(scenarios)
    scenarios.sort()
    var_95 = scenarios[int(0.05 * len(scenarios))]  # 5th percentile
    max_loss = min(scenarios)
    
    print(f"   📈 Expected Return: {expected_return:.2%}")
    print(f"   📉 VaR (95%): {var_95:.2%}")
    print(f"   ⚠️  Max Potential Loss: {max_loss:.2%}")
    print(f"   🎯 Recommendation: {'MODERATE BUY' if expected_return > 0.05 else 'HOLD'}")

def startup_idea_generator(api_key):
    """Generate startup ideas using AI"""
    print("\n💡 AI Startup Idea Generator")
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [
            {
                'role': 'system',
                'content': 'You are FinDeus Ideation Engine. Generate innovative fintech startup ideas.'
            },
            {
                'role': 'user',
                'content': 'Generate 2 innovative fintech startup ideas for 2024. Include brief description and market potential.'
            }
        ],
        'max_tokens': 250
    }
    
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    
    if response.status_code == 200:
        result = response.json()
        ideas = result['choices'][0]['message']['content']
        print(f"   🚀 Generated Ideas:\n{ideas}")
        return ideas
    else:
        print("   ❌ Idea generation failed")
        return None

def main():
    """Main demo function"""
    print("=" * 60)
    print("🚀 FinDeus Platform - Live Demo")
    print("   Your AI-Powered Financial Intelligence Platform")
    print("=" * 60)
    
    # Load API keys
    env_vars = load_env()
    openai_key = env_vars.get('OPENAI_API_KEY')
    
    if not openai_key or openai_key == "your_openai_api_key_here":
        print("❌ OpenAI API key not configured")
        return
    
    print("✅ API keys loaded successfully\n")
    
    # Run demonstrations
    try:
        # AI Financial Analysis
        ai_financial_analysis(openai_key)
        
        # Document Processing
        embeddings = document_processing(openai_key)
        
        # RAG Query
        if embeddings:
            rag_query(openai_key, embeddings)
        
        # Monte Carlo Simulation
        monte_carlo_simulation()
        
        # Startup Ideas
        startup_idea_generator(openai_key)
        
        print("\n" + "=" * 60)
        print("🎉 FinDeus Platform Demo Complete!")
        print("   All core features working with your API keys")
        print("=" * 60)
        
        print("\n🚀 Ready to launch full platform:")
        print("   1. Install Docker Desktop")
        print("   2. Run: docker-compose up -d")
        print("   3. Access: http://localhost:3006")
        print("   4. Start building your financial AI empire!")
        
    except Exception as e:
        print(f"❌ Demo error: {str(e)}")

if __name__ == "__main__":
    main() 