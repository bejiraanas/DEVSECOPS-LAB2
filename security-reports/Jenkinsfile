pipeline {
    agent any
    
    stages {
        stage('Checkout') {
            steps {
                echo '🔁 Cloning repository from GitHub...'
                git branch: 'main', 
                    url: 'https://github.com/bejiraanas/DEVSECOPS-LAB2.git'
                sh 'ls -la'
            }
        }
        
        stage('Setup Environment') {
            steps {
                echo '⚙️ Setting up environment...'
                sh '''
                    python --version || echo "Python not found"
                    pip --version || echo "Pip not found"
                    docker --version || echo "Docker not found"
                '''
            }
        }
        
        stage('Install Dependencies') {
            steps {
                echo '📦 Installing security tools...'
                sh '''
                    pip install bandit safety || echo "Failed to install tools"
                    bandit --version || echo "Bandit not available"
                    safety --version || echo "Safety not available"
                '''
            }
        }
        
        stage('Security Scan - Bandit') {
            steps {
                echo '🔍 Running Bandit scan...'
                sh '''
                    cd app
                    bandit -r . -f txt -o ../bandit-report.txt || echo "Bandit scan failed"
                    ls -la ../bandit-report.txt || echo "No bandit report generated"
                '''
            }
        }
        
        stage('Security Scan - Safety') {
            steps {
                echo '🔍 Running Safety scan...'
                sh '''
                    cd app
                    safety check --file requirements.txt > ../safety-report.txt || echo "Safety scan failed"
                    ls -la ../safety-report.txt || echo "No safety report generated"
                '''
            }
        }
        
        stage('Test Build') {
            steps {
                echo '🐳 Testing Docker build...'
                sh '''
                    cd docker
                    docker-compose build --no-cache || echo "Docker build failed"
                '''
            }
        }
    }
    
    post {
        always {
            echo '📊 Collecting results...'
            archiveArtifacts artifacts: '**/*-report.txt', fingerprint: true
            sh 'find . -name "*.txt" -type f | head -10'
        }
        success {
            echo '✅ Pipeline succeeded!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
    }
}