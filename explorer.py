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
        self.returning_to_base = False

        self.map = Map(path_priorities)

   
    
    # def deliberate(self) -> bool:
    #     """ The agent chooses the next action. The simulator calls this
    #     method at each cycle. Must be implemented in every agent"""

    #     # No more actions, time almost ended
    #     if self.rtime < 10.0: 
    #         # time to wake up the rescuer
    #         # pass the walls and the victims (here, they're empty)
    #         print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
    #         self.resc.go_save_victims([],[])
    #         return False
        
    #     dx = random.choice([-1, 0, 1])

    #     if dx == 0:
    #        dy = random.choice([-1, 1])
    #     else:
    #        dy = random.choice([-1, 0, 1])
        
    #     # Check the neighborhood obstacles
    #     obstacles = self.body.check_obstacles()


    #     # Moves the body to another position
    #     result = self.body.walk(dx, dy)

    #     # Update remaining time
    #     if dx != 0 and dy != 0:
    #         self.rtime -= self.COST_DIAG
    #     else:
    #         self.rtime -= self.COST_LINE

    #     # Test the result of the walk action
    #     if result == PhysAgent.BUMPED:
    #         walls = 1  # build the map- to do
    #         # print(self.name() + ": wall or grid limit reached")

    #     if result == PhysAgent.EXECUTED:
    #         # check for victim returns -1 if there is no victim or the sequential
    #         # the sequential number of a found victim
    #         seq = self.body.check_for_victim()
    #         if seq >= 0:
    #             vs = self.body.read_vital_signals(seq)
    #             self.rtime -= self.COST_READ
    #             # print("exp: read vital signals of " + str(seq))
    #             # print(vs)
                
    #     return True
    
    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        self.update_known_map() # Adiciona base na lista

        if self.time_to_get_back():
            # Returns to base and notify the rescuer
            # If agent is not at the base, returns True
            init_pos = (self.horizontal, self.vertical)
            return self.get_back_to_base(self.best_route, init_pos)

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
                    self.known_victims.append([self.horizontal, self.vertical, vs])
                # print("exp: read vital signals of " + str(seq))
                # print(vs)
                
        return True

    def calc_best_return_route(self, graphed_map):
        init_pos, init_neighbours = list(graphed_map.items())[-1]
        base_pos = (0, 0)
        return self.astar(graphed_map, init_pos, base_pos)

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

    def graph_known_map(self):

        map_copy = []

        for c in self.known_map:
            x = c[0]
            y = c[1]
            map_copy.append([x, y])

        for i, coord in enumerate(map_copy):
            neighbours = []
            if any(sublist[:2] == list([coord[0] - 1, coord[1]]) for sublist in map_copy):
                neighbours.append([coord[0] - 1, coord[1], self.COST_LINE])
            if any(sublist[:2] == list([coord[0], coord[1] - 1]) for sublist in map_copy):
                neighbours.append([coord[0], coord[1] - 1, self.COST_LINE])
            if any(sublist[:2] == list([coord[0] - 1, coord[1] - 1]) for sublist in map_copy):
                neighbours.append([coord[0] - 1, coord[1] - 1, self.COST_DIAG])
            if any(sublist[:2] == list([coord[0] + 1, coord[1]]) for sublist in map_copy):
                neighbours.append([coord[0] + 1, coord[1], self.COST_LINE])
            if any(sublist[:2] == list([coord[0], coord[1] + 1]) for sublist in map_copy):
                neighbours.append([coord[0], coord[1] + 1, self.COST_LINE])
            if any(sublist[:2] == list([coord[0] + 1, coord[1] + 1]) for sublist in map_copy):
                neighbours.append([coord[0] + 1, coord[1] + 1, self.COST_DIAG])
            if any(sublist[:2] == list([coord[0] - 1, coord[1] + 1]) for sublist in map_copy):
                neighbours.append([coord[0] - 1, coord[1] + 1, self.COST_DIAG])
            if any(sublist[:2] == list([coord[0] + 1, coord[1] - 1]) for sublist in map_copy):
                neighbours.append([coord[0] + 1, coord[1] - 1, self.COST_DIAG])
            
            coord.append(neighbours)

        # Transforma para formato em dicionario
        graph = {}
        for node_data in map_copy:
            x, y, neighbors = node_data
            node_coords = (x, y)
            neighbor_info = [((neighbor[0], neighbor[1]), neighbor[2]) for neighbor in neighbors]
            graph[node_coords] = neighbor_info

        return graph


    # # Moves the agent to the base
    # dx = 0
    # dy = 0
    # if self.horizontal < 0:
    #     dx = 1
    # elif self.horizontal > 0:
    #     dx = -1
    # if self.vertical < 0:
    #     dy = 1
    # elif self.vertical > 0:
    #     dy = -1
    #
    # movx = dx
    # movy = dy
    #
    # while not self.authorize(self.body.check_obstacles(), movx, movy):
    #     movy = random.choice([-1, 1, 0])
    #     movx = random.choice([-1, 1, 0])
    #
    # self.update_distance_to_base(movx, movy)
    #
    # # Moves the body to another position
    # result = self.body.walk(movx, movy)
    # self.update_known_map()
    #
    # # Update remaining time
    # self.update_remaining_time(dx, dy)
    #
    # if result == PhysAgent.EXECUTED:
    #     # check for victim returns -1 if there is no victim or the sequential
    #     # the sequential number of a found victim
    #     self.map.update_agent_position(dx, dy)
    #     seq = self.body.check_for_victim()
    #     if seq >= 0:
    #         vs = self.body.read_vital_signals(seq)
    #         self.rtime -= self.COST_READ
    #         # print("exp: read vital signals of " + str(seq))
    #         # print(vs)
    #
    # # self.resc.go_save_victims([],[])
    def get_back_to_base(self, movements, init_pos):

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

        graphed_map = self.graph_known_map()
        self.best_route = self.calc_best_return_route(graphed_map)
        cost = self.calculate_cost_to_base(list(self.best_route))
        if(cost + self.COST_DIAG >= self.rtime):
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
            

