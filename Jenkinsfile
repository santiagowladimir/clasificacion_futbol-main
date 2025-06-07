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
                    def djangoSuperuserUsername = "admin"
                    def djangoSuperuserEmail = "admin@example.com"
                    // **IMPORTANTE: Cambia esta contraseña en producción y usa Jenkins Credentials.**
                    def djangoSuperuserPassword = "12345678"

                    sh """
                        # Comando para crear superusuario sin interacción (si no existe)
                        docker-compose exec web bash -c "
                            python manage.py createsuperuser --noinput \\
                            --username ${djangoSuperuserUsername} \\
                            --email ${djangoSuperuserEmail} || true
                        "

                        # Comando robusto para establecer/actualizar la contraseña
                        # Escapamos la contraseña para el shell y para el script de Python.
                        # Es crucial que la contraseña se pase como un literal de cadena a Python.
                        docker-compose exec web bash -c "
                            SUPERUSER_USERNAME='${djangoSuperuserUsername}'
                            SUPERUSER_EMAIL='${djangoSuperuserEmail}'
                            SUPERUSER_PASSWORD='${djangoSuperuserPassword}'

                            # Script Python para ejecutar en manage.py shell
                            PYTHON_SCRIPT=\$(cat <<EOF
                        from django.contrib.auth import get_user_model
                        User = get_user_model()
                        username = '$SUPERUSER_USERNAME'
                        email = '$SUPERUSER_EMAIL'
                        password = '$SUPERUSER_PASSWORD'

                        if not User.objects.filter(username=username).exists():
                            User.objects.create_superuser(username, email, password)
                        else:
                            # Opcional: Si el usuario ya existe y quieres actualizar su contraseña
                            user = User.objects.get(username=username)
                            if not user.check_password(password): # Solo actualiza si la contraseña es diferente
                                user.set_password(password)
                                user.save()
                                print(f"Contraseña para {username} actualizada.")
                            else:
                                print(f"Usuario {username} ya existe con la misma contraseña.")
                        EOF
                        )
                                            echo "\$PYTHON_SCRIPT" | python manage.py shell
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