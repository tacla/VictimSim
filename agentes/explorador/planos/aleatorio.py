from random import choice
from agentes.utils.estado import Estado
from agentes.utils.problema import Problema


class PlanoAleatorio():
    """Representa o plano de execução aleatório do agente explorador
        para sua exploração sem informações do ambiente.
    """

    def __init__(self) -> None:
        """Define o plano aleatório tendo como base a posição inicial do agente.

        Args:
            estado_atual (Estado, optional): Estado inicial do agente. Default: Estado(0, 0).
        """
        # Variávies associadas ao plano
        self.passos_anteriores: list[Estado] = []
        self.direcoes_possiveis_cruz = {
            'O': {'linha': 0, 'coluna': -1},      # Oeste
            'N': {'linha': -1, 'coluna': 0},      # Norte
            'S': {'linha': 1, 'coluna': 0},       # Sul
            'L': {'linha': 0, 'coluna': 1}       # Leste
        }
        self.direcoes_possiveis_todas = {
            'O': {'linha': 0, 'coluna': -1},      # Oeste
            'N': {'linha': -1, 'coluna': 0},      # Norte
            'S': {'linha': 1, 'coluna': 0},       # Sul
            'L': {'linha': 0, 'coluna': 1},       # Leste
            'NO': {'linha': -1, 'coluna': -1},    # Noroeste
            'SO': {'linha': 1, 'coluna': -1},     # Sudoeste
            'SD': {'linha': 1, 'coluna': 1},      # Sudeste
            'ND': {'linha': -1, 'coluna': 1}     # Noreste
        }

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
        direcoes_nao_visitadas = [
            direcao for direcao, passo_direcao in self.direcoes_possiveis_cruz.items()
            if (problema_atual.verifica_estado_inedito(
                    self.__calcula_proximo_estado(estado_atual, passo_direcao)
                )
            )
        ]

        # Escolhe entre as direções que resultam em posições que ainda não foram visitadas
        if direcoes_nao_visitadas:
            direcao_escolhida = choice(direcoes_nao_visitadas)
        # Caso não tenha posição não visitada, escolhe qualquer uma entre todas
        else:
            direcao_escolhida = self.__escolhe_direcao_possivel_todas_escolhidas()

        # Retorna o passo escolhido para executar a movimentação
        return self.direcoes_possiveis_todas[direcao_escolhida]

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

    def __escolhe_direcao_possivel_todas_escolhidas(self) -> str:
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

        lista_keys_direcoes_possiveis = list(self.direcoes_possiveis_todas.keys())
        return choice(lista_keys_direcoes_possiveis)
