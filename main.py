# main.py
from scheduler import Scheduler
import pandas as pd

if __name__ == "__main__":
    # Verfügbarkeiten laden
    availability_df = pd.read_excel("Availability.xlsx", sheet_name="Tabelle1", header=1)
    availability_df.columns = availability_df.columns.str.strip()
    availability_df.rename(columns={availability_df.columns[0]: "Name"}, inplace=True)

    # Scheduler initialisieren und Verfügbarkeiten einlesen
    scheduler = Scheduler(availability_df)
    scheduler.parse_availability()

    # Pläne generieren und exportieren
    plans = scheduler.generate_plans(num_plans=3)

    for idx, plan in enumerate(plans):
        filename = f"Arbeitsplan_Vorschlag_{idx+1}"

        # Visualisierung erzeugen
        scheduler.visualize_plan(plan, filename=f"{filename}.png")

        # Excel-Datei exportieren (mit Pivot-Format)
        scheduler.export_excel(plan.copy(), filename=f"{filename}.xlsx")

    print("Planerstellung abgeschlossen.")
