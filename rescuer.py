##  RESCUER AGENT
### @Author: Tacla (UTFPR)
### Demo of use of VictimSim

import os
import random
import math
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from abc import ABC, abstractmethod


## Classe que define o Agente Rescuer com um plano fixo
class Rescuer(AbstractAgent):
    def __init__(self, env, config_file):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.plan = []              # a list of planned actions
        self.rtime = self.TLIM      # for controlling the remaining time
        self.n_explorer = 0
        self.mapa =[]
        self.vitimas=[]

        #clustering
        self.K_list = [[] for _ in range(4)]
        self.K_centers = [[] for _ in range(4)]

        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.body.set_state(PhysAgent.IDLE)

        # planning
        self.__planner()
    
    def go_save_victims(self, mapa, vitimas):
        if self.n_explorer == 0:
            self.mapa = mapa
        else:
            for i in range(len(mapa)):
                for j in range(len(mapa[i])):
                    if mapa[i][j] == -3 or (mapa[i][j] < self.mapa[i][j] and mapa[i][j]>0):
                        self.mapa[i][j] = mapa[i][j]
            
        self.n_explorer = self.n_explorer + 1
        self.vitimas.extend(vitimas)
        # Remove os duplicados mantendo apenas uma ocorrência de cada número
        self.vitimas = list(set(self.vitimas))

        if self.n_explorer == 4:
            print("NUMERO DE VITIMAS ENCONTRADAS:", len(self.vitimas))
            self.body.set_state(PhysAgent.ACTIVE)
            #CLUSTERING
            self.K_centers[0] = (len(mapa)*0.25, len(mapa)*0.25)
            self.K_centers[1] = (len(mapa)*0.75, len(mapa)*0.25)
            self.K_centers[2] = (len(mapa)*0.25, len(mapa)*0.75)
            self.K_centers[3] = (len(mapa)*0.75, len(mapa)*0.75)        
            
           

            for i in range(len(self.vitimas)):
                menor_distancia = float('inf')
                center_index = 0
                for j, center in enumerate(self.K_centers):
                    dist = self.distancia_entre_pontos(self.vitimas[i], center)
                    if dist < menor_distancia:
                        menor_distancia = dist
                        center_index = j
                self.K_list[center_index].append(self.vitimas[i])
                lista_centro = self.K_list[center_index]
                total_x = sum(x for x, _ in lista_centro) + self.K_centers[center_index][0]
                total_y = sum(y for _, y in lista_centro) + self.K_centers[center_index][1]
                n = len(lista_centro) + 1 
                self.K_centers[center_index] = (total_x / n, total_y / n)


    def distancia_entre_pontos(self,ponto1, ponto2):
        x1, y1 = ponto1
        x2, y2 = ponto2
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


    
    def __planner(self):
        """ A private method that calculates the walk actions to rescue the
        victims. Further actions may be necessary and should be added in the
        deliberata method"""

        # This is a off-line trajectory plan, each element of the list is
        # a pair dx, dy that do the agent walk in the x-axis and/or y-axis
        self.plan.append((0,1))
        self.plan.append((1,1))
        self.plan.append((1,0))
        self.plan.append((1,-1))
        self.plan.append((0,-1))
        self.plan.append((-1,0))
        self.plan.append((-1,-1))
        self.plan.append((-1,-1))
        self.plan.append((-1,1))
        self.plan.append((1,1))
        
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        # No more actions to do
        if self.plan == []:  # empty list, no more actions to do
           return False

        # Takes the first action of the plan (walk action) and removes it from the plan
        dx, dy = self.plan.pop(0)

        # Walk - just one step per deliberation
        result = self.body.walk(dx, dy)

        # Rescue the victim at the current position
        if result == PhysAgent.EXECUTED:
            # check if there is a victim at the current position
            seq = self.body.check_for_victim()
            if seq >= 0:
                res = self.body.first_aid(seq) # True when rescued             

        return True

