# main.py
from scheduler import Scheduler
import pandas as pd

if __name__ == "__main__":
    # Load the availability Excel
    availability_df = pd.read_excel("Bidding Vorlage.xlsx", sheet_name="Tabelle1", header=1)

    # Clean column names and rename first column
    availability_df.columns = availability_df.columns.str.strip()
    availability_df.rename(columns={availability_df.columns[0]: "Name"}, inplace=True)

    print("Spalten:", availability_df.columns.tolist())

    # Create Scheduler instance and process data
    scheduler = Scheduler(availability_df)
    scheduler.parse_availability()
    plans = scheduler.generate_plans(num_plans=3)

    # Export plans to Excel
    for idx, plan in enumerate(plans):
        plan.to_excel(f"Arbeitsplan_Vorschlag_{idx+1}.xlsx", index=False)

    print("3 Arbeitspläne wurden erfolgreich exportiert.")
