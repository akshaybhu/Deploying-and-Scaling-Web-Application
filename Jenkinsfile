pipeline {
    agent any
    
    environment {
        ECR_FRONTEND_REPO = "975050024946.dkr.ecr.us-east-1.amazonaws.com/aks-mern-frontend-repo"
        ECR_BACKEND_REPO = "975050024946.dkr.ecr.us-east-1.amazonaws.com/aks-mern-backend-helloservice-repo"
        ECR_PROFILE_BACKEND_REPO = "975050024946.dkr.ecr.us-east-1.amazonaws.com/aks-mern-backend-profileservice-repo"
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Frontend') {
            steps {
                dir('client') {
                    sh 'docker build -t mern-frontend .'
                    sh "docker tag mern-frontend:latest ${ECR_FRONTEND_REPO}:latest"
                }
            }
        }
        
        stage('Build Backend') {
            steps {
                dir('server') {
                    sh 'docker build -t mern-backend .'
                    sh "docker tag mern-backend:latest ${ECR_BACKEND_REPO}:latest"
                    sh 'docker build -t mern-backend-profile .'
                    sh "docker tag mern-backend:latest ${ECR_PROFILE_BACKEND_REPO}:latest"                
                }
            }
        }
        
        stage('Push to ECR') {
            steps {
                withAWS(credentials: 'aws-credentials', region: "us-east-1") {
                    sh "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 975050024946.dkr.ecr.us-east-1.amazonaws.com"
                    sh "docker push ${ECR_FRONTEND_REPO}:latest"
                    sh "docker push ${ECR_BACKEND_REPO}:latest"
                }
            }
        }
    }
}
