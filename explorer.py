## EXPLORER AGENT
### @Author: Tacla, UTFPR
### It walks randomly in the environment looking for victims.

import sys
import os
import random
import heapq
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from abc import ABC, abstractmethod


class Explorer(AbstractAgent):

    def __init__(self, env, config_file, resc, direction):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """

        super().__init__(env, config_file)
        
        # Specific initialization for the rescuer
        self.resc = resc           # reference to the rescuer agent
        self.rtime = self.TLIM     # remaining time to explore  

        # Criar uma matriz vazia
        self.mapa = []
        self.vitimas = []
        self.direction = direction # 0- cima, 1- direita, 2- baixo, 3- esquerda
        # Define as ações possíveis (movimentos)
        self.acoes = [(0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0), (-1, -1)]
        self.last = (0, 1)
        self.ult = (0, 1)

        self.x = int(self.rtime/2)
        self.y = int(self.rtime/2)

        self.loop = 0
        self.stuck = False


        # Preencher a matriz com elementos (-3 não foi explorado)
        for _ in range(int(self.rtime)):
            linha = [-3] * int(self.rtime)
            self.mapa.append(linha) 
        self.mapa[int(self.rtime/2)][int(self.rtime/2)] = 0

    def explorar(self, mapa, pAtual):
        if self.stuck:
            for i in range(0, 8):
                indice = (self.direction * 2 + i) % 8
                posicao = self.mapa[self.x + self.acoes[indice][0]][self.y + self.acoes[indice][1]]
                if posicao == -3:
                    self.stuck = False
                    return self.acoes[indice][0], self.acoes[indice][1]
            self.loop += 1
            if self.loop >= 4:
                self.loop = 0
                return random.choice(self.acoes)
            for i in range(0, 8):
                indice = (self.direction * 2 + i) % 8
                posicao = self.mapa[self.x + self.acoes[indice][0]][self.y + self.acoes[indice][1]]
                if posicao != -1 and posicao != -4 and (self.acoes[indice][0] != self.ult[0] * -1 or self.acoes[indice][1] != self.ult[1] * -1):
                    return self.acoes[indice][0], self.acoes[indice][1]

        if pAtual == (len(mapa)/2, len(mapa)/2):
            return self.acoes[self.direction * 2]
        
        #y ou x
        sentido = 1 if self.direction % 2 == 1 else 0

        #direita ou cima
        fix = -1 if self.direction <= 1 else 1

        diff = abs(pAtual[(sentido - 1) % 2] - len(mapa)/2)
        if diff % 2 == 1:
            sinal = -1
            if fix * (pAtual[sentido] - len(mapa)/2)  + ((diff + 1) // 2) != 0:
                if fix * (pAtual[sentido] - len(mapa)/2)  + ((diff + 1) // 2) < 0:
                    for i in range(0, 8):
                        indice = (self.last[0] + i * self.last[1]) % 8
                        posicao = self.mapa[self.x + self.acoes[indice][0]][self.y + self.acoes[indice][1]]
                        if posicao == -3:
                            dx = self.acoes[indice][0]
                            dy = self.acoes[indice][1]
                            return dx, dy
                    self.stuck = True
                    return 0, 0
                else:   
                    cod = ((self.direction * 2) + 2) % 8
                    tam = 4
            else:
                cod = (self.direction * 2)
                tam = 2
        else:
            sinal = 1
            if fix * (pAtual[sentido] - len(mapa)/2)- ((diff) // 2) != 0:
                if fix * (pAtual[sentido] - len(mapa)/2)- ((diff) // 2) > 0:
                    for i in range(0, 8):
                        indice = (self.last[0] + i * self.last[1]) % 8
                        posicao = self.mapa[self.x + self.acoes[indice][0]][self.y + self.acoes[indice][1]]
                        if posicao == -3:
                            dx = self.acoes[indice][0]
                            dy = self.acoes[indice][1]
                            return dx, dy
                    self.stuck = True
                    return 0, 0
                cod = ((self.direction * 2) - 2) % 8
                tam = 4
            else:
                cod = (self.direction * 2)
                tam = 2
        dx = self.acoes[cod][0]
        dy = self.acoes[cod][1]
        if self.mapa[pAtual[0] + dx][pAtual[1] + dy] == -1 or self.mapa[pAtual[0] + dx][pAtual[1] + dy] == -4:
            for i in range(1, tam + 1):
                indice = (cod + (sinal * i)) % 8
                if self.mapa[pAtual[0] + self.acoes[indice][0]][pAtual[1] + self.acoes[indice][1]] == -3:
                    dx = self.acoes[indice][0]
                    dy = self.acoes[indice][1]
                    return dx, dy

            for i in range(0, 8):
                posicao = self.mapa[self.x + self.acoes[i][0]][self.y + self.acoes[i][1]]
                if posicao == -3:
                    dx = self.acoes[i][0]
                    dy = self.acoes[i][1]
                    return dx, dy
            self.stuck = True
            return 0, 0

        self.last = (cod + ((tam + 1) * sinal) % 8, -1 * sinal)
        return dx, dy
    
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        # No more actions, time almost ended
        if self.rtime < self.mapa[self.x][self.y] + 3: 
            # back to base
            dx,dy = self.voltarBase()
            result = self.body.walk(dx, dy)

            if result == 1:
                self.x = self.x + dx
                self.y = self.y + dy
            
            # Update remaining time
            if dx != 0 and dy != 0:
                self.rtime -= self.COST_DIAG
            else:
                self.rtime -= self.COST_LINE
            print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
            
            if self.mapa[int(self.x)][int(self.y)] == 0:
                self.resc.go_save_victims(self.mapa,self.vitimas)
                return False
            else:
                return True

        # Check the neighborhood obstacles
        obstacles = self.body.check_obstacles()

        for i in range(0, 8):
            posicao = self.mapa[self.x + self.acoes[i][0]][self.y + self.acoes[i][1]]
            if posicao == -3:
                self.mapa[self.x + self.acoes[i][0]][self.y + self.acoes[i][1]] = obstacles[i]
        self.mapa[int(len(self.mapa)/2)][int(len(self.mapa)/2)] = 0
        
        dx, dy = self.explorar(self.mapa, (self.x,self.y))
        if self.mapa[self.x + dx][self.y + dy] >= 0 and not self.stuck:
            self.loop += 1
            if self.loop >= 4:
                self.stuck = True
                self.loop = 0
        self.ult = dx, dy
        # print(dx)
        # print(dy)

        # Moves the body to another position
        result = self.body.walk(dx, dy)

        if result == 1:
            self.x = self.x + dx
            self.y = self.y + dy
            self.preencheMapa()

        # Update remaining time
        if dx != 0 and dy != 0:
            self.rtime -= self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE

        # Test the result of the walk action
        if result == PhysAgent.BUMPED:
            walls = 1  # build the map- to do
            # print(self.name() + ": wall or grid limit reached")

        if result == PhysAgent.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            seq = self.body.check_for_victim()
            if seq >= 0:
                self.vitimas.append((self.x,self.y))
                vs = self.body.read_vital_signals(seq)
                self.rtime -= self.COST_READ
                # print("exp: read vital signals of " + str(seq))
                # print(vs)
                
        return True
    
    def preencheMapa(self):
        loc =  [[0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]]

        min = sys.maxsize
        yMin = 0
        xMin = 0

        for x in [-1,0,1]:
            for y in [-1, 0, 1]:
                loc[x][y] = self.mapa[int(self.x) + x][int(self.y) + y]
                if loc[x][y] < min and loc[x][y] >= 0:
                    yMin = y
                    xMin = x
                    min = loc[x][y]

        if min == 0:
            if self.y == len(self.mapa)//2 or self.x == len(self.mapa)//2:
                self.mapa[self.x][self.y] = 1
            else:
                self.mapa[self.x][self.y] = 1.5

        elif yMin == 0 or xMin == 0:
            self.mapa[self.x][self.y] = min + 1
        else:
            self.mapa[self.x][self.y] = min + 1.5

        # for y in range(-1,2):
        #     for x in range(-1,2):
        #         print("{:.1f}".format(self.mapa[self.x + x][self.y + y]), end= ' ')
        #     print()
        # print()


    def voltarBase(self):
        loc =  [[0, 0, 0],
                [0, 0, 0],
                [0, 0, 0]]
        
        min = sys.maxsize
        x_min = 0
        y_min = 0

        for x in [-1,0,1]:
            for y in [-1, 0, 1]:
                loc[x][y] = self.mapa[int(self.x) + x][int(self.y) + y]
                if loc[x][y] < min and loc[x][y] >= 0:
                    y_min = y
                    x_min = x
                    min = loc[x][y]

        return x_min, y_min