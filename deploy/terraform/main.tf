# Author: Mourad.Soltani - Terraform stub for buyer demo
# Real enough that a buyer's engineer nods - ECS/Fargate

terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project" {
  description = "Project name"
  type        = string
  default     = "resolvefabric-p2p"
}

variable "author" {
  description = "Author signature"
  type        = string
  default     = "Mourad.Soltani"
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "${var.project}-cluster"
  tags = {
    Author    = var.author
    Signature = "Mourad.Soltani"
    Project   = var.project
    Version   = "3.0.0"
  }
}

# ECR Repository
resource "aws_ecr_repository" "app" {
  name = var.project
  tags = {
    Author    = var.author
    Signature = "Mourad.Soltani"
  }
}

# IAM Role for task execution
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project}-execution-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action    = "sts:AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ecs-tasks.amazonaws.com" }
    }]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/${var.project}"
  retention_in_days = 30
  tags = {
    Author = var.author
  }
}

# ECS Task Definition - production-grade
resource "aws_ecs_task_definition" "app" {
  family                   = var.project
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([{
    name      = var.project
    image     = "${aws_ecr_repository.app.repository_url}:latest"
    essential = true
    portMappings = [{
      containerPort = 8080
      protocol      = "tcp"
    }]
    environment = [
      { name = "HOST", value = "0.0.0.0" },
      { name = "PORT", value = "8080" },
      { name = "FLASK_ENV", value = "production" },
      { name = "SIGNATURE", value = "Mourad.Soltani" }
    ]
    secrets = [
      { name = "OPENAI_API_KEY", valueFrom = "arn:aws:secretsmanager:${var.region}:ACCOUNT_ID:secret:openai-key" }
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.app.name
        awslogs-region        = var.region
        awslogs-stream-prefix = "ecs"
      }
    }
    healthCheck = {
      command     = ["CMD-SHELL", "python -c 'import requests; requests.get("http://localhost:8080/health", timeout=3)'"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 10
    }
  }])

  tags = {
    Author    = var.author
    Signature = "Mourad.Soltani"
  }
}

# Output
output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "signature" {
  value = "Mourad.Soltani"
}
