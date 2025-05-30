#!/usr/bin/env python3

import os
import numpy as np
import pyModeS as pms
import socket
import threading
import time

LOG_FILE = "log.txt"
ANOMALIES_FILE = "anomalies_report.txt"
RTL_HOST = '127.0.0.1'
RTL_PORT = 30002

adsb_messages = []
lock = threading.Lock()

# Inicializar el archivo de anomalías con el encabezado
with open(ANOMALIES_FILE, "w") as f:
    f.write("Análisis de Anomalías ADS-B\n")
    f.write("=" * 50 + "\n")
    f.write("Timestamp         Flight ID        Anomalía Detectada\n")
    f.write("=" * 50 + "\n")

def log_message(message):
    """ Registrar en el log """
    with open(LOG_FILE, "a") as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def log_error(error_message):
    """ Registrar errores """
    log_message(f"[ERROR] {error_message}")

def capture_realtime_data():
    """ Captura datos ADS-B en tiempo real desde el puerto 30002 de dump1090 """
    log_message("[DEBUG] Iniciando captura de datos en tiempo real...")

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((RTL_HOST, RTL_PORT))
            buffer = ""

            while True:
                try:
                    data = s.recv(1024).decode('utf-8')
                    buffer += data

                    while ";" in buffer:
                        parts = buffer.split(";")
                        for part in parts[:-1]:
                            msg = part.strip().lstrip("*")
                            if len(msg) == 28:
                                with lock:
                                    adsb_messages.append(msg)
                                    log_message(f"[CAPTURA] Mensaje Capturado: {msg}")
                            else:
                                log_message(f"[ERROR] Mensaje recibido con longitud inesperada: {msg}")

                        buffer = parts[-1]

                except Exception as e:
                    log_error(f"Error al recibir datos: {str(e)}")
                    continue

    except Exception as e:
        log_error(f"Error en conexión al puerto 30002: {str(e)}")

def extract_features(message):
    """ Extrae características de un mensaje ADS-B """
    log_message(f"[DEBUG] Procesando mensaje: {message}")

    if len(message) != 28:
        log_error(f"Longitud inesperada del mensaje: {len(message)} - {message}")
        return [0.0, 0.0, 0, "UNKNOWN"]

    flight_id = "UNKNOWN"
    alt = 0
    speed = 0
    heading = 0

    try:
        msg_type = pms.adsb.typecode(message)
        log_message(f"[DEBUG] Tipo de mensaje: {msg_type}")

        # Flight ID Extraction
        if msg_type in [4, 20, 21]:
            flight_id = pms.adsb.callsign(message).strip().upper()
            log_message(f"[DEBUG] Flight ID extraído: {flight_id}")

        # Altitude Extraction
        if msg_type in [9, 10, 11]:
            alt = pms.adsb.altitude(message) or 0
            log_message(f"[DEBUG] Altitud extraída: {alt}")

        # Speed and Heading Extraction
        if msg_type == 19:
            speed, heading = extract_velocity_heading(message)
            log_message(f"[DEBUG] Velocidad: {speed} knots, Rumbo: {heading}°")

        return [alt, speed, heading, flight_id]

    except Exception as e:
        log_error(f"Error en extract_features(): {e}")
        return [0.0, 0.0, 0, "UNKNOWN"]

def extract_velocity_heading(message):
    try:
        # Obtener velocidad y rumbo
        ground_speed = pms.adsb.velocity(message)[0] if pms.adsb.velocity(message) else 'UNKNOWN'
        heading = pms.adsb.velocity(message)[1] if pms.adsb.velocity(message) else 'UNKNOWN'
        return ground_speed, heading
    except Exception as e:
        log_error(f"Error al extraer velocidad/rumbo: {str(e)}")
        return 'UNKNOWN', 'UNKNOWN'

def classify_anomaly(features):
    """ Clasifica la anomalía basada en las características extraídas """
    alt, speed, heading, flight_id = features
    timestamp = time.strftime('%Y-%m-%d %H:%M')

    anomaly_detected = False
    anomaly_message = ""

    # Message Injection Detection (antes: Spoofing)
    if flight_id.startswith("TEST"):
        anomaly_detected = True
        anomaly_message = f"{timestamp}  {flight_id:<15} Message Injection (Flight ID: {flight_id})"

    # Velocidad Excesiva
    if speed != 'UNKNOWN' and speed > 900:
        anomaly_detected = True
        anomaly_message = f"{timestamp}  UNKNOWN          Velocidad Excesiva: {speed} knots"

    # Altitud Excesiva
    if alt > 60000:
        anomaly_detected = True
        anomaly_message = f"{timestamp}  UNKNOWN          Altitud Excesiva: {alt} ft"

    if anomaly_detected:
        with open(ANOMALIES_FILE, "a") as f:
            f.write(anomaly_message + "\n")
        log_message(f"[ALERTA] {anomaly_message}")

def analyze_data():
    """ Analiza los datos almacenados en el buffer """
    while True:
        with lock:
            while adsb_messages:
                msg = adsb_messages.pop(0)
                features = extract_features(msg)
                classify_anomaly(features)
        time.sleep(0.1)

def main():
    """ Función principal para iniciar los hilos de captura y análisis """
    log_message("[INFO] Iniciando el sistema de detección de anomalías ADS-B...")
    
    # Iniciar hilo de captura de datos
    capture_thread = threading.Thread(target=capture_realtime_data)
    capture_thread.daemon = True
    capture_thread.start()

    # Iniciar hilo de análisis de datos
    analysis_thread = threading.Thread(target=analyze_data)
    analysis_thread.daemon = True
    analysis_thread.start()

    # Mantener el script en ejecución
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()

