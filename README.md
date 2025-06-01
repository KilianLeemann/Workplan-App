# Workplan App
## Description

The Workplan App is designed to automatically generate a work schedule for a team of 10–12 employees responsible for two helpdesks. These helpdesks are open Monday through Friday from 10:00 AM to 6:00 PM. The working hours are divided into four 2-hour shifts: 10:00–12:00 (with 2 employees), and 12:00–14:00, 14:00–16:00, and 16:00–18:00 (with 3 employees each).

## Input: Employee Availability

Employees submit their availability in an Excel file named `Availability.xlsx`. Availability is expressed using a numerical preference system. Each employee may mark **a maximum of four shifts** with a 3 (highest preference), to ensure fairness across the team:  
A **3** means “I would most like to work this shift,”  
a **2** means “I would like to work this shift,”  
a **1** means “I could work if no one else is available,”  
and a **0** means the employee is not available at that time.  
The Excel file must be located in the same directory as the Python project.

## Functionality

The program processes the availability information and generates a work schedule that covers all required shifts, takes preferences into account as much as possible, and distributes the workload fairly. The scheduling algorithm processes the week in blocks, considering each day and time slot one at a time. It prioritizes assignments by availability score, starting with 3, then 2, then 1. Blocks marked with 0 for a person are skipped.

For each block, the program checks whether staff are still needed (2 people for 10:00–12:00, 3 people for all other blocks). If so, it selects suitable candidates—those who meet the availability preference, have enough remaining work capacity, and are available at that time.

The eligible employees are then ranked according to the following criteria:  
First, employees already scheduled for that day are preferred, in order to minimize the number of separate workdays and reduce commuting.  
Second, employees with fewer total assigned hours are favored to ensure a fair distribution of work.  
A third important aspect is the avoidance of schedule gaps. If assigning a person would create idle time between shifts—such as working 10:00–12:00 and then again at 14:00–16:00—the algorithm tries to avoid that. Such "gap sequences" are only accepted when no better options exist.

If a candidate passes all conditions, they are assigned to the shift. This process repeats until all time slots are optimally staffed.

## Running the Program

To run the program, all files (`main.py`, `scheduler.py`, `person.py`, and `Availability.xlsx`) must be located in the same directory. Required Python modules must be installed using the following command:

```
pip install pandas openpyxl matplotlib seaborn
```

The program can then be launched from the command line using:

```
python main.py
```

The final schedule will be saved in the same directory as an Excel file and a PNG graphic.

