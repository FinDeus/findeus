import { Router, Request, Response } from 'express';
import { MetaController } from '../services/MetaController';
import { logger } from '../utils/logger';

export const aiRoutes = (metaController: MetaController) => {
  const router = Router();

  // Process AI query
  router.post('/query', async (req: Request, res: Response) => {
    try {
      const { query, context, preferredModel, maxTokens, temperature } = req.body;

      if (!query) {
        return res.status(400).json({
          success: false,
          error: 'Query is required'
        });
      }

      const response = await metaController.processQuery({
        query,
        context,
        preferredModel,
        maxTokens,
        temperature
      });

      res.json({
        success: true,
        data: response
      });
    } catch (error) {
      logger.error('Error processing AI query:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to process query'
      });
    }
  });

  // Get performance metrics
  router.get('/metrics', async (req: Request, res: Response) => {
    try {
      const metrics = metaController.getPerformanceMetrics();
      res.json({
        success: true,
        data: metrics
      });
    } catch (error) {
      logger.error('Error getting performance metrics:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get metrics'
      });
    }
  });

  // Get available models
  router.get('/models', async (req: Request, res: Response) => {
    try {
      const healthStatus = metaController.getHealthStatus();
      res.json({
        success: true,
        data: healthStatus.models
      });
    } catch (error) {
      logger.error('Error getting models:', error);
      res.status(500).json({
        success: false,
        error: 'Failed to get models'
      });
    }
  });

  return router;
};

export default aiRoutes; 