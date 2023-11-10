## EXPLORER AGENT
### @Author: Tacla, UTFPR
### It walks randomly in the environment looking for victims.

import sys
import os
import random
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from map import Map
from abc import ABC, abstractmethod
import heapq
from node import Node
import time

class Explorer(AbstractAgent):
    def __init__(self, env, config_file, resc, path_priorities):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """

        super().__init__(env, config_file)
        
        # Specific initialization for the rescuer
        self.resc = resc           # reference to the rescuer agent
        self.rtime = self.TLIM     # remaining time to explore   
        self.horizontal = 0 # Incrementa se andar para a direita e decrementa se andar para a esquerda
        self.vertical = 0  # Incrementa se andar para baixo e decrementa se andar para cima
        self.number_of_moves = 0
        self.known_victims = []
        self.known_map = []
        self.best_route = []
        self.map_graph = {}
        self.returning_to_base = False

        self.map = Map(path_priorities)
    
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        self.update_known_map() # Adiciona base na lista
        
        if self.time_to_get_back():
            # Returns to base and notify the rescuer
            # If agent is not at the base, returns True
            return self.get_back_to_base()

        return self.explore()

    def calc_best_return_route(self, graphed_map):
        init_pos, init_neighbours = list(graphed_map.items())[-1]
        base_pos = (0, 0)
        result = self.astar(graphed_map, init_pos, base_pos)
        return result

    def astar(self, graph, start, goal):
        
        open_list = []  # Lista de nós a serem avaliados
        closed_set = set()  # Conjunto de nós já avaliados
        heur = self.get_heuristic_estimate(start[0], start[1])

        start_node = Node(start, None, 0, heur)
        heapq.heappush(open_list, start_node)

        while open_list:
            current_node = heapq.heappop(open_list)

            if current_node.state == goal:
                # Se chegamos ao objetivo, reconstrua o caminho e retorne-o
                return self.build_path(current_node)

            closed_set.add(current_node.state)

            for neighbor, cost in graph[current_node.state]:
                if neighbor not in closed_set:
                    # Cria um novo nó para o vizinho
                    neighbor_node = Node(neighbor, current_node, current_node.cost + cost,
                                         self.get_heuristic_estimate(neighbor[0], neighbor[1]))

                    # Se o vizinho já está na lista aberta com um custo menor, ignore-o
                    if not any(neighbor_node.state == node.state and neighbor_node.cost >= node.cost for node in
                               open_list):
                        heapq.heappush(open_list, neighbor_node)
        # Se não encontramos um caminho, retornamos None
        return None

    def build_path(self, node):
        # Reconstrói o caminho de volta do objetivo para o início
        path = []
        while node:
            path.append(node.state)
            node = node.parent
        return list(reversed(path))

    def movement_cost(self, pos1, pos2):
        if pos1[0] != pos2[0] and pos1[1] != pos2[1]:  # Diagonal
            return self.COST_DIAG
        return self.COST_LINE

    
    def explore(self):
         # Check the neighborhood obstacles
        obstacles = self.body.check_obstacles()
        
        mov = self.map.get_action()
        dy = mov[0]
        dx = mov[1]

        while not self.authorize(obstacles, dx, dy):
            mov = self.map.get_action()
            dy = mov[0]
            dx = mov[1]
            
        # Moves the body to another position
        result = self.body.walk(dx, dy)

        # Updates travel information
        self.update_distance_to_base(dx, dy)
        self.update_known_map()
        self.update_number_of_moves()

        # Update remaining time
        self.update_remaining_time(dx, dy)

        if result == PhysAgent.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            self.map.update_agent_position(dx,dy)
            seq = self.body.check_for_victim()
            if seq >= 0:
                vs = self.body.read_vital_signals(seq)
                self.rtime -= self.COST_READ
                if [self.horizontal, self.vertical] not in self.known_victims:
                    self.known_victims.append(((self.horizontal, self.vertical), vs))
                # print("exp: read vital signals of " + str(seq))
                # print(vs)
                
        return True

    def get_back_to_base(self):
        
        init_pos = (self.horizontal, self.vertical)
        movements = self.best_route
        mov = movements.pop(0)

        dx = mov[0] - init_pos[0]
        dy = mov[1] - init_pos[1]

        self.update_distance_to_base(dx, dy)
    
        # Moves the body to another position
        result = self.body.walk(dx, dy)
        # Update remaining time
        self.update_remaining_time(dx, dy)

        if not self.at_base():
            return True
        else:
            for i, r in enumerate(self.resc):
                self.resc[i].merge_maps(list(self.known_map), list(self.known_victims))
            return False

    def time_to_get_back(self):

        if self.returning_to_base:
            return True
        
        self.best_route = self.calc_best_return_route(self.map_graph)
        cost = self.calculate_cost_to_base(list(self.best_route))
        
        if(cost + 2*self.COST_DIAG + self.COST_READ >= self.rtime):
            self.returning_to_base = True
            self.best_route.pop(0)
            return True
        
        return False
    
    def calculate_cost_to_base(self, best_route):
        cost = 0
        for i in range(len(best_route) - 1):
            x1 = best_route[i][0]
            y1 = best_route[i][1]
            x2 = best_route[i + 1][0]
            y2 = best_route[i + 1][1]

            mov = (x2 - x1, y2 - y1)

            if(mov == (0,1) or mov == (0,-1) or mov == (1,0) or mov == (-1,0)):
                cost += self.COST_LINE
            else:
                cost += self.COST_DIAG

        return cost

    
    def update_remaining_time(self, dx, dy):
         # Update remaining time
        if dx != 0 and dy != 0:
            self.rtime -= self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE

    def at_base(self):
        return self.horizontal == 0 and self.vertical == 0

    def update_distance_to_base(self, dx, dy):
        self.horizontal += dx
        self.vertical += dy

    def update_number_of_moves(self):
        self.number_of_moves += 1

    def update_known_map(self):
        if [self.horizontal, self.vertical] not in self.known_map:
            self.known_map.append([self.horizontal, self.vertical])
            discovered = (self.horizontal, self.vertical)
            self.map_graph[discovered] = []
            for coord in self.map_graph.keys():
                cost = self.is_neighbour(discovered, coord)
                if cost != None:
                    self.map_graph[discovered].append([coord, cost])
                    self.map_graph[coord].append([discovered, cost])
            end_time = time.time()
                
    def is_neighbour(self, coord1, coord2):
        if (coord1[0] - 1, coord1[1]) == coord2:
            return self.COST_LINE
        if (coord1[0], coord1[1] - 1) == coord2:
            return self.COST_LINE
        if (coord1[0] - 1, coord1[1] - 1) == coord2:
            return self.COST_DIAG
        if (coord1[0] + 1, coord1[1]) == coord2:
            return self.COST_LINE
        if (coord1[0], coord1[1] + 1) == coord2:
            return self.COST_LINE
        if (coord1[0] + 1, coord1[1] + 1) == coord2:
            return self.COST_DIAG
        if (coord1[0] + 1, coord1[1] - 1) == coord2:
            return self.COST_DIAG
        if (coord1[0] - 1, coord1[1] + 1) == coord2:
            return self.COST_DIAG
        return None

    def get_heuristic_estimate(self, dx, dy):
        # Estima o gasto necessário para voltar para a base a partir da coord atual
        valor = min(abs(dx), abs(dy)) * self.COST_DIAG  # Anda o máximo que pode na diagonal
        valor += abs((abs(dx) - abs(dy))) * self.COST_LINE # Anda o restante na vertical/horizontal
        return valor

    def authorize(self, obstacles, x, y):
        if x == 0 and y == -1:
            if obstacles[0] != 0:
                return False
        if x == 1 and y == -1:
            if obstacles[1] != 0:
                return False
        if x == 1 and y == 0:
            if obstacles[2] != 0:
                return False
        if x == 1 and y == 1:
            if obstacles[3] != 0:
                return False
        if x == 0 and y == 1:
            if obstacles[4] != 0:
                return False
        if x == -1 and y == 1:
            if obstacles[5] != 0:
                return False
        if x == -1 and y == 0:
            if obstacles[6] != 0:
                return False
        if x == -1 and y == -1:
            if obstacles[7] != 0:
                return False
        return True
            

