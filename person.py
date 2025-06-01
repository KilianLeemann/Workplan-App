# person.py

class Person:
    """
    Represents one person (an employee) including:
      - name (string)
      - availability for each time slot (dictionary mapping (day, time) to a number)
      - maximum number of slots that can be assigned (max_blocks)
      - list of slots that have been assigned (assigned_blocks)
    """

    def __init__(self, name, availability, max_blocks):
        """
        Initialize a Person instance.

        Parameters:
        - name (str): The person's name, for example "Alice".
        - availability (dict): Each key is a (day, time) tuple, and each value is a number (0 = unavailable, 1 or higher = available).
        - max_blocks (int): The maximum number of time slots this person may be assigned.
        """
        self.name = name
        self.availability = availability
        self.max_blocks = max_blocks
        # Start with no assigned slots
        self.assigned_blocks = []

    def reset_blocks(self):
        """
        Clear any previously assigned slots so that the person has none before a new scheduling attempt.
        """
        self.assigned_blocks = []

    def block_count(self):
        """
        Return the number of slots currently assigned to this person.
        """
        return len(self.assigned_blocks)

    def available_blocks_count(self, min_level=1):
        """
        Count how many slots are marked with availability >= min_level (default is 1).

        Parameters:
        - min_level (int): The minimum availability threshold (slots with availability below this are not counted).

        Returns:
        - int: The count of slots meeting or exceeding the threshold.
        """
        count = 0
        for level in self.availability.values():
            if level >= min_level:
                count += 1
        return count

    def can_receive_block(self, block):
        """
        Determine whether this person is available for the given slot.

        Parameters:
        - block (tuple): A (day, time) tuple, for example ("Monday", "10-12").

        Returns:
        - bool: True if availability for that slot is greater than zero.
        """
        return block in self.availability and self.availability[block] > 0

    def add_block(self, block):
        """
        Assign the specified slot to this person by adding it to assigned_blocks.
        """
        self.assigned_blocks.append(block)

    def wants_block(self, block):
        """
        Return the availability value for the given slot; 0 if the slot is not listed.

        Parameters:
        - block (tuple): A (day, time) tuple.

        Returns:
        - int: The availability level for that slot.
        """
        return self.availability.get(block, 0)

    def assigned_hours(self):
        """
        Calculate total hours assigned, assuming each time slot covers 2 hours:
          - "10-12" = 2 hours,
          - "12-14" = 2 hours, etc.

        Returns:
        - int: The sum of hours for all assigned slots.
        """
        hours_per_slot = {"10-12": 2, "12-14": 2, "14-16": 2, "16-18": 2}
        total = 0
        for day, time in self.assigned_blocks:
            total += hours_per_slot.get(time, 0)
        return total
