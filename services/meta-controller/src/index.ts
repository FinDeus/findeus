import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import compression from 'compression';
import dotenv from 'dotenv';
import { createPrometheusMetrics } from './utils/metrics';
import { logger } from './utils/logger';
import { errorHandler } from './middleware/errorHandler';
import { requestLogger } from './middleware/requestLogger';
import { aiRoutes } from './routes/aiRoutes';
import { healthRoutes } from './routes/healthRoutes';
import { MetaController } from './services/MetaController';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;

// Initialize Prometheus metrics
const metrics = createPrometheusMetrics();

// Middleware
app.use(helmet());
app.use(cors());
app.use(compression());
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));
app.use(requestLogger);

// Metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', metrics.register.contentType);
  res.end(metrics.register.metrics());
});

// Initialize Meta Controller
const metaController = new MetaController();

// Routes
app.use('/api/ai', aiRoutes(metaController));
app.use('/api/health', healthRoutes(metaController));

// Error handling
app.use(errorHandler);

// Start server
app.listen(PORT, () => {
  logger.info(`Meta-controller service running on port ${PORT}`);
});

// Graceful shutdown
process.on('SIGINT', () => {
  logger.info('Shutting down meta-controller service...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('Shutting down meta-controller service...');
  process.exit(0);
});
