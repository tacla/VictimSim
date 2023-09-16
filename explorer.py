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
    def __init__(self, env, config_file, resc):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """

        super().__init__(env, config_file)
        
        # Specific initialization for the rescuer
        self.resc = resc           # reference to the rescuer agent
        self.rtime = self.TLIM     # remaining time to explore   
        
        self.map = Map()  

   
    
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

        # No more actions, time almost ended
        if self.rtime < 10.0: 
            # time to wake up the rescuer
            # pass the walls and the victims (here, they're empty)
            print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
            self.resc.go_save_victims([],[])
            return False
        
        mov = self.map.get_action()
        
        dy = mov[0]
        dx = mov[1]
        
        # Check the neighborhood obstacles
        obstacles = self.body.check_obstacles()


        # Moves the body to another position
        result = self.body.walk(dx, dy)

        # Update remaining time
        if dx != 0 and dy != 0:
            self.rtime -= self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE

        # Test the result of the walk action
        if result == PhysAgent.BUMPED:
            walls = 1  # build the map- to do
            self.map.update_agent_position(0,0)
            # print(self.name() + ": wall or grid limit reached")

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

