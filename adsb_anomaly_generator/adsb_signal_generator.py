# adsb_signal_generator.py

import time
import random
import struct
import os

# Directorio para guardar los logs y señales generadas
LOG_DIR = "./logs"
SIGNAL_FILE = os.path.join(LOG_DIR, "generated_signals.bin")
ANOMALY_LOG = os.path.join(LOG_DIR, "anomaly_log.txt")

# Crear directorios si no existen
os.makedirs(LOG_DIR, exist_ok=True)

def log_anomaly(anomaly_type, flight_id, details):
    with open(ANOMALY_LOG, "a") as log_file:
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_file.write(f"{timestamp} - [ANOMALY] {anomaly_type} - Flight ID: {flight_id} - {details}\n")
        print(f"[LOG] {timestamp} - {anomaly_type} - {flight_id} - {details}")

def generate_adsb_message(flight_id, altitude, speed, heading, anomaly_type="Normal"):
    # Generar un mensaje ADS-B sintético (28 caracteres hexadecimales)
    # Estructura básica: Hex (6) + Altitud (6) + Velocidad (6) + Heading (4) + Tipo de mensaje (6)
    hex_code = f"8D{flight_id:06X}"
    alt_code = f"{altitude:06X}"
    speed_code = f"{speed:04X}"
    heading_code = f"{heading:04X}"
    msg_type = "40C3" if anomaly_type == "Normal" else "66FB"  # "66FB" indica un mensaje anómalo

    # Mensaje completo
    adsb_message = f"{hex_code}{alt_code}{speed_code}{heading_code}{msg_type}"
    return adsb_message

def generate_attack_scenario():
    """
    Genera diferentes tipos de ataques cibernéticos ADS-B.
    """
    scenarios = [
        {"type": "Spoofing", "flight_id": "123456", "altitude": 35000, "speed": 450, "heading": 90},
        {"type": "Injection", "flight_id": "654321", "altitude": 10000, "speed": 300, "heading": 180},
        {"type": "Malformed", "flight_id": "000000", "altitude": 99999, "speed": 999, "heading": 999},
    ]

    selected = random.choice(scenarios)
    log_anomaly(selected["type"], selected["flight_id"], f"Altitude: {selected['altitude']}, Speed: {selected['speed']}, Heading: {selected['heading']}")

    return generate_adsb_message(
        flight_id=int(selected["flight_id"]),
        altitude=selected["altitude"],
        speed=selected["speed"],
        heading=selected["heading"],
        anomaly_type=selected["type"]
    )

def main():
    print("[INFO] Iniciando generador de señales ADS-B con anomalías...")
    
    with open(SIGNAL_FILE, "wb") as signal_file:
        while True:
            # Generar mensaje normal
            normal_message = generate_adsb_message(flight_id=random.randint(1, 999999), altitude=30000, speed=400, heading=270)
            signal_file.write(normal_message.encode('utf-8'))
            
            # Generar un ataque cada 5 mensajes normales
            if random.randint(1, 5) == 3:
                attack_message = generate_attack_scenario()
                signal_file.write(attack_message.encode('utf-8'))
            
            signal_file.flush()
            time.sleep(1)  # Simular tráfico ADS-B

if __name__ == "__main__":
    main()

