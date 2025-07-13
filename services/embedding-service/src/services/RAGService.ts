import { EmbeddingService } from './EmbeddingService';
import { VectorStoreService, SearchResult } from './VectorStoreService';
import { logger } from '../utils/logger';
import * as fs from 'fs';
import * as path from 'path';
import pdfParse from 'pdf-parse';
import mammoth from 'mammoth';
import * as cheerio from 'cheerio';

export interface RAGQuery {
  query: string;
  topK?: number;
  filter?: { [key: string]: any };
  includeContext?: boolean;
}

export interface RAGResponse {
  query: string;
  context: SearchResult[];
  contextText: string;
  retrievalTime: number;
  totalResults: number;
}

export interface DocumentIngestionRequest {
  filePath: string;
  metadata?: {
    title?: string;
    source?: string;
    type?: string;
    [key: string]: any;
  };
  chunkSize?: number;
  overlapSize?: number;
}

export interface DocumentChunk {
  content: string;
  metadata: any;
  chunkIndex: number;
}

export class RAGService {
  private embeddingService: EmbeddingService;
  private vectorStoreService: VectorStoreService;

  constructor(embeddingService: EmbeddingService, vectorStoreService: VectorStoreService) {
    this.embeddingService = embeddingService;
    this.vectorStoreService = vectorStoreService;
  }

  async query(request: RAGQuery): Promise<RAGResponse> {
    const startTime = Date.now();
    
    try {
      logger.info(`Processing RAG query: ${request.query.substring(0, 100)}...`);

      // Generate embedding for the query
      const queryEmbedding = await this.embeddingService.generateEmbedding({
        text: request.query
      });

      // Search for relevant documents
      const searchResults = await this.vectorStoreService.searchVectors({
        embedding: queryEmbedding.embedding,
        topK: request.topK || 5,
        filter: request.filter,
        includeMetadata: true
      });

      // Prepare context text
      const contextText = this.buildContextText(searchResults);

      const retrievalTime = Date.now() - startTime;

      return {
        query: request.query,
        context: searchResults,
        contextText,
        retrievalTime,
        totalResults: searchResults.length
      };
    } catch (error) {
      logger.error('Error processing RAG query:', error);
      throw error;
    }
  }

  async ingestDocument(request: DocumentIngestionRequest): Promise<{ chunksProcessed: number; vectorsStored: number }> {
    try {
      logger.info(`Ingesting document: ${request.filePath}`);

      // Extract text from document
      const documentText = await this.extractTextFromFile(request.filePath);
      
      // Chunk the document
      const chunks = this.chunkDocument(documentText, {
        chunkSize: request.chunkSize || 1000,
        overlapSize: request.overlapSize || 200,
        metadata: request.metadata || {}
      });

      // Generate embeddings for chunks
      const embeddingPromises = chunks.map(async (chunk, index) => {
        const embedding = await this.embeddingService.generateEmbeddingForDocument(
          chunk.content,
          {
            ...chunk.metadata,
            chunkIndex: index,
            totalChunks: chunks.length
          }
        );

        return {
          id: `${path.basename(request.filePath)}_chunk_${index}`,
          embedding: embedding.embedding,
          metadata: {
            ...embedding.metadata,
            content: chunk.content.substring(0, 500) // Store first 500 chars for context
          }
        };
      });

      const vectorDocuments = await Promise.all(embeddingPromises);

      // Store vectors in batch
      await this.vectorStoreService.storeBatchVectors(vectorDocuments);

      logger.info(`Successfully ingested document with ${chunks.length} chunks`);

      return {
        chunksProcessed: chunks.length,
        vectorsStored: vectorDocuments.length
      };
    } catch (error) {
      logger.error('Error ingesting document:', error);
      throw error;
    }
  }

  private async extractTextFromFile(filePath: string): Promise<string> {
    const extension = path.extname(filePath).toLowerCase();
    
    try {
      switch (extension) {
        case '.pdf':
          return await this.extractTextFromPDF(filePath);
        case '.docx':
          return await this.extractTextFromDocx(filePath);
        case '.txt':
          return fs.readFileSync(filePath, 'utf-8');
        case '.html':
          return await this.extractTextFromHTML(filePath);
        default:
          throw new Error(`Unsupported file type: ${extension}`);
      }
    } catch (error) {
      logger.error(`Error extracting text from ${filePath}:`, error);
      throw error;
    }
  }

