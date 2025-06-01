# main.py

from scheduler import Scheduler
import pandas as pd

if __name__ == "__main__":
    # Load availability data from an Excel file.
    # We assume the first sheet is named "Tabelle1" and that the actual data starts on row 2,
    # so header=1 skips the first row of metadata. Adjust as needed if your file structure changes.
    availability_df = pd.read_excel("Availability.xlsx", sheet_name="Tabelle1", header=1)
    
    # Strip any leading/trailing whitespace from column names to avoid mismatches.
    availability_df.columns = availability_df.columns.str.strip()
    
    # Rename the first column to "Name" (it likely contains employee names).
    availability_df.rename(columns={availability_df.columns[0]: "Name"}, inplace=True)

    # Initialize the Scheduler with the DataFrame of availability.
    # The Scheduler class will parse this DataFrame and build Person objects internally.
    scheduler = Scheduler(availability_df)
    
    # Parse the availability DataFrame to create internal Person instances
    # and populate each Person’s availability structure.
    scheduler.parse_availability()

    # Generate a specified number of scheduling proposals. In this case, 3 different plans.
    # Each "plan" is typically represented as a DataFrame or similar structure.
    plans = scheduler.generate_plans(num_plans=3)

    # Iterate through all generated plans and export each to both a PNG (visualization)
    # and an Excel file (pivoted, showing who is assigned to which block).
    for idx, plan in enumerate(plans):
        filename = f"Arbeitsplan_Vorschlag_{idx+1}"

        # Create and save a visual chart of the schedule (e.g., a heatmap or bar chart).
        scheduler.visualize_plan(plan, filename=f"{filename}.png")

        # Export the plan to an Excel file. This method pivots the data so that
        # each employee appears as a row and each time block is a column.
        scheduler.export_excel(plan.copy(), filename=f"{filename}.xlsx")

    print("Planerstellung abgeschlossen.")  # Indicates that scheduling is complete.
