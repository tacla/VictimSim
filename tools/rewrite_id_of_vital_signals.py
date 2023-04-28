## Le o arquivo de sinais vitais e reescreve o id sequencial das vitimas
## iniciando em 1
            
import csv

inp_sv = "sinais_vitais.txt"
out_sv = "out_sinais_vitais.txt"


# Open the input and output CSV files
with open(inp_sv, 'r') as input_file, open(out_sv, 'w', newline='') as output_file:
    # Create a CSV reader and writer objects
    reader = csv.reader(input_file)
    writer = csv.writer(output_file)
    
    
    # Iterate over the rows in the input file
    for i, row in enumerate(reader):
        # Extract the float values from the row
        values = [float(x) for x in row[1:7]]
        
        # Write the row to the output file with the index as the first column
        writer.writerow([i+1] + values + [int(row[7])])




     
            
