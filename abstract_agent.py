##  ABSTRACT AGENT
### @Author: Tacla (UTFPR)
### It has the default methods for all the agents supposed to run in
### the environment

import os
import random
from abc import ABC, abstractmethod
from physical_agent import PhysAgent


class AbstractAgent:
    """ This class represents a generic agent and must be implemented by a concrete class. """
    
    
    def __init__(self, env, config_file):
        """ 
        Any class that inherits from this one will have these attributes available.
        @param env referencia o ambiente
        @param config_file: the absolute path to the agent's config file
        """
       
        self.env = env              # ref. to the environment
        self.body = None            # ref. to the physical part of the agent in the environment
        self.NAME = ""              # the name of the agent
        self.TLIM = 0.0             # time limit to execute (cannot be exceeded)
        self.COST_LINE = 0.0        # cost to walk one step hor or vertically
        self.COST_DIAG = 0.0        # cost to walk one step diagonally
        self.COST_READ = 0.0        # cost to read a victim's vital sign
        self.COST_FIRST_AID = 0.0   # cost to drop the first aid package to a victim
        self.COLOR = (100,100,100)  # color of the agent
        self.TRACE_COLOR = (140,140,140) # color for the visited cells
        
        # Read agents config file for controlling time
        with open(config_file, "r") as file:

            # Read each line of the file
            for line in file:
                # Split the line into words
                words = line.split()

                # Get the keyword and value
                keyword = words[0]
                if keyword=="NAME":
                    self.NAME = words[1]
                elif keyword=="COLOR":
                    r = int(words[1].strip('(), '))
                    g = int(words[2].strip('(), '))
                    b = int(words[3].strip('(), '))
                    self.COLOR=(r,g,b)  # a tuple
                elif keyword=="TRACE_COLOR":
                    r = int(words[1].strip('(), '))
                    g = int(words[2].strip('(), '))
                    b = int(words[3].strip('(), '))
                    self.TRACE_COLOR=(r,g,b)  # a tuple
                elif keyword=="TLIM":
                    self.TLIM = float(words[1])
                elif keyword=="COST_LINE":
                    self.COST_LINE = float(words[1])
                elif keyword=="COST_DIAG":
                    self.COST_DIAG = float(words[1])
                elif keyword=="COST_FIRST_AID":
                    self.COST_FIRST_AID = float(words[1])
                elif keyword=="COST_READ":    
                    self.COST_READ = float(words[1])
                    
        # Register within the environment - creates a physical body
        # Starts in the ACTIVE state
        self.body = env.add_agent(self, PhysAgent.ACTIVE)

      
    @abstractmethod
    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        pass

