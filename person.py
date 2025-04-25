# person.py
class Person:
    def __init__(self, name, availability, max_blocks):
        self.name = name
        self.availability = availability
        self.max_blocks = max_blocks
        self.assigned_blocks = []

    def available_blocks_count(self, min_level=1):
        return sum(1 for v in self.availability.values() if v >= min_level)

    def can_receive_block(self, block):
        return block in self.availability and self.availability[block] > 0

    def add_block(self, block):
        self.assigned_blocks.append(block)

    def reset_blocks(self):
        self.assigned_blocks = []

    def block_count(self):
        return len(self.assigned_blocks)

    def wants_block(self, block):
        return self.availability.get(block, 0)
