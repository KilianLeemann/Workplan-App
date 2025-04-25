# scheduler.py
import pandas as pd
from person import Person
from collections import defaultdict
import matplotlib.pyplot as plt
import seaborn as sns

class Scheduler:
    def __init__(self, df):
        self.df = df
        self.persons = []
        self.days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']
        self.times = ['10-12', '12-14', '14-16', '16-18']
        self.blocks = [(day, time) for day in self.days for time in self.times]

    def parse_availability(self):
        for _, row in self.df.iterrows():
            name = row.get("Name", row[row.index[0]])
            availability = {}
            idx = 1
            for day in self.days:
                for time in self.times:
                    availability[(day, time)] = row.iloc[idx]
                    idx += 1
            max_blocks = row.iloc[-1]
            self.persons.append(Person(name, availability, max_blocks))

    def generate_plans(self, num_plans=3):
        plans = []
        for _ in range(num_plans):
            for person in self.persons:
                person.reset_blocks()
            plans.append(self._generate_single_plan())
        return plans

    def _generate_single_plan(self):
        plan = []
        slots = defaultdict(list)

        for block in self.blocks:
            needed = 2 if block[1] == '10-12' else 3
            slots[block] = []

        persons_sorted = sorted(self.persons, key=lambda p: -p.available_blocks_count())

        for block in self.blocks:
            eligible = [p for p in persons_sorted if p.can_receive_block(block)]
            eligible.sort(key=lambda p: (-p.wants_block(block), p.block_count()))
            for p in eligible:
                if len(slots[block]) < (2 if block[1] == '10-12' else 3) and p.block_count() < p.max_blocks:
                    if self._would_create_gap_sequence(p, block):
                        continue
                    p.add_block(block)
                    slots[block].append(p.name)

        plan_data = []
        for block in self.blocks:
            for person in slots[block]:
                plan_data.append({
                    'Day': block[0],
                    'Time': block[1],
                    'Person': person
                })

        return pd.DataFrame(plan_data)

    def _would_create_gap_sequence(self, person, new_block):
        day, time = new_block
        available = [t for t in self.times if person.availability.get((day, t), 0) >= 1]
        if len(available) < 3:
            return False

        assigned = [t for d, t in person.assigned_blocks if d == day]
        test_blocks = sorted(set(assigned + [time]), key=self.times.index)

        available_idx = [self.times.index(t) for t in available]
        first_idx = min(self.times.index(t) for t in test_blocks)
        last_idx = max(self.times.index(t) for t in test_blocks)

        for idx in range(first_idx, last_idx + 1):
            t = self.times[idx]
            if t in available and t not in test_blocks:
                return True
        return False

    def visualize_plan(self, plan_df, filename="plan.png"):
        if plan_df.empty:
            print("Kein Plan zum Visualisieren.")
            return

        plan_df["Block"] = plan_df["Day"] + " " + plan_df["Time"]

        # Sortier-Reihenfolge für Tage und Zeiten definieren
        day_order = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']
        time_order = ['10-12', '12-14', '14-16', '16-18']
        full_order = [f"{day} {time}" for day in day_order for time in time_order]

        plan_df["Block"] = pd.Categorical(plan_df["Block"], categories=full_order, ordered=True)

        # Pivot-Tabelle für Heatmap
        pivot = plan_df.pivot_table(index="Person", columns="Block", aggfunc="size", fill_value=0)
        pivot = pivot.reindex(columns=full_order, fill_value=0)

        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=(len(full_order) * 0.6, len(pivot) * 0.5 + 1))
        ax = sns.heatmap(pivot, cmap="YlGnBu", linewidths=0.5, linecolor='gray', cbar=False)

        # Fette vertikale Linien zur Trennung der Tage (nach je 4 Zeitslots)
        for i in range(4, len(full_order), 4):
            ax.axvline(i, color='black', linewidth=2)

        plt.title("Visualisierung Arbeitsplan")
        plt.xlabel("Zeitblöcke")
        plt.ylabel("Mitarbeitende")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"Visualisierung gespeichert als: {filename}")


