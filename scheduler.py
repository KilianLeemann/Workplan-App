# scheduler.py

import pandas as pd
from person import Person
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import random

class Scheduler:
    """
    This class transforms a table of availability into one or more work schedules.
    It also provides methods to create a visual representation and export each schedule to Excel.
    """

    def __init__(self, df):
        """
        Initialize the Scheduler instance.

        Parameters:
        - df (pd.DataFrame): A table where each row represents one person.
          Columns include the person's name, their availability for each day/time slot,
          and the maximum number of hours (or blocks) they can work.
        """
        # Store the provided table in an internal variable
        self.df = df

        # This list will hold Person objects after parsing availability
        self.persons = []

        # Define the weekdays that will appear in the schedule (Monday through Friday)
        self.days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']

        # Define the time slots for each of those days
        self.times = ['10-12', '12-14', '14-16', '16-18']

        # Create a complete list of all (day, time) combinations
        # For example: ('Montag', '10-12'), ('Montag', '12-14'), ..., ('Freitag', '16-18')
        self.blocks = [(day, time) for day in self.days for time in self.times]

    def parse_availability(self):
        """
        Convert each row of the DataFrame into a Person object.

        For each row (each person):
          1. Retrieve the name from the "Name" column. If "Name" is missing, use the first column.
          2. Build a dictionary of availability: each (day, time) maps to the person's availability value.
             The DataFrame is assumed to list these availability values in the columns immediately after the name,
             in the order of self.days and self.times.
          3. Read the final column as max_blocks (the maximum number of hours or blocks this person can work).
          4. Create a Person object using name, availability dictionary, and max_blocks.
             Add this Person to the internal list self.persons.
        """
        for _, row in self.df.iterrows():
            # 1. Get the person's name; fallback to the first column if "Name" is not present.
            name = row.get("Name", row[row.index[0]])

            # 2. Build the availability dictionary.
            #    The availability values are taken in the exact order of self.days and self.times.
            availability = {}
            idx = 1  # Start from the second column (index 1) since index 0 is the name
            for day in self.days:
                for time in self.times:
                    availability[(day, time)] = row.iloc[idx]
                    idx += 1

            # 3. The last column of the row indicates the maximum hours (or blocks) this person can work.
            max_blocks = row.iloc[-1]

            # 4. Instantiate a Person and add to the list.
            self.persons.append(Person(name, availability, max_blocks))

    def generate_plans(self, num_plans=3):
        """
        Produce a specified number of scheduling proposals.

        Each proposal follows these steps:
          a) Clear previously assigned blocks for every Person in self.persons.
          b) Call an internal helper to build a single plan, passing a seed for reproducible randomness.
          c) Collect each generated plan (as a DataFrame) in a list.

        Returns:
        - A list of DataFrames; each DataFrame represents one possible work schedule.
        """
        plans = []

        for i in range(num_plans):
            # a) Reset all assigned blocks before starting a new plan
            for person in self.persons:
                person.reset_blocks()

            # b) Generate one schedule, using the index i as a random seed
            plans.append(self._generate_single_plan(seed=i))

        return plans

    def _generate_single_plan(self, seed=None):
        """
        Build one schedule (plan) of assignments.

        Steps in detail:
          1. If a seed is provided, set it for the random number generator.
          2. Create an empty structure `slots` that will map each (day, time) to a list of assigned names.
          3. Sort persons by the number of slots they can work (descending), then shuffle to mix order.
          4. Define a helper function assign_blocks(priority_level) that:
             - Iterates over every (day, time) block in self.blocks.
             - For each block, determines how many people are needed (2 for '10-12', otherwise 3).
             - Skips blocks that already have enough people assigned.
             - Finds persons whose availability for that block equals the priority_level,
               who have enough remaining hours, and who are available (can_receive_block).
             - Orders those candidates to avoid gap sequences, minimize assigned hours, and maximize remaining availability.
             - Assigns up to the needed number of persons for that block.
          5. Call assign_blocks for priority levels 3, then 2, then 1 (highest availability first).
          6. For any person who still has capacity and enough overall availability:
             - Offer additional blocks in day/time order (Monday 10-12 → Friday 16-18),
               subject to gap-sequence checks and capacity.
          7. For any remaining free blocks (not fully staffed), fill them with whichever available persons remain,
             respecting their capacity and gap rules.
          8. After all assignments, build a list of dictionaries (plan_data) with one entry per assigned (day, time, person).
          9. Compute total hours per person (each block = 2 hours).
         10. Create a DataFrame from plan_data and include a column "Hours" with each person’s total hours.
         11. Return this final DataFrame representing the single plan.
        """
        if seed is not None:
            random.seed(seed)

        # 2. Initialize the slots structure so that each (day, time) maps to an empty list of names
        slots = defaultdict(list)
        for block in self.blocks:
            slots[block] = []

        # 3. Sort persons by how many blocks they can work (descending), then shuffle to mix priorities
        persons_sorted = sorted(self.persons, key=lambda p: -p.available_blocks_count())
        random.shuffle(persons_sorted)

        # 4. Define the helper to assign blocks at a given availability level
        def assign_blocks(priority_level):
            for block in self.blocks:
                # Determine how many people are required for this block:
                #   - If the time is '10-12', exactly 2 people are needed.
                #   - Otherwise, 3 people are needed.
                needed = 2 if block[1] == '10-12' else 3

                # Skip if block already has enough people
                if len(slots[block]) >= needed:
                    continue

                # Find persons matching the criteria:
                #   a) wants_block(block) == priority_level
                #   b) assigned_hours + 2 <= max_blocks (enough capacity)
                #   c) can_receive_block(block) (actually available for that slot)
                eligible = [
                    p for p in persons_sorted
                    if p.wants_block(block) == priority_level
                    and p.assigned_hours() + 2 <= p.max_blocks
                    and p.can_receive_block(block)
                ]

                # Sort eligible persons to avoid creating gaps in a single day, then minimize assigned hours,
                # and finally prefer those with fewer total availability remaining.
                eligible.sort(key=lambda p: (
                    # 0 if a block already assigned on that day, else 1 (prefer no-day-gap)
                    0 if any(d == block[0] for d, t in p.assigned_blocks) else 1,
                    # Fewer assigned hours first
                    p.assigned_hours(),
                    # More remaining availability first (negative means more)
                    -p.available_blocks_count()
                ))

                # Assign up to the needed number of persons for this block
                for p in eligible:
                    if len(slots[block]) < needed:
                        # Skip if assigning this block would create a gap sequence
                        if self._would_create_gap_sequence(p, block):
                            continue
                        p.add_block(block)
                        slots[block].append(p.name)

        # 5. First pass: assign blocks for priority levels 3, then 2, then 1
        for level in [3, 2, 1]:
            assign_blocks(level)

        # 6. Second pass: ensure that any person with high overall availability (5+ blocks)
        #    and fewer than 8 assigned hours gets extra blocks in chronological order
        for p in persons_sorted:
            if p.available_blocks_count() >= 5 and p.assigned_hours() < 8:
                # List all blocks that the person can take and is not yet assigned
                additional_blocks = [
                    block for block in self.blocks
                    if p.can_receive_block(block) and p.name not in slots[block]
                ]
                # Sort by day, then by time order
                additional_blocks.sort(key=lambda x: (x[0], self.times.index(x[1])))

                for block in additional_blocks:
                    needed = 2 if block[1] == '10-12' else 3
                    if len(slots[block]) < needed and p.assigned_hours() + 2 <= p.max_blocks:
                        if self._would_create_gap_sequence(p, block):
                            continue
                        p.add_block(block)
                        slots[block].append(p.name)

        # 7. Third pass: fill any remaining free slots regardless of priority,
        #    choosing among those with capacity and availability
        free_blocks = [
            block for block in self.blocks
            if len(slots[block]) < (2 if block[1] == '10-12' else 3)
        ]
        for block in free_blocks:
            needed = 2 if block[1] == '10-12' else 3
            if len(slots[block]) >= needed:
                continue

            eligible = [
                p for p in persons_sorted
                if p.can_receive_block(block) and p.assigned_hours() + 2 <= p.max_blocks
            ]
            eligible.sort(key=lambda p: (
                # 0 if a block already assigned on that day, else 1
                0 if any(d == block[0] for d, t in p.assigned_blocks) else 1,
                # prefer those with less remaining availability (negative reversed)
                -p.available_blocks_count(),
                # fewer assigned hours first
                p.assigned_hours()
            ))
            for p in eligible:
                if len(slots[block]) < needed:
                    if self._would_create_gap_sequence(p, block):
                        continue
                    p.add_block(block)
                    slots[block].append(p.name)

        # 8. Build a list of assigned entries: each entry is a dictionary with 'Day', 'Time', and 'Person'
        plan_data = []
        for block in self.blocks:
            for person_name in slots[block]:
                plan_data.append({
                    'Day': block[0],
                    'Time': block[1],
                    'Person': person_name
                })

        # 9. Calculate total hours per person (each block adds 2 hours)
        block_hours = {'10-12': 2, '12-14': 2, '14-16': 2, '16-18': 2}
        hours_per_person = defaultdict(int)
        for entry in plan_data:
            hours_per_person[entry['Person']] += block_hours[entry['Time']]

        # 10. Create a DataFrame from plan_data and add a column "Hours"
        df = pd.DataFrame(plan_data)
        df["Hours"] = df["Person"].map(hours_per_person)

        # 11. Return the completed schedule DataFrame
        return df

    def _would_create_gap_sequence(self, person, new_block):
        """
        Check whether assigning new_block to the person would create a “gap” on that same day.

        A gap sequence means that the person would have an assigned slot in the morning and another
        in the afternoon but no slot in between, even though they are available in that middle slot.
        This method returns True if the new assignment would introduce such a gap.

        Steps:
          1. List all time slots on new_block’s day where the person is available (availability >= 1).
          2. If fewer than 3 slots are available on that day, no gap is possible → return False.
          3. Collect all currently assigned times on that day (from person.assigned_blocks).
          4. Add new_block’s time to that list, then sort by the order in self.times.
          5. If any time between the first and last assigned time is available but not assigned → return True.
          6. Otherwise → return False.
        """
        day, time = new_block
        # 1. Find all times on that day where the person’s availability >= 1
        available = [
            t for t in self.times
            if person.availability.get((day, t), 0) >= 1
        ]
        # 2. If fewer than 3 slots are available on that day, no risk of a gap
        if len(available) < 3:
            return False

        # 3. List currently assigned times on that day
        assigned = [t for d, t in person.assigned_blocks if d == day]

        # 4. Combine assigned times with the potential new time, then sort
        test_blocks = sorted(set(assigned + [time]), key=self.times.index)

        # 5. Check for any “gap” between the earliest and latest assigned slot
        first_idx = min(self.times.index(t) for t in test_blocks)
        last_idx = max(self.times.index(t) for t in test_blocks)
        for idx in range(first_idx, last_idx + 1):
            t = self.times[idx]
            if t in available and t not in test_blocks:
                # A gap is found: available but not assigned
                return True

        # 6. No gap detected
        return False

    def visualize_plan(self, plan_df, filename="plan.png"):
        """
        Create and save a heatmap visualization of the schedule.

        Steps:
          1. If the plan DataFrame is empty, print a message and return immediately.
          2. Add a "Block" column combining Day and Time (e.g., "Montag 10-12").
          3. Define the order of all possible "Block" labels so that columns line up correctly.
          4. Convert the "Block" column to a categorical type with that full order.
          5. Pivot the table so each row is a Person, each column is a Block, and values count assignments (0 or 1).
          6. Add a "Total Hours" column so that total assigned hours appear at the end of each row.
          7. Draw a heatmap with seaborn, using color to show assigned slots.
             - Vertical lines highlight day boundaries.
             - The "Total Hours" value is drawn as text at the end of each row.
          8. Save the figure to the given filename.
        """
        # 1. If no assignments exist, indicate that no plan is available for visualization
        if plan_df.empty:
            print("Kein Plan zum Visualisieren.")
            return

        # 2. Combine Day and Time into a single string called "Block"
        plan_df["Block"] = plan_df["Day"] + " " + plan_df["Time"]

        # 3. Define the full order of possible Block labels (Monday 10-12 → Friday 16-18)
        day_order = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']
        time_order = ['10-12', '12-14', '14-16', '16-18']
        full_order = [f"{day} {time}" for day in day_order for time in time_order]

        # 4. Convert "Block" column to categorical type with the specified order
        plan_df["Block"] = pd.Categorical(plan_df["Block"], categories=full_order, ordered=True)

        # 5. Pivot so each row is a Person, each column is a Block, and values count assignments (0 or 1)
        pivot = plan_df.pivot_table(
            index="Person",
            columns="Block",
            aggfunc="size",
            fill_value=0
        )
        # Ensure that all columns appear in the correct order
        pivot = pivot.reindex(columns=full_order, fill_value=0)

        # 6. Add a "Total Hours" column using the first "Hours" entry for each person
        pivot["Total Hours"] = plan_df.groupby("Person")["Hours"].first()

        # 7. Draw the heatmap
        plt.figure(figsize=(len(full_order) * 0.6, len(pivot) * 0.5 + 1))
        ax = sns.heatmap(
            pivot.drop(columns=["Total Hours"]),  # Exclude the Total Hours from the colored grid
            cmap="YlGnBu",                         # Color palette
            linewidths=0.5,
            linecolor='gray',
            cbar=False
        )

        # Draw thicker vertical lines every 4 columns to separate days
        for i in range(4, len(full_order), 4):
            ax.axvline(i, color='black', linewidth=2)

        # 7b. Draw each person's total hours to the right of their row
        for y, person in enumerate(pivot.index):
            ax.text(
                len(full_order) + 0.5,
                y + 0.5,
                f"{pivot.loc[person, 'Total Hours']} h",
                va='center',
                ha='left',
                fontsize=10,
                fontweight='bold'
            )

        plt.title("Visualisierung Arbeitsplan")
        plt.xlabel("Zeitblöcke")
        plt.ylabel("Mitarbeitende")
        plt.xticks(rotation=90)
        plt.tight_layout()

        # 8. Save and close the figure
        plt.savefig(filename)
        plt.close()
        print(f"Visualisierung gespeichert als: {filename}")

    def export_excel(self, plan_df, filename):
        """
        Export the schedule into an Excel file in a pivoted format.

        Steps:
          1. Add a "Block" column by combining Day and Time.
          2. Pivot so that each row is a Person, each column is a Block, and cells show assignment counts (0 or 1).
          3. Add a "Total Hours" column summing the hours for each person.
          4. Reset the index so that "Person" becomes a regular column again.
          5. Write the resulting table to the specified Excel file.
        """
        # 1. Combine Day and Time for each row
        plan_df["Block"] = plan_df["Day"] + " " + plan_df["Time"]

        # 2. Pivot to count how many times each person appears in each block
        pivot = plan_df.pivot_table(
            index="Person",
            columns="Block",
            aggfunc="size",
            fill_value=0
        )

        # 3. Add "Total Hours" by summing the "Hours" column for each person
        pivot["Total Hours"] = plan_df.groupby("Person")["Hours"].first()

        # 4. Reset index so "Person" becomes a column again
        pivot.reset_index().to_excel(filename, index=False)

        # 5. Indicate that the Excel file was created successfully
        print(f"Excel exportiert als: {filename}")
