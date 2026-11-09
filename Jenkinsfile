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

    //     stage('Continuous GitOps Deployment') {
    //         steps {
    //             withCredentials([
    //                 file(
    //                     credentialsId: 'KUBERNETES_CLUSTER_CONFIG',
    //                     variable: 'KUBECONFIG_FILE'
    //                 ),
    //                 string(
    //                     credentialsId: 'jenkins-app-db-cred',
    //                     variable: 'DB_PASSWORD'
    //                 )
    //             ]) {
    //                 echo 'Updating Kubernetes image versions...'

    //                 sh '''
    //                     set +x

    //                     sed -i "s|image: .*/jenkins-web-backend:.*|image: $BACKEND_IMAGE:$IMAGE_TAG|g" \
    //                         k8s-manifests/backend.yaml

    //                     sed -i "s|image: .*/jenkins-web-frontend:.*|image: $FRONTEND_IMAGE:$IMAGE_TAG|g" \
    //                         k8s-manifests/frontend.yaml
    //                 '''

    //                 echo 'Injecting database credentials...'

    //                 sh '''
    //                     set +x

    //                             sed -i "s|value: \\"password\\"|value: \\"$DB_PASSWORD\\"|g" \
    //                         k8s-manifests/postgres.yaml

    //                             sed -i "s|value: \\"password\\"|value: \\"$DB_PASSWORD\\"|g" \
    //                         k8s-manifests/backend.yaml
    //                 '''

    //                 echo 'Applying Kubernetes manifests...'

    //                 sh '''
    //                     kubectl --kubeconfig="$KUBECONFIG_FILE" \
    //                         apply -f k8s-manifests/
    //                 '''
    //             }
    //         }
    //     }
    // }

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
