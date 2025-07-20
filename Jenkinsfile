pipeline {
    agent { label 'Docker-Servers' } // <-- ¡IMPORTANTE! Reemplaza con la etiqueta del nodo.
    environment {
        // Variables de SonarQube
        SONARQUBE_PROJECT_KEY = 'TFM' // Clave del proyecto en SonarQube
        SONARQUBE_PROJECT_NAME = 'TFM' // Nombre visible en SonarQube
        PYTHON_VERSION = '3.10' // Versión de Python del proyecto
    }
    
    stages {
        stage('Análisis SonarQube') {
            steps {
                script {
                     withSonarQubeEnv('sonarqube') { // nombre de la conexión SonarQube en Jenkins
                        def sonarScannerHome = tool 'Qube' // 'Nombre del SonarQube Scanner configurado en 'Manage Jenkins' -> 'Global Tool Configuration'

                        // Comando para ejecutar el SonarScanner
                        sh "${sonarScannerHome}/bin/sonar-scanner " +
                            "-Dsonar.projectKey=${SONARQUBE_PROJECT_KEY} " +
                            "-Dsonar.projectName=${SONARQUBE_PROJECT_NAME} " +
                            "-Dsonar.sources=. " +
                            "-Dsonar.python.version=${PYTHON_VERSION} " +
                            "-Dsonar.sourceEncoding=UTF-8 " +
                            "-Dsonar.python.xunit.reportPaths=results/junit.xml " +
                            "-Dsonar.python.coverage.reportPaths=results/coverage.xml"
                    }
                }
            }
        }
        stage("Quality Gate"){
            steps {
                script {
                    timeout(time: 5, unit: 'MINUTES') {
                        def qg = waitForQualityGate('sonarqube')
                        if (qg.status != 'OK') {
                            error "Pipeline aborted due to quality gate failure: ${qg.status}"
                        }
                    }
                }
            }
        }
        stage('Detener servicios anteriores') {
            steps {
                echo 'Deteniendo servicios remanentes...'
                script {
                    // Directorio donde se encuentra el docker-compose.yml.
                    sh 'cd /home/docker-server/jenkins/jenkins/workspace/clasificacion-futbol-main'                
                    sh 'docker-compose down -v'
                }
            }
        }
        stage('Levantar Servicios Docker Compose') {
            steps {
                echo 'Construyendo y levantando servicios con Docker Compose...'
                script {
                    // Directorio donde se encuentra el docker-compose.yml
                    sh 'cd /home/docker-server/jenkins/jenkins/workspace/clasificacion-futbol-main'
                    // Ejecuta docker-compose up para construir y levantar los servicios en segundo plano.
                    sh 'docker-compose up -d --build'
               }
            }
        } 
    }
  // Bloque post para acciones que se ejecutan al finalizar el pipeline, independientemente del éxito o fallo.
    post {
        always {
            echo 'Pipeline de Docker Compose finalizado.'
        }
        failure {
            echo 'El pipeline falló. Por favor, revisa los logs.'
        }
        success {
            echo 'El pipeline se ejecutó exitosamente.'
        }
    }
}