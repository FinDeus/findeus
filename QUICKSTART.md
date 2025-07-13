# FinDeus Quick Start Guide

This guide will help you get the FinDeus platform up and running in minutes.

## 🚀 Quick Setup (5 minutes)

### 1. Prerequisites
```bash
# Verify you have the required tools
docker --version        # Should be 20.10+
docker-compose --version # Should be 2.0+
node --version          # Should be 18+
git --version           # Any recent version
```

### 2. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-org/findeus.git
cd findeus

# Copy environment file
cp .env.example .env

# Edit .env with your API keys (minimum required)
# OPENAI_API_KEY=your_openai_api_key_here
# JWT_SECRET=your_jwt_secret_here
```

### 3. Start the Platform
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Access the Platform
- **UI Dashboard**: http://localhost:3006
- **API Gateway**: http://localhost:3000
- **Grafana**: http://localhost:3007 (admin/findeus123)

## 🔧 Development Setup

### Install Dependencies
```bash
# Install root dependencies
npm install

# Install service dependencies
npm run install:services
```

### Start Individual Services
```bash
# Start databases first
docker-compose up -d postgres redis neo4j elasticsearch

# Start services in development mode
npm run dev:meta-controller
npm run dev:embedding-service
npm run dev:knowledge-graph
npm run dev:finance-engine
npm run dev:ideation-engine
npm run dev:api-gateway
npm run dev:ui
```

## 🧪 Testing the Platform

### 1. Health Check
```bash
# Check all services are healthy
curl http://localhost:3000/health

# Check individual services
curl http://localhost:3001/api/health  # Meta-controller
curl http://localhost:3002/api/health  # Embedding service
curl http://localhost:3003/api/health  # Knowledge graph
```

### 2. Test AI Query
```bash
curl -X POST http://localhost:3000/api/ai/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the best investment strategies for 2024?",
    "preferredModel": "gpt-4"
  }'
```

### 3. Test Embedding Generation
```bash
curl -X POST http://localhost:3000/api/embeddings/generate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Financial markets analysis document",
    "model": "text-embedding-3-small"
  }'
```

## 📊 Monitoring

### Access Monitoring Tools
- **Grafana**: http://localhost:3007 (admin/findeus123)
- **Prometheus**: http://localhost:9090
- **Neo4j Browser**: http://localhost:7474 (neo4j/findeus123)
- **Kibana**: http://localhost:5601

### Key Metrics to Watch
- Service response times
- AI model performance
- Database connections
- Memory and CPU usage

## 🔍 Troubleshooting

### Common Issues

#### Services won't start
```bash
# Check Docker resources
docker system df
docker system prune -f

# Restart with fresh containers
docker-compose down -v
docker-compose up -d
```

#### Database connection errors
```bash
# Check database status
docker-compose logs postgres
docker-compose logs redis
docker-compose logs neo4j

# Reset databases
docker-compose down -v
docker-compose up -d postgres redis neo4j
```

#### API key errors
```bash
# Verify environment variables
docker-compose exec meta-controller env | grep API_KEY

# Update .env file and restart
docker-compose restart meta-controller
```

### Logs and Debugging
```bash
# View service logs
docker-compose logs -f [service-name]

# Check service status
docker-compose ps

# Execute commands in containers
docker-compose exec [service-name] /bin/sh
```

## 📚 Next Steps

### 1. Configure API Keys
Add your API keys to `.env`:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here
```

### 2. Load Sample Data
```bash
# Load sample financial data
npm run load-sample-data

# Import knowledge graph data
npm run import-graph-data
```

### 3. Explore the Platform
- Visit the UI dashboard at http://localhost:3006
- Try the "Ask FinDeus" chat widget
- Explore the knowledge graph visualization
- Run a sample backtest

### 4. Development
- Read the [Development Guide](docs/development.md)
- Check the [API Documentation](docs/api.md)
- Review the [Architecture Guide](docs/architecture.md)

## 🆘 Getting Help

- **Documentation**: Check the `docs/` directory
- **Issues**: Create an issue on GitHub
- **Discussions**: Join GitHub Discussions
- **Community**: Join our Discord server

## 🎯 Key Features to Try

1. **AI-Powered Analysis**: Ask complex financial questions
2. **Document Processing**: Upload and analyze financial documents
3. **Knowledge Graph**: Explore relationships between entities
4. **Backtesting**: Test investment strategies
5. **Idea Generation**: Generate startup ideas and pitch decks

---

**Happy coding! 🚀** 