pipeline {
    agent { label 'Docker-Servers' } // <-- ¡IMPORTANTE! Reemplaza con la etiqueta de tu nodo.

    stages {
        stage('Checkout de Código') {
            steps {
                echo 'Clonando el repositorio Git...'
                // Reemplaza 'https://github.com/tu_usuario/tu_repositorio.git' con la URL real de tu repositorio.
                // Si el repositorio es privado, asegúrate de tener las credenciales configuradas en Jenkins.
                git 'https://github.com/santiagowladimir/clasificacion_futbol-main.git' // 
            }
        }

        stage('Levantar Servicios Docker Compose') { // Etapa renombrada para mayor claridad
            steps {
                echo 'Construyendo y levantando servicios con Docker Compose...'
                script {
                    // Navegar al directorio donde se encuentra tu docker-compose.yml si no está en la raíz del repositorio.
                    // Por ejemplo, si está en una subcarpeta 'docker/':
                    sh 'cd clasificacion_futbol-main'

                    // Ejecuta docker-compose up para construir y levantar los servicios en segundo plano.
                    // La opción '--build' asegura que las imágenes se reconstruyan si el Dockerfile ha cambiado.
                    sh 'docker-compose up -d --build'

                    echo 'Servicios Docker Compose levantados. Esperando unos segundos para su inicialización...'
                    // Esto es una pausa simple. En producción, considera health checks más robustos.
                    sh 'sleep 15' // Ajusta el tiempo según lo que tarden tus servicios en arrancar.
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