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
                url: 'https://github.com/Xlvin95/DEVOPS-CI-CD-Process-Flow-Visualizer.git'
            }
        }

        stage('Build') {
            steps {
                echo "Building the application"
                sh "echo Build step executed"
            }
        }

        stage('Test') {
            steps {
                echo "Testing the application"
                sh "echo No tests configured"
            }
        }

        stage('SonarQube Analysis') {
            steps {
                echo "Skipping SonarQube for now"
            }
        }

        stage('Docker Build') {
            steps {
                echo "Building Docker Image"
                sh "docker build -t process-flow-visualizer:latest ."
            }
        }

        stage('Docker Tag') {
            steps {
                echo "Tagging Docker Image"
                sh "docker tag process-flow-visualizer:latest process-flow-visualizer:v1"
            }
        }

        stage('End') {
            steps {
                echo "Pipeline completed successfully"
            }
        }
    }
}

