# script.py

# Generar la secuencia para housemodel y respectivo job
for i in range(52, 134):
    if i != 60 and i != 62 and i != 64 and i != 65 and i != 75 and i != 77 and i != 78 and i != 79 and i != 80 and i != 81 and i != 82 and i != 83 and i != 84 and i != 86 and i != 92 and i != 93 and i != 104 and i != 110 and i != 112:
        for j in range(36, 45):
            if j != 37 and j != 39 and j != 43:
                print(f"{i}\t,{j}")
