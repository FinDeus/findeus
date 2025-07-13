terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }

  backend "s3" {
    bucket = "findeus-terraform-state"
    key    = "infrastructure/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# Data sources
data "aws_availability_zones" "available" {
  state = "available"
}

data "aws_caller_identity" "current" {}

# VPC
resource "aws_vpc" "findeus_vpc" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "findeus-vpc"
    Environment = var.environment
  }
}

# Internet Gateway
resource "aws_internet_gateway" "findeus_igw" {
  vpc_id = aws_vpc.findeus_vpc.id

  tags = {
    Name        = "findeus-igw"
    Environment = var.environment
  }
}

# Public Subnets
resource "aws_subnet" "public_subnets" {
  count = length(var.public_subnet_cidrs)

  vpc_id                  = aws_vpc.findeus_vpc.id
  cidr_block              = var.public_subnet_cidrs[count.index]
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name        = "findeus-public-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "public"
  }
}

# Private Subnets
resource "aws_subnet" "private_subnets" {
  count = length(var.private_subnet_cidrs)

  vpc_id            = aws_vpc.findeus_vpc.id
  cidr_block        = var.private_subnet_cidrs[count.index]
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name        = "findeus-private-subnet-${count.index + 1}"
    Environment = var.environment
    Type        = "private"
  }
}

# NAT Gateways
resource "aws_eip" "nat_eips" {
  count = length(aws_subnet.public_subnets)

  domain = "vpc"
  depends_on = [aws_internet_gateway.findeus_igw]

  tags = {
    Name        = "findeus-nat-eip-${count.index + 1}"
    Environment = var.environment
  }
}

resource "aws_nat_gateway" "nat_gateways" {
  count = length(aws_subnet.public_subnets)

  allocation_id = aws_eip.nat_eips[count.index].id
  subnet_id     = aws_subnet.public_subnets[count.index].id

  tags = {
    Name        = "findeus-nat-gateway-${count.index + 1}"
    Environment = var.environment
  }
}

# Route Tables
resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.findeus_vpc.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.findeus_igw.id
  }

  tags = {
    Name        = "findeus-public-rt"
    Environment = var.environment
  }
}

resource "aws_route_table" "private_rt" {
  count = length(aws_nat_gateway.nat_gateways)

  vpc_id = aws_vpc.findeus_vpc.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat_gateways[count.index].id
  }

  tags = {
    Name        = "findeus-private-rt-${count.index + 1}"
    Environment = var.environment
  }
}

# Route Table Associations
resource "aws_route_table_association" "public_rta" {
  count = length(aws_subnet.public_subnets)

  subnet_id      = aws_subnet.public_subnets[count.index].id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "private_rta" {
  count = length(aws_subnet.private_subnets)

  subnet_id      = aws_subnet.private_subnets[count.index].id
  route_table_id = aws_route_table.private_rt[count.index].id
}

# Security Groups
resource "aws_security_group" "eks_cluster_sg" {
  name        = "findeus-eks-cluster-sg"
  description = "Security group for EKS cluster"
  vpc_id      = aws_vpc.findeus_vpc.id

  ingress {
    from_port = 443
    to_port   = 443
    protocol  = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name        = "findeus-eks-cluster-sg"
    Environment = var.environment
  }
}

resource "aws_security_group" "rds_sg" {
  name        = "findeus-rds-sg"
  description = "Security group for RDS instances"
  vpc_id      = aws_vpc.findeus_vpc.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name        = "findeus-rds-sg"
    Environment = var.environment
  }
}

# EKS Cluster
resource "aws_eks_cluster" "findeus_cluster" {
  name     = "findeus-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = var.kubernetes_version

  vpc_config {
    subnet_ids              = concat(aws_subnet.public_subnets[*].id, aws_subnet.private_subnets[*].id)
    security_group_ids      = [aws_security_group.eks_cluster_sg.id]
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
    aws_iam_role_policy_attachment.eks_service_policy,
  ]

  tags = {
    Environment = var.environment
  }
}

# EKS Node Group
resource "aws_eks_node_group" "findeus_nodes" {
  cluster_name    = aws_eks_cluster.findeus_cluster.name
  node_group_name = "findeus-nodes"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = aws_subnet.private_subnets[*].id

  scaling_config {
    desired_size = var.node_desired_size
    max_size     = var.node_max_size
    min_size     = var.node_min_size
  }

  instance_types = [var.node_instance_type]

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]

  tags = {
    Environment = var.environment
  }
}

# RDS Subnet Group
resource "aws_db_subnet_group" "findeus_db_subnet_group" {
  name       = "findeus-db-subnet-group"
  subnet_ids = aws_subnet.private_subnets[*].id

  tags = {
    Name        = "findeus-db-subnet-group"
    Environment = var.environment
  }
}

# RDS Instance
resource "aws_db_instance" "findeus_db" {
  identifier             = "findeus-db"
  engine                 = "postgres"
  engine_version         = "15.4"
  instance_class         = var.db_instance_class
  allocated_storage      = var.db_allocated_storage
  storage_encrypted      = true
  
  db_name  = "findeus"
  username = var.db_username
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.findeus_db_subnet_group.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = var.environment != "production"

  tags = {
    Name        = "findeus-db"
    Environment = var.environment
  }
}

# ElastiCache Subnet Group
resource "aws_elasticache_subnet_group" "findeus_cache_subnet_group" {
  name       = "findeus-cache-subnet-group"
  subnet_ids = aws_subnet.private_subnets[*].id

  tags = {
    Name        = "findeus-cache-subnet-group"
    Environment = var.environment
  }
}

# ElastiCache Redis
resource "aws_elasticache_replication_group" "findeus_redis" {
  replication_group_id       = "findeus-redis"
  description                = "Redis cluster for FinDeus"
  
  node_type                  = var.redis_node_type
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.findeus_cache_subnet_group.name
  security_group_ids = [aws_security_group.redis_sg.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Name        = "findeus-redis"
    Environment = var.environment
  }
}

# Security Group for Redis
resource "aws_security_group" "redis_sg" {
  name        = "findeus-redis-sg"
  description = "Security group for Redis cluster"
  vpc_id      = aws_vpc.findeus_vpc.id

  ingress {
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name        = "findeus-redis-sg"
    Environment = var.environment
  }
}

# OpenSearch Domain
resource "aws_opensearch_domain" "findeus_opensearch" {
  domain_name    = "findeus-opensearch"
  engine_version = "OpenSearch_2.3"

  cluster_config {
    instance_type  = var.opensearch_instance_type
    instance_count = var.opensearch_instance_count
  }

  vpc_options {
    subnet_ids         = aws_subnet.private_subnets[*].id
    security_group_ids = [aws_security_group.opensearch_sg.id]
  }

  ebs_options {
    ebs_enabled = true
    volume_size = var.opensearch_volume_size
  }

  encrypt_at_rest {
    enabled = true
  }

  node_to_node_encryption {
    enabled = true
  }

  domain_endpoint_options {
    enforce_https = true
  }

  tags = {
    Name        = "findeus-opensearch"
    Environment = var.environment
  }
}

# Security Group for OpenSearch
resource "aws_security_group" "opensearch_sg" {
  name        = "findeus-opensearch-sg"
  description = "Security group for OpenSearch cluster"
  vpc_id      = aws_vpc.findeus_vpc.id

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = [var.vpc_cidr]
  }

  tags = {
    Name        = "findeus-opensearch-sg"
    Environment = var.environment
  }
} 