import axios from 'axios';
import { logger } from '../utils/logger';

export interface AIProvider {
  name: string;
  endpoint: string;
  apiKey?: string;
  maxTokens?: number;
  temperature?: number;
}

export interface QueryRequest {
  query: string;
  context?: any;
  preferredModel?: string;
  maxTokens?: number;
  temperature?: number;
}

export interface QueryResponse {
  response: string;
  model: string;
  confidence: number;
  processingTime: number;
  tokensUsed?: number;
}

export interface ModelPerformance {
  model: string;
  avgResponseTime: number;
  successRate: number;
  avgConfidence: number;
  totalRequests: number;
}

export class MetaController {
  private providers: Map<string, AIProvider> = new Map();
  private performanceMetrics: Map<string, ModelPerformance> = new Map();
  private fallbackOrder: string[] = ['gpt-4', 'claude-3', 'grok'];

  constructor() {
    this.initializeProviders();
  }

  private initializeProviders(): void {
    // Initialize AI providers
    this.providers.set('gpt-4', {
      name: 'GPT-4',
      endpoint: process.env.OPENAI_ENDPOINT || 'https://api.openai.com/v1/chat/completions',
      apiKey: process.env.OPENAI_API_KEY,
      maxTokens: 4096,
      temperature: 0.7
    });

    this.providers.set('claude-3', {
      name: 'Claude-3',
      endpoint: process.env.ANTHROPIC_ENDPOINT || 'https://api.anthropic.com/v1/messages',
      apiKey: process.env.ANTHROPIC_API_KEY,
      maxTokens: 4096,
      temperature: 0.7
    });

    this.providers.set('grok', {
      name: 'Grok',
      endpoint: process.env.GROK_ENDPOINT || 'https://api.x.ai/v1/chat/completions',
      apiKey: process.env.GROK_API_KEY,
      maxTokens: 4096,
      temperature: 0.7
    });

    // Initialize performance metrics
    this.fallbackOrder.forEach(model => {
      this.performanceMetrics.set(model, {
        model,
        avgResponseTime: 0,
        successRate: 1.0,
        avgConfidence: 0.8,
        totalRequests: 0
      });
    });
  }

  async processQuery(request: QueryRequest): Promise<QueryResponse> {
    const startTime = Date.now();
    let selectedModel = this.selectBestModel(request);
    
    logger.info(`Processing query with model: ${selectedModel}`, {
      query: request.query.substring(0, 100),
      model: selectedModel
    });

    try {
      const response = await this.queryModel(selectedModel, request);
      this.updatePerformanceMetrics(selectedModel, Date.now() - startTime, true, response.confidence);
      return response;
    } catch (error) {
      logger.error(`Error with model ${selectedModel}:`, error);
      this.updatePerformanceMetrics(selectedModel, Date.now() - startTime, false, 0);
      
      // Try fallback models
      const fallbackModels = this.fallbackOrder.filter(m => m !== selectedModel);
      for (const fallbackModel of fallbackModels) {
        try {
          logger.info(`Trying fallback model: ${fallbackModel}`);
          const response = await this.queryModel(fallbackModel, request);
          this.updatePerformanceMetrics(fallbackModel, Date.now() - startTime, true, response.confidence);
          return response;
        } catch (fallbackError) {
          logger.error(`Fallback model ${fallbackModel} also failed:`, fallbackError);
          this.updatePerformanceMetrics(fallbackModel, Date.now() - startTime, false, 0);
        }
      }
      
      throw new Error('All AI models failed to respond');
    }
  }

  private selectBestModel(request: QueryRequest): string {
    if (request.preferredModel && this.providers.has(request.preferredModel)) {
      return request.preferredModel;
    }

    // Select based on performance metrics and query type
    let bestModel = this.fallbackOrder[0];
    let bestScore = 0;

    for (const model of this.fallbackOrder) {
      const metrics = this.performanceMetrics.get(model);
      if (!metrics) continue;

      // Calculate score based on success rate, response time, and confidence
      const score = (metrics.successRate * 0.5) + 
                   (metrics.avgConfidence * 0.3) + 
                   ((1 / Math.max(metrics.avgResponseTime, 100)) * 0.2);

      if (score > bestScore) {
        bestScore = score;
        bestModel = model;
      }
    }

    return bestModel;
  }

