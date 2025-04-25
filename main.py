# main programm
import random
from collections import defaultdict

# Konfiguration
mitarbeitende = [
    "Anna", "Ben", "Clara", "David", "Eva",
    "Felix", "Gina", "Hans", "Ina", "Jonas", "Klara", "Lars"
]
tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
zeitbloecke = ["10-12", "12-14", "14-16", "16-18"]

# Verfügbarkeiten abfragen (simuliert)
verfugbarkeiten = defaultdict(list)

print("Verfügbarkeiten abfragen:")
for mitarbeiter in mitarbeitende:
    print(f"\nVerfügbarkeit für {mitarbeiter} eingeben (j/n für jeden Block):")
    for tag in tage:
        for block in zeitbloecke:
            eingabe = input(f"Ist {mitarbeiter} verfügbar am {tag} ({block})? [j/n]: ")
            if eingabe.lower() == 'j':
                verfugbarkeiten[mitarbeiter].append((tag, block))

# Arbeitsplan erstellen
erforderlich_pro_block = {
    "10-12": 2,
    "12-14": 3,
    "14-16": 3,
    "16-18": 3
}

arbeitsplan = defaultdict(lambda: defaultdict(list))  # tag -> block -> [mitarbeiter]

for tag in tage:
    for block in zeitbloecke:
        verfugbar = [m for m in mitarbeitende if (tag, block) in verfugbarkeiten[m]]
        zufallsauswahl = random.sample(verfugbar, min(len(verfugbar), erforderlich_pro_block[block]))
        arbeitsplan[tag][block] = zufallsauswahl

# Arbeitsplan anzeigen
print("\nGenerierter Arbeitsplan:")
for tag in tage:
    print(f"\n{tag}:")
    for block in zeitbloecke:
        mitarbeiter = arbeitsplan[tag][block]
        print(f"  {block}: {', '.join(mitarbeiter) if mitarbeiter else 'KEINE BESETZUNG'}")