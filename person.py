# person.py

class Person:
    """
    Represents a single employee (or person) who can be assigned to work blocks.
    Each Person has:
      - a name (string)
      - a dictionary of availability, mapping (day, time) tuples to an integer "preference" or "availability level"
      - a maximum number of blocks they can work (max_blocks)
      - a list of blocks they've been assigned (assigned_blocks)
    """

    def __init__(self, name, availability, max_blocks):
        """
        Initialize a Person instance.

        Parameters:
        - name (str): The employee's name.
        - availability (dict): A mapping from (day, time) tuples to availability levels (e.g., 0 = unavailable, 1 or higher = available).
        - max_blocks (int): Maximum number of time blocks the person should be assigned in one schedule.
        """
        self.name = name
        self.availability = availability
        self.max_blocks = max_blocks
        self.assigned_blocks = []  # List of (day, time) tuples representing blocks assigned to this person.

    def reset_blocks(self):
        """
        Reset this person's assigned blocks.
        Call this before starting a fresh scheduling attempt to clear any prior assignments.
        """
        self.assigned_blocks = []

    def block_count(self):
        """
        Return the current number of blocks assigned to this person.
        """
        return len(self.assigned_blocks)

    def available_blocks_count(self, min_level=1):
        """
        Count how many blocks this person is willing to work, based on a minimum availability level.

        Parameters:
        - min_level (int): The minimum availability threshold (default is 1). Only blocks with availability >= min_level are counted.

        Returns:
        - int: Number of available blocks meeting the threshold.
        """
        return sum(1 for v in self.availability.values() if v >= min_level)

    def can_receive_block(self, block):
        """
        Check if this person is available (availability > 0) for the given block.

        Parameters:
        - block (tuple): A (day, time) tuple to check.

        Returns:
        - bool: True if the person can be assigned to that block.
        """
        return block in self.availability and self.availability[block] > 0

    def add_block(self, block):
        """
        Assign a block to this person by appending it to their assigned_blocks list.

        Parameters:
        - block (tuple): A (day, time) tuple that is being assigned to this person.
        """
        self.assigned_blocks.append(block)

    def wants_block(self, block):
        """
        Return how much this person "wants" or can handle a given block,
        typically based on their availability mapping.

        Parameters:
        - block (tuple): A (day, time) tuple.

        Returns:
        - int: The availability level for that block (0 if not present).
        """
        return self.availability.get(block, 0)

    def assigned_hours(self):
        """
        Calculate the total number of hours this person has been assigned,
        assuming each time block is 2 hours long for these specific slots.

        Returns:
        - int: Total assigned hours.
        """
        # Define the hours for each time block; here each block is 2 hours.
        block_hours = {'10-12': 2, '12-14': 2, '14-16': 2, '16-18': 2}
        # Sum the hours for each assigned block
        return sum(block_hours[time] for (day, time) in self.assigned_blocks)
