pipeline {
    agent { label 'Docker-Servers' } // <-- ¡IMPORTANTE! Reemplaza con la etiqueta de tu nodo.
    environment {
        // Variables de SonarQube
        // Asegúrate de que 'Qube' es el nombre del SonarQube Scanner configurado en Jenkins
        SONARQUBE_URL = 'http://54.227.78.73:9000' // Tu URL de SonarQube
        SONARQUBE_PROJECT_KEY = 'TFM' // Clave de tu proyecto en SonarQube
        SONARQUBE_PROJECT_NAME = 'TFM' // Nombre visible en SonarQube
        PYTHON_VERSION = '3.10' // Versión de Python de tu proyecto
        SONARQUBE_SERVER_NAME = 'sonarqube'
        // Asegúrate de que 'sonarqube-token' es el ID de la credencial de Jenkins donde guardaste tu token de SonarQube
        SONARQUBE_LOGIN_CREDENTIAL_ID = 'gene-token'
    }
    stages {
        stage('Detener servicios anteriores') { // Etapa renombrada para mayor claridad
            steps {
                echo 'Deteniendo servicios remanentes...'
                script {
                    // Navegar al directorio donde se encuentra tu docker-compose.yml si no está en la raíz del repositorio.
                    // Por ejemplo, si está en una subcarpeta 'docker/':
                    sh 'cd /home/docker-server/jenkins/jenkins/workspace/clasificacion-futbol-main'                
                    sh 'docker-compose down -v'
                    sh 'sleep 15' // Ajusta el tiempo según lo que tarden tus servicios en arrancar.
                }
            }
        }
        stage('Levantar Servicios Docker Compose') { // Etapa renombrada para mayor claridad
            steps {
                echo 'Construyendo y levantando servicios con Docker Compose...'
                script {
                    // Navegar al directorio donde se encuentra tu docker-compose.yml si no está en la raíz del repositorio.
                    // Por ejemplo, si está en una subcarpeta 'docker/':
                    sh 'cd /home/docker-server/jenkins/jenkins/workspace/clasificacion-futbol-main'

                    // Ejecuta docker-compose up para construir y levantar los servicios en segundo plano.
                    // La opción '--build' asegura que las imágenes se reconstruyan si el Dockerfile ha cambiado.
                    sh 'docker-compose up -d --build'

                    echo 'Servicios Docker Compose levantados. Prueba final esperando unos 15 segundos para su inicialización...'
                    // Esto es una pausa simple. En producción, considera health checks más robustos.
                    sh 'sleep 45' // Ajusta el tiempo según lo que tarden tus servicios en arrancar.
                }
            }
        }
        stage('Ejecutar Migraciones de Django') {
            steps {
                echo 'Ejecutando migraciones de base de datos Django...'
                // Asegúrate de que 'web' es el nombre de tu servicio Django en docker-compose.yml
                sh 'docker-compose exec web python manage.py migrate'
                // O si también necesitas makemigrations si hay cambios en el modelo
                sh 'docker-compose exec web python manage.py makemigrations'
                sh 'docker-compose exec web python manage.py makemigrations clubes'
                sh 'docker-compose exec web python manage.py makemigrations users'
                sh 'docker-compose exec web python manage.py migrate'
                sh 'docker-compose exec web python manage.py migrate'
            }
        }
        stage('Crear Superusuario Django') {
            steps {
                echo 'Creando superusuario de Django (solo si no existe o para desarrollo)...'
                sh "docker-compose exec web sh -c \"echo \\\"from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', '12345678')\\\" | python manage.py shell\""
            }
        }
        stage('Análisis SonarQube') {
            steps {
                script {
                    // Asegúrate de que 'Mi SonarQube' es el nombre del servidor SonarQube configurado en Jenkins
                    def sonarScannerHome = tool 'Qube'
                        // Comando para ejecutar el SonarScanner
                    withCredentials([string(credentialsId: "${SONARQUBE_LOGIN_CREDENTIAL_ID}", variable: 'SONAR_AUTH_TOKEN')]) {
                        sh "${sonarScannerHome}/bin/sonar-scanner " +
                            "-Dsonar.projectKey=${SONARQUBE_PROJECT_KEY} " +
                            "-Dsonar.projectName=${SONARQUBE_PROJECT_NAME} " +
                            "-Dsonar.sources=. " +
                            "-Dsonar.host.url=${SONARQUBE_URL} " +
                            "-Dsonar.python.version=${PYTHON_VERSION} " +
                            "-Dsonar.sourceEncoding=UTF-8 " +
                            "-Dsonar.python.xunit.reportPaths=results/junit.xml " +
                            "-Dsonar.python.coverage.reportPaths=results/coverage.xml " +
                            "-Dsonar.login=${SONAR_AUTH_TOKEN}" // Token de autenticación, inyectado por Jenkins
                    }
                }    
            }        
        }

        stage('Quality Gate Check') {
            steps {
                timeout(time: 5, unit: 'MINUTES') { // Tiempo máximo para esperar la respuesta de SonarQube
                    script {
                        echo "Waiting for SonarQube Quality Gate status..."
                        // 'serverName' debe coincidir con el nombre de tu configuración de servidor SonarQube en Jenkins
                        def qg = waitForQualityGate serverName: "${SONARQUBE_SERVER_NAME}"

                        if (qg.status != 'OK') {
                            error "Pipeline abortado: La Puerta de Calidad de SonarQube falló con estado: ${qg.status}. Detalles en: ${qg.projectStatus.analysisUrl}"
                        } else {
                            echo "SonarQube Quality Gate Passed: ${qg.status}"
                        }
                    }
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