import time
import random
import os
import csv
import requests
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Workspace System Parameters Configuration [cite: 1182]
THINGSPEAK_WRITE_TOKEN = "YOUR_THINGSPEAK_WRITE_KEY" 
DATA_LOG_PATH = os.path.join("data", "agriculture_sensor_logs.csv")
PLOT_GRAPH_PATH = os.path.join("outputs", "crop_microclimate_trends.png")

def evaluate_irrigation_logic(soil_val, temp_val):
    """Executes dynamic boundary rule auditing for automated water deployment[cite: 1057, 1058]."""
    if soil_val < 30.0:  # Critical volumetric saturation drop point [cite: 1144]
        return "ACTIVE", "CRITICAL: Low soil moisture detected. Activating water pump."
    elif temp_val > 38.0: # Thermal threshold overload parameter [cite: 1145]
        return "ACTIVE", "CAUTION: Thermal ceiling overrun. Running cooling pump."
    else:
        return "INACTIVE", "Normal environmental profile. Pump on standby."

def run_agri_simulation_pipeline(steps=12):
    """Simulates real-world microclimatic environmental cycles across farming zones."""
    print("[SYSTEM] Booting Virtual Crop Microclimate Telemetry Core Framework...")
    
    if not os.path.exists("data"): os.makedirs("data")
    if not os.path.exists("outputs"): os.makedirs("outputs")

    csv_headers = ["Timestamp", "Soil_Moisture_Pct", "Temperature_C", "Humidity_Pct", "Light_Intensity_Lux", "Pump_State", "Diagnostic_Msg"]
    if not os.path.exists(DATA_LOG_PATH):
        with open(DATA_LOG_PATH, mode='w', newline='') as file:
            csv.writer(file).writerow(csv_headers)

    # Simulated microclimate environmental states [cite: 1143]
    crop_scenarios = ["Optimal Baseline", "Arid Drought Stress", "Thermal Heatwave Overrun", "Saturated Root Hydration"]

    for step in range(1, steps + 1):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        active_scenario = crop_scenarios[(step - 1) % len(crop_scenarios)]
        
        print(f"\n--- Data Point: {step}/{steps} | Active Microclimate Zone: {active_scenario} ---")

        # Generate target matrix paths based on the active environmental scenario
        if active_scenario == "Optimal Baseline":
            soil_moisture = random.uniform(45.0, 65.0)
            temp = random.uniform(24.0, 28.0)
            humidity = random.uniform(55.0, 65.0)
            light_lux = random.uniform(4000, 6000)
        elif active_scenario == "Arid Drought Stress":
            soil_moisture = random.uniform(15.0, 28.0)  # Trigger water pump [cite: 1144]
            temp = random.uniform(29.0, 33.0)
            humidity = random.uniform(40.0, 50.0)
            light_lux = random.uniform(7000, 9500)
        elif active_scenario == "Thermal Heatwave Overrun":
            soil_moisture = random.uniform(35.0, 45.0)
            temp = random.uniform(39.2, 44.5)           # Trigger cooling pump [cite: 1145]
            humidity = random.uniform(25.0, 35.0)
            light_lux = random.uniform(10000, 12000)
        else: # Saturated Root Hydration
            soil_moisture = random.uniform(75.0, 90.0)
            temp = random.uniform(22.0, 25.0)
            humidity = random.uniform(70.0, 85.0)
            light_lux = random.uniform(1500, 3000)

        pump_status, alert_log = evaluate_irrigation_logic(soil_moisture, temp)
        print(f"[{timestamp}] Sensors -> Soil Moisture: {soil_moisture:.1f}% | Temp: {temp:.1f}°C | Humid: {humidity:.1f}%")
        print(f"[{timestamp}] Edge Output -> System Alert Level: {alert_log} [Pump: {pump_status}]")

        # Save record log step cleanly to disk telemetry ledger [cite: 1132, 1150]
        with open(DATA_LOG_PATH, mode='a', newline='') as file:
            csv.writer(file).writerow([timestamp, f"{soil_moisture:.1f}", f"{temp:.1f}", f"{humidity:.1f}", f"{light_lux:.0f}", pump_status, alert_log])

        # Synchronize live telemetry streams directly to the ThingSpeak Cloud via HTTP POST [cite: 1130]
        if THINGSPEAK_WRITE_TOKEN != "YOUR_THINGSPEAK_WRITE_KEY":
            try:
                endpoint_url = f"https://api.thingspeak.com/update?api_key={THINGSPEAK_WRITE_TOKEN}"
                payload = {
                    "field1": f"{soil_moisture:.1f}",
                    "field2": f"{temp:.1f}",
                    "field3": f"{humidity:.1f}",
                    "field4": f"{light_lux:.0f}",
                    "field5": "1.0" if pump_status == "ACTIVE" else "0.0",
                    "status": f"Zone Profile: {active_scenario}"
                }
                response = requests.post(endpoint_url, data=payload, timeout=5)
                if response.status_code == 200 and response.text != "0":
                    print("[CLOUD] Cloud synchronization complete. Visual panels updated.")
            except Exception as ex:
                print(f"[CLOUD] Transmission interface error loop: {ex}")
        else:
            print("[CLOUD] Notice: Remote streaming bypassed. Insert valid Write Channel key token.")

        if step < steps:
            print("[SYSTEM] Waiting 15 seconds to ensure clean communication windows...")
            time.sleep(15)

def generate_crop_historical_plots():
    """Generates detailed analytical plots to cross-examine microclimate variations[cite: 1133]."""
    if not os.path.exists(DATA_LOG_PATH): return
    df = pd.read_csv(DATA_LOG_PATH)
    if df.empty: return

    # Construct the comparative plot visualization dashboard
    fig, ax1 = plt.subplots(figsize=(10, 5))

    ax1.set_xlabel("Recorded Timeline Instants")
    ax1.set_ylabel("Soil Volumetric Saturation (%)", color="teal")
    ax1.plot(df["Timestamp"], df["Soil_Moisture_Pct"], marker='o', color="teal", linewidth=2, label="Soil Moisture")
    ax1.tick_params(axis='y', labelcolor="teal")
    ax1.axhline(y=30, color="red", linestyle="--", alpha=0.6, label="Critical Wilting Ceiling")
    
    ax2 = ax1.twinx()
    ax2.set_ylabel("Ambient Heat Temperature (°C)", color="crimson")
    ax2.plot(df["Timestamp"], df["Temperature_C"], marker='s', color="crimson", linewidth=1.5, linestyle=":", label="Air Temp")
    ax2.tick_params(axis='y', labelcolor="crimson")

    plt.title("Crop Matrix Microclimatic Profile & Adaptive Irrigation Analysis", fontsize=12, fontweight='bold')
    fig.tight_layout()
    plt.savefig(PLOT_GRAPH_PATH, dpi=300)
    plt.close()
    print(f"[VISUALIZATION] Microclimate plot exported successfully: {PLOT_GRAPH_PATH}")

if __name__ == "__main__":
    run_agri_simulation_pipeline(cycles=4)
    generate_crop_historical_plots()