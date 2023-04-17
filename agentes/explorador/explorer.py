"""## EXPLORER AGENT
### @Author: Tacla, UTFPR
### It walks randomly in the environment looking for victims.
"""

#PLANOS POSSÍVEIS PARA O AGENTE EXPLORADOR
from agentes.explorador.planos.aleatorio import PlanoAleatorio
from agentes.explorador.planos.retorno import PlanoRetornoBase

from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from agentes.resgate.rescuer import Rescuer


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

        # Inicializações específicas para o agente de resgate
        self.resc: Rescuer = resc # Referência ao agente de resgate
        self.rtime: float = self.TLIM # Tempo restante para explorar

        # Instancia o plano de exploração às cegas
        self.plano_aleatorio = PlanoAleatorio()
        # Instancia o plano de retorno à base (A*)
        self.plano_retorno_base = PlanoRetornoBase()

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        # Indica o que tem na posição atual do explorador
        condicao_posicao_atual: str = ''
        # Indica se o explorador deve continuar ou parar a exploração
        flag_exploracao_ativa = True
        # Indica se a vítima já teve seus sinais vitais lidos ou não
        flag_nova_vitima = False
        # Indica se o explorador trocou de posição
        explorador_movimentou: bool = True

        if self.plano_retorno_base.verifica_retorno_base():
            flag_exploracao_ativa = False

        if self.rtime < 10.0:
            # time to wake up the rescuer and pass the walls and the victims (here, they're empty)
            print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
            self.resc.go_save_victims([],[])
            return False

        if flag_exploracao_ativa:
            # Escolhe o próximo passo a ser realizado
            passo_atual = self.plano_aleatorio.escolhe_variacao_posicao()
            # Adiciona o passo_atual ao histórico de passos realizados
            self.plano_aleatorio.passos_anteriores.append(passo_atual)
        else:
            passo_atual = self.plano_retorno_base.escolhe_variacao_posicao()

        # Movimenta o explorador para outra posição
        result = self.body.walk(
            passo_atual['coluna'], # passo_atual['coluna'] == dx
            passo_atual['linha'] # passo_atual['linha'] == dy
        )

        self.__atualiza_tempo_restante(passo_atual)

        # Test the result of the walk action
        if result == PhysAgent.BUMPED:
            condicao_posicao_atual = 'w'
            explorador_movimentou = False

        if result == PhysAgent.EXECUTED:
            # Verifica se tem vítimas retornando o número sequencial (>=0) da mesma
            id_vitima = self.body.check_for_victim()
            if id_vitima >= 0:
                condicao_posicao_atual = 'v'

        # Não encontrou vítima, nem parede ou limite, portanto a posição atual está vazia
        if condicao_posicao_atual == '':
            condicao_posicao_atual = 'e'

        # Verifica se houve movimentação, atualiza as crenças do agente explorador
        if flag_exploracao_ativa:
            if explorador_movimentou:
                # Veriica se a vítima é inédita
                if (
                    condicao_posicao_atual == 'v'
                    and self.plano_aleatorio.eh_nova_vitima(passo_atual)
                ):
                    flag_nova_vitima = True

                self.plano_aleatorio.atualiza_estado_atual(passo_atual)
                self.plano_aleatorio.adiciona_posicao_mapa(condicao_posicao_atual)

                # Leitura dos sinais vitais da nova vítima
                if flag_nova_vitima:
                    sinais_vitais = self.body.read_vital_signals(id_vitima)
                    # Aplica o custo de leitura dos sinais vitais no tempo
                    self.rtime -= self.COST_READ

                    print("exp: read vital signals of " + str(id_vitima))
                    print(sinais_vitais)
                    self.plano_aleatorio.adiciona_sinais_vitais_vitima(sinais_vitais)
            else:
                self.plano_aleatorio.adiciona_parede_ou_limite_mapa(
                    passo_atual,
                    condicao_posicao_atual
                )

        return True

    def __atualiza_tempo_restante(self, passo_atual: dict) -> None:
        """Faz a atualização do tempo restante conforme a movimentação decidida
            pelo explorador.

        - Custo de tempo de movimentos na mesma linha (vertical/horizontal) depende do ambiente.
        - Custo de tempo de movimentos nas diagonais depende do ambiente.

        Args:
            passo_atual (dict): variação das posições nos eixos x e y.
        """
        if passo_atual['linha'] != 0 and passo_atual['coluna'] != 0:
            self.rtime -= self.COST_DIAG
        else:
            self.rtime -= self.COST_LINE
