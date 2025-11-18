pipeline{
    agent any
    stages{
        stage ('Start'){
            steps{
                echo "pipeline started by Elvin"
            }
        }
        stage ('Checkout'){
            steps{
                git branch: 'main',
                    url: 'https://github.com/Xlvin95/DEVOPS-CI-CD-Process-Flow-Visualizer.git'
            }
        }
        stage ('Build'){
            steps{
                echo 'Building the application'
            }
        }
        stage ('Test'){
            steps{
                echo 'Testing the application'
            }
        }
        stage ('Deploy'){
            steps{
                echo 'Deploying the application'
            }
        }
    }
}