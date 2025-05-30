# ADS-B-Cybersecurity-Risk-Assesment
El presente proyecto tiene la finalidad de la identificación de los reisgos cibernéticos del sistema ADS-B. Donde finalmente se hicieron unas pruebas de laboratorio controladas en la didentificación de las vulnerabilidades del sistema.

# 🛰️ Detección de Vulnerabilidades en el Sistema ADS-B (Automatic Dependent Surveillance–Broadcast)

Este repositorio contiene el desarrollo de un sistema híbrido para la **detección de vulnerabilidades en señales ADS-B** en ambientes simulados y reales, utilizando técnicas de Machine Learning, detección basada en reglas y señales generadas con SDR.

---

## 📌 Objetivo

Detectar, clasificar y registrar **vulnerabilidades críticas** en mensajes ADS-B que podrían comprometer la seguridad operacional en entornos aeronáuticos, como:

- Inyección de mensajes (`Message Injection`)
- Spoofing GPS
- Eliminación y modificación de mensajes
- Repetición de señales (`Message Replay`)

---

## 🧠 Componentes del Proyecto

### `adsb_signal_generator.py`
Generador de señales ADS-B sintéticas, con posibilidad de inyectar mensajes vulnerables como spoofing, altitud irreal o velocidades extremas.

### `adsb_anomaly_detector.py`
Sistema de detección de vulnerabilidades en tiempo real desde `dump1090`, utilizando modelos LSTM, reglas fuzzy y clasificación basada en características del mensaje.

### `adsb_anomaly_analyzer.py`
Analiza mensajes simulados, detecta irregularidades y registra los eventos en archivos estructurados.

---

## 🚀 Scripts de Ejecución

- `start_generator.sh`: Inicia el generador de señales sintéticas.
- `start_analyzer.sh`: Ejecuta el analizador de mensajes simulados.
- `start_adsb_project.sh`: Integra `dump1090`, activa el entorno virtual y lanza el detector en producción.

---

## 📂 Requisitos

Instalar los siguientes paquetes (puede usarse `pip install -r requirements.txt`):

```txt
dump1090
numpy
scikit-learn
pyModeS
keras
tensorflow
scikit-fuzzy
