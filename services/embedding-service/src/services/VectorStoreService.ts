import { PineconeClient } from 'pinecone-client';
import { Client as ElasticsearchClient } from '@elastic/elasticsearch';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '../utils/logger';

export interface VectorDocument {
  id: string;
  embedding: number[];
  metadata: {
    title?: string;
    content?: string;
    source?: string;
    type?: string;
    timestamp?: string;
    [key: string]: any;
  };
}

export interface SearchResult {
  id: string;
  score: number;
  metadata: any;
}

export interface SearchRequest {
  embedding: number[];
  topK?: number;
  filter?: { [key: string]: any };
  includeMetadata?: boolean;
}

export class VectorStoreService {
  private pinecone: PineconeClient;
  private elasticsearch: ElasticsearchClient;
  private indexName: string;
  private esIndexName: string;

  constructor() {
    this.indexName = process.env.PINECONE_INDEX_NAME || 'findeus-embeddings';
    this.esIndexName = process.env.ELASTICSEARCH_INDEX_NAME || 'findeus-documents';
    
    this.initializePinecone();
    this.initializeElasticsearch();
  }

  private async initializePinecone(): Promise<void> {
    try {
      if (!process.env.PINECONE_API_KEY) {
        logger.warn('Pinecone API key not found, skipping Pinecone initialization');
        return;
      }

      this.pinecone = new PineconeClient({
        apiKey: process.env.PINECONE_API_KEY,
        environment: process.env.PINECONE_ENVIRONMENT || 'us-east-1-aws',
      });

      await this.pinecone.init();
      logger.info('Pinecone initialized successfully');
    } catch (error) {
      logger.error('Error initializing Pinecone:', error);
    }
  }

  private async initializeElasticsearch(): Promise<void> {
    try {
      if (!process.env.ELASTICSEARCH_URL) {
        logger.warn('Elasticsearch URL not found, skipping Elasticsearch initialization');
        return;
      }

      this.elasticsearch = new ElasticsearchClient({
        node: process.env.ELASTICSEARCH_URL,
        auth: {
          username: process.env.ELASTICSEARCH_USERNAME || 'elastic',
          password: process.env.ELASTICSEARCH_PASSWORD || 'changeme'
        }
      });

      // Test connection
      await this.elasticsearch.ping();
      logger.info('Elasticsearch initialized successfully');

      // Create index if it doesn't exist
      await this.createElasticsearchIndex();
    } catch (error) {
      logger.error('Error initializing Elasticsearch:', error);
    }
  }

  private async createElasticsearchIndex(): Promise<void> {
    try {
      const exists = await this.elasticsearch.indices.exists({
        index: this.esIndexName
      });

      if (!exists) {
        await this.elasticsearch.indices.create({
          index: this.esIndexName,
          body: {
            mappings: {
              properties: {
                id: { type: 'keyword' },
                embedding: {
                  type: 'dense_vector',
                  dims: 1536 // OpenAI embedding dimensions
                },
                metadata: {
                  properties: {
                    title: { type: 'text' },
                    content: { type: 'text' },
                    source: { type: 'keyword' },
                    type: { type: 'keyword' },
                    timestamp: { type: 'date' }
                  }
                }
              }
            }
          }
        });
        logger.info(`Created Elasticsearch index: ${this.esIndexName}`);
      }
    } catch (error) {
      logger.error('Error creating Elasticsearch index:', error);
    }
  }

  async storeVector(document: VectorDocument): Promise<void> {
    try {
      const id = document.id || uuidv4();
      
      // Store in Pinecone
      if (this.pinecone) {
        await this.pinecone.upsert({
          indexName: this.indexName,
          vectors: [{
            id,
            values: document.embedding,
            metadata: document.metadata
          }]
        });
      }

      // Store in Elasticsearch
      if (this.elasticsearch) {
        await this.elasticsearch.index({
          index: this.esIndexName,
          id,
          body: {
            id,
            embedding: document.embedding,
            metadata: document.metadata
          }
        });
      }

      logger.info(`Stored vector with ID: ${id}`);
    } catch (error) {
      logger.error('Error storing vector:', error);
      throw error;
    }
  }

