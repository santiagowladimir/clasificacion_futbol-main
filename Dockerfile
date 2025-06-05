# Usa una imagen oficial de Python 3.10
FROM python:3.10.11-slim

# Establece el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia el archivo de requisitos de Python al contenedor
COPY requirements.txt /app/

# Instala las dependencias desde el archivo requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente al contenedor
COPY . /app/

# Copia el script de entrada al contenedor
COPY entrypoint.sh /usr/local/bin/entrypoint.sh

# Hazlo ejecutable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Establece el entrypoint para el contenedor
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# CMD es el comando por defecto que se pasa al ENTRYPOINT (si no se especifica en docker run/compose)
# En este caso, el ENTRYPOINT ya ejecuta el runserver, así que CMD podría ser solo un placeholder o vacío
CMD []

# EXPOSE el puerto de tu aplicación
EXPOSE 8000

# Comando para iniciar el servidor de desarrollo de Django
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
