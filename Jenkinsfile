pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                sh 'docker build -t cpu-scheduler .'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                docker stop cpu-app || true
                docker rm cpu-app || true
                docker run -d -p 5000:5000 --name cpu-app cpu-scheduler
                '''
            }
        }
    }
}
