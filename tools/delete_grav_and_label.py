## Le o arquivo de sinais vitais com label e gera um novo arquivo sem
## o valor de gravidade e sem o label de gravidade.
## Uso: gerar arquivo de teste cego
            
import csv

inp_sv = "teste_sinais_vitais_com_label.txt"
out_sv = "teste_cego_sinais_vitais.txt"


# Open the input and output CSV files
with open(inp_sv, 'r') as input_file, open(out_sv, 'w', newline='') as output_file:
    # Create a CSV reader and writer objects
    reader = csv.reader(input_file)
    writer = csv.writer(output_file)
    
    
    # Iterate over the rows in the input file
    for i, row in enumerate(reader):
        # Extract the float values from the row excluding the gravity
        values = [float(x) for x in row[1:6]]
        
        # Write the row to the output file with the index as the first column
        writer.writerow([int(row[0])] + values)
        if i%10 == 0:
            print(f"{i}")

print("fim")


     
            
