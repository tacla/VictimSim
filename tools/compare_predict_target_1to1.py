## Compara as predições de um classificador sobre a classe de gravidade das vítimas e de um regressor
## sobre o valor de gravidade contra um arquivo de referência.
##
## Os arquivos a serem comparados são: 
##    file_target: arquivo com os resultados de referência
##    file_predict: arquivo com os resultados preditos
##    formato dos dois arquivoos: <id, x, y, gravity, class>
##
## Os arquivos de referência e de predição devem ter tamanhos idênticos.
## Os casamentos das linhas são feitos por leitura sincronizada.

import numpy as np
import csv
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score, mean_squared_error

# Input CSV file names
file_target = 'file_verif.txt'
file_predict = 'file_predict.txt'

# Initialize empty lists for the actual labels (target) and predicted class labels
actual_labels = []
predicted_labels = []

# Initialize empty lists for the actual gravity values and predicted values
actual_values = []
predicted_values = []

# Read the last column of file_target and file_predict
with open(file_target, 'r') as target_file, open(file_predict, 'r') as predict_file:
    target_reader = csv.reader(target_file)
    predict_reader = csv.reader(predict_file)

    for target_row, predict_row in zip(target_reader, predict_reader):        
        # Gravity class
        actual_label = int(target_row[-1])
        predicted_label = int(predict_row[-1])
        actual_labels.append(actual_label)
        predicted_labels.append(predicted_label)

        # Gravity value
        actual_value = float(target_row[-2])  # Assuming the values are in the penultimate column
        predicted_value = float(predict_row[-2])  # Assuming the values are in the penultimate column
        actual_values.append(actual_value)
        predicted_values.append(predicted_value)


# Calculate RMSE
rmse = np.sqrt(mean_squared_error(actual_values, predicted_values))

# Print the RMSE
print(f"\nRoot Mean Square Error (RMSE): {rmse:.2f}\n")

# Calculate the confusion matrix
conf_matrix = confusion_matrix(actual_labels, predicted_labels)

# Calculate accuracy
accuracy = accuracy_score(actual_labels, predicted_labels)

# Generate a classification report to get precision, recall, and F1-score
class_report = classification_report(actual_labels, predicted_labels, target_names=['Critico', 'Instavel', 'Pot Estavel', 'Estavel'])

# Print the results
print("Confusion Matrix:")
print(conf_matrix)
print("\nAccuracy:", accuracy)
print("\nClassification Report:")
print(class_report)
