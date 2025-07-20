# Imagen oficial de Python 3.10
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

# Ejecutable
RUN chmod +x /usr/local/bin/entrypoint.sh

# Establece el entrypoint para el contenedor
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]

# Inicialización del servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# EXPOSE del puerto de la aplicación
EXPOSE 8000