pipeline {
    agent { label 'docker-slave' }
       environment {
           PDS_BLUEPRINT_PATH = "/blueprints"
           OIDC_CLIENT_ID = "TEST_ID"
           OIDC_CLIENT_SECRET = "TEST_SECRET"
           OIDC_INTROSPECTION_ENDPOINT = "http://localhost:8080/auth/realms/SODALITE/protocol/openid-connect/token"
           PDS_STORAGE_KEY = "TEST_STORAGE_KEY"
           SECRET_VAULT_LOGIN_URI = "http://localhost:8200/v1/auth/jwt/login"
           SECRET_VAULT_URI = "http://localhost:8200/v1/"
       }
    stages {
        stage ('Pull repo code from github') {
            steps {
                checkout scm
            }
        }
        stage('Test PDS') {
            steps {
                sh  """ #!/bin/bash
                        python3 -m venv venv-test
                        . venv-test/bin/activate                        
                        pip3 install -r requirements.txt
                        ./generate.sh
                        cd src
                        touch *.xml
                        python3 -m pytest --pyargs -s tests --junitxml="results.xml" --cov=./pds/api --cov=./ansible_collections/sodalite --cov-report xml tests/
                    """
                junit 'src/results.xml'
            }
        }
        stage('SonarQube analysis'){
            environment {
            scannerHome = tool 'SonarQubeScanner'
            }
            steps {
                withSonarQubeEnv('SonarCloud') {
                    sh  """ #!/bin/bash        
                            cd src                    
                            ${scannerHome}/bin/sonar-scanner
                        """
                }
            }
        } /*
        stage('Build Platform Discovery Service Docker Image') {
            steps {
                sh """#!/bin/bash
                    ./make_docker.sh build platform-discovery-service
                    """
            }
        }
        stage('Push Platform Discovery Service to DockerHub') {
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            ./make_docker.sh push platform-discovery-service production
                        """
                }
            }
        }     */   

    }
}