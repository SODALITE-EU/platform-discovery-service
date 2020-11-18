pipeline {
    agent { label 'docker-slave' }
       environment {
           PDS_BLUEPRINT_PATH = "/testpath/testfolder"
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
                        . generate.sh
                        cd src
                        touch *.xml
                        python3 -m pytest --pyargs -s tests --junitxml="results.xml" --cov=./pds/api  --cov-report xml tests/
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
                            cd src/
                            ${scannerHome}/bin/sonar-scanner
                        """
                }
            }
        }        

    }
}