#!/usr/bin/env bash
# wait-for-it.sh
#
# Espera a que un host y puerto estén disponibles.
# Adaptado para Fedora/Red Hat.
#
# Uso: ./wait-for-it.sh host:port [-t timeout] [-- command args]

# Valores por defecto
TIMEOUT=15
QUIET=0 # 0 para mostrar mensajes, 1 para ser silencioso

# --- Funciones de Ayuda ---

# Función para imprimir mensajes de error
error() {
  if [ "$QUIET" -eq 0 ]; then
    printf '\e[31m%s\e[0m\n' "$@" 1>&2 # Mensaje en rojo a stderr
  fi
}

# Función para imprimir mensajes de información
info() {
  if [ "$QUIET" -eq 0 ]; then
    printf '\e[32m%s\e[0m\n' "$@" # Mensaje en verde a stdout
  fi
}

# Función para mostrar uso
usage() {
  cat << USAGE >&2
Usage:
  $0 host:port [-t timeout] [-- command args]
  $0 host:port [-s] [-t timeout] [-- command args]

  host:port
    Dirección del host y puerto a esperar.
  -t timeout | --timeout timeout
    Tiempo en segundos para esperar que el host:port esté disponible (por defecto: $TIMEOUT).
  -s | --strict
    Solo ejecuta el comando si el host:port está disponible.
  -q | --quiet
    No muestra mensajes de salida.
  -- command args
    Comando a ejecutar después de que el host:port esté disponible (opcional).

USAGE
  exit 1
}

# --- Procesar Argumentos ---
# (Este bucle es crucial para parsear opciones antes y después del host:port)

# Extraer el host:port que siempre debe ser el primer argumento sin guiones
if [[ "$1" == "--" ]]; then
  usage
fi
HOST_PORT="$1"
shift

# Verificar que el host:port tenga el formato correcto
if [[ "$HOST_PORT" =~ ^([^:]+):([0-9]+)$ ]]; then
  HOST="${BASH_REMATCH[1]}"
  PORT="${BASH_REMATCH[2]}"
else
  error "Formato de host:port inválido: $HOST_PORT"
  usage
fi

# Parsear el resto de los argumentos
while true; do
  case "$1" in
    -t | --timeout)
      if [ -n "$2" ] && [[ "$2" =~ ^[0-9]+$ ]]; then
        TIMEOUT="$2"
        shift 2
      else
        error "Error: --timeout requiere un valor numérico."
        usage
      fi
      ;;
    -s | --strict)
      STRICT=1
      shift
      ;;
    -q | --quiet)
      QUIET=1
      shift
      ;;
    --)
      shift
      CLI_COMMAND=("$@")
      break
      ;;
    -*)
      error "Opción desconocida: $1"
      usage
      ;;
    *)
      if [ -n "$1" ]; then
        error "Argumento inesperado: $1"
        usage
      fi
      break
      ;;
  esac
done

# --- Lógica Principal del Script ---

info "Esperando $HOST_PORT durante un máximo de $TIMEOUT segundos..."

start_time=$(date +%s)
while : ; do
  (echo > /dev/tcp/"$HOST"/"$PORT") >/dev/null 2>&1
  # La construcción /dev/tcp es una característica de bash que simula una conexión TCP.
  # Es común en sistemas Linux.
  result=$?
  if [ $result -eq 0 ]; then
    info "El servicio en $HOST_PORT está disponible."
    break
  fi
  current_time=$(date +%s)
  elapsed_time=$((current_time - start_time))
  if [ "$elapsed_time" -ge "$TIMEOUT" ]; then
    error "Tiempo de espera agotado después de $TIMEOUT segundos en $HOST_PORT."
    if [ "$STRICT" -eq 1 ]; then
      exit 1
    else
      info "Continuando sin que el servicio esté listo (modo no estricto)."
      exit 0 # Salir con éxito para continuar el flujo si no es estricto
    fi
  fi
  sleep 1
done

# --- Ejecutar Comando Opcional ---

if [ ${#CLI_COMMAND[@]} -gt 0 ]; then
  exec "${CLI_COMMAND[@]}" # Reemplaza el proceso actual con el comando dado
fi