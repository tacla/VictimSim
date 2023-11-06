import math

class RescueRoute:

    def __init__(self):
        self.victim_sequence = []

    def fitness(self):
        pass
    
    def add_victim(self, victim):
        self.victim_sequence(victim)

    def total_distance(self):
        
        distance = 0

        for i in range(len(self.victim_sequence) - 1):
            distance += self.distance_between_victims(self.victim_sequence[i], self.victim_sequence[i + 1])

        return distance
            

    def distance_between_victims(self, v1, v2):
        #A* para encontrar a melhor rota entre duas vítimas
        pass