  async storeBatchVectors(documents: VectorDocument[]): Promise<void> {
    try {
      // Store in Pinecone
      if (this.pinecone) {
        const vectors = documents.map(doc => ({
          id: doc.id || uuidv4(),
          values: doc.embedding,
          metadata: doc.metadata
        }));

        await this.pinecone.upsert({
          indexName: this.indexName,
          vectors
        });
      }

      // Store in Elasticsearch
      if (this.elasticsearch) {
        const body = documents.flatMap(doc => [
          { index: { _index: this.esIndexName, _id: doc.id || uuidv4() } },
          {
            id: doc.id || uuidv4(),
            embedding: doc.embedding,
            metadata: doc.metadata
          }
        ]);

        await this.elasticsearch.bulk({ body });
      }

      logger.info(`Stored ${documents.length} vectors in batch`);
    } catch (error) {
      logger.error('Error storing batch vectors:', error);
      throw error;
    }
  }

  async searchVectors(request: SearchRequest): Promise<SearchResult[]> {
    try {
      const topK = request.topK || 10;
      
      // Try Pinecone first
      if (this.pinecone) {
        const queryRequest = {
          indexName: this.indexName,
          vector: request.embedding,
          topK,
          includeMetadata: request.includeMetadata !== false,
          filter: request.filter
        };

        const results = await this.pinecone.query(queryRequest);
        
        return results.matches.map(match => ({
          id: match.id,
          score: match.score,
          metadata: match.metadata
        }));
      }

      // Fallback to Elasticsearch
      if (this.elasticsearch) {
        const searchBody: any = {
          query: {
            script_score: {
              query: { match_all: {} },
              script: {
                source: "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                params: { query_vector: request.embedding }
              }
            }
          },
          size: topK
        };

        if (request.filter) {
          searchBody.query.script_score.query = {
            bool: {
              must: [{ match_all: {} }],
              filter: Object.entries(request.filter).map(([key, value]) => ({
                term: { [`metadata.${key}`]: value }
              }))
            }
          };
        }

        const response = await this.elasticsearch.search({
          index: this.esIndexName,
          body: searchBody
        });

        return response.body.hits.hits.map((hit: any) => ({
          id: hit._id,
          score: hit._score,
          metadata: hit._source.metadata
        }));
      }

      throw new Error('No vector store available');
    } catch (error) {
      logger.error('Error searching vectors:', error);
      throw error;
    }
  }

  async deleteVector(id: string): Promise<void> {
    try {
      // Delete from Pinecone
      if (this.pinecone) {
        await this.pinecone.delete({
          indexName: this.indexName,
          ids: [id]
        });
      }

      // Delete from Elasticsearch
      if (this.elasticsearch) {
        await this.elasticsearch.delete({
          index: this.esIndexName,
          id
        });
      }

      logger.info(`Deleted vector with ID: ${id}`);
    } catch (error) {
      logger.error('Error deleting vector:', error);
      throw error;
    }
  }

  async getVectorById(id: string): Promise<VectorDocument | null> {
    try {
      // Try Elasticsearch first for full document retrieval
      if (this.elasticsearch) {
        const response = await this.elasticsearch.get({
          index: this.esIndexName,
          id
        });

        if (response.body.found) {
          return {
            id: response.body._id,
            embedding: response.body._source.embedding,
            metadata: response.body._source.metadata
          };
        }
      }

      return null;
    } catch (error) {
      logger.error('Error getting vector by ID:', error);
      return null;
    }
  }

  async getStats(): Promise<{ totalVectors: number; indexSize: number }> {
    try {
      let totalVectors = 0;
      let indexSize = 0;

      // Get stats from Pinecone
      if (this.pinecone) {
        const stats = await this.pinecone.describeIndexStats({
          indexName: this.indexName
        });
        totalVectors = stats.totalVectorCount || 0;
      }

      // Get stats from Elasticsearch
      if (this.elasticsearch) {
        const stats = await this.elasticsearch.indices.stats({
          index: this.esIndexName
        });
        indexSize = stats.body.indices[this.esIndexName]?.total?.store?.size_in_bytes || 0;
      }

      return { totalVectors, indexSize };
    } catch (error) {
      logger.error('Error getting vector store stats:', error);
      return { totalVectors: 0, indexSize: 0 };
    }
  }

  async disconnect(): Promise<void> {
    try {
      if (this.elasticsearch) {
        await this.elasticsearch.close();
      }
      logger.info('Vector store connections closed');
    } catch (error) {
      logger.error('Error disconnecting from vector store:', error);
    }
  }

  getHealthStatus(): { pinecone: boolean; elasticsearch: boolean } {
    return {
      pinecone: !!this.pinecone,
      elasticsearch: !!this.elasticsearch
    };
  }
} 