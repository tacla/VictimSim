from agentes.utils.estado import Estado

class Problema:
    """Problema a ser resolvido pelo agente.

    Contém os atributos:
        - posicao_base (Estado): par ordenado que indica a posicao inicial do agente.
        - posicao_objetivo (Estado): par ordenado que indica o estado objetivo.
        - crencas_ambiente (dict[int, dict[int, int]]): posições do ambiente e seu conteúdo.
    """
    def __init__(self) -> None:
        self.posicao_base = Estado(0, 0)
        self.posicao_objetivo = Estado(0, 0)

        self.tamanho_max_linhas = 1
        self.tamanho_max_colunas = 1

        # Crenças do ambiente: {linha: {coluna: 'descricao'}}
        self.crencas_ambiente: dict[int, dict[int, int]] = {0: {0: 'b'}}
        self.crenca_grafo: dict[str, list[str]] = {'0:0': []}

        # Sinais vitais das vítimas: {id_vitima: [s.i, i.n, a.i, s.v, i.t, a.i, s]}
        self.sinais_vitais_vitimas: dict[int, list[float]] = {}

    def set_posicao_base(self, linha: int, coluna: int) -> None:
        """Define a posição inicial do problema a ser resolvido.

        Args:
            linha (int): linha da posição inicial.
            coluna (int): coluna da posição inicial.
        """
        self.posicao_base.linha = linha
        self.posicao_base.coluna = coluna

    def set_posicao_objetivo(self, linha: int, coluna: int) -> None:
        """Define a posição de objetivo para se chegar.

        Args:
            linha (int): linha da posição objetivo.
            coluna (int): coluna da posição objetivo.
        """
        self.posicao_objetivo.linha = linha
        self.posicao_objetivo.coluna = coluna

    def set_crencas_ambiente(self, crencas: dict[str, dict[str, int]]) -> None:
        """Define crenças já descobertas para resolver o problema.

        Args:
            crencas (dict[str, dict[str, int]]): cren
        """
        self.crencas_ambiente = crencas

    def atualiza_crenca_posicao_ambiente(
            self,
            passo: dict[str, int],
            posicao: Estado,
            descricao: str
        ) -> None:
        """Atualiza a crença de uma posição do ambiente com o que foi encontrado nela.

        Args:
            posicao (Estado): ojbeto Estado que identifica a posição.
            descricao (str): descrição do que foi encontrado na posição.
        """
        if descricao != 'w':
            chave = str(posicao.linha)+':'+str(posicao.coluna)
            if chave not in self.crenca_grafo:
                self.crenca_grafo[chave] = []

            posicao_anterior = Estado()
            posicao_anterior.linha = posicao.linha - passo['linha']
            posicao_anterior.coluna = posicao.coluna - passo['coluna']

            chave_anterior = str(posicao_anterior.linha)+':'+str(posicao_anterior.coluna)
            self.crenca_grafo[chave_anterior].append(chave)
            self.crenca_grafo[chave].append(chave_anterior)

            for chave, adj_chave in self.crenca_grafo.items():
                str_pos_chave = chave.split(':')
                for aux_chave in self.crenca_grafo:
                    if aux_chave == chave:
                        continue
                    if aux_chave in adj_chave:
                        continue
                    if aux_chave in self.obtem_adjacencias(str_pos_chave):
                        self.crenca_grafo[chave].append(aux_chave)
            print(posicao_anterior)
            print(posicao)
            print(self.crenca_grafo)

        if posicao.linha not in self.crencas_ambiente:
            self.crencas_ambiente[posicao.linha] = {}

        self.crencas_ambiente[posicao.linha][posicao.coluna] = descricao
        print(self.crencas_ambiente)

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
        lista_adjacencias.append(f"{str(linha - 1)}:{str(coluna)}") # (-1, 0)
        lista_adjacencias.append(f"{str(linha - 1)}:{str(coluna + 1)}") # (-1, 1)
        lista_adjacencias.append(f"{str(linha)}:{str(coluna - 1)}") # (0, -1)
        lista_adjacencias.append(f"{str(linha)}:{str(coluna + 1)}") # (0, 1)
        lista_adjacencias.append(f"{str(linha + 1)}:{str(coluna - 1)}") # (1, -1)
        lista_adjacencias.append(f"{str(linha + 1)}:{str(coluna)}") # (1, 0)
        lista_adjacencias.append(f"{str(linha + 1)}:{str(coluna + 1)}") # (1, 1)

        return lista_adjacencias

    def get_custo_acao(self, descricao_action: str) -> float:
        """Retorna o custo de determinada ação.

        Args:
            descricao_action (str): descrição da ação a ser realizada.

        Returns:
            float: custo da ação.
        """
        if descricao_action == 'nop':
            return 0

        if descricao_action == "checkVitalSignals":
            return 2.0

        if descricao_action in ("N", "L", "O", "S"):
            return 1.0
        return 1.5

    def tem_vitima_posicao(self, posicao: Estado) -> bool:
        """_summary_

        Args:
            posicao (Estado): _description_

        Returns:
            bool: True se há uma vítima na posição passada, False caso contrário.
        """
        return self.crencas_ambiente[posicao.linha][posicao.coluna] == 'vitima'

    def set_sinais_vitais_vitima(self, sinais_vitais: list):
        """Salva os sinais vitais da vítima de acordo com o seu número identificador.

        Args:
            sinais_vitais (list): sinais vitais da vítima.
        """
        self.sinais_vitais_vitimas[sinais_vitais[0]] = sinais_vitais
