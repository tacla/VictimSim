"""##  RESCUER AGENT
### @Author: Tacla (UTFPR)
### Demo of use of VictimSim
"""
from abstract_agent import AbstractAgent
from physical_agent import PhysAgent

# Módulos do problema e do estado
from agentes.utils.problema import Problema
from agentes.utils.estado import Estado

# Módulo do plano do agente
from agentes.resgate.planos.resgate_genetico import PlanoResgateGenetico
from agentes.explorador.planos.retorno import PlanoRetornoBase

class Rescuer(AbstractAgent):
    """Classe que define o Agente Rescuer com um plano fixo
    """

    def __init__(self, env, config_file):
        """ 
        @param env: a reference to an instance of the environment class
        @param config_file: the absolute path to the agent's config file"""

        super().__init__(env, config_file)

        # Specific initialization for the rescuer
        self.plan = []              # a list of planned actions
        self.rtime = self.TLIM      # for controlling the remaining time

        # Starts in IDLE state.
        # It changes to ACTIVE when the map arrives
        self.body.set_state(PhysAgent.IDLE)

        # Informações do mapa e vítimas no problema
        self.problema: Problema = None
        self.estado_atual: Estado = Estado()

        self.flag_resgate_ativo: bool = True
        self.vitimas_resgatadas: list[str] = []

        # Planos do agente de resgate
        self.plano_genetico: PlanoResgateGenetico = None
        self.plano_retorno: PlanoRetornoBase = PlanoRetornoBase()


    def go_save_victims(self, problema_montado: Problema):
        """ The explorer sends the map containing the walls and
        victims' location. The rescuer becomes ACTIVE. From now,
        the deliberate method is called by the environment
        
        Args: 
            problema (Problema): problema contendo as informações do mapa e vítimas."""
        self.body.set_state(PhysAgent.ACTIVE)
        self.problema = problema_montado

        self.plano_genetico = PlanoResgateGenetico(
            self.problema,
            self.rtime
        )
        self.plan = self.plano_genetico.executar()

    def deliberate(self) -> bool:
        """ This is the choice of the next action. The simulator calls this
        method at each reasonning cycle if the agent is ACTIVE.
        Must be implemented in every agent
        @return True: there's one or more actions to do
        @return False: there's no more action to do """

        if (self.flag_resgate_ativo and self.plano_retorno.verifica_retorno_base(
                self.problema,
                self.estado_atual.get_chave_posicao(),
                self.rtime,
            )
        ):
            self.flag_resgate_ativo = False

        if (not self.flag_resgate_ativo
            and self.estado_atual.get_chave_posicao() == '0:0'
        ):
            print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
            return False

        # No more actions to do
        if not self.plan:  # empty list, no more actions to do
            return False

        if self.flag_resgate_ativo:
            passo_linha, passo_coluna = self.plan.pop()
        else:
            dict_passo = self.plano_retorno.escolhe_variacao_posicao()
            passo_linha = dict_passo['linha']
            passo_coluna = dict_passo['coluna']

        # Atualiza a posição atual do agente para ele mesmo
        self.atualiza_estado_atual(passo_linha, passo_coluna)

        # Walk - just one step per deliberation
        result = self.body.walk(passo_coluna, passo_linha)

        # Atualiza o tempo restante do agente para cálculos de retorno à base
        self.__atualiza_tempo_restante(passo_linha, passo_coluna)

        # Rescue the victim at the current position
        if self.estado_atual.get_chave_posicao() in self.problema.sinais_vitais_vitimas:
            if result == PhysAgent.EXECUTED:
                # check if there is a victim at the current position
                seq = self.body.check_for_victim()
                if (
                    self.estado_atual.get_chave_posicao() not in self.vitimas_resgatadas
                    and seq >= 0
                ):
                    res = self.body.first_aid(seq) # True when rescued
                    self.rtime -= 1.0
                    self.vitimas_resgatadas.append(self.estado_atual.get_chave_posicao())

        return True

    def atualiza_estado_atual(self, passo_linha: int, passo_coluna: int) -> None:
        """Realiza a atuliação do estado atual do agente explorador para ele mesmo.

        Args:
            passo_linha (int): variação da posição do agente na linha.
            passo_coluna (int): variação da posição do agente na coluna.
        """
        self.estado_atual.linha += passo_linha
        self.estado_atual.coluna += passo_coluna

    def __atualiza_tempo_restante(self, passo_linha: int, passo_coluna: int) -> None:
        """Faz a atualização do tempo restante conforme a movimentação decidida
            pelo explorador.

        - Custo de tempo de movimentos na mesma linha (vertical/horizontal) depende do ambiente.
        - Custo de tempo de movimentos nas diagonais depende do ambiente.

        Args:
            passo_atual (dict): variação das posições nos eixos x e y.
        """
        if passo_linha != 0 and passo_coluna != 0:
            self.rtime -= self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE
