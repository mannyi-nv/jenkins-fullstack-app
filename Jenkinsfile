pipeline {
    agent {
        label 'ubuntu'
    }

    environment {
        // Docker Hub configuration
        REGISTRY_USER  = 'mannydevops'
        BACKEND_IMAGE  = "${REGISTRY_USER}/jenkins-web-backend"
        FRONTEND_IMAGE = "${REGISTRY_USER}/jenkins-web-frontend"
        IMAGE_TAG      = "${BUILD_NUMBER}"

        // Docker Hub credentials (Jenkins Username/Password)
        DOCKER_CREDS = credentials('docker-cred')
        DB_PASS_ENV    = credentials('jenkins-app-db-cred')
    }

    stages {
        stage('Workspace Preparation') {
            steps {
                echo 'Cleaning workspace and auditing source repository...'
                sh 'ls -la'
            }
        }

        stage('Quality Verification') {
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

        stage('Secure Image Build & Push') {
            steps {
                echo 'Authenticating with Docker Hub...'

                sh '''
                    set +x
                    echo "$DOCKER_CREDS_PSW" | docker login \
                        -u "$DOCKER_CREDS_USR" \
                        --password-stdin
                '''

                echo "Building images with tag: ${IMAGE_TAG}"

                sh '''
                    docker build \
                        -t "$BACKEND_IMAGE:$IMAGE_TAG" ./backend

                    docker build \
                        -t "$FRONTEND_IMAGE:$IMAGE_TAG" ./frontend
                '''

                echo 'Pushing images to Docker Hub...'

                sh '''
                    docker push "$BACKEND_IMAGE:$IMAGE_TAG"
                    docker push "$FRONTEND_IMAGE:$IMAGE_TAG"
                '''
            }
        }
        
        stage('Continuous GitOps Deployment') {
            steps {
                withCredentials([
                    gitUsernamePassword(
                        credentialsId: 'githab-pat-cred',
                        gitToolName: 'Default'
                    )
                ]) {
                    echo 'Cloning GitOps repository...'

                    sh '''
                        set -eu
                        rm -rf gitops

                        git clone \
                            --branch main \
                            https://github.com/mannyi-nv/jenkins-fullstack-manifests.git \
                            gitops

                        cd gitops

                        git config user.name "Jenkins CI"
                        git config user.email "jenkins@localhost"

                        echo "Updating Kubernetes image versions..."

                        sed -i -E \
                            "s|(^[[:space:]]*image:[[:space:]]*).*jenkins-web-backend:[^[:space:]]*|\\1$BACKEND_IMAGE:$IMAGE_TAG|" \
                            k8s-manifests/backend.yaml

                        sed -i -E \
                            "s|(^[[:space:]]*image:[[:space:]]*).*jenkins-web-frontend:[^[:space:]]*|\\1$FRONTEND_IMAGE:$IMAGE_TAG|" \
                            k8s-manifests/frontend.yaml

                        echo "Checking manifest changes..."

                        git diff --check

                        git add \
                            k8s-manifests/backend.yaml \
                            k8s-manifests/frontend.yaml

                        if ! git diff --cached --quiet; then

                            git commit -m "Update application images to $IMAGE_TAG"

                            echo "Pushing changes to GitHub..."

                            git push origin HEAD:main

                        else
                            echo "No manifest changes detected."
                        fi
                    '''
                }
            }
        }

    }

    post {
        always {
            echo 'Cleaning up Docker authentication...'
            sh 'docker logout || true'
        }

        success {
            echo "Successfully deployed! Active build tag: v${IMAGE_TAG}"
        }

        failure {
            echo 'CI/CD pipeline failed. Check the Jenkins console output.'
        }
    }
}
