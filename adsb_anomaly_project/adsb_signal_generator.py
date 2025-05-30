#!/usr/bin/env python3

import numpy as np
import random

# Archivo de salida
OUTPUT_FILE = "adsb_synthetic_signal.bin"
SAMPLE_RATE = 130e6  # Frecuencia de muestreo
DURATION = 10  # Duración en segundos

def generate_message():
    """ Genera un mensaje ADS-B con etiquetas sospechosas """
    messages = {
        "Spoofing": "8D40621D58C382D67500AC2863A7",
        "TEST1235": "8D4FA0B123456789ABCDEF123456",
        "FAKE123": "8D1A2B3C12345678901234567890"
    }
    return random.choice(list(messages.items()))

def message_to_signal(message):
    """ Convierte un mensaje en una señal de bits """
    signal = []
    for char in message:
        bits = bin(int(char, 16))[2:].zfill(4)
        for bit in bits:
            value = 1 if bit == "1" else -1
            signal.extend([value] * int(SAMPLE_RATE / 1e6))
    return np.array(signal, dtype=np.float32)

def main():
    samples = []
    print("[INFO] Generando señales ADS-B sintéticas...")
    for _ in range(100):
        msg, label = generate_message()
        signal = message_to_signal(msg)
        samples.extend(signal)
        print(f"[INFO] Generando mensaje {label}: {msg}")
    
    # Guardar la señal en un archivo binario
    with open(OUTPUT_FILE, "wb") as f:
        np.array(samples, dtype=np.float32).tofile(f)

    print(f"[INFO] Señal guardada en {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
