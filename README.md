# FinDeus - Complete ASI Software Platform

**FinDeus** is a comprehensive Artificial Super Intelligence (ASI) software platform that delivers end-to-end capabilities in money management, investment strategy, business ideation, and profit optimization.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        FinDeus Platform                         │
├─────────────────────────────────────────────────────────────────┤
│  UI Dashboard (React)                                           │
│  ├─ Ask FinDeus Chat Widget                                     │
│  ├─ Live Backtester with P&L Charts                           │
│  └─ Knowledge Graph Explorer                                    │
├─────────────────────────────────────────────────────────────────┤
│  API Gateway (Express.js)                                      │
│  ├─ JWT Authentication                                          │
│  ├─ Rate Limiting                                               │
│  └─ Request Routing                                             │
├─────────────────────────────────────────────────────────────────┤
│  Microservices Layer                                           │
│  ├─ Meta-Controller (AI Model Routing)                         │
│  ├─ Embedding Service (RAG & Vector Search)                    │
│  ├─ Knowledge Graph (Neo4j)                                    │
│  ├─ Finance Engine (Monte Carlo, VaR, RL)                      │
│  └─ Ideation Engine (Startup Ideas & Pitch Decks)            │
├─────────────────────────────────────────────────────────────────┤
│  Data Layer                                                     │
│  ├─ PostgreSQL (Structured Data)                               │
│  ├─ Neo4j (Knowledge Graph)                                    │
│  ├─ Elasticsearch (Vector Search)                              │
│  └─ Redis (Caching & Sessions)                                 │
├─────────────────────────────────────────────────────────────────┤
│  Monitoring & Infrastructure                                   │
│  ├─ Prometheus (Metrics Collection)                            │
│  ├─ Grafana (Dashboards)                                       │
│  └─ Docker Compose (Orchestration)                             │
└─────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for development)
- Git

### Environment Setup

1. **Clone the repository:**
```bash
git clone https://github.com/your-org/findeus.git
cd findeus
```

2. **Create environment file:**
```bash
cp .env.example .env
```

3. **Configure API keys in `.env`:**
```env
# AI Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GROK_API_KEY=your_grok_api_key_here

# Vector Database
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=us-east-1-aws

# Security
JWT_SECRET=your_jwt_secret_here
```

4. **Start the platform:**
```bash
# Development mode
npm run dev

# Or using Docker Compose directly
docker-compose up -d
```

5. **Access the services:**
- **UI Dashboard**: http://localhost:3006
- **API Gateway**: http://localhost:3000
- **Grafana Monitoring**: http://localhost:3007 (admin/findeus123)
- **Neo4j Browser**: http://localhost:7474 (neo4j/findeus123)
- **Kibana**: http://localhost:5601

## 📋 Service Endpoints

### Meta-Controller (Port 3001)
- `POST /api/ai/query` - Route query to best AI model
- `GET /api/ai/metrics` - Get AI model performance metrics
- `GET /api/ai/models` - List available AI models
- `GET /api/health` - Health check

### Embedding Service (Port 3002)
- `POST /api/embeddings/generate` - Generate embeddings
- `POST /api/embeddings/batch` - Generate batch embeddings
- `POST /api/rag/query` - Perform RAG query
- `POST /api/rag/ingest` - Ingest documents
- `GET /api/health` - Health check

### Knowledge Graph (Port 3003)
- `POST /api/graph/query` - Execute Cypher queries
- `POST /api/graph/entities` - Create entities
- `POST /api/graph/relationships` - Create relationships
- `GET /api/graph/schema` - Get graph schema

### Finance Engine (Port 3004)
- `POST /api/finance/monte-carlo` - Run Monte Carlo simulation
- `POST /api/finance/var` - Calculate Value at Risk
- `POST /api/finance/backtest` - Run strategy backtest
- `GET /api/finance/models` - List available models

### Ideation Engine (Port 3005)
- `POST /api/ideation/generate` - Generate startup ideas
- `POST /api/ideation/pitch-deck` - Create pitch deck
- `GET /api/ideation/trends` - Get market trends
- `POST /api/ideation/analyze` - Analyze business idea

## 🛠️ Development

### Local Development Setup

1. **Install dependencies:**
```bash
npm install
```

2. **Start individual services:**
```bash
# Meta-controller
cd services/meta-controller && npm run dev

# Embedding service
cd services/embedding-service && npm run dev

# Knowledge graph
cd services/knowledge-graph && npm run dev

# Finance engine
cd services/finance-engine && npm run dev

# Ideation engine
cd services/ideation-engine && npm run dev

# API Gateway
cd services/api-gateway && npm run dev

# UI Dashboard
cd ui-dashboard && npm run dev
```

### Running Tests

```bash
# Run all tests
npm test

# Run tests for specific service
cd services/meta-controller && npm test

# Run tests in watch mode
npm run test:watch
```

### Code Quality

```bash
# Lint all code
npm run lint

# Format code
npm run format

# Type checking
npm run type-check
```

## 🔧 Configuration

### Environment Variables

Each service can be configured via environment variables. See individual `.env.example` files in each service directory.

### Database Configuration

