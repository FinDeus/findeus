import OpenAI from 'openai';
import { logger } from '../utils/logger';

export interface EmbeddingRequest {
  text: string;
  model?: string;
}

export interface EmbeddingResponse {
  embedding: number[];
  model: string;
  tokensUsed: number;
  dimensions: number;
}

export interface BatchEmbeddingRequest {
  texts: string[];
  model?: string;
}

export interface BatchEmbeddingResponse {
  embeddings: number[][];
  model: string;
  totalTokensUsed: number;
  dimensions: number;
}

export class EmbeddingService {
  private openai: OpenAI;
  private defaultModel: string = 'text-embedding-3-small';

  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  async generateEmbedding(request: EmbeddingRequest): Promise<EmbeddingResponse> {
    try {
      const model = request.model || this.defaultModel;
      
      logger.info(`Generating embedding for text (length: ${request.text.length})`, {
        model,
        textLength: request.text.length
      });

      const response = await this.openai.embeddings.create({
        model,
        input: request.text,
      });

      const embedding = response.data[0].embedding;
      
      return {
        embedding,
        model,
        tokensUsed: response.usage.total_tokens,
        dimensions: embedding.length
      };
    } catch (error) {
      logger.error('Error generating embedding:', error);
      throw new Error(`Failed to generate embedding: ${error.message}`);
    }
  }

  async generateBatchEmbeddings(request: BatchEmbeddingRequest): Promise<BatchEmbeddingResponse> {
    try {
      const model = request.model || this.defaultModel;
      
      logger.info(`Generating batch embeddings for ${request.texts.length} texts`, {
        model,
        batchSize: request.texts.length
      });

      const response = await this.openai.embeddings.create({
        model,
        input: request.texts,
      });

      const embeddings = response.data.map(item => item.embedding);
      
      return {
        embeddings,
        model,
        totalTokensUsed: response.usage.total_tokens,
        dimensions: embeddings[0]?.length || 0
      };
    } catch (error) {
      logger.error('Error generating batch embeddings:', error);
      throw new Error(`Failed to generate batch embeddings: ${error.message}`);
    }
  }

  async generateEmbeddingForDocument(
    content: string,
    metadata: { title?: string; source?: string; type?: string } = {}
  ): Promise<EmbeddingResponse & { metadata: any }> {
    try {
      // Clean and prepare content
      const cleanContent = this.cleanText(content);
      
      const embeddingResponse = await this.generateEmbedding({
        text: cleanContent
      });

      return {
        ...embeddingResponse,
        metadata: {
          ...metadata,
          originalLength: content.length,
          cleanedLength: cleanContent.length,
          timestamp: new Date().toISOString()
        }
      };
    } catch (error) {
      logger.error('Error generating document embedding:', error);
      throw error;
    }
  }

  private cleanText(text: string): string {
    // Remove extra whitespace and normalize
    return text
      .replace(/\s+/g, ' ')
      .replace(/\n+/g, '\n')
      .trim();
  }

  async getEmbeddingModels(): Promise<string[]> {
    // Return available embedding models
    return [
      'text-embedding-3-small',
      'text-embedding-3-large',
      'text-embedding-ada-002'
    ];
  }

  calculateCosineSimilarity(embedding1: number[], embedding2: number[]): number {
    if (embedding1.length !== embedding2.length) {
      throw new Error('Embeddings must have the same dimensions');
    }

    let dotProduct = 0;
    let norm1 = 0;
    let norm2 = 0;

    for (let i = 0; i < embedding1.length; i++) {
      dotProduct += embedding1[i] * embedding2[i];
      norm1 += embedding1[i] * embedding1[i];
      norm2 += embedding2[i] * embedding2[i];
    }

    return dotProduct / (Math.sqrt(norm1) * Math.sqrt(norm2));
  }

  async searchSimilar(
    queryEmbedding: number[],
    candidateEmbeddings: { embedding: number[]; metadata: any }[],
    topK: number = 5
  ): Promise<{ similarity: number; metadata: any }[]> {
    try {
      const similarities = candidateEmbeddings.map(candidate => ({
        similarity: this.calculateCosineSimilarity(queryEmbedding, candidate.embedding),
        metadata: candidate.metadata
      }));

      // Sort by similarity (descending) and return top K
      return similarities
        .sort((a, b) => b.similarity - a.similarity)
        .slice(0, topK);
    } catch (error) {
      logger.error('Error searching similar embeddings:', error);
      throw error;
    }
  }

  getHealthStatus(): { status: string; model: string; available: boolean } {
    return {
      status: 'healthy',
      model: this.defaultModel,
      available: !!process.env.OPENAI_API_KEY
    };
  }
} 