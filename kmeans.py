import random
import math

class KMeans():
    
    def __init__(self):
        self.redistributed = True

    def execute(self, victims, n):
        
        groups = self.generate_random_groups(victims, n)

        while self.redistributed:
            groups = self.update_groups(groups)

        return groups
    
    def update_groups(self, groups):

        for group in groups:
            new_centroid = self.centroid(group[1])
            group[0] = new_centroid

        return self.redistribute(groups)

    def generate_random_groups(self, victims, n):
        centroids = self.initial_centroids(victims, n)
        return self.distribute(victims, centroids)
    
    def distribute(self, victims, centroids):
        # Distribuição das vítimas para formar os grupos iniciais
        groups = [[centroid, []] for centroid in centroids]

        for victim in victims:
            minor_distance = float(9999)
            centroid_index = 0
            # Checa a qual centróide a vítima da iteração irá pertencer
            for i, centroid in enumerate(centroids):
                distance_to_centroid = self.distance_to_centroid(victim, centroid)
                if distance_to_centroid < minor_distance:
                    minor_distance = distance_to_centroid
                    centroid_index = i
            
            groups[centroid_index][1].append(victim)
        
        return groups
            

    def redistribute(self, groups):
        self.redistributed = False

        centroids = [group[0] for group in groups]
        new_groups = [[centroid, []] for centroid in centroids]
        victim_groups = [group[1] for group in groups]

        for i, victims in enumerate(victim_groups):
            
            for victim in victims:
                minor_distance = float(9999)
                current_centroid_index = i
                next_centroid_index = i

                # Checa a qual centróide a vítima da iteração irá pertencer
                for j, centroid in enumerate(centroids):
                    distance_to_centroid = self.distance_to_centroid(victim, centroid)
                    if distance_to_centroid < minor_distance:
                        minor_distance = distance_to_centroid
                        next_centroid_index = j

                # Caso a vítima tenha que ser redirecionada a outro grupo
                if next_centroid_index != current_centroid_index:
                    self.redistributed = True
                
                new_groups[next_centroid_index][1].append(victim)

        return new_groups

    def initial_centroids(self, victims, n):
        centroids = []

        for i in range(0, n):
            min_x = 9999
            max_x = -9999
            min_y = 9999
            max_y = -9999

            for victim in victims:  
                if victim[0][0] > max_x:
                    max_x = victim[0][0]
                if victim[0][0] < min_x:
                    min_x = victim[0][0]
                if victim[0][1] > max_y:
                    max_y = victim[0][1]
                if victim[0][1] < min_y:
                    min_y = victim[0][1]

            x = random.randint(min_x, max_x)
            y = random.randint(min_y, max_y)
            centroids.append((x, y))

        return centroids

    def centroid(self, group):
        x_average = 0
        y_average = 0

        for victim in group:
            x_average += victim[0][0]
            y_average += victim[0][1]
            
        x_average /= len(group)
        y_average /= len(group)

        return (x_average, y_average)

    def distance_to_centroid(self, victim, centroid):
        return math.sqrt((centroid[0] - victim[0][0])**2 + (centroid[1] - victim[0][1])**2)