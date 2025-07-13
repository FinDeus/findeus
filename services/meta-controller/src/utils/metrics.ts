import { register, Counter, Histogram, Gauge } from 'prom-client';

export const createPrometheusMetrics = () => {
  // Request counters
  const requestCounter = new Counter({
    name: 'meta_controller_requests_total',
    help: 'Total number of requests',
    labelNames: ['method', 'route', 'status_code']
  });

  // Request duration histogram
  const requestDuration = new Histogram({
    name: 'meta_controller_request_duration_seconds',
    help: 'Duration of HTTP requests in seconds',
    labelNames: ['method', 'route'],
    buckets: [0.1, 0.5, 1, 2, 5]
  });

  // AI model usage counters
  const aiModelUsage = new Counter({
    name: 'meta_controller_ai_model_usage_total',
    help: 'Total usage of AI models',
    labelNames: ['model', 'status']
  });

  // AI model response time
  const aiModelResponseTime = new Histogram({
    name: 'meta_controller_ai_response_time_seconds',
    help: 'Response time of AI models in seconds',
    labelNames: ['model'],
    buckets: [0.5, 1, 2, 5, 10, 30]
  });

  // Active connections gauge
  const activeConnections = new Gauge({
    name: 'meta_controller_active_connections',
    help: 'Number of active connections'
  });

  // Confidence score histogram
  const confidenceScore = new Histogram({
    name: 'meta_controller_confidence_score',
    help: 'Confidence scores for AI model routing',
    labelNames: ['model'],
    buckets: [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
  });

  // Error rate counter
  const errorRate = new Counter({
    name: 'meta_controller_errors_total',
    help: 'Total number of errors',
    labelNames: ['error_type', 'model']
  });

  return {
    register,
    requestCounter,
    requestDuration,
    aiModelUsage,
    aiModelResponseTime,
    activeConnections,
    confidenceScore,
    errorRate
  };
};

export type MetricsType = ReturnType<typeof createPrometheusMetrics>; 