  private async extractTextFromPDF(filePath: string): Promise<string> {
    const dataBuffer = fs.readFileSync(filePath);
    const data = await pdfParse(dataBuffer);
    return data.text;
  }

  private async extractTextFromDocx(filePath: string): Promise<string> {
    const result = await mammoth.extractRawText({ path: filePath });
    return result.value;
  }

  private async extractTextFromHTML(filePath: string): Promise<string> {
    const html = fs.readFileSync(filePath, 'utf-8');
    const $ = cheerio.load(html);
    return $.text();
  }

  private chunkDocument(text: string, options: {
    chunkSize: number;
    overlapSize: number;
    metadata: any;
  }): DocumentChunk[] {
    const chunks: DocumentChunk[] = [];
    const words = text.split(/\s+/);
    let currentChunk = '';
    let chunkIndex = 0;

    for (let i = 0; i < words.length; i++) {
      const word = words[i];
      const testChunk = currentChunk + (currentChunk ? ' ' : '') + word;

      if (testChunk.length > options.chunkSize && currentChunk) {
        // Save current chunk
        chunks.push({
          content: currentChunk.trim(),
          metadata: {
            ...options.metadata,
            chunkIndex,
            startWord: i - currentChunk.split(/\s+/).length,
            endWord: i - 1
          },
          chunkIndex
        });

        // Start new chunk with overlap
        const overlapWords = currentChunk.split(/\s+/).slice(-Math.floor(options.overlapSize / 5));
        currentChunk = overlapWords.join(' ') + ' ' + word;
        chunkIndex++;
      } else {
        currentChunk = testChunk;
      }
    }

    // Add the last chunk
    if (currentChunk.trim()) {
      chunks.push({
        content: currentChunk.trim(),
        metadata: {
          ...options.metadata,
          chunkIndex,
          startWord: words.length - currentChunk.split(/\s+/).length,
          endWord: words.length - 1
        },
        chunkIndex
      });
    }

    return chunks;
  }

  private buildContextText(searchResults: SearchResult[]): string {
    return searchResults
      .map((result, index) => {
        const title = result.metadata.title || `Document ${index + 1}`;
        const content = result.metadata.content || '';
        return `[${title}]\n${content}\n`;
      })
      .join('\n---\n');
  }

  async searchSimilarDocuments(query: string, options: {
    topK?: number;
    filter?: { [key: string]: any };
    threshold?: number;
  } = {}): Promise<SearchResult[]> {
    try {
      const queryEmbedding = await this.embeddingService.generateEmbedding({
        text: query
      });

      const searchResults = await this.vectorStoreService.searchVectors({
        embedding: queryEmbedding.embedding,
        topK: options.topK || 10,
        filter: options.filter,
        includeMetadata: true
      });

      // Filter by threshold if specified
      if (options.threshold) {
        return searchResults.filter(result => result.score >= options.threshold);
      }

      return searchResults;
    } catch (error) {
      logger.error('Error searching similar documents:', error);
      throw error;
    }
  }

  async getDocumentSummary(documentId: string): Promise<{
    id: string;
    title: string;
    totalChunks: number;
    content: string;
    metadata: any;
  } | null> {
    try {
      const document = await this.vectorStoreService.getVectorById(documentId);
      
      if (!document) {
        return null;
      }

      return {
        id: document.id,
        title: document.metadata.title || 'Untitled Document',
        totalChunks: document.metadata.totalChunks || 1,
        content: document.metadata.content || '',
        metadata: document.metadata
      };
    } catch (error) {
      logger.error('Error getting document summary:', error);
      return null;
    }
  }

  async deleteDocument(documentId: string): Promise<void> {
    try {
      await this.vectorStoreService.deleteVector(documentId);
      logger.info(`Deleted document: ${documentId}`);
    } catch (error) {
      logger.error('Error deleting document:', error);
      throw error;
    }
  }

  getHealthStatus(): { status: string; embeddingService: any; vectorStore: any } {
    return {
      status: 'healthy',
      embeddingService: this.embeddingService.getHealthStatus(),
      vectorStore: this.vectorStoreService.getHealthStatus()
    };
  }
} 