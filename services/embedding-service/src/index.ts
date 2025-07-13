import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import multer from 'multer';
import { logger } from './utils/logger';
import { errorHandler } from './middleware/errorHandler';
import { requestLogger } from './middleware/requestLogger';
import { embeddingRoutes } from './routes/embeddingRoutes';
import { ragRoutes } from './routes/ragRoutes';
import { healthRoutes } from './routes/healthRoutes';
import { EmbeddingService } from './services/EmbeddingService';
import { VectorStoreService } from './services/VectorStoreService';
import { RAGService } from './services/RAGService';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3002;

// Configure multer for file uploads
const upload = multer({
  dest: 'uploads/',
  limits: {
    fileSize: 50 * 1024 * 1024, // 50MB limit
  },
});

// Middleware
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(requestLogger);

// Initialize services
const embeddingService = new EmbeddingService();
const vectorStoreService = new VectorStoreService();
const ragService = new RAGService(embeddingService, vectorStoreService);

// Routes
app.use('/api/embeddings', embeddingRoutes(embeddingService, upload));
app.use('/api/rag', ragRoutes(ragService, upload));
app.use('/api/health', healthRoutes(embeddingService, vectorStoreService, ragService));

// Error handling
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  logger.info(`Embedding service running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', async () => {
  logger.info('Shutting down embedding service...');
  await vectorStoreService.disconnect();
  process.exit(0);
});

process.on('SIGTERM', async () => {
  logger.info('Shutting down embedding service...');
  await vectorStoreService.disconnect();
  process.exit(0);
}); 