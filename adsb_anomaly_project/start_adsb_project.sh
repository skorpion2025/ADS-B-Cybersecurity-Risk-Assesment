#!/bin/bash

# Directorios del proyecto
DUMP1090_DIR=~/dump1090
PROJECT_DIR=~/adsb_anomaly_project

# Archivo de log
LOG_FILE="$PROJECT_DIR/log.txt"

# Registrar inicio en el log
echo "==== Proyecto Iniciado el $(date) ====" >> $LOG_FILE

# Iniciar dump1090 en segundo plano
echo "Iniciando dump1090..." | tee -a $LOG_FILE
cd $DUMP1090_DIR
./dump1090 --interactive --net --net-http-port 8080 &>> $LOG_FILE &
DUMP1090_PID=$!

# Esperar unos segundos para que dump1090 se inicie correctamente
sleep 3

# Activar el entorno virtual
echo "Activando entorno virtual..." | tee -a $LOG_FILE
cd $PROJECT_DIR
source env/bin/activate

# Ejecutar el script Python en segundo plano y redirigir toda la salida a log.txt
echo "Ejecutando el script de detección de anomalías..." | tee -a $LOG_FILE
python adsb_anomaly_detector.py &>> $LOG_FILE &
SCRIPT_PID=$!

# Esperar a que se presione CTRL+C para detener ambos procesos
echo "Presiona CTRL+C para detener el proyecto..." | tee -a $LOG_FILE
trap "kill $DUMP1090_PID $SCRIPT_PID; deactivate; echo 'Proceso detenido el $(date)' >> $LOG_FILE; exit" INT

# Mantener el script activo hasta que se reciba CTRL+C
wait

