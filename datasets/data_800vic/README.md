Data de criação: 12/9/2023
Script MatLab
Autor: Cesar Augusto Tacla

** Atributos **
id: número sequencial
pSist: pressão sistólica
pDiast: pressão diastólica
qPA: qualidade da pressão arterial (complia pSist e pDiast)
pulso: pulsação
fResp: frequência respiratória
grav: representa a gravidade da vítima em uma escala de 0 a 100, sendo 100 a MENOS GRAVE.
label: 1=CRÍTICO 2=INSTÁVEL 3=POTENCIALMENTE INSTÁVEL 4=ESTÁVEL

** Arquivos **
* sinais_vitais_com_label.txt
Atributos: [id, pSist, pDiast, qPA, pulso, fResp, grav, label]

* sinais_vitais_sem_label.txt
Atributos: [id, pSist, pDiast, qPA, pulso, resp, grav]

** Contagens **
1=critico.....: 119 (14.875%)
2=instável....: 455 (56.875%)
3=pot. estável: 211 (26.375%)
4=estavel.....: 15  ( 1.875%)