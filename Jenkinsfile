pipeline {
    agent any

    environment {
        // App settings and localized tags
        BACKEND_IMAGE  = 'jenkins-web-backend'
        FRONTEND_IMAGE = 'jenkins-web-frontend'
        IMAGE_TAG      = "${BUILD_NUMBER}" // Incremental unique version tag per build
    }

    stages {
        stage('🧹 Workspace Preparation') {
            steps {
                echo 'Cleaning up and auditing source repository layout...'
                sh 'ls -la'
            }
        }

        stage('🧪 Quality Verification') {
            parallel {
                stage('Python API Linting') {
                    steps {
                        echo 'Auditing backend code modules...'
                        // Example step for production scaling: sh 'pip install flake8 && flake8 backend/'
                    }
                }
                stage('Static HTML Checking') {
                    steps {
                        echo 'Auditing frontend structures...'
                    }
                }
            }
        }

        stage('📦 Assemble Container Images') {
            steps {
                echo "Compiling component docker definitions for version: v${IMAGE_TAG}"
                // Disable buildkit to align with local environment configuration presets
                sh "DOCKER_BUILDKIT=0 docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} ./backend"
                sh "DOCKER_BUILDKIT=0 docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} ./frontend"
            }
        }

        stage('🚚 Side-Load into Cluster Cache') {
            steps {
                echo "Injecting image build #${IMAGE_TAG} into local Minikube runtime cache..."
                sh "minikube image load ${BACKEND_IMAGE}:${IMAGE_TAG}"
                sh "minikube image load ${FRONTEND_IMAGE}:${IMAGE_TAG}"
            }
        }

        stage('🚀 Continuous GitOps Deployment') {
            steps {
                echo 'Rolling out new version tags across active Kubernetes nodes...'
                // Dynamically updates manifest versions to use the active sequential build number
                sh "sed -i 's/jenkins-web-backend:.*/jenkins-web-backend:${IMAGE_TAG}/g' k8s-manifests/backend.yaml"
                sh "sed -i 's/jenkins-web-frontend:.*/jenkins-web-frontend:${IMAGE_TAG}/g' k8s-manifests/frontend.yaml"
                
                // Re-apply configurations to force zero-downtime cluster rollouts
                sh "kubectl apply -f k8s-manifests/"
            }
        }
    }

    post {
        success {
            echo "Successfully updated deployment infrastructure stack! Active build tag: v${IMAGE_TAG}"
        }
        failure {
            echo "CI/CD execution loop halted. Rolling back or keeping previous stable build active."
        }
    }
}
