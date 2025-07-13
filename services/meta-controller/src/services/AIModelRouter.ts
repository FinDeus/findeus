import axios from 'axios';
import { logger } from '../utils/logger';
import { PerformanceMonitor } from './PerformanceMonitor';

export interface AIModel {
  name: string;
  endpoint: string;
  apiKey: string;
  confidence: number;
  responseTime: number;
  isHealthy: boolean;
}

export interface QueryRequest {
  query: string;
  context?: any;
  preferences?: {
    model?: string;
    temperature?: number;
    maxTokens?: number;
  };
}

export interface QueryResponse {
  response: string;
  model: string;
  confidence: number;
  responseTime: number;
  metadata: any;
}

export class AIModelRouter {
  private models: Map<string, AIModel> = new Map();
  private performanceMonitor: PerformanceMonitor;

  constructor(performanceMonitor: PerformanceMonitor) {
    this.performanceMonitor = performanceMonitor;
    this.initializeModels();
  }

  private initializeModels(): void {
    // Initialize GPT model
    this.models.set('gpt', {
      name: 'GPT-4',
      endpoint: process.env.OPENAI_ENDPOINT || 'https://api.openai.com/v1/chat/completions',
      apiKey: process.env.OPENAI_API_KEY || '',
      confidence: 0.9,
      responseTime: 0,
      isHealthy: true
    });

    // Initialize Claude model
    this.models.set('claude', {
      name: 'Claude-3',
      endpoint: process.env.ANTHROPIC_ENDPOINT || 'https://api.anthropic.com/v1/messages',
      apiKey: process.env.ANTHROPIC_API_KEY || '',
      confidence: 0.85,
      responseTime: 0,
      isHealthy: true
    });

    // Initialize Grok model (placeholder)
    this.models.set('grok', {
      name: 'Grok',
      endpoint: process.env.GROK_ENDPOINT || 'https://api.x.ai/v1/chat/completions',
      apiKey: process.env.GROK_API_KEY || '',
      confidence: 0.8,
      responseTime: 0,
      isHealthy: true
    });
  }

  async routeQuery(request: QueryRequest): Promise<QueryResponse> {
    const startTime = Date.now();
    
    try {
      // Determine best model based on confidence and health
      const selectedModel = this.selectBestModel(request);
      
      logger.info(`Routing query to ${selectedModel.name}`);
      
      // Make request to selected model
      const response = await this.queryModel(selectedModel, request);
      
      const responseTime = Date.now() - startTime;
      
      // Update performance metrics
      this.performanceMonitor.recordResponse(selectedModel.name, responseTime, true);
      
      return {
        response: response.content,
        model: selectedModel.name,
        confidence: selectedModel.confidence,
        responseTime,
        metadata: response.metadata
      };
      
    } catch (error) {
      logger.error('Error routing query:', error);
      
      // Try fallback model
      const fallbackModel = this.getFallbackModel();
      if (fallbackModel) {
        try {
          const response = await this.queryModel(fallbackModel, request);
          const responseTime = Date.now() - startTime;
          
          return {
            response: response.content,
            model: fallbackModel.name,
            confidence: fallbackModel.confidence * 0.8, // Reduced confidence for fallback
            responseTime,
            metadata: { ...response.metadata, fallback: true }
          };
        } catch (fallbackError) {
          logger.error('Fallback model also failed:', fallbackError);
        }
      }
      
      throw new Error('All AI models failed to respond');
    }
  }

  private selectBestModel(request: QueryRequest): AIModel {
    // If user specified a model preference, use it
    if (request.preferences?.model) {
      const preferredModel = this.models.get(request.preferences.model);
      if (preferredModel && preferredModel.isHealthy) {
        return preferredModel;
      }
    }

    // Select model based on confidence and health
    const healthyModels = Array.from(this.models.values())
      .filter(model => model.isHealthy)
      .sort((a, b) => b.confidence - a.confidence);

    if (healthyModels.length === 0) {
      throw new Error('No healthy AI models available');
    }

    return healthyModels[0];
  }

  private getFallbackModel(): AIModel | null {
    const healthyModels = Array.from(this.models.values())
      .filter(model => model.isHealthy)
      .sort((a, b) => a.responseTime - b.responseTime);

    return healthyModels.length > 0 ? healthyModels[0] : null;
  }

  private async queryModel(model: AIModel, request: QueryRequest): Promise<any> {
    const headers = {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${model.apiKey}`
    };

    let payload: any;

    // Format payload based on model type
    if (model.name.includes('GPT')) {
      payload = {
        model: 'gpt-4',
        messages: [{ role: 'user', content: request.query }],
        temperature: request.preferences?.temperature || 0.7,
        max_tokens: request.preferences?.maxTokens || 1000
      };
    } else if (model.name.includes('Claude')) {
      payload = {
        model: 'claude-3-opus-20240229',
        messages: [{ role: 'user', content: request.query }],
        max_tokens: request.preferences?.maxTokens || 1000
      };
    } else {
      // Generic format for other models
      payload = {
        messages: [{ role: 'user', content: request.query }],
        temperature: request.preferences?.temperature || 0.7,
        max_tokens: request.preferences?.maxTokens || 1000
      };
    }

    const response = await axios.post(model.endpoint, payload, { headers });
    
    // Extract content based on model response format
    let content = '';
    if (response.data.choices && response.data.choices[0]) {
      content = response.data.choices[0].message?.content || response.data.choices[0].text;
    } else if (response.data.content) {
      content = response.data.content;
    }

    return {
      content,
      metadata: {
        model: model.name,
        tokens: response.data.usage?.total_tokens || 0,
        cost: this.calculateCost(model.name, response.data.usage?.total_tokens || 0)
      }
    };
  }

  private calculateCost(modelName: string, tokens: number): number {
    const costPerToken = {
      'GPT-4': 0.00003,
      'Claude-3': 0.000015,
      'Grok': 0.00001
    };

    return (costPerToken[modelName as keyof typeof costPerToken] || 0) * tokens;
  }

  getModelStatus(): any {
    return Array.from(this.models.entries()).map(([key, model]) => ({
      id: key,
      name: model.name,
      confidence: model.confidence,
      responseTime: model.responseTime,
      isHealthy: model.isHealthy
    }));
  }

  async healthCheck(): Promise<void> {
    for (const [key, model] of this.models.entries()) {
      try {
        // Simple health check query
        await this.queryModel(model, { query: 'Hello' });
        model.isHealthy = true;
      } catch (error) {
        logger.warn(`Health check failed for ${model.name}:`, error);
        model.isHealthy = false;
      }
    }
  }
}
