# scheduler.py
import pandas as pd
from person import Person
from collections import defaultdict
import random

class Scheduler:
    def __init__(self, df):
        self.df = df
        self.persons = []
        self.blocks = [(day, time) for day in ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']
                       for time in ['10-12', '12-14', '14-16', '16-18']]
        self.plan = []

    def parse_availability(self):
        for _, row in self.df.iterrows():
            name = row['Name']
            availability = {}
            idx = 1
            for day in ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']:
                for time in ['10-12', '12-14', '14-16', '16-18']:
                    availability[(day, time)] = row.iloc[idx]
                    idx += 1
            max_blocks = row.iloc[-1]
            self.persons.append(Person(name, availability, max_blocks))

    def generate_plans(self, num_plans=3):
        return [self._generate_single_plan() for _ in range(num_plans)]

    def _generate_single_plan(self):
        # Basic greedy strategy for demo purposes
        plan = []
        slots = defaultdict(list)

        # initialize empty plan with 2/3 slots per block
        for block in self.blocks:
            needed = 2 if block[1] == '10-12' else 3
            slots[block] = []

        persons_sorted = sorted(self.persons, key=lambda p: -p.available_blocks_count())

        for block in self.blocks:
            eligible = [p for p in persons_sorted if p.can_receive_block(block)]
            eligible.sort(key=lambda p: (-p.wants_block(block), p.block_count()))
            for p in eligible:
                if len(slots[block]) < (2 if block[1] == '10-12' else 3):
                    if p.block_count() < p.max_blocks:
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
