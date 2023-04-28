## Faz matching do arquivo de coordenadas das vitimas com o de sinais vitais.
## Imprime vítima x coordenada sempre considerando o arquivo de menor número de registros.

import sys
import os
import csv

victims = []

# Open the file for reading
current_dir = os.path.abspath(os.getcwd())
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

#print(parent_dir)
folder = "data_teste1"
filename = 'env_victims.txt'
victims_file = os.path.join(parent_dir, folder, filename)
print(victims_file)

with open(victims_file, "r") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        x = int(row[0])
        y = int(row[1])
        victims.append((x, y))

print(f"Total of coordinates: {len(victims)}")


filename = 'sinais_vitais.txt'
vital_signals=[]
vs_file = os.path.join(parent_dir, folder, filename)
with open(vs_file, "r") as csvfile:
    csvreader = csv.reader(csvfile)
    for row in csvreader:
        vital_signals.append(row)



# Print victim id, (x,y), label gravidade
tot_classe=[0,0,0,0]
print(f"** SIGNAL VITALS ({len(vital_signals)}) **")
tot_grav = 0.0

print("id grav  label")
for vs in vital_signals:
    c = int(vs[7])
    print(f"{int(str(vs[0])):2d}: {float(vs[6]):.2f} {c:1d}")
    tot_grav = tot_grav + float(vs[6])
    tot_classe[c-1]+=1


print(f"Total de gravidade acumulado {tot_grav:.2f} médio {tot_grav/len(vital_signals):.2f}")
print(f"Total por classe")
print(f"1 CRITICO.....: {tot_classe[0]} {tot_classe[0]/len(vital_signals):.2f}")
print(f"2 INSTAVEL....: {tot_classe[1]} {tot_classe[1]/len(vital_signals):.2f}")
print(f"3 POT INSTAVEL: {tot_classe[2]} {tot_classe[2]/len(vital_signals):.2f}")
print(f"4 ESTAVEL.....: {tot_classe[3]} {tot_classe[3]/len(vital_signals):.2f}")

