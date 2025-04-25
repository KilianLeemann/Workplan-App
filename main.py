# main.py
from scheduler import Scheduler
import pandas as pd

if __name__ == "__main__":
    # Load the availability Excel
    availability_df = pd.read_excel("/Users/kilianleemann/Documents/HSG/Master/MLE/3_Semester/Programming with Advanced Computer Languages/Project/hsg-workplanapp/Bidding Vorlage.xlsx", sheet_name="Tabelle1", header=1)
    
    # ist nur für den Test
    availability_df.columns = availability_df.columns.str.strip()  # säubert Leerzeichen
    print("Spalten:", availability_df.columns.tolist())
    
    '''
    # Clean column names from invisible characters
    availability_df.columns = availability_df.columns.str.strip()

    # Debug: print available columns
    print("Spalten:", availability_df.columns.tolist())

    # Create Scheduler instance and process data
    scheduler = Scheduler(availability_df)
    scheduler.parse_availability()
    plans = scheduler.generate_plans(num_plans=3)

    # Export plans to Excel
    for idx, plan in enumerate(plans):
        plan.to_excel(f"Arbeitsplan_Vorschlag_{idx+1}.xlsx", index=False)

    print("3 Arbeitspläne wurden erfolgreich exportiert.")'''
