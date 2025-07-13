import { Router } from 'express';
import { AIModelRouter } from '../services/AIModelRouter';
import { logger } from '../utils/logger';

export const aiRoutes = (aiModelRouter: AIModelRouter) => {
  const router = Router();

  // Query AI models
  router.post('/query', async (req, res) => {
    try {
      const { query, context, preferences } = req.body;

      if (!query) {
        return res.status(400).json({ error: 'Query is required' });
      }

      const response = await aiModelRouter.routeQuery({
        query,
        context,
        preferences
      });

      res.json(response);
    } catch (error) {
      logger.error('Error processing AI query:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // Get model status
  router.get('/models/status', (req, res) => {
    try {
      const status = aiModelRouter.getModelStatus();
      res.json(status);
    } catch (error) {
      logger.error('Error getting model status:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  // Health check for models
  router.post('/models/health-check', async (req, res) => {
    try {
      await aiModelRouter.healthCheck();
      res.json({ message: 'Health check completed' });
    } catch (error) {
      logger.error('Error during health check:', error);
      res.status(500).json({ error: 'Internal server error' });
    }
  });

  return router;
};
