import os
import numpy as np
import pyModeS as pms
from sklearn.preprocessing import MinMaxScaler
from keras.models import Sequential
from keras.layers import LSTM, RepeatVector, TimeDistributed, Dense
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import socket
import threading
import time

# Rutas de archivos
LOG_FILE = "log.txt"
ANOMALIES_FILE = "anomalies_report.txt"
IQ_FILE_PATH = "/tmp/adsb_iq.bin"
RAW_FILE_PATH = "/tmp/adsb_raw.txt"

# Configuración de RTL-SDR
RTL_HOST = '127.0.0.1'
RTL_PORT = 30002

# Variables globales
adsb_messages = []
lock = threading.Lock()

# Inicializar archivos de log
with open(ANOMALIES_FILE, "w") as f:
    f.write("ID, Error, Riesgo, Tipo de Amenaza\n")

def capture_realtime_data():
    """ Captura datos en tiempo real desde dump1090 """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((RTL_HOST, RTL_PORT))
        while True:
            data = s.recv(1024).decode('utf-8').strip()
            if len(data) == 28:
                with lock:
                    adsb_messages.append(data)

def extract_features(messages):
    features = []
    for msg in messages:
        try:
            df = pms.df(msg)
            if df in [17, 18]:
                lat, lon = pms.adsb.position_with_ref(msg, 0, 0)
                alt = pms.adsb.altitude(msg)
                velocity = pms.adsb.velocity(msg)
                speed, heading = velocity[0], velocity[1] if velocity else (0, 0)
                squawk = pms.idcode(msg) if pms.df(msg) in [5, 21] else 0
                if lat and lon:
                    features.append([lat, lon, alt, speed, heading, squawk])
        except Exception as e:
            log_message(f"[ERROR] Error al extraer características: {str(e)}")
            continue
    return np.array(features)

def build_lstm_model(input_shape):
    model = Sequential([
        LSTM(64, activation='relu', input_shape=input_shape, return_sequences=True),
        LSTM(32, activation='relu', return_sequences=False),
        RepeatVector(input_shape[0]),
        LSTM(32, activation='relu', return_sequences=True),
        TimeDistributed(Dense(input_shape[1]))
    ])
    model.compile(optimizer='adam', loss='mse')
    return model

def classify_anomaly(feature):
    """ Clasificación de la anomalía basada en los parámetros detectados """
    lat, lon, alt, speed, heading, squawk = feature

    # Nuevos criterios de detección
    if squawk == 7500:
        return "Spoofing"
    elif speed > 1000:
        return "DoS (Denegación de Servicio)"
    elif heading < 0 or heading > 360:
        return "Modificación de Mensajes"
    elif alt > 60000:
        return "Inyección de Mensajes"
    elif alt == 0 and speed == 0:
        return "Eliminación de Mensajes"
    elif squawk == 7600:
        return "Fallo de Comunicaciones"
    elif squawk == 7700:
        return "Emergencia General"
    else:
        return "Normal"

def log_anomaly(anomaly_id, error, risk, threat_type):
    """ Registra las anomalías detectadas en un archivo específico """
    with open(ANOMALIES_FILE, "a") as f:
        f.write(f"{anomaly_id}, {error:.4f}, {risk:.2f}%, {threat_type}\n")

def log_message(message):
    """ Registro detallado de cada mensaje procesado """
    with open(LOG_FILE, "a") as log:
        log.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

def evaluate_risk(speed, heading):
    """ Lógica difusa para evaluar el riesgo """
    # Reglas simples de evaluación
    if speed > 1000:
        return 90.0
    elif heading < 0 or heading > 360:
        return 75.0
    elif speed > 500:
        return 60.0
    else:
        return 10.0

def main():
    # Iniciar captura en tiempo real
    threading.Thread(target=capture_realtime_data, daemon=True).start()

    while True:
        with lock:
            messages = adsb_messages.copy()
            adsb_messages.clear()

        features = extract_features(messages)
        if len(features) == 0:
            time.sleep(5)
            continue

        scaler = MinMaxScaler()
        scaled_data = scaler.fit_transform(features)
        X = scaled_data.reshape((scaled_data.shape[0], 1, scaled_data.shape[1]))

        model = build_lstm_model((1, X.shape[2]))
        model.fit(X, X, epochs=5, batch_size=32, validation_split=0.1)

        X_pred = model.predict(X)
        mse = np.mean(np.power(X - X_pred, 2), axis=(1, 2))
        threshold = 0.02

        for i, error in enumerate(mse):
            risk_level = evaluate_risk(features[i][3], features[i][4])
            threat_type = classify_anomaly(features[i])

            # Registro detallado del mensaje procesado
            log_message(f"Mensaje {i+1}: Error: {error:.4f}, Riesgo: {risk_level:.2f}%, Tipo: {threat_type}")

            # Si es anomalía, registrarla en anomalies_report.txt
            if threat_type != "Normal":
                log_anomaly(i + 1, error, risk_level, threat_type)

        time.sleep(5)

if __name__ == "__main__":
    main()
