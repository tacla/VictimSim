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
folder = "data_teste2"
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
print(f"** SIGNAL VITALS ({len(vital_signals)}) **")
tot_grav = 0.0
if len(victims) <= len(vital_signals):
    v=0
    for vs in vital_signals:
        if v < len(victims):
           print(str(v) + ") id: " + str(vs[0]) + " at (" + str(victims[v][0]) + ", " + str(victims[v][1]) + ") label=" + str(vs[7]))
        else:
           print(str(v) + ") id: " + str(vs[0]) + " at (not defined) label=" + str(vs[7]) + "\n")

        tot_grav = tot_grav + float(vs[6])
        v = v + 1
else:
    vs=0
    for v in victims:
        if vs < len(vital_signals):
           print(str(vs) + ") id: " + str(vital_signals[vs][0]) + " at (" + str(v[0]) + ", " + str(v[1]) + ") label=" + str(vital_signals[vs][7]))
        else:
           print(str(vs) + ") id: no id at (" + str(v[0]) + ", " + str(v[1]) + ") label= not defined")

        tot_grav = tot_grav + float(vital_signals[vs][6])
        vs = vs + 1

print(f"Total de gravidade acumulado {tot_grav:.2f} médio {tot_grav/len(vital_signals):.2f}")

