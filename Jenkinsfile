pipeline {
    agent any

    stages {

        stage('Start') {
            steps {
                echo "Pipeline started by Elvin"
            }
        }

        stage('Checkout') {
            steps {
                git branch: 'main',
                url: 'https://github.com/XIvin95/DEVOPS-CI-CD-Process-Flow-Visualizer.git'
            }
        }

        stage('Build') {
            steps {
                echo "Building the application"
                bat "echo Build step executed"
            }
        }

        stage('Test') {
            steps {
                echo "Testing the application"
                bat "echo No tests configured"
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "Running SonarQube Scan"
                bat "echo SonarQube scanning (dummy for demo)"
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker Image"
                bat "docker build -t process-flow-visualizer:latest ."
            }
        }

        stage('Docker Tag') {
            steps {
                echo "Tagging Docker Image"
                bat "docker tag process-flow-visualizer:latest process-flow-visualizer:v1"
            }
        }

        stage('End') {
            steps {
                echo "Pipeline completed successfully"
            }
        }
    }
}
