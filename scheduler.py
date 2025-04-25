# scheduler.py
import pandas as pd
from person import Person
from collections import defaultdict

class Scheduler:
    def __init__(self, df):
        self.df = df
        self.persons = []
        self.days = ['Montag', 'Dienstag', 'Mittwoch', 'Donnerstag', 'Freitag']
        self.times = ['10-12', '12-14', '14-16', '16-18']
        self.blocks = [(day, time) for day in self.days for time in self.times]
        self.plan = []

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
        return [self._generate_single_plan() for _ in range(num_plans)]

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
                    if self._creates_gap(p, block):
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

    def _creates_gap(self, person, new_block):
        day_blocks = [t for t in self.times if person.availability.get((new_block[0], t), 0) >= 1]
        if len(day_blocks) < 3:
            return False

        person_blocks = [t for d, t in person.assigned_blocks if d == new_block[0]]
        test_blocks = person_blocks + [new_block[1]]
        test_blocks_sorted = sorted(set(test_blocks), key=self.times.index)

        for i in range(1, len(test_blocks_sorted) - 1):
            prev = test_blocks_sorted[i - 1]
            next_ = test_blocks_sorted[i + 1]
            if self.times.index(next_) - self.times.index(prev) == 2:
                mid = self.times[self.times.index(prev) + 1]
                if mid not in test_blocks_sorted:
                    return True
        return False
