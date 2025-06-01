# main.py

from scheduler import Scheduler
import pandas as pd

if __name__ == "__main__":
    # Read an Excel file named "Availability.xlsx".
    # The sheet called "Tabelle1" is used, and the first row is skipped as it may contain a title.
    availability_df = pd.read_excel("Availability.xlsx", sheet_name="Tabelle1", header=1)
    
    # Remove any extra spaces around column names so that " Name " becomes "Name".
    availability_df.columns = availability_df.columns.str.strip()
    
    # Rename the first column to "Name", assuming it contains the names of the people.
    availability_df.rename(columns={availability_df.columns[0]: "Name"}, inplace=True)

    # Create a Scheduler object, providing the table of availability.
    scheduler = Scheduler(availability_df)
    
    # Convert each row of the table into a Person object, capturing availability details.
    scheduler.parse_availability()

    # Generate three different possible work schedules; each returned plan is a small table.
    plans = scheduler.generate_plans(num_plans=3)

    # For each generated plan:
    for idx, plan in enumerate(plans):
        # Form a filename like "Arbeitsplan_Vorschlag_1", "Arbeitsplan_Vorschlag_2", etc.
        filename = f"Arbeitsplan_Vorschlag_{idx+1}"

        # Create and save a picture (PNG) illustrating the schedule in a grid format.
        scheduler.visualize_plan(plan, filename=f"{filename}.png")

        # Save the schedule as an Excel file, with people as rows and time slots as columns.
        scheduler.export_excel(plan.copy(), filename=f"{filename}.xlsx")

    # Indicate that scheduling has finished.
    print("Planerstellung abgeschlossen.")
