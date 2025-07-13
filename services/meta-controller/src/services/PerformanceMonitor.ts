import { logger } from '../utils/logger';

export interface PerformanceMetrics {
  modelName: string;
  responseTime: number;
  success: boolean;
  timestamp: Date;
  tokensUsed: number;
  cost: number;
}

export class PerformanceMonitor {
  private metrics: PerformanceMetrics[] = [];
  private modelStats: Map<string, any> = new Map();

  constructor() {
    this.initializeStats();
  }

  private initializeStats(): void {
    const models = ['GPT-4', 'Claude-3', 'Grok'];
    models.forEach(model => {
      this.modelStats.set(model, {
        totalRequests: 0,
        successfulRequests: 0,
        averageResponseTime: 0,
        totalCost: 0,
        confidence: 0.8
      });
    });
  }

  recordResponse(modelName: string, responseTime: number, success: boolean, tokensUsed: number = 0, cost: number = 0): void {
    const metric: PerformanceMetrics = {
      modelName,
      responseTime,
      success,
      timestamp: new Date(),
      tokensUsed,
      cost
    };

    this.metrics.push(metric);
    this.updateModelStats(modelName, metric);

    // Keep only last 1000 metrics
    if (this.metrics.length > 1000) {
      this.metrics = this.metrics.slice(-1000);
    }
  }

  private updateModelStats(modelName: string, metric: PerformanceMetrics): void {
    const stats = this.modelStats.get(modelName);
    if (!stats) return;

    stats.totalRequests++;
    if (metric.success) {
      stats.successfulRequests++;
    }

    // Update average response time
    stats.averageResponseTime = (stats.averageResponseTime * (stats.totalRequests - 1) + metric.responseTime) / stats.totalRequests;
    
    // Update total cost
    stats.totalCost += metric.cost;

    // Update confidence based on success rate and response time
    const successRate = stats.successfulRequests / stats.totalRequests;
    const responseTimeFactor = Math.max(0, 1 - (stats.averageResponseTime / 10000)); // Penalize slow responses
    stats.confidence = (successRate * 0.7 + responseTimeFactor * 0.3);

    this.modelStats.set(modelName, stats);
  }

  getModelStats(): any {
    return Array.from(this.modelStats.entries()).map(([model, stats]) => ({
      model,
      ...stats,
      successRate: stats.totalRequests > 0 ? stats.successfulRequests / stats.totalRequests : 0
    }));
  }

  getRecentMetrics(minutes: number = 60): PerformanceMetrics[] {
    const cutoff = new Date(Date.now() - minutes * 60 * 1000);
    return this.metrics.filter(metric => metric.timestamp >= cutoff);
  }

  startMonitoring(): void {
    // Run health checks every 5 minutes
    setInterval(() => {
      this.runHealthChecks();
    }, 5 * 60 * 1000);

    logger.info('Performance monitoring started');
  }

  private runHealthChecks(): void {
    // This would typically ping each model endpoint
    logger.info('Running health checks...');
    
    // Update model health status based on recent performance
    const recentMetrics = this.getRecentMetrics(10); // Last 10 minutes
    
    for (const [modelName, stats] of this.modelStats.entries()) {
      const modelMetrics = recentMetrics.filter(m => m.modelName === modelName);
      
      if (modelMetrics.length > 0) {
        const recentSuccessRate = modelMetrics.filter(m => m.success).length / modelMetrics.length;
        const avgResponseTime = modelMetrics.reduce((sum, m) => sum + m.responseTime, 0) / modelMetrics.length;
        
        // Update confidence based on recent performance
        const responseTimeFactor = Math.max(0, 1 - (avgResponseTime / 10000));
        stats.confidence = (recentSuccessRate * 0.7 + responseTimeFactor * 0.3);
        
        logger.info(`${modelName} health: ${(recentSuccessRate * 100).toFixed(1)}% success, ${avgResponseTime.toFixed(0)}ms avg response`);
      }
    }
  }
}
