import neo4j, { Driver, Session, Result, Record } from 'neo4j-driver';
import { logger } from '../utils/logger';

export interface GraphNode {
  id: string;
  labels: string[];
  properties: { [key: string]: any };
}

export interface GraphRelationship {
  id: string;
  type: string;
  startNodeId: string;
  endNodeId: string;
  properties: { [key: string]: any };
}

export interface GraphResult {
  nodes: GraphNode[];
  relationships: GraphRelationship[];
}

export interface QueryResult {
  records: Record[];
  summary: any;
}

export class Neo4jService {
  private driver: Driver;
  private uri: string;
  private username: string;
  private password: string;

  constructor() {
    this.uri = process.env.NEO4J_URI || 'bolt://localhost:7687';
    this.username = process.env.NEO4J_USERNAME || 'neo4j';
    this.password = process.env.NEO4J_PASSWORD || 'password';
  }

  async initialize(): Promise<void> {
    try {
      this.driver = neo4j.driver(
        this.uri,
        neo4j.auth.basic(this.username, this.password)
      );

      // Test the connection
      await this.driver.verifyConnectivity();
      logger.info('Neo4j connection established successfully');

      // Create initial constraints and indexes
      await this.createConstraintsAndIndexes();
    } catch (error) {
      logger.error('Failed to initialize Neo4j connection:', error);
      throw error;
    }
  }

  private async createConstraintsAndIndexes(): Promise<void> {
    const session = this.driver.session();
    
    try {
      // Create constraints
      const constraints = [
        'CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE',
        'CREATE CONSTRAINT investor_id IF NOT EXISTS FOR (i:Investor) REQUIRE i.id IS UNIQUE',
        'CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE',
        'CREATE CONSTRAINT round_id IF NOT EXISTS FOR (r:Round) REQUIRE r.id IS UNIQUE',
        'CREATE CONSTRAINT regulation_id IF NOT EXISTS FOR (reg:Regulation) REQUIRE reg.id IS UNIQUE'
      ];

      for (const constraint of constraints) {
        try {
          await session.run(constraint);
        } catch (error) {
          // Constraint might already exist
          logger.debug(`Constraint creation result: ${error.message}`);
        }
      }

      // Create indexes
      const indexes = [
        'CREATE INDEX company_name IF NOT EXISTS FOR (c:Company) ON (c.name)',
        'CREATE INDEX investor_name IF NOT EXISTS FOR (i:Investor) ON (i.name)',
        'CREATE INDEX person_name IF NOT EXISTS FOR (p:Person) ON (p.name)',
        'CREATE INDEX round_date IF NOT EXISTS FOR (r:Round) ON (r.date)',
        'CREATE INDEX regulation_type IF NOT EXISTS FOR (reg:Regulation) ON (reg.type)'
      ];

      for (const index of indexes) {
        try {
          await session.run(index);
        } catch (error) {
          // Index might already exist
          logger.debug(`Index creation result: ${error.message}`);
        }
      }

      logger.info('Database constraints and indexes created successfully');
    } catch (error) {
      logger.error('Error creating constraints and indexes:', error);
    } finally {
      await session.close();
    }
  }

  async runQuery(query: string, parameters: any = {}): Promise<QueryResult> {
    const session = this.driver.session();
    
    try {
      logger.debug(`Executing query: ${query}`, { parameters });
      const result = await session.run(query, parameters);
      
      return {
        records: result.records,
        summary: result.summary
      };
    } catch (error) {
      logger.error('Error executing query:', error);
      throw error;
    } finally {
      await session.close();
    }
  }

  async createNode(labels: string[], properties: any): Promise<GraphNode> {
    const labelString = labels.map(label => `:${label}`).join('');
    const query = `
      CREATE (n${labelString})
      SET n = $properties
      RETURN n
    `;

    const result = await this.runQuery(query, { properties });
    const record = result.records[0];
    const node = record.get('n');

    return {
      id: node.identity.toString(),
      labels: node.labels,
      properties: node.properties
    };
  }

