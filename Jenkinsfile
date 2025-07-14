pipeline {
    agent { label 'Docker-Servers' } // <-- ¡IMPORTANTE! Reemplaza con la etiqueta de tu nodo.

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
                    withSonarQubeEnv('Mi SonarQube') {
                        // Comando para ejecutar el SonarScanner
                        sh 'sonar-scanner ' +
                           '-Dsonar.projectKey=mi_proyecto_django ' + // Clave única para tu proyecto en SonarQube
                           '-Dsonar.projectName=Mi Proyecto Django ' + // Nombre visible en SonarQube
                           '-Dsonar.sources=. ' + // Directorio raíz de tu código fuente
                           '-Dsonar.host.url=http://3.92.169.236:9000 ' + // URL del servidor SonarQube desde el contenedor Jenkins
                           '-Dsonar.python.version=3.10 ' + // Ajusta a la versión de Python de tu proyecto
                           '-Dsonar.sourceEncoding=UTF-8 ' +
                           '-Dsonar.python.xunit.reportPath=results/junit.xml ' + // Ruta al informe de pruebas JUnit XML
                           '-Dsonar.python.coverage.reportPaths=results/coverage.xml ' + // Ruta al informe de cobertura Cobertura XML
                           '-Dsonar.login=${SONAR_AUTH_TOKEN}' // Token de autenticación, inyectado por Jenkins
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