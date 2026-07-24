pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    parameters {
        booleanParam(
            name: 'RUN_DOCKER_BUILD',
            defaultValue: false,
            description: 'Build the Docker Compose stack after tests pass.'
        )
    }

    environment {
        VENV_DIR = '.venv-jenkins'
        PYTHON_BIN = "${WORKSPACE}/.venv-jenkins/bin/python"
        PIP_BIN = "${WORKSPACE}/.venv-jenkins/bin/pip"
        REPORTS_DIR = 'reports'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Env') {
            steps {
                sh '''
                    set -eu
                    mkdir -p "$REPORTS_DIR"
                    python3 -m venv "$VENV_DIR"
                    "$PIP_BIN" install --upgrade pip
                    "$PIP_BIN" install -r requirements.txt
                '''
            }
        }

        stage('Pytest') {
            steps {
                sh '''
                    set -eu
                    "$PYTHON_BIN" -m pytest -q --junitxml="$REPORTS_DIR/pytest.xml"
                '''
            }
        }

        stage('Compose Config') {
            steps {
                sh '''
                    set -eu
                    if ! command -v docker >/dev/null 2>&1; then
                        echo "Docker CLI not installed on agent; failing Compose validation."
                        exit 1
                    fi
                    docker compose config >"$REPORTS_DIR/docker-compose.rendered.yaml"
                    test -s "$REPORTS_DIR/docker-compose.rendered.yaml"
                '''
            }
        }

        stage('Docker Policy') {
            steps {
                script {
                    def branchName = env.BRANCH_NAME ?: env.GIT_BRANCH ?: 'detached'
                    def autoBuildBranch = branchName == 'main' || branchName == 'develop' || branchName ==~ /^release\/.*$/
                    env.EFFECTIVE_BRANCH_NAME = branchName
                    env.AUTO_DOCKER_BUILD = autoBuildBranch ? 'true' : 'false'
                    env.SHOULD_RUN_DOCKER_BUILD = (autoBuildBranch || params.RUN_DOCKER_BUILD) ? 'true' : 'false'
                    currentBuild.displayName = "#${env.BUILD_NUMBER} ${env.EFFECTIVE_BRANCH_NAME}"
                    currentBuild.description = "docker-build=${env.SHOULD_RUN_DOCKER_BUILD} auto-branch=${env.AUTO_DOCKER_BUILD}"

                    echo "Branch detected: ${env.EFFECTIVE_BRANCH_NAME}"
                    echo "Automatic Docker build branch: ${env.AUTO_DOCKER_BUILD}"
                    echo "Docker build stage enabled: ${env.SHOULD_RUN_DOCKER_BUILD}"
                }
            }
        }

        stage('Docker Build') {
            when {
                expression { return env.SHOULD_RUN_DOCKER_BUILD == 'true' }
            }
            steps {
                sh '''
                    set -eu
                    docker info >/dev/null 2>&1
                    docker compose build
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'reports/pytest.xml', allowEmptyResults: true
            archiveArtifacts artifacts: 'README.md,docker-compose.yml,Jenkinsfile,reports/**', onlyIfSuccessful: false
            sh '''
                if command -v docker >/dev/null 2>&1; then
                    docker compose down --volumes --remove-orphans >/dev/null 2>&1 || true
                fi
                rm -rf "$VENV_DIR"
            '''
        }
    }
}
