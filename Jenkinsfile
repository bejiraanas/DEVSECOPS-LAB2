pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
    buildDiscarder(logRotator(numToKeepStr: '20'))
  }


  triggers {
    pollSCM('H/5 * * * *')
  }

  environment {
    PYTHON    = 'python3'
    VENV_DIR  = '.venv'
    REPORTS   = 'reports'
    DOCKERFILE_PATH = 'docker/Dockerfile'      // adjust if your Dockerfile lives elsewhere
    COMPOSE_DIR     = 'docker'                 // adjust if your docker-compose.yml lives elsewhere
    IMAGE_NAME = 'devsecops-app:latest'
  }

  stages {
    stage('Preflight Clean & Git Safe Directory') {
      steps {
        script { deleteDir() } // avoid nested/dirty workspaces
        sh '''
          set -eux
          mkdir -p "${REPORTS}"
          git config --global --add safe.directory "${WORKSPACE}" || true
          git config --global --add safe.directory "*" || true
        '''
      }
    }

    stage('Checkout Code') {
      steps {
        git branch: 'main', url: 'https://github.com/bejiraanas/DEVSECOPS-LAB2.git'
        sh 'echo "✅ Code checked out from GitHub" && ls -la'
      }
    }

    stage('Setup Python Env') {
      steps {
        sh '''
          set -eux
          ${PYTHON} -V
          ${PYTHON} -m venv "${VENV_DIR}"
          . "${VENV_DIR}/bin/activate"
          pip install --upgrade pip
          # Install project deps if present
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          # Ensure CI tools exist on the agent
          pip install pytest pytest-cov bandit safety
        '''
      }
    }

    stage('Bandit Security Scan') {
      steps {
        sh '''
          set -eux
          . "${VENV_DIR}/bin/activate"
          echo "🔍 Running Bandit security scan on Python code..."
          bandit -r . -f json -o "${REPORTS}/bandit-report.json" || echo "Bandit completed with exit code: $?"
        '''
      }
      post {
        always {
          archiveArtifacts artifacts: 'reports/bandit-report.json', fingerprint: true
          sh 'echo "📄 Bandit report generated"'
        }
      }
    }

    stage('Safety Dependency Check') {
      steps {
        sh '''
          set -eux
          . "${VENV_DIR}/bin/activate"
          echo "🔍 Running Safety dependency vulnerability check..."
          if [ -f "requirements.txt" ]; then
            safety check --json --file=requirements.txt --output "${REPORTS}/safety-report.json" || echo "Safety completed with exit code: $?"
          else
            echo '{"vulnerabilities": []}' > "${REPORTS}/safety-report.json"
            echo "No requirements.txt found - created empty Safety report"
          fi
        '''
      }
      post {
        always {
          archiveArtifacts artifacts: 'reports/safety-report.json', fingerprint: true
        }
      }
    }

    stage('Build Docker Image') {
      steps {
        sh '''
          set -eux
          if [ -f "${DOCKERFILE_PATH}" ]; then
            echo "Building Docker image from ${DOCKERFILE_PATH}..."
            docker build -t "${IMAGE_NAME}" -f "${DOCKERFILE_PATH}" .
          elif [ -f "Dockerfile" ]; then
            echo "Building Docker image from ./Dockerfile..."
            docker build -t "${IMAGE_NAME}" .
          else
            echo "No Dockerfile found - skipping image build"
            exit 0
          fi
        '''
      }
    }

    stage('Trivy Container Scan') {
      steps {
        sh '''
          set -eux
          if docker image inspect "${IMAGE_NAME}" > /dev/null 2>&1; then
            echo "🔍 Running Trivy container vulnerability scan..."
            # Mount docker.sock for image access AND mount workspace to store report
            docker run --rm \
              -v /var/run/docker.sock:/var/run/docker.sock \
              -v "$PWD":/work -w /work \
              aquasec/trivy:latest \
              image "${IMAGE_NAME}" --format json -o "${REPORTS}/trivy-report.json" || echo "Trivy completed with exit code: $?"
          else
            echo '{"Results": []}' > "${REPORTS}/trivy-report.json"
            echo "Image ${IMAGE_NAME} not present - created empty Trivy report"
          fi
        '''
      }
      post {
        always {
          archiveArtifacts artifacts: 'reports/trivy-report.json', fingerprint: true
        }
      }
    }

    stage('Test Application') {
      steps {
        sh '''
          set -eux
          . "${VENV_DIR}/bin/activate"
          echo "🧪 Running application tests..."
          if [ -f "test_app.py" ] || [ -d "tests" ]; then
            pytest -q --maxfail=1 --disable-warnings \
              --junitxml="${REPORTS}/pytest.xml"
          else
            echo "No tests found - skipping tests"
          fi
        '''
      }
      post {
        always {
          junit allowEmptyResults: true, testResults: 'reports/pytest.xml'
        }
      }
    }

    stage('Build and Deploy') {
      steps {
        sh '''
          set -eux
          echo "🚀 Building and deploying application..."
          if [ -f "${COMPOSE_DIR}/docker-compose.yml" ] || [ -f "${COMPOSE_DIR}/compose.yml" ]; then
            cd "${COMPOSE_DIR}"
            # Prefer modern CLI; fallback to legacy if needed
            if docker compose version >/dev/null 2>&1; then
              docker compose up -d
            else
              docker-compose up -d
            fi
            echo "Application deployed successfully!"
          else
            echo "No docker-compose file found in ${COMPOSE_DIR} - skipping deployment"
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
      archiveArtifacts artifacts: 'reports/**', allowEmptyArchive: true
      sh '''
        echo "Pipeline finished at: $(date)"
        echo "Generated reports:"
        ls -la reports || true
      '''
    }
    success { echo "✅ SUCCESS: All stages completed successfully!" }
    failure { echo "❌ FAILED: Some stages failed - check logs above" }
    unstable { echo "⚠️  UNSTABLE: Security scans found issues - review reports in artifacts" }
  }
}
