import sys
import os
import pygame
import random
import csv
import time

## Class PhysAgent
""" It is the representation of an agent in the environment
It MUST NOT be used by the rescuer or explorer """
class PhysAgent:
    # States of the body of the agent
    ENDED = 2   # Successfully ended
    ACTIVE = 1  # still running
    IDLE = 0    # not active, but alive
    DEAD  = -1  # fatal error

    # Possible results for the walk action
    BUMPED = -1        # agent bumped into a wall or reached the end of the grid
    TIME_EXCEEDED = -2 # agent reached the time limit - no more battery
    EXECUTED = 1       # action successfully executed
    

    def __init__(self, mind, env, x_base, y_base, state=ACTIVE):
        """Instatiates a physical agent
        @param self: the physical agent
        @param mind: the mind of the physical agent
        @param env: the environment object
        @param x_base: initial value for the coordinate x
        @param y_base: initial value for the coordinate y"""

        self.mind = mind              # it is the agent's mind
        self.env = env                # it is the environment
        self.x_base = x_base          # x coordinate of the base
        self.y_base = y_base          # y coordinate of the base
        self.x = x_base               # current x coordinate: at Base
        self.y = y_base               # current y coordinate
        self.rtime = mind.TLIM        # current remaining time
        self.state = state            # -1=dead  0=successfully ended 1=alive

    def set_state(self, state):
        self.state = state

    def end_of_time(self):
        """ This  method test if time limit was reached and if the agent is at the base.
        @return: True - time exceeded
                 False - time not exceeded"""
        if self.rtime < 0.0:
           return True
        
        return False

    def at_base(self):
        """ This  method test if the agent is at the base.
        @return: True - the agent is at the base position
                 False - the agent is not at the base position"""
   
        if self.x == self.env.dic["BASE"][0] and self.y == self.env.dic["BASE"][1]:
           return True
       
        return False

    def walk(self, dx, dy):
        """ Public method for moving the agent's body one cell to any direction (if possible)
        @param dx: an int value corresponding to deplacement in the x axis
        @param dy: an int value corresponding to deplacement in the y axis
        @returns -1 = the agent bumped into a wall or reached the end of grid
        @returns -2 = the agent has no enough time to execute the action
        @returns 1 = the action is succesfully executed
        In every case, action's executing time is discounted from time limit"""
        
        ## consume time
        if dx != 0 and dy != 0:   # diagonal
            self.rtime -= self.mind.COST_DIAG
        else:
            self.rtime -= self.mind.COST_LINE


        ## agent is dead
        if self.rtime < 0:
           return PhysAgent.TIME_EXCEEDED
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        if new_x >= 0 and new_x < self.env.dic["GRID_WIDTH"]and new_y >= 0 and new_y < self.env.dic["GRID_HEIGHT"] and self.env.walls[new_x][new_y] == 0:
            self.x = new_x
            self.y = new_y
            self.env.visited[new_x][new_y] = self.mind.TRACE_COLOR
            return PhysAgent.EXECUTED
        else:
            return PhysAgent.BUMPED

    def check_for_victim(self):
        """ Public method for testing if there is a victim in the current position of the agent
        @returns int: the sequential number of the victim starting from zero (in the list that corresponds to the
        victims.txt and sinais_vitais.txt)
        @returns -1: if there is no victim at the current position of the agent"""

        seq = -1

        if (self.x, self.y) in self.env.victims:
            seq = self.env.victims.index((self.x, self.y))

        return seq

    def read_vital_signals(self, seq):
        """ Public method for reading the vital signals and marking a victim as found.
        @param seq: identifies the victim starting from zero 
        @returns list of vital signals if seq corresponds to a victim or an empty
        list if the seq is not found."""

        ## Consume time
        self.rtime -= self.mind.COST_READ
    
        ## Agent is dead
        if self.rtime < 0:
           return PhysAgent.TIME_EXCEEDED

        ## Null victim
        if seq >= self.env.nb_of_victims:
            return []
        
        # Mark the victim as found by this agent.
        # More than one agent can found the same victim, so it's a list
        self.env.found[seq].append(self)
        return self.env.signals[seq]

    def first_aid(self, seq):
        """ Public method for dropping the first aid package to the victim identified
        by the seq number. This method marks the victim as saved.
        @param seq: identifies the victim starting from zero 
        @returns list of vital signals if seq corresponds to a victim or an empty
        list if the seq is not found."""

        ## Consume time
        self.rtime -= self.mind.COST_FIRST_AID

        ## Agent is dead
        if self.rtime < 0:
           return PhysAgent.TIME_EXCEEDED

        ## Null victim
        if seq >= self.env.nb_of_victims:
            return False
        
        # Mark the victim as found by this agent.
        # More than one agent can drop a first-aid package to the same victim, so it's a list
        self.env.saved[seq].append(self)
        return True

    def get_found_victims(self):
        """ Public method for returning the number of found victims by the agent
        @returns a list with the sequential number of found victims """

        victims = []

        v = 0
        for finders in self.env.found:
            if self in finders:
                victims.append(v)
            v = v + 1
  
        return victims

    def get_saved_victims(self):
        """ Public method for returning the number of saved victims by the agent
        @returns a list with the sequential number of saved victims """

        victims = []

        v = 0
        for rescuers in self.env.saved:
            if self in rescuers:
                victims.append(v)
            v = v + 1
  
        return victims 
                
            
