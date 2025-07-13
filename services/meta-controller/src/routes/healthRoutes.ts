import { Router, Request, Response } from 'express';
import { MetaController } from '../services/MetaController';
import { logger } from '../utils/logger';

export const healthRoutes = (metaController: MetaController) => {
  const router = Router();

  // Health check endpoint
  router.get('/', async (req: Request, res: Response) => {
    try {
      const healthStatus = metaController.getHealthStatus();
      res.json({
        success: true,
        data: healthStatus,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      logger.error('Error getting health status:', error);
      res.status(500).json({
        success: false,
        error: 'Health check failed',
        timestamp: new Date().toISOString()
      });
    }
  });

  // Detailed health check
  router.get('/detailed', async (req: Request, res: Response) => {
    try {
      const healthStatus = metaController.getHealthStatus();
      const performanceMetrics = metaController.getPerformanceMetrics();
      
      res.json({
        success: true,
        data: {
          ...healthStatus,
          performanceMetrics,
          uptime: process.uptime(),
          memory: process.memoryUsage(),
          timestamp: new Date().toISOString()
        }
      });
    } catch (error) {
      logger.error('Error getting detailed health status:', error);
      res.status(500).json({
        success: false,
        error: 'Detailed health check failed',
        timestamp: new Date().toISOString()
      });
    }
  });

  // Readiness probe
  router.get('/ready', async (req: Request, res: Response) => {
    try {
      const healthStatus = metaController.getHealthStatus();
      const isReady = healthStatus.status === 'healthy';
      
      if (isReady) {
        res.json({
          success: true,
          ready: true,
          timestamp: new Date().toISOString()
        });
      } else {
        res.status(503).json({
          success: false,
          ready: false,
          timestamp: new Date().toISOString()
        });
      }
    } catch (error) {
      logger.error('Error checking readiness:', error);
      res.status(503).json({
        success: false,
        ready: false,
        error: 'Readiness check failed',
        timestamp: new Date().toISOString()
      });
    }
  });

  // Liveness probe
  router.get('/live', async (req: Request, res: Response) => {
    res.json({
      success: true,
      alive: true,
      timestamp: new Date().toISOString()
    });
  });

  return router;
};

export default healthRoutes; 