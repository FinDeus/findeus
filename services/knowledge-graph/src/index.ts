import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import { logger } from './utils/logger';
import { errorHandler } from './middleware/errorHandler';
import { requestLogger } from './middleware/requestLogger';
import { graphRoutes } from './routes/graphRoutes';
import { dataRoutes } from './routes/dataRoutes';
import { healthRoutes } from './routes/healthRoutes';
import { Neo4jService } from './services/Neo4jService';
import { DataIngestionService } from './services/DataIngestionService';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3003;

// Middleware
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(requestLogger);

// Initialize services
const neo4jService = new Neo4jService();
const dataIngestionService = new DataIngestionService(neo4jService);

// Initialize database
neo4jService.initialize().then(() => {
  logger.info('Neo4j service initialized successfully');
}).catch((error) => {
  logger.error('Failed to initialize Neo4j service:', error);
});

// Routes
app.use('/api/graph', graphRoutes(neo4jService));
app.use('/api/data', dataRoutes(dataIngestionService));
app.use('/api/health', healthRoutes(neo4jService));

// Error handling
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  logger.info(`Knowledge graph service running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', async () => {
  logger.info('Shutting down knowledge graph service...');
  await neo4jService.close();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  logger.info('Shutting down knowledge graph service...');
  await neo4jService.close();
  process.exit(0);
}); 