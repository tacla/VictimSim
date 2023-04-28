from agentes.utils.estado import Estado

class Problema:
    """Representa um problema para servir de informações aos agentes.

    - O agente explorador elabora o problema (coleta informações do ambiente).
    - O agente de resgate usa essas informações para tomada de decisões.

    Contém os atributos:
        - ambiente_crencas (dict[int, dict[int, int]]): posições do ambiente e seu conteúdo.
        - grafo_posicoes (dict[str, list[str]]): lista de adjacências das posições visitadas.
        - sinais_vitais_vitimas (dict[str, list[float]]): sinais vitais das vítimas encontradas.
    """
    def __init__(self) -> None:
        """Instância um problema para servir de troca de informações
            entre os agentes explorador e de resgate.
        """
        # Crenças do ambiente: {linha: {coluna: 'descricao'}}
        self.ambiente_crencas: dict[int, dict[int, int]] = {0: {0: 'b'}}

        # Grafo das posições: {'linha:coluna': [lista_adjacencia]}
        self.grafo_posicoes: dict[str, list[str]] = {'0:0': []}

        # Sinais vitais das vítimas: {'linha:coluna': [s.i, i.n, a.i, s.v, i.t, a.i, s]}
        self.sinais_vitais_vitimas: dict[str, list[float]] = {}

    def atualiza_crenca_posicao_ambiente(
            self,
            passo_usado: dict[str, int],
            posicao_atual: Estado,
            descricao: str
        ) -> None:
        """Atualiza a crença de uma posição do ambiente com o que foi encontrado nela.

        Args:
            passo_usado (dict[str, int]): passo utilziado.
            posicao_atual (Estado): ojbeto Estado que identifica a posição.
            descricao (str): descrição do quê foi encontrado na posição.
        """
        # Se não for uma parede, atualiza o grafo_posicoes
        if descricao != 'w':
            posicao_anterior = Estado(
                linha = (posicao_atual.linha - passo_usado['linha']),
                coluna = (posicao_atual.coluna - passo_usado['coluna'])
            )
            chave_pos_atual = posicao_atual.get_chave_posicao()
            chave_pos_anterior = posicao_anterior.get_chave_posicao()

            if chave_pos_atual not in self.grafo_posicoes:
                self.grafo_posicoes[chave_pos_atual] = []

            if chave_pos_anterior not in self.grafo_posicoes[chave_pos_atual]:
                self.grafo_posicoes[chave_pos_atual].append(chave_pos_anterior)

            if chave_pos_atual not in self.grafo_posicoes[chave_pos_anterior]:
                self.grafo_posicoes[chave_pos_anterior].append(chave_pos_atual)

            for chave_posicao, adjacencias_posicao in self.grafo_posicoes.items():
                for chave_pos_grafo in self.grafo_posicoes:
                    if chave_pos_grafo == chave_posicao:
                        continue
                    if chave_pos_grafo in adjacencias_posicao:
                        continue
                    if chave_pos_grafo in self.obtem_adjacencias(chave_posicao.split(':')):
                        adjacencias_posicao.append(chave_pos_grafo)

            self.__adiciona_posicao_nas_crencas(posicao_atual, descricao)
            # print(f"{posicao_anterior} -> {posicao_atual}")
            # print(self.grafo_posicoes)
        else:
            posicao_bloqueada = Estado(
                (posicao_atual.linha + passo_usado['linha']),
                (posicao_atual.coluna + passo_usado['coluna'])
            )
            self.__adiciona_posicao_nas_crencas(posicao_bloqueada, descricao)

    def __adiciona_posicao_nas_crencas(self, posicao: Estado, descricao: str) -> None:
        if posicao.linha not in self.ambiente_crencas:
            self.ambiente_crencas[posicao.linha] = {}

        self.ambiente_crencas[posicao.linha][posicao.coluna] = descricao
        # print(self.ambiente_crencas)

    def obtem_adjacencias(self, posicao: list) -> list[str]:
        """Retorna uma lista de strings onde cada item é a
            chave de uma posição adjacente.

        Args:
            posicao (list): posição que se deseja descobrir as adjacências.

        Returns:
            list[str]: lista com as chaves das posições adjacentes.
        """
        lista_adjacencias = []
        linha = int(posicao[0])
        coluna = int(posicao[1])

        lista_adjacencias.append(f"{str(linha - 1)}:{str(coluna - 1)}") # (-1, -1)
        lista_adjacencias.append(f"{str(linha - 1)}:{str(coluna)}")     # (-1, 0)
        lista_adjacencias.append(f"{str(linha - 1)}:{str(coluna + 1)}") # (-1, 1)
        lista_adjacencias.append(f"{str(linha)}:{str(coluna - 1)}")     # (0, -1)
        lista_adjacencias.append(f"{str(linha)}:{str(coluna + 1)}")     # (0, 1)
        lista_adjacencias.append(f"{str(linha + 1)}:{str(coluna - 1)}") # (1, -1)
        lista_adjacencias.append(f"{str(linha + 1)}:{str(coluna)}")     # (1, 0)
        lista_adjacencias.append(f"{str(linha + 1)}:{str(coluna + 1)}") # (1, 1)

        return lista_adjacencias

    def verifica_estado_inedito(self, estado_futuro: Estado) -> bool:
        """Verifica se a posição ainda não foi visitada no mapa.

        Args:
            estado_futuro (Estado): objeto Estado que representa a possível
                futura nova posição do agente.
        
        Returns:
            bool: True se o estado é inedito, False caso contrário.
        """
        if estado_futuro.linha not in self.ambiente_crencas:
            return True
        if estado_futuro.coluna not in self.ambiente_crencas[estado_futuro.linha]:
            return True
        return False

    def set_sinais_vitais_vitima(self, chave_posicao: str, sinais_vitais: list):
        """Salva os sinais vitais da vítima de acordo com a sua posição no ambiente.

        Args:
            chave_posicao (str): chave da posição da vítima.
            sinais_vitais (list): sinais vitais da vítima.
        """
        if self.verifica_vitima_inedita(chave_posicao):
            self.sinais_vitais_vitimas[chave_posicao] = sinais_vitais
        # print(self.sinais_vitais_vitimas)

    def verifica_vitima_inedita(self, chave_posicao: str) -> bool:
        """Verifica se a chave da posição passada está presente na chave do
            dicionário dos sinais vitais.

        Args:
            chave_posicao (str): chave que identifica a posição da vítima.
        Returns:
            bool: True se a vítima nunca foi encontrada, False caso contrário.
        """
        return chave_posicao not in self.sinais_vitais_vitimas
