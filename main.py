# main.py
from scheduler import Scheduler
import pandas as pd

if __name__ == "__main__":
    availability_df = pd.read_excel("Availability.xlsx", sheet_name="Tabelle1", header=1)
    availability_df.columns = availability_df.columns.str.strip()
    availability_df.rename(columns={availability_df.columns[0]: "Name"}, inplace=True)

    scheduler = Scheduler(availability_df)
    scheduler.parse_availability()
    plans = scheduler.generate_plans(num_plans=3)

    for idx, plan in enumerate(plans):
        filename = f"Arbeitsplan_Vorschlag_{idx+1}"
        plan.to_excel(f"{filename}.xlsx", index=False)
        scheduler.visualize_plan(plan, filename=f"{filename}.png")

    print("Planerstellung abgeschlossen.")
