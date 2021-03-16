pipeline {
    agent { label 'docker-slave' }
        environment {
            // TESTING ENV
            PDS_BLUEPRINT_PATH = "/blueprints"
            OIDC_CLIENT_ID = "TEST_ID"
            OIDC_CLIENT_SECRET = "TEST_SECRET"
            OIDC_INTROSPECTION_ENDPOINT = "http://localhost:8080/auth/realms/SODALITE/protocol/openid-connect/token"
            PDS_STORAGE_KEY = "TEST_STORAGE_KEY"
            SECRET_VAULT_LOGIN_URI = "http://localhost:8200/v1/auth/jwt/login"
            SECRET_VAULT_URI = "http://localhost:8200/v1/"

            // DEPLOY ENV
            // OPENSTACK SETTINGS
            ssh_key_name = "jenkins-opera"
            image_name = "centos7"
            network_name = "orchestrator-network"
            security_groups = "default,sodalite-remote-access,sodalite-uc"
            flavor_name = "m1.medium"
            // DOCKER SETTINGS
            docker_network = "sodalite"
            docker_registry_ip = credentials('jenkins-docker-registry-ip')
            docker_registry_cert_country_name = "SI"
            docker_registry_cert_organization_name = "XLAB"
            docker_public_registry_url = "registry.hub.docker.com"
            docker_registry_cert_email_address = "dragan.radolovic@xlab.si"
            //KEYCLOAK SETTINGS
            KEYCLOAK_URL = credentials('keycloak-url')
            KEYCLOAK_CLIENT_ID = credentials('keycloak-client-id')
            KEYCLOAK_CLIENT_SECRET = credentials('keycloak-client-secret')
            // OPENSTACK DEPLOYMENT FALLBACK SETTINGS
            OS_PROJECT_DOMAIN_NAME = "Default"
            OS_USER_DOMAIN_NAME = "Default"
            OS_PROJECT_NAME = "orchestrator"
            OS_TENANT_NAME = "orchestrator"
            OS_USERNAME = credentials('os-username')
            OS_PASSWORD = credentials('os-password')
            OS_AUTH_URL = credentials('os-auth-url')
            OS_INTERFACE = "public"
            OS_IDENTITY_API_VERSION = "3"
            OS_REGION_NAME = "RegionOne"
            OS_AUTH_PLUGIN = "password"
            // ROOT X.509 CERTIFICATES
            ca_crt_file = credentials('xopera-ca-crt')
            ca_key_file = credentials('xopera-ca-key')

            // CI-CD vars
            // When triggered from git tag, $BRANCH_NAME is actually GIT's tag_name
            TAG_SEM_VER_COMPLIANT = """${sh(
                    returnStdout: true,
                    script: './validate_tag.sh SemVar $BRANCH_NAME'
                )}"""

            TAG_MAJOR_RELEASE = """${sh(
                    returnStdout: true,
                    script: './validate_tag.sh MajRel $BRANCH_NAME'
                )}"""

            TAG_PRODUCTION = """${sh(
                    returnStdout: true,
                    script: './validate_tag.sh production $BRANCH_NAME'
                )}"""

            TAG_STAGING = """${sh(
                    returnStdout: true,
                    script: './validate_tag.sh staging $BRANCH_NAME'
                )}"""
        }
    stages {
        stage ('Pull repo code from github') {
            steps {
                checkout scm
            }
        }
        stage('Inspect GIT TAG'){
            steps {
                sh """ #!/bin/bash
                echo 'TAG: $BRANCH_NAME'
                echo 'Tag is compliant with SemVar 2.0.0: $TAG_SEM_VER_COMPLIANT'
                echo 'Tag is Major release: $TAG_MAJOR_RELEASE'
                echo 'Tag is production: $TAG_PRODUCTION'
                echo 'Tag is staging: $TAG_STAGING'
                """
            }

        }
        stage('Test PDS') {
            steps {
                sh  """ #!/bin/bash
                        python3 -m venv venv-test
                        . venv-test/bin/activate
                        pip3 install --upgrade pip
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
        }
        stage('Build Platform Discovery Service Docker Image') {
            when {
                allOf {
                    // Triggered on every tag, that is considered for staging or production
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
             }
            steps {
                sh """#!/bin/bash
                    ./make_docker.sh build platform-discovery-service
                    """
            }
        }
        stage('Push Platform Discovery Service to SODALITE registry') {
            when {
                allOf {
                    // Triggered on every tag, that is considered for staging or production
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
             }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            ./make_docker.sh push platform-discovery-service staging
                        """
                }
            }
        }
        stage('Push Platform Discovery Service to DockerHub') {
            when {
                allOf {
                    // Triggered on every tag, that is considered for staging or production
                    expression{tag "*"}
                    expression{
                        TAG_PRODUCTION == 'true'
                    }
                }
             }
            steps {
                withDockerRegistry(credentialsId: 'jenkins-sodalite.docker_token', url: '') {
                    sh  """#!/bin/bash
                            ./make_docker.sh push platform-discovery-service production
                        """
                }
            }
        }
        stage('Install deploy dependencies') {
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true' || TAG_PRODUCTION == 'true'
                    }
                }
            }
            steps {
                sh """#!/bin/bash
                    python3 -m venv venv-deploy
                    . venv-deploy/bin/activate
                    python3 -m pip install --upgrade pip
                    python3 -m pip install opera==0.6.4 openstacksdk==0.52.0 docker
                    rm -r -f pds-openstack/modules/
                    git clone -b 3.3.0 https://github.com/SODALITE-EU/iac-modules.git pds-openstack/modules/
                    ansible-galaxy install -r pds-openstack/modules/requirements.yml --force
                    cp ${ca_crt_file} pds-openstack/modules/docker/artifacts/ca.crt
                    cp ${ca_crt_file} pds-openstack/modules/misc/tls/artifacts/ca.crt
                    cp ${ca_key_file} pds-openstack/modules/docker/artifacts/ca.key
                    cp ${ca_key_file} pds-openstack/modules/misc/tls/artifacts/ca.key
                   """
            }
        }
        stage('Deploy to openstack for staging') {
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_STAGING == 'true'
                    }
                }
            }
            environment {
                vm_name = 'pds-dev'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh """#!/bin/bash
                        # create input.yaml file from template
                        envsubst < pds-openstack/input.yaml.tmpl > pds-openstack/input.yaml
                        . venv-deploy/bin/activate
                        cd pds-openstack
                        rm -r -f .opera
                        opera deploy service.yaml -i input.yaml
                       """
                }
            }
        }
        stage('Deploy to openstack for production') {
            when {
                allOf {
                    expression{tag "*"}
                    expression{
                        TAG_PRODUCTION == 'true'
                    }
                }
            }
            environment {
                vm_name = 'pds'
            }
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'xOpera_ssh_key', keyFileVariable: 'xOpera_ssh_key_file', usernameVariable: 'xOpera_ssh_username')]) {
                    sh """#!/bin/bash
                        # create input.yaml file from template
                        envsubst < pds-openstack/input.yaml.tmpl > pds-openstack/input.yaml
                        . venv-deploy/bin/activate
                        cd pds-openstack
                        rm -r -f .opera
                        opera deploy service.yaml -i input.yaml
                       """
                }
            }
        }

    }
}