  async createRelationship(
    startNodeId: string,
    endNodeId: string,
    relationshipType: string,
    properties: any = {}
  ): Promise<GraphRelationship> {
    const query = `
      MATCH (start), (end)
      WHERE ID(start) = $startNodeId AND ID(end) = $endNodeId
      CREATE (start)-[r:${relationshipType}]->(end)
      SET r = $properties
      RETURN r, ID(start) as startId, ID(end) as endId
    `;

    const result = await this.runQuery(query, {
      startNodeId: parseInt(startNodeId),
      endNodeId: parseInt(endNodeId),
      properties
    });

    const record = result.records[0];
    const relationship = record.get('r');

    return {
      id: relationship.identity.toString(),
      type: relationship.type,
      startNodeId: record.get('startId').toString(),
      endNodeId: record.get('endId').toString(),
      properties: relationship.properties
    };
  }

  async findNodes(labels: string[], properties: any = {}): Promise<GraphNode[]> {
    const labelString = labels.map(label => `:${label}`).join('');
    const whereClause = Object.keys(properties).length > 0 
      ? `WHERE ${Object.keys(properties).map(key => `n.${key} = $${key}`).join(' AND ')}`
      : '';

    const query = `
      MATCH (n${labelString})
      ${whereClause}
      RETURN n
    `;

    const result = await this.runQuery(query, properties);
    
    return result.records.map(record => {
      const node = record.get('n');
      return {
        id: node.identity.toString(),
        labels: node.labels,
        properties: node.properties
      };
    });
  }

  async findRelationships(
    startNodeId?: string,
    endNodeId?: string,
    relationshipType?: string
  ): Promise<GraphRelationship[]> {
    let query = 'MATCH (start)-[r';
    
    if (relationshipType) {
      query += `:${relationshipType}`;
    }
    
    query += ']->(end)';
    
    const conditions = [];
    const parameters: any = {};
    
    if (startNodeId) {
      conditions.push('ID(start) = $startNodeId');
      parameters.startNodeId = parseInt(startNodeId);
    }
    
    if (endNodeId) {
      conditions.push('ID(end) = $endNodeId');
      parameters.endNodeId = parseInt(endNodeId);
    }
    
    if (conditions.length > 0) {
      query += ` WHERE ${conditions.join(' AND ')}`;
    }
    
    query += ' RETURN r, ID(start) as startId, ID(end) as endId';

    const result = await this.runQuery(query, parameters);
    
    return result.records.map(record => {
      const relationship = record.get('r');
      return {
        id: relationship.identity.toString(),
        type: relationship.type,
        startNodeId: record.get('startId').toString(),
        endNodeId: record.get('endId').toString(),
        properties: relationship.properties
      };
    });
  }

  async getNodeById(nodeId: string): Promise<GraphNode | null> {
    const query = `
      MATCH (n)
      WHERE ID(n) = $nodeId
      RETURN n
    `;

    const result = await this.runQuery(query, { nodeId: parseInt(nodeId) });
    
    if (result.records.length === 0) {
      return null;
    }

    const node = result.records[0].get('n');
    return {
      id: node.identity.toString(),
      labels: node.labels,
      properties: node.properties
    };
  }

  async deleteNode(nodeId: string): Promise<void> {
    const query = `
      MATCH (n)
      WHERE ID(n) = $nodeId
      DETACH DELETE n
    `;

    await this.runQuery(query, { nodeId: parseInt(nodeId) });
  }

  async deleteRelationship(relationshipId: string): Promise<void> {
    const query = `
      MATCH ()-[r]-()
      WHERE ID(r) = $relationshipId
      DELETE r
    `;

    await this.runQuery(query, { relationshipId: parseInt(relationshipId) });
  }

