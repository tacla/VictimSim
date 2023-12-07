# Dada uma pasta que contém diversos arquivos com resultados float de um regressor
# lê cada um dos arquivos e compara o resultado com o de referência (contido no arquivo target_values.txt)
# Ao final, imprime o RMSE calculado em ordem ascendente

import os
import numpy as np
from sklearn.metrics import mean_squared_error

# Folder path where files are stored
folder_path = './resultado_teste_cego'  # Change this to your folder path

# Read target values from target_values.txt
target_values_file = os.path.join(folder_path, 'target_values.txt')
with open(target_values_file, 'r') as target_file:
    target_values = np.array([float(line.strip()) for line in target_file])

# Store filename and RMSE pairs in a list of tuples
results = []

# Process each file in the folder
for filename in os.listdir(folder_path):
    filepath = os.path.join(folder_path, filename)
    if os.path.isfile(filepath) and filename != 'target_values.txt':
        with open(filepath, 'r') as file:
            # Read float numbers from the current file
            file_values = np.array([float(line.strip()) for line in file])
            
            # Calculate RMSE using target values and file values
            rmse = np.sqrt(mean_squared_error(target_values, file_values))
            
            # Append filename and RMSE to results list
            results.append((filename, rmse))

# Sort the results list by ascending order of RMSE
results.sort(key=lambda x: x[1])

# Print the classified results by ascending order of RMSE
print("RMSE\tEquipe")
for filename, rmse in results:
    print(f"{rmse:.3f}\t{filename}")

