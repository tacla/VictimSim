"""## EXPLORER AGENT
### @Author: Tacla, UTFPR
### It walks randomly in the environment looking for victims.
"""

from random import choice
from rescuer import Rescuer
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent

class Explorer(AbstractAgent):
    """Classe que define um agente explorador no ambiente e suas deliberações.
    """

    def __init__(self, env, config_file: str, resc: Rescuer):
        """ Construtor do agente random on-line
        @param env referencia o ambiente
        @config_file: the absolute path to the explorer's config file
        @param resc referencia o rescuer para poder acorda-lo
        """
        self.body: PhysAgent
        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.resc: Rescuer = resc # reference to the rescuer agent
        self.rtime: float = self.TLIM # remaining time to explore

        self.__inicializa_mapa()

    def __inicializa_mapa(self) -> None:
        """Realiza a inicialização de atributos para o correto funcionamento do mapa."""
        self.direcoes_possiveis = {
            'NO':{'x':-1, 'y':-1},    # Noroeste
            'O':{'x':-1, 'y':0},      # Oeste
            'SO':{'x':-1, 'y':1},     # Sudoeste
            'S':{'x':0, 'y':1},       # Sul
            'SD':{'x':1, 'y':1},      # Sudeste
            'L':{'x':1, 'y':0},       # Leste
            'ND':{'x':1, 'y':-1},     # Noreste
            'N':{'x':0, 'y':-1}       # Norte
        }

        self.passos_anteriores: list = []
        self.posicao_atual: dict = {'x':0, 'y':0}
        self.mapa: dict = {f"{self.posicao_atual['x']}:{self.posicao_atual['y']}":'b'}

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""

        # Variável auxiliar para indicar o que tem na posição atual do explorador
        condicao_posicao_atual: str = ''

        # Variável auxiliar para indicar se o explorador trocou de posição
        explorador_movimentou: bool = True

        # TODO: função pra ver se o agente volta pra base considerando o tempo restante e dist.
        if self.rtime < 10.0:
            # time to wake up the rescuer and pass the walls and the victims (here, they're empty)
            print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
            self.resc.go_save_victims([],[])

            return False

        passo_atual = self.escolhe_variacao_posicao()

        # Adiciona o passo_atual ao histórico de passos realizados
        self.passos_anteriores.append(passo_atual)

        # Movimenta o explorador para outra posição
        result = self.body.walk(passo_atual['x'], passo_atual['y'])

        self.__atualiza_tempo_restante(passo_atual)

        # Test the result of the walk action
        if result == PhysAgent.BUMPED:
            condicao_posicao_atual = 'w'
            explorador_movimentou = False
            # walls = 1  # build the map- to do
            # print(self.name() + ": wall or grid limit reached")

        if result == PhysAgent.EXECUTED:
            # Verifica se tem vítimas retornando o número sequencial (>=0) da mesma
            seq = self.body.check_for_victim()
            if seq >= 0:
                _ = self.body.read_vital_signals(seq)
                self.rtime -= self.COST_READ
                # print("exp: read vital signals of " + str(seq))
                # print(sinais_vitais)
                condicao_posicao_atual = 'v'

        # Não encontrou vítima, nem parede ou limite, portanto a posição atual está vazia
        if condicao_posicao_atual == '':
            condicao_posicao_atual = 'e'

        # Verifica se houve movimentação, atualiza o conhecimento do agente explorador
        if explorador_movimentou:
            self.atualiza_posicao_atual(passo_atual)
            if self.verifica_posicao_inedita(self.posicao_atual):
                self.adiciona_nova_posicao_mapa(condicao_posicao_atual)
        else:
            self.adiciona_nova_parede_ou_limite_mapa(passo_atual, condicao_posicao_atual)

        print(self.passos_anteriores)
        print(self.mapa)

        return True

    def escolhe_variacao_posicao(self) -> dict[str, int]:
        """Decide qual a variação da posição em cada eixo da posição do explorador.
        """
        # Lista com as direções que a partir da posição atual resultam em posições não visitadas
        direcoes_nao_visitadas = [
            direcao for direcao, passo_direcao in self.direcoes_possiveis.items()
            if (
                self.verifica_posicao_inedita(
                    self.calcula_proxima_posicao(passo_direcao)
                )
            )
        ]

        # Escolhe entre as direções que resultam em posições que ainda não foram visitadas
        if direcoes_nao_visitadas:
            direcao_escolhida = choice(direcoes_nao_visitadas)
        else:
            direcao_escolhida = choice(list(self.direcoes_possiveis.keys()))

        # Define o passo com base na direção escolhida
        passo_x = self.direcoes_possiveis[direcao_escolhida]['x']
        passo_y = self.direcoes_possiveis[direcao_escolhida]['y']

        # Retorna o passo escolhido para executar a movimentação
        return {'x': passo_x, 'y': passo_y}

    def __atualiza_tempo_restante(self, passo_atual: dict) -> None:
        """Faz a atualização do tempo restante conforme a movimentação decidida
            pelo explorador.

        - Custo de tempo de movimentos na mesma linha (vertical/horizontal) depende do ambiente.
        - Custo de tempo de movimentos nas diagonais depende do ambiente.

        Args:
            passo_atual (dict): variação das posições nos eixos x e y.
        """
        if passo_atual['y'] != 0 and passo_atual['y'] != 0:
            self.rtime -= self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE

    def atualiza_posicao_atual(self, passo: dict) -> None:
        """Atualiza a posição atual do explorador para ele mesmo.

        Args:
            passo_atual (dict): variação da posição nos eixos x e y.
        """
        posicao_atual = self.calcula_proxima_posicao(passo)
        self.posicao_atual['x'] = posicao_atual['x']
        self.posicao_atual['y'] = posicao_atual['y']

    def calcula_proxima_posicao(self, passo: dict) -> dict[str, int]:
        """Efetua o cálculo para o agente saber qual será a sua nova posição no mapa.

        Args:
            passo (dict): passo que o agente tenta relizar.

        Returns:
            dict[str, int]: a sua nova posição caso o passo seja bem sucedido.
        """
        posicao = {}
        posicao['x'] = self.posicao_atual['x'] + passo['x']
        posicao['y'] = self.posicao_atual['y'] + passo['y']
        return posicao

    def verifica_posicao_inedita(self, posicao) -> bool:
        """Verifica se a posição ainda não foi visitada no mapa.

        Returns:
            bool: True se a posicao é nova, False caso já tenha sido visitada.
        """
        print(self.mapa.keys())
        if f"{posicao['x']}:{posicao['y']}" not in list(self.mapa.keys()):
            return True
        return False

    def adiciona_nova_posicao_mapa(self, condicao_posicao: str) -> None:
        """Inclui a nova posição no mapa.
        """
        self.mapa[f"{self.posicao_atual['x']}:{self.posicao_atual['y']}"] = condicao_posicao

    def adiciona_nova_parede_ou_limite_mapa(self, passo: dict, condicao: str) -> None:
        """Adiciona no mapa as paredes ou limites do mapa.

        Args:
            passo (dict): tentativa de passo realizada pelo agente.
            condicao (str): condicao da posição encontrada a frente.
        """
        proxima_posicao = self.calcula_proxima_posicao(passo)
        self.mapa[f"{proxima_posicao['x']}:{proxima_posicao['y']}"] = condicao
