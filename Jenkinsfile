pipeline {
    agent {
        docker {
            image 'python:3.10-slim'
            args '-u root:root'   // allow installing dependencies
        }
    }

    stages {

        stage('Checkout code') {
            steps {
                checkout scm
                sh 'ls -la'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    pip install --upgrade pip
                    pip install flask pytest bandit safety
                '''
            }
        }

        stage('Run Tests (pytest)') {
            steps {
                sh '''
                    cd app
                    pytest --maxfail=1 --disable-warnings -q
                '''
            }
        }

        stage('Run Bandit Scan') {
            steps {
                sh '''
                    cd app
                    bandit -r . -f txt -o ../security-reports/bandit-report.txt
                '''
            }
        }

        stage('Run Safety Scan') {
            steps {
                sh '''
                    safety check --file app/requirements.txt --full-report > security-reports/safety-report.txt
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                sh '''
                    docker --version
                    docker build -t devsecops-lab-app -f docker/Dockerfile .
                '''
            }
        }
    }

    post {
        always {
            echo "📊 Collecting artifacts..."
            archiveArtifacts artifacts: 'security-reports/*.txt', fingerprint: true
        }
    }
}
