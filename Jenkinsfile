pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'SonarQube'
        GITLEAKS_VERSION = "v8.18.0"
        IMAGE_NAME = "library-app"
        REGISTRY = "docker.io/yourdockerid"
        TAG = "v${env.BUILD_NUMBER}"
        FULL_IMAGE = "${REGISTRY}/${IMAGE_NAME}:${TAG}"
        KUBE_CONTEXT = "your-kube-context"
        NAMESPACE = "default"
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Credential Scan - GitLeaks') {
            steps {
                sh '''
                if ! command -v gitleaks &> /dev/null
                then
                    curl -sSL https://github.com/gitleaks/gitleaks/releases/download/${GITLEAKS_VERSION}/gitleaks-linux-amd64 > gitleaks
                    chmod +x gitleaks
                    sudo mv gitleaks /usr/local/bin/
                fi
                
                gitleaks detect --source . --report-format json --report-path gitleaks-report.json || true
                '''
            }
            post {
                always { archiveArtifacts 'gitleaks-report.json' }
            }
        }

        stage('SonarQube - SAST') {
            steps {
                withSonarQubeEnv("${SONARQUBE_SERVER}") {
                    sh '''
                    sonar-scanner \
                    -Dsonar.projectKey=python-app \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=$SONAR_HOST_URL \
                    -Dsonar.login=$SONAR_TOKEN
                    '''
                }
            }
        }

        stage('Python Unit Tests') {
            steps {
                sh '''
                pip install -r requirements.txt
                pytest
                '''
            }
        }

        stage('Coverage Report') {
            steps {
                sh '''
                pytest --cov=. --cov-report=xml
                '''
            }
            post {
                always {
                    archiveArtifacts 'coverage.xml'
                }
            }
        }

        stage('Dependency Scan - pip-audit') {
            steps {
                sh '''
                pip install pip-audit
                pip-audit --output pip-audit-report.json || true
                '''
            }
            post {
                always { archiveArtifacts 'pip-audit-report.json' }
            }
        }

        stage('Docker Build') {
            steps {
                sh "docker build -t ${FULL_IMAGE} ."
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([string(credentialsId: 'dockerhub-token', variable: 'DOCKER_TOKEN')]) {
                    sh '''
                    echo "$DOCKER_TOKEN" | docker login -u yourdockerid --password-stdin
                    docker push ${FULL_IMAGE}
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                withKubeConfig(credentialsId: 'kubeconfig') {
                    sh '''
                    echo "Updating image in Kubernetes Deployment..."
                    kubectl set image deployment/library-app-deployment library-app=${FULL_IMAGE} -n ${NAMESPACE}
                    
                    echo "Verifying rollout..."
                    kubectl rollout status deployment/library-app-deployment -n ${NAMESPACE}
                    '''
                }
            }
        }
    }

    post {
        success {
            echo "CI/CD Pipeline executed successfully!"
        }
        failure {
            echo "Pipeline Failed. Investigate issues."
        }
    }
}