- **PostgreSQL**: Default connection on port 5432
- **Neo4j**: Default connection on port 7687
- **Elasticsearch**: Default connection on port 9200
- **Redis**: Default connection on port 6379

### AI Model Configuration

Configure AI providers in the meta-controller service:

```typescript
// services/meta-controller/src/config/providers.ts
export const AI_PROVIDERS = {
  'gpt-4': {
    endpoint: 'https://api.openai.com/v1/chat/completions',
    apiKey: process.env.OPENAI_API_KEY,
    maxTokens: 4096
  },
  'claude-3': {
    endpoint: 'https://api.anthropic.com/v1/messages',
    apiKey: process.env.ANTHROPIC_API_KEY,
    maxTokens: 4096
  },
  'grok': {
    endpoint: 'https://api.x.ai/v1/chat/completions',
    apiKey: process.env.GROK_API_KEY,
    maxTokens: 4096
  }
};
```

## 📊 Monitoring & Observability

### Prometheus Metrics

All services expose metrics on `/metrics` endpoint:

- Request counters and latency
- AI model usage and performance
- Database connection status
- Custom business metrics

### Grafana Dashboards

Pre-configured dashboards for:

- **System Overview**: Service health, response times
- **AI Model Performance**: Usage, confidence scores, fallback rates
- **Financial Metrics**: Backtest results, risk calculations
- **Business Intelligence**: User engagement, feature usage

### Health Checks

Each service provides health endpoints:

- `/api/health` - Basic health check
- `/api/health/detailed` - Detailed health with dependencies
- `/api/health/ready` - Kubernetes readiness probe
- `/api/health/live` - Kubernetes liveness probe

## 🔐 Security

### Authentication

- JWT-based authentication
- Role-based access control (RBAC)
- API key management for external services

### Rate Limiting

- Per-user rate limiting
- IP-based rate limiting
- Service-to-service rate limiting

### Data Protection

- Encryption at rest and in transit
- PII data anonymization
- Audit logging for compliance

## 🚀 Deployment

### Docker Deployment

```bash
# Build all services
docker-compose build

# Deploy to production
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes manifests
kubectl apply -f infrastructure/k8s/

# Check deployment status
kubectl get pods -n findeus
```

### Cloud Deployment

Infrastructure as Code (IaC) configurations are provided for:

- **AWS**: EKS, RDS, ElastiCache, OpenSearch
- **GCP**: GKE, Cloud SQL, Memorystore, Vertex AI
- **Azure**: AKS, Azure Database, Redis Cache

## 📈 Performance Optimization

### Caching Strategy

- **Redis**: Session storage, API response caching
- **In-memory**: Frequently accessed data
- **CDN**: Static assets and API responses

### Database Optimization

- **Connection pooling**: Optimized connection management
- **Query optimization**: Indexed queries and prepared statements
- **Sharding**: Horizontal scaling for large datasets

### AI Model Optimization

- **Model routing**: Intelligent routing based on performance
- **Batch processing**: Efficient batch operations
- **Caching**: Response caching for repeated queries

## 🤝 Contributing

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- **TypeScript**: Strict type checking enabled
- **ESLint**: Airbnb configuration
- **Prettier**: Code formatting
- **Husky**: Pre-commit hooks

### Testing Requirements

- Unit tests for all business logic
- Integration tests for API endpoints
- E2E tests for critical user flows
- Minimum 80% code coverage

## 📚 API Documentation

### OpenAPI Specification

Each service provides OpenAPI/Swagger documentation:

- **Meta-Controller**: http://localhost:3001/api-docs
- **Embedding Service**: http://localhost:3002/api-docs
- **Knowledge Graph**: http://localhost:3003/api-docs
- **Finance Engine**: http://localhost:3004/api-docs
- **Ideation Engine**: http://localhost:3005/api-docs

### Example Usage

```javascript
// Query the meta-controller
const response = await fetch('http://localhost:3001/api/ai/query', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    query: 'What are the best investment strategies for 2024?',
    preferredModel: 'gpt-4'
  })
});

// Generate embeddings
const embeddings = await fetch('http://localhost:3002/api/embeddings/generate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${token}`
  },
  body: JSON.stringify({
    text: 'Financial markets analysis document',
    model: 'text-embedding-3-small'
  })
});
```

## 🔄 Roadmap

### Phase 1 (Current)
- ✅ Core microservices architecture
- ✅ AI model routing and management
- ✅ Vector search and RAG implementation
- ✅ Basic UI dashboard

### Phase 2 (Next Quarter)
- 🔄 Advanced financial modeling
- 🔄 Real-time market data integration
- 🔄 Enhanced knowledge graph
- 🔄 Mobile application

### Phase 3 (Future)
- 📋 Advanced AI agents
- 📋 Regulatory compliance tools
- 📋 Multi-tenant architecture
- 📋 Advanced analytics and reporting

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.findeus.com](https://docs.findeus.com)
- **Issues**: [GitHub Issues](https://github.com/your-org/findeus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/findeus/discussions)
- **Email**: support@findeus.com

## 🙏 Acknowledgments

- OpenAI for GPT models
- Anthropic for Claude models
- Pinecone for vector database
- Neo4j for graph database
- The open-source community

---

**Built with ❤️ by the FinDeus Team** 