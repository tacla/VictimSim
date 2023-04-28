from random import randint
from random import choice
from agentes.utils.estado import Estado
from agentes.utils.problema import Problema

class ExploracaoDFS:
    """Representa o plano de execução aleatório do agente explorador
        para sua exploração sem informações do ambiente.
    """

    def __init__(self) -> None:
        """Define o plano aleatório tendo como base a posição inicial do agente.
        """
        # Estados relacionados ao plano (inicial e atual)
        # self.estado_inicial = estado_inicial
        # self.estado_atual = estado_atual
        # self.passo_realizado = {'linha': 0, 'coluna': 0}

        # Variávies associadas ao plano
        self.passos_anteriores: list[Estado] = []
        self.direcoes_possiveis = {
            'O': {'linha': 0, 'coluna': -1},      # Oeste
            'N': {'linha': -1, 'coluna': 0},      # Norte
            'S': {'linha': 1, 'coluna': 0},       # Sul
            'L': {'linha': 0, 'coluna': 1},       # Leste
        }

        # Estrutura do problema
        # self.problema = Problema()

        self.actions = ["S", "L", "N", "O"]
        self.untried = dict()  # mostra um array de ações ainda não tentadas no estado
        self.unbacktracked = []  # mostra uma fila de estados que levaram ao estado s
        self.result = {}  # mostra o estado resultado s' após executar ação a partir de s

    def escolhe_variacao_posicao(
            self,
            problema_atual: Problema,
            estado_atual: Estado
        ) -> dict[str, int]:
        """Decide qual a variação da posição em cada eixo da posição do explorador.

        Args:
            problema_atual (Problema): usado para verificar se uma próxima posição é inédita.
            estado_atual (Estado): usado para calcular as possíveis próximas posições.
        """

        # Lista com as direções que a partir da posição atual resultam em posições não visitadas
        direcoes_nao_visitadas = self.__escolhe_direcao_possivel_todas_escolhidas(estado_atual, problema_atual)

        # Escolhe entre as direções que resultam em posições que ainda não foram visitadas
        if direcoes_nao_visitadas:
            rand = randint(0, len(direcoes_nao_visitadas)-1)
            direcao_escolhida = direcoes_nao_visitadas[rand]
            self.unbacktracked.append(direcao_escolhida)
            direcoes_nao_visitadas.pop(rand)
            self.untried[str(estado_atual)] = direcoes_nao_visitadas
            # print(direcoes_nao_visitadas)
            # print(self.unbacktracked)
        # Caso não tenha posição não visitada, escolhe qualquer uma entre todas
        else:
            if self.unbacktracked:
                ultima_direcao = self.unbacktracked.pop()
            else:
                return True
            # print('desempilhado -> ',ultima_direcao)          # Preciso andar até está direção que saiu da pilha e ver se lá tem caminho livre, usando a função self.__escolhe_direcao_possivel_todas_escolhidas()
                # Aqui ele precisa anda para a posição q desempilhou mas acho q tem condição pra ele ve se já andou la no explorer por isso nao vai

            direcao_escolhida = self.escolhe_direcao_oposta(ultima_direcao)
            # print('andou-> ', direcao_escolhida)

            return self.direcoes_possiveis[direcao_escolhida]
        # Retorna o passo escolhido para executar a movimentação
        return self.direcoes_possiveis[direcao_escolhida]
    
    def escolhe_direcao_oposta(self, ultima_direcao):
        if ultima_direcao == 'O':
            return 'L'
        if ultima_direcao == 'L':
            return 'O'
        if ultima_direcao == 'N':
            return 'S'
        if ultima_direcao == 'S':
            return 'N'

    def __calcula_proximo_estado(self, estado_atual: Estado, passo: dict[str, int]) -> Estado:
        """Efetua o cálculo para o agente verificar qual será a sua nova posição no mapa.

        Args:
            passo (dict[str, int]): passo que o agente tenta relizar.

        Returns:
            Estado: a sua nova posição caso o passo seja bem sucedido.
        """
        estado_futuro = Estado()
        estado_futuro.linha = estado_atual.linha + passo['linha']
        estado_futuro.coluna = estado_atual.coluna + passo['coluna']
        return estado_futuro

    def __escolhe_direcao_possivel_todas_escolhidas(self, estado_atual: Estado, problema: Problema) -> list:
        """Escolhe uma direção entre as direções possíveis quando
            todas as direções já foram exploradas.

        - Evita paredes;
        - Busca nas posições adjacentes próximas qual a direção com a posição
            que possui uma direção que leva a uma posição ainda não visitada.

        Returns:
            str: direção escolhida (chave do dicionário direcoes_possiveis).
        """
        # TODO: evitar paredes
        # TODO: busca nas posições adjacentes...

        direcoes_nao_visitadas = [
            direcao for direcao, passo_direcao in self.direcoes_possiveis.items()
            if (problema.verifica_estado_inedito(
                    self.__calcula_proximo_estado(estado_atual, passo_direcao)
                )
            )
        ]

        return direcoes_nao_visitadas
