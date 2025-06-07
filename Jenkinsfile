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

                    echo 'Servicios Docker Compose levantados. Prueba esperando unos 15 segundos para su inicialización...'
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
                script {
                    // Define las variables de entorno para el superusuario
                    def djangoSuperuserUsername = "admin"
                    def djangoSuperuserEmail = "admin@example.com"
                    def djangoSuperuserPassword = "12345678" // ¡CAMBIA ESTO EN PRODUCCIÓN!

                    // Ejecuta el comando crea superusuario no interactivo
                    // Se usa el comando 'bash -c' para poder concatenar comandos con '|| true'
                    // '|| true' hace que la etapa no falle si el comando devuelve un error (ej. si el usuario ya existe)
                    sh """
                        docker-compose exec web bash -c "
                            python manage.py createsuperuser --noinput \\
                            --username ${djangoSuperuserUsername} \\
                            --email ${djangoSuperuserEmail} || true
                        "
                        # Si el usuario ya existe, el comando anterior puede no haber establecido la contraseña.
                        # Este comando es más robusto para establecer/actualizar la contraseña.
                        docker-compose exec web bash -c "
                            echo \"from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(username='${djangoSuperuserUsername}').exists() or User.objects.create_superuser('${djangoSuperuserUsername}', '${djangoSuperuserEmail}', '${djangoSuperuserPassword}')\" | python manage.py shell
                        "
                    """
                    echo "Superusuario '${djangoSuperuserUsername}' intentado crear/actualizar."
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