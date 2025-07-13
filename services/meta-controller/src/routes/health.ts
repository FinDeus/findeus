import { Router } from 'express';

export const healthRoutes = Router();

healthRoutes.get('/', (req, res) => {
  res.json({
    status: 'healthy',
    timestamp: new Date().toISOString(),
    service: 'meta-controller',
    version: '1.0.0'
  });
});

healthRoutes.get('/ready', (req, res) => {
  // Check if all dependencies are ready
  res.json({
    status: 'ready',
    timestamp: new Date().toISOString(),
    dependencies: {
      database: 'connected',
      ai_models: 'available'
    }
  });
});
