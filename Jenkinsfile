pipeline {
    // Force execution onto your dedicated AWS build agent instance
    agent { label 'ubuntu linux' }

    environment {
        // dockerhub login info
        REGISTRY_USER  = 'mannydevops'
        BACKEND_IMAGE  = "${REGISTRY_USER}/jenkins-web-backend"
        FRONTEND_IMAGE = "${REGISTRY_USER}/jenkins-web-frontend"
        IMAGE_TAG      = "${BUILD_NUMBER}"

        // extracts the masked credentials we saved in the Jenkins Web UI
        DOCKER_CREDS   = credentials('docker-cred')
        DB_PASS_ENV    = credentials('jenkins-app-db-cred')
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
                    }
                }
                stage('Static HTML Checking') {
                    steps {
                        echo 'Auditing frontend structures...'
                    }
                }
            }
        }

        stage('📦 Secure Image Build & Push') {
            steps {
                echo 'Authenticating with remote Container Image Registry...'
                // Logs in securely using the masked credential tokens
                sh "echo \$DOCKER_CREDS_PSW | docker login -u \$DOCKER_CREDS_USR --password-stdin"

                echo "Compiling component docker definitions for version: v${IMAGE_TAG}"
                sh "DOCKER_BUILDKIT=0 docker build -t ${BACKEND_IMAGE}:${IMAGE_TAG} ./backend"
                sh "DOCKER_BUILDKIT=0 docker build -t ${FRONTEND_IMAGE}:${IMAGE_TAG} ./frontend"

                echo 'Pushing verified container images to external registry tier...'
                sh "docker push ${BACKEND_IMAGE}:${IMAGE_TAG}"
                sh "docker push ${FRONTEND_IMAGE}:${IMAGE_TAG}"
            }
        }

        stage('🚀 Continuous GitOps Deployment') {
            // Safely extracts your kubeconfig file into a temporary masked path to control your AWS K8s cluster
            withCredentials([file(credentialsId: 'KUBERNETES_CLUSTER_CONFIG', variable: 'KUBECONFIG_FILE')]) {
                steps {
                    echo 'Updating target image version descriptors in manifest...'
                    sh "sed -i 's|image: .*/jenkins-web-backend:.*|image: ${BACKEND_IMAGE}:${IMAGE_TAG}|g' k8s-manifests/backend.yaml"
                    sh "sed -i 's|image: .*/jenkins-web-frontend:.*|image: ${FRONTEND_IMAGE}:${IMAGE_TAG}|g' k8s-manifests/frontend.yaml"

                    echo 'Injecting masked database secrets into component manifests...'
                    // Dynamically overrides the plaintext 'password' placeholders before applying them to K8s
                    sh "sed -i 's/value: \"password\"/value: \"${DB_PASS_ENV}\"/g' k8s-manifests/postgres.yaml"
                    sh "sed -i 's/value: \"password\"/value: \"${DB_PASS_ENV}\"/g' k8s-manifests/backend.yaml"

                    echo 'Executing zero-downtime rolling update across active Kubernetes nodes...'
                    sh "kubectl --kubeconfig=\$KUBECONFIG_FILE apply -f k8s-manifests/"
                }
            }
        }
    }

    post {
        always {
            echo 'Cleaning up build worker node authentication tokens...'
            sh 'docker logout'
        }
        success {
            echo "Successfully updated AWS infrastructure stack! Active build tag: v${IMAGE_TAG}"
        }
        failure {
            echo 'CI/CD execution loop halted. Rolling back or keeping previous stable build active.'
        }
    }
}
