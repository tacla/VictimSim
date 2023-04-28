import heapq
from copy import deepcopy
from agentes.resgate.planos.algoritmo_genetico import Otimizador
from agentes.utils.problema import Problema

class PlanoResgateGenetico:
    """Plano de resgate das vítimas potencializado com algoritmo genético.
    """
    def __init__(
        self,
        problema_atual: Problema,
        tempo_restante: float
    ) -> None:
        self.problema = problema_atual
        self.probabilidade_eventos = {
            'chance_mutacao': 0.1,
            'chace_selecao_aleatoria': 0.05,
            'percentagem_retencao_populacao': 0.35
        }

        self.otimizador = Otimizador(
            n_populacao = 10000,
            n_geracoes = 6,
            probabilidade_eventos = self.probabilidade_eventos,
            tempo_disponivel = tempo_restante
        )

    def executar(self) -> None:
        """Executa o otimzador com algoritmo genético.
        """
        caminhos_possiveis = self.processa_problema()

        self.otimizador.evoluir(self.problema, caminhos_possiveis)
        passos_resgates = self.obtem_passos_trajeto(caminhos_possiveis)

        return passos_resgates

    def obtem_passos_trajeto(
            self,
            caminhos_possiveis: dict[str, dict[str, list[str]]]
        ) -> list[tuple[int, int]]:
        """Transcreve as origens e destinos da sequência de sub-caminhos obtidos em
            passos que podem ser executados pelo agente socorrista.

        Args:
            caminhos_possiveis (dict[str, dict[str, list[str]]]): caminhos possíveis para
                cada posição, computado com algoritmo de Dijkstra.

        Returns:
            list[tuple[int, int]]: retorna uma lista de passos a serem realizados para o
                agente socorrista executar todo o trajeto.
        """
        passos_trajeto = []
        melhores_caminhos = self.otimizador.melhor_individuo_.genes['trajeto']
        for origem, destino in melhores_caminhos:
            posicoes_trajeto = caminhos_possiveis[origem][destino]
            posicao_anterior = self.obtem_inteiros_chave_posicao(origem)
            for posicao, _ in posicoes_trajeto:
                posicao_atual = self.obtem_inteiros_chave_posicao(posicao)
                var_linha = posicao_atual[0] - posicao_anterior[0]
                var_coluna = posicao_atual[1] - posicao_anterior[1]
                posicao_anterior = deepcopy(posicao_atual)
                passos_trajeto.append((var_linha, var_coluna))
        passos_trajeto.reverse()
        return passos_trajeto

    def obtem_inteiros_chave_posicao(self, chave_posicao: str) -> tuple[int, int]:
        """Retorna os valores inteiros das posições de uma chave posição 
            (representa um estado do ambiente)

        Args:
            chave_posicao (str): chave posição para se obter os inteiros.

        Returns:
            tuple[int, int]: retorna os inteiros da chave da posição.
        """
        posicoes = chave_posicao.split(':')
        return int(posicoes[0]), int(posicoes[1])

    def processa_problema(self) -> dict[str, dict[str, list[str]]]:
        """Faz o processamento do problema permitindo encontrar todos os sub-caminhos
            entre todas as posições chave
        
        - base e vítimas, vítimas e vítimas e vítimas e base.

        Returns:
            dict[str, dict[str, list[str]]]: _description_
        """
        caminhos = self.encontrar_caminhos(
            self.problema.grafo_posicoes,
            self.problema.sinais_vitais_vitimas
        )
        return caminhos

    def encontrar_caminhos(
            self,
            grafo_posicoes: dict[str, list[str]],
            vitimas: dict[str, list[float]]
        ) -> dict[str, dict[str, list[str]]]:
        """Por meio do algoritmo de Dijkstra, monta um dicionário com todos os sub-caminhos ótimos
            ótimos dado origens para as posições chave.

        - base e vítimas, vítimas e vítimas e vítimas e base.

        Args:
            grafo_posicoes (dict[str, list[str]]): dicionário com as posições e suas adjacências.
            vitimas (dict[str, list[float]]): lista com os sinais vitais e posição das vítimas.

        Returns:
            dict[str, dict[str, list[str]]]: _description_
        """
        caminhos = {}
        for vitima1 in ['0:0'] + list(vitimas):
            caminhos[vitima1] = {}
            for vitima2 in ['0:0'] + list(vitimas):
                if vitima1 == vitima2:
                    continue
                caminho = self.dijkstra(grafo_posicoes, vitima1, vitima2)
                caminhos[vitima1][vitima2] = caminho
        return caminhos

    def dijkstra(
            self,
            grafo_posicoes: dict[str, list[str]],
            origem: str, destino: str
        ) -> list[str]:
        """Algoritmo de Dijkstra adaptado para o problema a ser resolvido.

        Args:
            grafo_posicoes (dict[str, list[str]]): dicionário com as posições e suas adjacências.
            origem (str): chave posição da origem do sub-caminho.
            destino (str): chave posição do destino do sub-caminho.

        Returns:
            list[str]: sequência de posições que devem ser alcançadas para
                completar o sub-caminho.
        """
        distancias = {posicao: float('inf') for posicao in grafo_posicoes}
        distancias[origem] = 0.0
        fila = [(0.0, origem, [])]
        while fila:
            (distancia, posicao, caminho) = heapq.heappop(fila)
            if posicao == destino:
                return caminho

            if distancia > distancias[posicao]:
                continue

            for adjacente in grafo_posicoes[posicao]:
                custo = self.__calcular_custo(posicao, adjacente)
                nova_distancia = distancia + custo
                if nova_distancia < distancias[adjacente]:
                    distancias[adjacente] = nova_distancia
                    novo_caminho = caminho + [(adjacente, custo)]
                    heapq.heappush(fila, (nova_distancia, adjacente, novo_caminho))
        return []

    def __calcular_custo(self, origem: str, destino: str) -> float:
        """Obtém o custo de realizar um movimento de passo.

        Args:
            origem (str): chave posição da origem.
            destino (str): chave posição do destino.

        Returns:
            float: custo para realizar o passo.
        """
        ox, oy = map(int, origem.split(':'))
        dx, dy = map(int, destino.split(':'))
        if ox == dx or oy == dy:
            return 1.0
        return 1.5