  async getSubgraph(
    startNodeId: string,
    depth: number = 2,
    relationshipTypes: string[] = []
  ): Promise<GraphResult> {
    const relationshipFilter = relationshipTypes.length > 0
      ? `[${relationshipTypes.map(type => `:${type}`).join('|')}]`
      : '';

    const query = `
      MATCH path = (start)-${relationshipFilter}*1..${depth}-(end)
      WHERE ID(start) = $startNodeId
      UNWIND nodes(path) as n
      UNWIND relationships(path) as r
      RETURN DISTINCT n, r
    `;

    const result = await this.runQuery(query, { startNodeId: parseInt(startNodeId) });
    
    const nodes: GraphNode[] = [];
    const relationships: GraphRelationship[] = [];
    const nodeIds = new Set<string>();
    const relationshipIds = new Set<string>();

    result.records.forEach(record => {
      const node = record.get('n');
      const relationship = record.get('r');

      if (node && !nodeIds.has(node.identity.toString())) {
        nodes.push({
          id: node.identity.toString(),
          labels: node.labels,
          properties: node.properties
        });
        nodeIds.add(node.identity.toString());
      }

      if (relationship && !relationshipIds.has(relationship.identity.toString())) {
        relationships.push({
          id: relationship.identity.toString(),
          type: relationship.type,
          startNodeId: relationship.start.toString(),
          endNodeId: relationship.end.toString(),
          properties: relationship.properties
        });
        relationshipIds.add(relationship.identity.toString());
      }
    });

    return { nodes, relationships };
  }

  async getSchema(): Promise<{
    nodeLabels: string[];
    relationshipTypes: string[];
    propertyKeys: string[];
  }> {
    const labelQuery = 'CALL db.labels()';
    const relationshipQuery = 'CALL db.relationshipTypes()';
    const propertyQuery = 'CALL db.propertyKeys()';

    const [labelResult, relationshipResult, propertyResult] = await Promise.all([
      this.runQuery(labelQuery),
      this.runQuery(relationshipQuery),
      this.runQuery(propertyQuery)
    ]);

    return {
      nodeLabels: labelResult.records.map(record => record.get('label')),
      relationshipTypes: relationshipResult.records.map(record => record.get('relationshipType')),
      propertyKeys: propertyResult.records.map(record => record.get('propertyKey'))
    };
  }

  async getStats(): Promise<{
    nodeCount: number;
    relationshipCount: number;
    labelCounts: { [label: string]: number };
    relationshipTypeCounts: { [type: string]: number };
  }> {
    const nodeCountQuery = 'MATCH (n) RETURN count(n) as count';
    const relationshipCountQuery = 'MATCH ()-[r]->() RETURN count(r) as count';
    const labelCountQuery = 'MATCH (n) RETURN labels(n) as labels, count(n) as count';
    const relationshipTypeCountQuery = 'MATCH ()-[r]->() RETURN type(r) as type, count(r) as count';

    const [nodeResult, relationshipResult, labelResult, relationshipTypeResult] = await Promise.all([
      this.runQuery(nodeCountQuery),
      this.runQuery(relationshipCountQuery),
      this.runQuery(labelCountQuery),
      this.runQuery(relationshipTypeCountQuery)
    ]);

    const labelCounts: { [label: string]: number } = {};
    labelResult.records.forEach(record => {
      const labels = record.get('labels');
      const count = record.get('count').toNumber();
      labels.forEach((label: string) => {
        labelCounts[label] = (labelCounts[label] || 0) + count;
      });
    });

    const relationshipTypeCounts: { [type: string]: number } = {};
    relationshipTypeResult.records.forEach(record => {
      const type = record.get('type');
      const count = record.get('count').toNumber();
      relationshipTypeCounts[type] = count;
    });

    return {
      nodeCount: nodeResult.records[0].get('count').toNumber(),
      relationshipCount: relationshipResult.records[0].get('count').toNumber(),
      labelCounts,
      relationshipTypeCounts
    };
  }

  async isHealthy(): Promise<boolean> {
    try {
      await this.driver.verifyConnectivity();
      return true;
    } catch (error) {
      logger.error('Neo4j health check failed:', error);
      return false;
    }
  }

  async close(): Promise<void> {
    if (this.driver) {
      await this.driver.close();
      logger.info('Neo4j connection closed');
    }
  }
} 