from random import choice
from agentes.utils.estado import Estado
from agentes.utils.problema import Problema


class PlanoAleatorio():
    """Representa o plano de execução aleatório do agente explorador
        para sua exploração sem informações do ambiente.
    """

    def __init__(
            self,
            estado_inicial: Estado = Estado(0, 0),
            estado_atual: Estado = Estado(0, 0)
        ) -> None:
        """Define o plano aleatório tendo como base a posição inicial do agente.

        Args:
            estado_inicial (Estado, optional): Estado da base do agente. Default: Estado(0, 0).
            estado_atual (Estado, optional): Estado inicial do agente. Default: Estado(0, 0).
        """
        # Estados relacionados ao plano (inicial e atual)
        self.estado_inicial = estado_inicial
        self.estado_atual = estado_atual
        self.passo_realizado = {'linha': 0, 'coluna': 0}

        # Variávies associadas ao plano
        self.passos_anteriores: list[Estado] = []
        self.direcoes_possiveis = {
            'O': {'linha': 0, 'coluna': -1},      # Oeste
            'N': {'linha': -1, 'coluna': 0},      # Norte
            'S': {'linha': 1, 'coluna': 0},       # Sul
            'L': {'linha': 0, 'coluna': 1},       # Leste
            'NO': {'linha': -1, 'coluna': -1},    # Noroeste
            'SO': {'linha': 1, 'coluna': -1},     # Sudoeste
            'SD': {'linha': 1, 'coluna': 1},      # Sudeste
            'ND': {'linha': -1, 'coluna': 1},     # Noreste
        }

        # Estrutura do problema
        self.problema = Problema()

    def escolhe_variacao_posicao(self) -> dict[str, int]:
        """Decide qual a variação da posição em cada eixo da posição do explorador.
        """
        # Lista com as direções que a partir da posição atual resultam em posições não visitadas
        direcoes_nao_visitadas = [
            direcao for direcao, passo_direcao in self.direcoes_possiveis.items()
            if (self.__verifica_estado_inedito(
                self.__calcula_proximo_estado(passo_direcao)
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
        return self.direcoes_possiveis[direcao_escolhida]

    def __calcula_proximo_estado(self, passo: dict[str, int]) -> Estado:
        """Efetua o cálculo para o agente verificar qual será a sua nova posição no mapa.

        Args:
            passo (dict[str, int]): passo que o agente tenta relizar.

        Returns:
            Estado: a sua nova posição caso o passo seja bem sucedido.
        """
        estado = Estado()
        estado.linha = self.estado_atual.linha + passo['linha']
        estado.coluna = self.estado_atual.coluna + passo['coluna']
        return estado

    def __verifica_estado_inedito(self, estado_futuro: Estado) -> bool:
        """Verifica se a posição ainda não foi visitada no mapa.

        Args:
            estado_futuro (Estado): objeto Estado que representa a possível
                futura nova posição atual do agente.
        
        Returns:
            bool: True se o estado é inedito, False caso contrário.
        """
        if estado_futuro.linha not in self.problema.crencas_ambiente:
            return True
        if estado_futuro.coluna not in self.problema.crencas_ambiente[estado_futuro.linha]:
            return True
        return False

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

        lista_keys_direcoes_possiveis = list(self.direcoes_possiveis.keys())
        return choice(lista_keys_direcoes_possiveis)

    def atualiza_estado_atual(self, passo_realizado: Estado):
        """Atualiza o estado atual do explorador para ele mesmo em seu plano.

        Args:
            passo_realizado (dict[str, int]): variação da posição para linha e coluna.
        """
        self.passo_realizado = passo_realizado
        self.estado_atual.linha += self.passo_realizado['linha']
        self.estado_atual.coluna += self.passo_realizado['coluna']

    def adiciona_posicao_mapa(self, condicao: str) -> None:
        """Inclui uma posição e seu conteúdo nas crenças do ambiente para o agente.

        Args:
            condicao (str): conteúdo da posição visitada pelo agente.
        """
        if self.__verifica_estado_inedito(self.estado_atual):
            self.problema.atualiza_crenca_posicao_ambiente(
                self.passo_realizado,
                self.estado_atual,
                condicao
            )

    def adiciona_parede_ou_limite_mapa(
        self,
        passo_utilizado: dict[str, int],
        condicao: str
    ) -> None:
        """Inclui uma posição bloqueada nas crenças do ambiente para o agente.

        Args:
            passo_utilizado (dict[str, int]): passo utilizado para chegar na posição bloqueada.
            condicao (str): 
        """
        # Obtêm o objeto Estado para o estado bloqueado
        estado_bloqueado = self.__calcula_proximo_estado(passo_utilizado)
        if self.__verifica_estado_inedito(estado_bloqueado):
            self.problema.atualiza_crenca_posicao_ambiente(
                passo_utilizado,
                estado_bloqueado,
                condicao
            )

    def eh_nova_vitima(self, passo_utilizado: dict[str, int]) -> bool:
        """Retorna um booleano indicando se a vítima encontrada é uma nova vítima.

        Args:
            passo_utilizado (dict[str, int]): passo utilizado para achar a nova posição.

        Returns:
            bool: True se é uma nova vítima, False caso contrário.
        """
        pos_linha = str(self.estado_atual.linha + passo_utilizado['linha'])
        pos_coluna = str(self.estado_atual.coluna + passo_utilizado['coluna'])
        chave_posicao = pos_linha + ':' + pos_coluna

        return self.problema.chave_posicao_vitima_ausente(chave_posicao)


    def adiciona_sinais_vitais_vitima(self, sinais_vitais: list) -> None:
        """Inclui a chave da posição e os sinais vitais da vítima no problema. 

        Args:
            sinais_vitais (list): vetor que identifica a vítima e seus sinais vitais.
        """
        posicao_chave = str(self.estado_atual.linha) + ':' + str(self.estado_atual.coluna)
        self.problema.set_sinais_vitais_vitima(posicao_chave, sinais_vitais)
