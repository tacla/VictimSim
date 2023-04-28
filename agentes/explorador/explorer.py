"""## EXPLORER AGENT
### @Author: Tacla, UTFPR
### It walks randomly in the environment looking for victims.
"""

#PLANOS POSSÍVEIS PARA O AGENTE EXPLORADOR
from agentes.explorador.planos.aleatorio import PlanoAleatorio
from agentes.explorador.planos.exploracao_dfs import ExploracaoDFS
from agentes.explorador.planos.retorno import PlanoRetornoBase

# PROBLEMA A SER DESENVOLVIDO PELO AGENTE EXPLORADOR
from agentes.utils.problema import Problema
from agentes.utils.estado import Estado

from abstract_agent import AbstractAgent
from physical_agent import PhysAgent
from agentes.resgate.rescuer import Rescuer


class Explorer(AbstractAgent):
    """Classe que define um agente explorador no ambiente e suas deliberações.
    """

    def __init__(self, env, config_file: str, resc: Rescuer):
        """Construtor do agente explorador.

        Args:
            env (_type_): referencia ao ambiente em que os agentes estão situados.
            config_file (str): path absoluto para arquivos de configuração do explorador.
            resc (Rescuer): referência ao agente de resgate para poder acordá-lo.
        """
        self.body: PhysAgent
        super().__init__(env, config_file)

        # Inicializações específicas para o agente de resgate
        self.agente_resgate: Rescuer = resc # Referência ao agente de resgate
        self.rtime: float = self.TLIM # Tempo restante para explorar

        # Indica se o explorador deve continuar ou parar a exploração
        self.flag_exploracao_ativa = True

        # Estado que representa a posição atual do agente explorador
        self.estado_atual: Estado = Estado()
        # Problema a ser elaborado através das descobertas do agente explorador
        self.problema: Problema = Problema()

        # Instancia o plano de exploração às cegas
        # self.plano_aleatorio = PlanoAleatorio()
        self.plano_aleatorio = ExploracaoDFS()
        # Instancia o plano de retorno à base (A*)
        self.plano_retorno_base = PlanoRetornoBase()

    def deliberate(self) -> bool:
        """ The agent chooses the next action. The simulator calls this
        method at each cycle. Must be implemented in every agent"""
        # Indica o que tem na posição atual do explorador
        condicao_posicao_atual: str = ''
        # Indica se o explorador trocou de posição
        explorador_movimentou: bool = True

        if (self.flag_exploracao_ativa and self.plano_retorno_base.verifica_retorno_base(
                self.problema,
                self.estado_atual.get_chave_posicao(),
                self.rtime,
            )
        ):
            self.flag_exploracao_ativa = False

        if (not self.flag_exploracao_ativa
            and self.estado_atual.get_chave_posicao() == '0:0'
        ):
            # time to wake up the rescuer and pass the walls and the victims (here, they're empty)
            print(f"{self.NAME} I believe I've remaining time of {self.rtime:.1f}")
            self.agente_resgate.go_save_victims(self.problema)
            return False

        if self.flag_exploracao_ativa:
            # Escolhe o próximo passo a ser realizado
            passo_atual = self.plano_aleatorio.escolhe_variacao_posicao(
                self.problema,
                self.estado_atual
            )
            if type(passo_atual) == bool:
                passo_atual = {'linha': 0, 'coluna': 0}
                self.flag_exploracao_ativa = False

            # Adiciona o passo_atual ao histórico de passos realizados
            self.plano_aleatorio.passos_anteriores.append(passo_atual)
        else:
            passo_atual = self.plano_retorno_base.escolhe_variacao_posicao()

        # Movimenta o explorador para outra posição
        result = self.body.walk(
            dy = passo_atual['linha'],
            dx = passo_atual['coluna']
        )

        self.__atualiza_tempo_restante(passo_atual)

        # Test the result of the walk action
        if result == PhysAgent.BUMPED:
            condicao_posicao_atual = 'w'
            self.plano_aleatorio.unbacktracked.pop()
            explorador_movimentou = False

        if result == PhysAgent.EXECUTED:
            # Verifica se tem vítimas retornando o número sequencial (>=0) da mesma
            id_vitima = self.body.check_for_victim()
            if id_vitima >= 0:
                condicao_posicao_atual = 'v'

        # Verifica se houve movimentação, atualiza as crenças do agente explorador
        if self.flag_exploracao_ativa:
            # Não encontrou vítima, nem parede ou limite, portanto a posição atual está vazia
            if condicao_posicao_atual == '':
                condicao_posicao_atual = 'e'

            if explorador_movimentou:
                self.__atualiza_estado_atual(passo_atual)
                self.problema.atualiza_crenca_posicao_ambiente(
                    passo_usado = passo_atual,
                    posicao_atual = self.estado_atual,
                    descricao = condicao_posicao_atual
                )

                # Leitura dos sinais vitais da vítima se for inédita ao problema
                if (condicao_posicao_atual == 'v'
                    and self.problema.verifica_vitima_inedita(
                        self.estado_atual.get_chave_posicao()
                    )
                ):
                    # Faz a leitura dos sinais vitais da vítima
                    sinais_vitais = self.body.read_vital_signals(id_vitima)
                    # Aplica o custo de leitura dos sinais vitais no tempo
                    self.rtime -= self.COST_READ

                    print("exp: read vital signals of " + str(id_vitima))
                    # print(sinais_vitais)
                    self.problema.set_sinais_vitais_vitima(
                        self.estado_atual.get_chave_posicao(),
                        sinais_vitais
                    )
            else:
                self.problema.atualiza_crenca_posicao_ambiente(
                    passo_usado = passo_atual,
                    posicao_atual = self.estado_atual,
                    descricao = condicao_posicao_atual
                )
        else:
            if explorador_movimentou:
                self.__atualiza_estado_atual(passo_atual)

        return True

    def __atualiza_estado_atual(self, passo_realizado: dict[str, int]) -> None:
        """Atualiza o estado atual do explorador para ele mesmo.

        Args:
            passo_realizado (dict[str, int]): variação da posição para linha e coluna.
        """
        self.estado_atual.linha += passo_realizado['linha']
        self.estado_atual.coluna += passo_realizado['coluna']

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
