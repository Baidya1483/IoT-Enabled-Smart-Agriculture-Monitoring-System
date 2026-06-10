from python_simulation.agri_simulator import run_agri_simulation_pipeline, generate_crop_historical_plots

def main():
    print("======================================================================")
    print("   IoT-ENABLED SMART AGRICULTURE MONITORING PIPELINE SYSTEM ENGINE   ")
    print("======================================================================\n")
    
    # Run a four-cycle structural verification trace matching placement criteria
    run_agri_simulation_pipeline(steps=4)
    generate_crop_historical_plots()
    
    print("\n[COMPLETE] Agricultural simulation telemetry processing loop completed.")

if __name__ == "__main__":
    main()