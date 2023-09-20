
class Node:
    def __init__(self, state, parent=None, cost=0, heuristic=0):
        self.state = state  # O estado deste nó no grafo
        self.parent = parent  # O nó pai (nó anterior) neste caminho
        self.cost = cost  # Custo acumulado para alcançar este nó
        self.heuristic = heuristic  # Valor heurístico estimado para o objetivo

    def __lt__(self, other):
        # Comparação com base no custo total (f = custo + heurística)
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)