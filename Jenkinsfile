pipeline {
    agent any

    environment {
        SONARQUBE_SERVER = 'SonarQube'
        GITLEAKS_VERSION = "v8.18.0"
        IMAGE_NAME = "library-app"
        REGISTRY = "docker.io/anithaannem"
        TAG = "v${env.BUILD_NUMBER}"
        FULL_IMAGE = "${REGISTRY}/${IMAGE_NAME}:${TAG}"
        KUBE_CONTEXT = "your-kube-context"
        NAMESPACE = "default"
        PATH = "${env.HOME}/.local/bin:${env.PATH}" // Ensure pip local bin is in PATH
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
                gitleaks detect --source . --report-format json --report-path gitleaks-report.json || true
                '''
            }
            post {
                always { archiveArtifacts 'gitleaks-report.json' }
            }
        }

        stage('SonarQube - SAST') {
            steps {
                sh '''
                docker run --rm -v $(pwd):/usr/src sonarsource/sonar-scanner-cli \
                -Dsonar.projectKey=python \
                -Dsonar.sources=. \
                -Dsonar.host.url=http://44.222.237.153:9000 \
                -Dsonar.login=sqp_eaf31e33a6b46be434c32e854385525d34deda97
                '''
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
                ~/.local/bin/pip-audit --output pip-audit-report.json || true
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

        // ✅ Docker Image Scan stage added
        stage('Docker Image Scan') {
            steps {
                sh '''
                # Scan the built image for vulnerabilities using Trivy
                trivy image --format json -o trivy-report.json ${FULL_IMAGE} || true
                '''
            }
            post {
                always {
                    archiveArtifacts 'trivy-report.json'
                }
            }
        }

        stage('Docker Push') {
            steps {
                withCredentials([string(credentialsId: 'dockerhub-token', variable: 'DOCKER_TOKEN')]) {
                    sh '''
                    echo "$DOCKER_TOKEN" | docker login -u anithaannem --password-stdin
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