  private async queryModel(model: string, request: QueryRequest): Promise<QueryResponse> {
    const provider = this.providers.get(model);
    if (!provider) {
      throw new Error(`Provider ${model} not found`);
    }

    const startTime = Date.now();
    let response: any;

    try {
      switch (model) {
        case 'gpt-4':
          response = await this.queryOpenAI(provider, request);
          break;
        case 'claude-3':
          response = await this.queryClaude(provider, request);
          break;
        case 'grok':
          response = await this.queryGrok(provider, request);
          break;
        default:
          throw new Error(`Unsupported model: ${model}`);
      }

      const processingTime = Date.now() - startTime;
      const confidence = this.calculateConfidence(response, processingTime);

      return {
        response: response.content,
        model,
        confidence,
        processingTime,
        tokensUsed: response.tokensUsed
      };
    } catch (error) {
      logger.error(`Error querying ${model}:`, error);
      throw error;
    }
  }

  private async queryOpenAI(provider: AIProvider, request: QueryRequest): Promise<any> {
    const response = await axios.post(provider.endpoint, {
      model: 'gpt-4',
      messages: [
        { role: 'user', content: request.query }
      ],
      max_tokens: request.maxTokens || provider.maxTokens,
      temperature: request.temperature || provider.temperature
    }, {
      headers: {
        'Authorization': `Bearer ${provider.apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    return {
      content: response.data.choices[0].message.content,
      tokensUsed: response.data.usage.total_tokens
    };
  }

  private async queryClaude(provider: AIProvider, request: QueryRequest): Promise<any> {
    const response = await axios.post(provider.endpoint, {
      model: 'claude-3-sonnet-20240229',
      max_tokens: request.maxTokens || provider.maxTokens,
      messages: [
        { role: 'user', content: request.query }
      ]
    }, {
      headers: {
        'x-api-key': provider.apiKey,
        'Content-Type': 'application/json',
        'anthropic-version': '2023-06-01'
      }
    });

    return {
      content: response.data.content[0].text,
      tokensUsed: response.data.usage.input_tokens + response.data.usage.output_tokens
    };
  }

  private async queryGrok(provider: AIProvider, request: QueryRequest): Promise<any> {
    const response = await axios.post(provider.endpoint, {
      model: 'grok-beta',
      messages: [
        { role: 'user', content: request.query }
      ],
      max_tokens: request.maxTokens || provider.maxTokens,
      temperature: request.temperature || provider.temperature
    }, {
      headers: {
        'Authorization': `Bearer ${provider.apiKey}`,
        'Content-Type': 'application/json'
      }
    });

    return {
      content: response.data.choices[0].message.content,
      tokensUsed: response.data.usage.total_tokens
    };
  }

  private calculateConfidence(response: any, processingTime: number): number {
    // Simple confidence calculation based on response length and processing time
    const responseLength = response.content.length;
    const lengthScore = Math.min(responseLength / 1000, 1.0);
    const timeScore = Math.max(0, 1 - (processingTime / 10000));
    
    return (lengthScore * 0.6) + (timeScore * 0.4);
  }

  private updatePerformanceMetrics(model: string, responseTime: number, success: boolean, confidence: number): void {
    const metrics = this.performanceMetrics.get(model);
    if (!metrics) return;

    const totalRequests = metrics.totalRequests + 1;
    const successRate = success 
      ? (metrics.successRate * metrics.totalRequests + 1) / totalRequests
      : (metrics.successRate * metrics.totalRequests) / totalRequests;
    
    const avgResponseTime = (metrics.avgResponseTime * metrics.totalRequests + responseTime) / totalRequests;
    const avgConfidence = success 
      ? (metrics.avgConfidence * metrics.totalRequests + confidence) / totalRequests
      : metrics.avgConfidence;

    this.performanceMetrics.set(model, {
      model,
      avgResponseTime,
      successRate,
      avgConfidence,
      totalRequests
    });
  }

  getPerformanceMetrics(): ModelPerformance[] {
    return Array.from(this.performanceMetrics.values());
  }

  getHealthStatus(): { status: string; models: any[] } {
    const models = Array.from(this.providers.entries()).map(([key, provider]) => {
      const metrics = this.performanceMetrics.get(key);
      return {
        name: provider.name,
        key,
        available: true, // This could be enhanced with actual health checks
        metrics
      };
    });

    return {
      status: 'healthy',
      models
    };
  }
} 