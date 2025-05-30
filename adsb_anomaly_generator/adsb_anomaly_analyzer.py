import os
from datetime import datetime

ANALYSIS_FILE = "analysis_report.txt"

def log_anomaly(timestamp, flight_id, anomaly_type):
    """
    Registra las anomalías detectadas en un formato alineado y estructurado.
    """
    header = (
        "Análisis de Anomalías ADS-B\n"
        "==================================================\n"
        "Timestamp         Flight ID        Anomalía Detectada\n"
        "==================================================\n"
    )

    # Formatear la línea de salida con alineación específica
    log_entry = f"{timestamp:<17} {flight_id:<15} {anomaly_type}\n"

    # Verificar si el archivo ya existe y si está vacío
    file_exists = os.path.exists(ANALYSIS_FILE)

    # Escribir el encabezado solo si el archivo no existe o está vacío
    if not file_exists or os.path.getsize(ANALYSIS_FILE) == 0:
        with open(ANALYSIS_FILE, "w") as file:
            file.write(header)

    # Agregar la entrada de anomalía al archivo
    with open(ANALYSIS_FILE, "a") as file:
        file.write(log_entry)


def analyze_adsb_message(message):
    """
    Analiza un mensaje ADS-B y detecta anomalías.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    # Ejemplo de datos simulados (puedes reemplazarlos con los mensajes reales)
    anomalies = [
        {"flight_id": "TEST1234", "type": "Spoofing (Flight ID: TEST1234)"},
        {"flight_id": "UNKNOWN", "type": "Velocidad Excesiva: 950 knots"},
        {"flight_id": "UNKNOWN", "type": "Altitud Excesiva: 61000 ft"},
    ]

    for anomaly in anomalies:
        log_anomaly(timestamp, anomaly["flight_id"], anomaly["type"])


def simulate_adsb_messages():
    """
    Simula mensajes ADS-B para pruebas.
    """
    print("[INFO] Iniciando el análisis de señales ADS-B...")
    simulated_messages = [
        "8D000000990001322004001200C5",
        "8D000000205054D4C72CF474FA15",
        "8D00000058B98000000000466BFB"
    ]

    for message in simulated_messages:
        print(f"[DEBUG] Mensaje capturado: {message}")
        analyze_adsb_message(message)


if __name__ == "__main__":
    simulate_adsb_messages()

