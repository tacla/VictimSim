from enum import Enum
from collections import defaultdict
import os
import csv
        
class Fuzzy:
    def __init__(self):
        self.rules = {} #Mapa das regras inferidas pelo Wang-Mendel
        self.dic = defaultdict(int) #Dicionario, conta quantas vezes uma regra aparece - 2 passo do wang mendel
        self.wang_mendel("datasets/data_800vic/sinais_vitais_com_label.txt")  #Treina com varios arquivos
        self.wang_mendel("datasets/data_12x12_10vic/sinais_vitais.txt")         
        self.wang_mendel("datasets/data_20x20_42vic/sinais_vitais.txt")
        self.wang_mendel("datasets/data_teste_sala/sinais_vitais.txt")
        #self.teste_800vit()
  
    def fuzzyfy(self,max,var): #Divide cada variavel em 17 grupos - fuzzy triangular
        fuz_vec = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #Cada posicao indica o valor fuzzy 
        if(var < max/8):
            fuz_vec[0] = -(1600/max) * var + 100
            fuz_vec[1] = (1600/max) * var
        elif(var >= max/16 and var < max/8):
            fuz_vec[1] = -(1600/max) * var + 200
            fuz_vec[2] = (1600/max) * var - 100
        elif(var >= max/8 and var < max*3/16):
            fuz_vec[2] = -(1600/max) * var + 300
            fuz_vec[3] = (1600/max) * var - 200
        elif(var >= max*3/16 and var < max/4):
            fuz_vec[3] = -(1600/max) * var + 400
            fuz_vec[4] = (1600/max) * var - 300
        elif(var >= max/4 and var < max*5/16):
            fuz_vec[4] = -(1600/max) * var + 500
            fuz_vec[5] = (1600/max) * var - 400
        elif(var >= max*5/16 and var < max*3/8):
            fuz_vec[5] = -(1600/max) * var + 600
            fuz_vec[6] = (1600/max) * var - 500
        elif(var >= max*3/8 and var < max*7/16):
            fuz_vec[6] = -(1600/max) * var + 700
            fuz_vec[7] = (1600/max) * var - 600
        elif(var >= max*7/16 and var < max/2):
            fuz_vec[7] = -(1600/max) * var + 800
            fuz_vec[8] = (1600/max) * var - 700
        elif(var >= max/2 and var < max*9/16):
            fuz_vec[8] = -(1600/max) * var + 900
            fuz_vec[9] = (1600/max) * var - 800
        elif(var >= max*9/16 and var < max*5/8):
            fuz_vec[9] = -(1600/max) * var + 1000
            fuz_vec[10] = (1600/max) * var - 900
        elif(var >= max*5/8 and var < max*11/16):
            fuz_vec[10] = -(1600/max) * var + 1100
            fuz_vec[11] = (1600/max) * var - 1000
        elif(var >= max*11/16 and var < max*3/4):
            fuz_vec[11] = -(1600/max) * var + 1200
            fuz_vec[12] = (1600/max) * var - 1100
        elif(var >= max*3/4 and var < max*13/16):
            fuz_vec[12] = -(1600/max) * var + 1300
            fuz_vec[13] = (1600/max) * var - 1200
        elif(var >= max*13/16 and var < max*7/8):
            fuz_vec[13] = -(1600/max) * var + 1400
            fuz_vec[14] = (1600/max) * var - 1300
        elif(var >= max*7/8 and var < max*15/16):
            fuz_vec[14] = -(1600/max) * var + 1500
            fuz_vec[15] = (1600/max) * var - 1400
        else:
            fuz_vec[15] = -(1600/max) * var + 1600
            fuz_vec[16] = (1600/max) * var - 1500
        return fuz_vec
        
    def wang_mendel(self, path):
        rules = [] #Todas as regras geradas, mesmo as repetidas
        signals = [] #Vetor das caracteristicas da vitima (pressão, batimentos, etc)
        
        vs_file = os.path.join(path) #Arquivo de teste
        
        with open(vs_file, 'r') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                qp = float(row[3]) #Pressao
                pf = float(row[4]) #Batimentos
                rf = float(row[5]) #Respiração
                lb = int(row[7])  #Grupo verdadeiro 
                
                signals.append([qp, pf, rf, lb])
                
        for vic in signals:
            fuz_qPA = self.fuzzyfy(20,vic[0]+10) #Chama a fuzzyfy para as tres caracteristicas
            fuz_pulse = self.fuzzyfy(200,vic[1])
            fuz_fResp = self.fuzzyfy(22,vic[2])
            rules.append([fuz_qPA.index(max(fuz_qPA)),fuz_pulse.index(max(fuz_pulse)),fuz_fResp.index(max(fuz_fResp)),vic[3]]) #cria uma regra, usando o grupo com maior valor obtido para cada variavel
            
        for rule in rules:
            precedent = tuple(rule[:3])  #A tupla das variaveis precedentes
            consequent = rule[3]  #O grupo de gravidade (Verdadeiro)

            if precedent not in self.rules or self.dic[precedent] < self.dic[precedent + (consequent,)]: #Adiciona as regras unicas se for a primeira aparição, ou se a regra apareceu mais vezes
                self.rules[precedent] = consequent

            self.dic[precedent + (consequent,)] += 1

           
    def defuzzyfy(self,vec): #Para um vetor de vitimas com pressao, batimentos e respiração, retorna um vetor com os grupos inferidos pelo processo fuzzy
        out = []
        for vic in vec:
            grav = [0,0,0,0] #Vetor que armazena a maior inferencia para cada grupo, dentre todas as regras
            fuz_qPA = self.fuzzyfy(20,vic[0]+10)
            fuz_pulse = self.fuzzyfy(200,vic[1])
            fuz_fResp = self.fuzzyfy(22,vic[2])
            for rule, value in self.rules.items(): #Testa todas as regras
                smallest_fuzzy = min(fuz_qPA[rule[0]], fuz_pulse[rule[1]], fuz_fResp[rule[2]]) #Como é um and, pega sempre o menor valor
                if smallest_fuzzy > grav[value - 1]: #Armazena se o resultado for maior que o ja existente (para o grupo)
                    grav[value - 1] = smallest_fuzzy
            out.append(grav.index(max(grav))+1)
        return out
    
    def measurement(self, generated, original): #Calcula as métricas
        matrix = [[0 for _ in range(4)] for _ in range(4)]

        for i in range(len(original)):
            matrix[original[i]-1][generated[i]-1] += 1 
        
        precision_1 = matrix[0][0]/sum(matrix[0])
        precision_2 = matrix[1][1]/sum(matrix[1])
        precision_3 = matrix[2][2]/sum(matrix[2])
        precision_4 = matrix[3][3]/sum(matrix[3])
        
        recall_1 = matrix[0][0]/sum(line[0] for line in matrix)
        recall_2 = matrix[1][1]/sum(line[1] for line in matrix)
        recall_3 = matrix[2][2]/sum(line[2] for line in matrix)
        recall_4 = matrix[3][3]/sum(line[3] for line in matrix)
        
        accuracy = (matrix[0][0] + matrix[1][1] + matrix[2][2] + matrix[3][3])/ len(original)
                
        f_measure_1 = 2 * precision_1 * recall_1 / (precision_1 + recall_1)
        f_measure_2 = 2 * precision_2 * recall_2 / (precision_2 + recall_2)
        f_measure_3 = 2 * precision_3 * recall_3 / (precision_3 + recall_3)
        f_measure_4 = 2 * precision_4 * recall_4 / (precision_4 + recall_4)
        
        print("\n\n*****MEASUREMENT*****")
        print("Inferred groups:")
        print(generated)
        print("Real groups:")
        print(original)
        print("\nConfusion Matrix:")
        print(matrix[0])
        print(matrix[1])
        print(matrix[2])
        print(matrix[3])
        print("\nPrecision:")
        print(f"Group 1: {precision_1:.3f}")
        print(f"Group 2: {precision_2:.3f}")
        print(f"Group 3: {precision_3:.3f}")
        print(f"Group 4: {precision_4:.3f}")
        print("\nRecall:")
        print(f"Group 1: {recall_1:.3f}")
        print(f"Group 2: {recall_2:.3f}")
        print(f"Group 3: {recall_3:.3f}")
        print(f"Group 4: {recall_4:.3f}")
        print("\nF-Measure:")
        print(f"Group 1: {f_measure_1:.3f}")
        print(f"Group 2: {f_measure_2:.3f}")
        print(f"Group 3: {f_measure_3:.3f}")
        print(f"Group 4: {f_measure_4:.3f}")
        print(f"\nTOTAL ACCURACY: {accuracy:.3f}\n")
        
    # def teste_800vit(self):
    #     signals = []
        
    #     vs_file = os.path.join("datasets/data_800vic/sinais_vitais_com_label.txt")
    
    #     with open(vs_file, 'r') as csvfile:
    #         csvreader = csv.reader(csvfile)
    #         for row in csvreader:
    #             qp = float(row[3]) #Pressao
    #             pf = float(row[4]) #Batimentos
    #             rf = float(row[5]) #Respiração
    #             lb = int(row[7])  #Grupo verdadeiro 
                
    #             signals.append([qp, pf, rf, lb])
        
    #     original = []
    #     saida = []
    #     for x in signals:
    #         original.append(tuple(x[:3]))
    #         saida.append(x[3])
        
    #     teste = self.defuzzyfy(original)
        
    #     self.measurement(teste,saida)