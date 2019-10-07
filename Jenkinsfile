def stackName = 'qat'
def workerLabel = "verify-${stackName}"
def dockerHubAccount = 'mytardis'
def dockerImageName = 'k8s-verify'
def dockerImageTag = ''
def dockerImageFullNameTag = ''
def dockerImageFullNameLatest = "${dockerHubAccount}/${dockerImageName}:latest"
def k8sDeploymentNamespace = 'mytardis'

podTemplate(
    label: workerLabel,
    serviceAccount: 'jenkins',
    automountServiceAccountToken: true,
    containers: [
        containerTemplate(
            name: 'docker',
            image: 'docker:18.06.1-ce-dind',
            ttyEnabled: true,
            command: 'cat',
            envVars: [
                containerEnvVar(key: 'DOCKER_CONFIG', value: '/tmp/docker')
            ],
            resourceRequestCpu: '500m',
            resourceLimitCpu: '500m'
        ),
        containerTemplate(
            name: 'rabbitmq',
            image: 'rabbitmq:3.7',
            alwaysPullImage: false,
            envVars: [
                envVar(key: 'RABBITMQ_DEFAULT_USER', value: 'user'),
                envVar(key: 'RABBITMQ_DEFAULT_PASS', value: 'password')
            ]
        ),
        containerTemplate(
            name: 'kubectl',
            image: 'lachlanevenson/k8s-kubectl:v1.13.0',
            ttyEnabled: true,
            command: 'cat',
            envVars: [
                containerEnvVar(key: 'KUBECONFIG', value: '/tmp/kube/admin.conf')
            ],
            resourceLimitCpu: '250m'
        )
    ],
    volumes: [
        secretVolume(secretName: "kube-config-${stackName}", mountPath: '/tmp/kube'),
        secretVolume(secretName: 'docker-config', mountPath: '/tmp/docker'),
        hostPathVolume(hostPath: '/var/run/docker.sock', mountPath: '/var/run/docker.sock')
    ]
) {
    node(workerLabel) {
        stage('Clone repository') {
            checkout scm
        }
        dockerImageTag = sh(returnStdout: true, script: 'git log -n 1 --pretty=format:"%h"').trim()
        dockerImageFullNameTag = "${dockerHubAccount}/${dockerImageName}:${dockerImageTag}"
        stage('Build image for tests') {
            container('docker') {
                sh("docker build . --tag ${dockerImageFullNameTag} --target=test")
            }
        }
        def tests = [:]
        [
            'pylint': "docker run ${dockerImageFullNameTag} pylint --rcfile .pylintrc tardis",
            'flake8': "docker run ${dockerImageFullNameTag} flake8 --config=.flake8 tardis",
            'tests': "docker run ${dockerImageFullNameTag} python manage.py test"
        ].each { name, command ->
            tests[name] = {
                stage("Run test - ${name}") {
                    container('docker') {
                        sh(command)
                    }
                }
            }
        }
        parallel tests
        stage('Build image for production') {
            container('docker') {
                sh("docker build . --tag ${dockerImageFullNameTag} --target=builder")
            }
        }
        stage('Push image to DockerHub') {
            container('docker') {
                sh("docker push ${dockerImageFullNameTag}")
                sh("docker tag ${dockerImageFullNameTag} ${dockerImageFullNameLatest}")
                sh("docker push ${dockerImageFullNameLatest}")
            }
        }
        stage('Deploy image to Kubernetes') {
            container('kubectl') {
                ['verify'].each { item ->
                    sh ("kubectl -n ${k8sDeploymentNamespace} set image deployment/${item} ${item}=${dockerImageFullNameTag}")
                }
            }
        }
    }
}
