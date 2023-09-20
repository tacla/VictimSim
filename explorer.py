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
        self.horizontal = 0 #Incrementa se andar para a direita e decrementa se andar para a esquerda
        self.vertical = 0  # Incrementa se andar para baixo e decrementa se andar para cima
        self.number_of_moves = 0

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

        if self.time_to_get_back():
            # Returns to base and notify the rescuer
            # If agent is not at the base, returns True
            return self.get_back_to_base()

        # Check the neighborhood obstacles
        obstacles = self.body.check_obstacles()
        
        mov = self.map.get_action()
        dy = mov[0]
        dx = mov[1]

        while not self.authorize(obstacles,dx,dy):
            mov = self.map.get_action()
            dy = mov[0]
            dx = mov[1]
            
        # Moves the body to another position
        result = self.body.walk(dx, dy)

        # Updates travel information
        self.update_distance_to_base()
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
                # print("exp: read vital signals of " + str(seq))
                # print(vs)
                
        return True
    
    def get_back_to_base(self):
        # Moves the agent to the base
        dx = 0
        dy = 0
        if self.horizontal < 0:
            dx = 1
        elif self.horizontal > 0:
            dx = -1
        if self.vertical < 0:
            dy = 1
        elif self.vertical > 0:
            dy = -1

        movx = dx
        movy = dy

        while not self.authorize(self.body.check_obstacles(), movx, movy):
            movy = random.choice([-1, 1, 0])
            movx = random.choice([-1, 1, 0])

        self.update_distance_to_base(movx, movy)

        # Moves the body to another position
        result = self.body.walk(movx, movy)

        # Update remaining time
        self.update_remaining_time(dx, dy)

        if result == PhysAgent.EXECUTED:
            # check for victim returns -1 if there is no victim or the sequential
            # the sequential number of a found victim
            self.map.update_agent_position(dx, dy)
            seq = self.body.check_for_victim()
            if seq >= 0:
                vs = self.body.read_vital_signals(seq)
                self.rtime -= self.COST_READ
                # print("exp: read vital signals of " + str(seq))
                # print(vs)

        #self.resc.go_save_victims([],[])
        if not self.at_base():
            return True
        else:
            self.resc.go_save_victims([],[])
            return False

    def time_to_get_back(self):
        return (abs(self.horizontal) + abs(self.vertical) + self.number_of_moves/5 >= self.rtime)
    
    def update_remaining_time(self, dx, dy):
         # Update remaining time
        if dx != 0 and dy != 0:
            self.rtime -= self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE

    def at_base(self):
        return (self.horizontal == 0 and self.vertical == 0)

    def update_distance_to_base(self, dx, dy):
        self.horizontal += dx
        self.vertical += dy

    def update_number_of_moves(self):
        self.number_of_moves += 1
    
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
            

