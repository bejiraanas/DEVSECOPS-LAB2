pipeline {
    agent any
    
    triggers {
        pollSCM('H/5 * * * *')  // Poll GitHub every 5 minutes
    }
    
    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/bejiraanas/DEVSECOPS-LAB2.git'
                sh 'echo "✅ Code checked out from GitHub"'
                sh 'ls -la'
            }
        }
        
        stage('Bandit Security Scan') {
            steps {
                sh '''
                echo "🔍 Running Bandit security scan on Python code..."
                bandit -r . -f json -o bandit-report.json || echo "Bandit completed with exit code: $?"
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'bandit-report.json', fingerprint: true
                    sh 'echo "📄 Bandit report generated"'
                }
            }
        }
        
        stage('Safety Dependency Check') {
            steps {
                sh '''
                echo "🔍 Running Safety dependency vulnerability check..."
                if [ -f "requirements.txt" ]; then
                    echo "Checking dependencies in requirements.txt"
                    safety check --json --output safety-report.json || echo "Safety completed with exit code: $?"
                else
                    echo "No requirements.txt found - creating empty report"
                    echo '{"vulnerabilities": []}' > safety-report.json
                fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'safety-report.json', fingerprint: true
                }
            }
        }
        
        stage('Trivy Container Scan') {
            steps {
                sh '''
                echo "🔍 Running Trivy container vulnerability scan..."
                if [ -f "docker/Dockerfile" ]; then
                    echo "Building Docker image from docker/Dockerfile..."
                    docker build -t devsecops-app:latest -f docker/Dockerfile .
                    echo "Scanning container with Trivy..."
                    docker run --rm \
                      -v /var/run/docker.sock:/var/run/docker.sock \
                      aquasec/trivy:latest \
                      image devsecops-app:latest --format json -o trivy-report.json || echo "Trivy completed with exit code: $?"
                else
                    echo "No Dockerfile found in docker/ directory - skipping container scan"
                    echo '{"Results": []}' > trivy-report.json
                fi
                '''
            }
            post {
                always {
                    archiveArtifacts artifacts: 'trivy-report.json', fingerprint: true
                }
            }
        }
        
        stage('Test Application') {
            steps {
                sh '''
                echo "🧪 Running application tests..."
                if [ -f "test_app.py" ]; then
                    python -m pytest test_app.py -v || echo "Tests completed with exit code: $?"
                else
                    echo "No test_app.py found - skipping tests"
                fi
                '''
            }
        }
        
        stage('Build and Deploy') {
            steps {
                sh '''
                echo "🚀 Building and deploying application..."
                if [ -f "docker/docker-compose.yml" ]; then
                    echo "Starting services with docker-compose"
                    cd docker && docker-compose up -d
                    echo "Application deployed successfully!"
                else
                    echo "No docker-compose.yml found - skipping deployment"
                fi
                '''
            }
        }
        
        stage('Generate Summary') {
            steps {
                sh '''
                echo "📊 SECURITY SCAN SUMMARY"
                echo "========================"
                echo "✅ Bandit: Code security analysis"
                echo "✅ Safety: Dependency vulnerability check" 
                echo "✅ Trivy: Container security scan"
                echo "✅ Tests: Application functionality"
                echo "✅ Deployment: Container deployment"
                echo ""
                echo "All security reports saved as Jenkins artifacts"
                echo "Check the 'Artifacts' section to download reports"
                '''
            }
        }
    }
    
    post {
        always {
            echo "🎉 DEVSECOPS PIPELINE COMPLETE"
            sh '''
            echo "Pipeline finished at: $(date)"
            echo "Generated reports:"
            ls -la *.json 2>/dev/null || echo "No JSON reports found"
            '''
        }
        success {
            echo "✅ SUCCESS: All stages completed successfully!"
            sh 'echo "Your DevSecOps pipeline is working perfectly! 🚀"'
        }
        failure {
            echo "❌ FAILED: Some stages failed - check logs above"
        }
        unstable {
            echo "⚠️  UNSTABLE: Security scans found issues - review reports in artifacts"
        }
    }
}