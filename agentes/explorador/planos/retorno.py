from queue import PriorityQueue
from agentes.utils.problema import Problema

class PlanoRetornoBase:
    """Representa o plano de retorno à base do agente explorador
        para sua exploração de acordo com uma busca informada A*.
    """

    def __init__(self) -> None:
        """Define o plano de retorno à base, é recalculado à toda iteração.
        """
        # Trajeto a ser feito de volta à base
        self.trajeto_base: dict[str, dict[str, int]] = {}
        self.ordem_trajeto: list[str] = []

    def verifica_retorno_base(
            self,
            problema: Problema,
            chave_posicao_atual: str,
            tempo_restante: float
        ) -> bool:
        """Se necessário, volta para base pelo motivo de não ser possível 
            retornar na próxima interação do agente com o ambiente.

        Args:
            problema (Problema): problema a ser resolvido com o plano de retorno.
            chave_posicao_atual (str): chave que identifica a posição atual do agente.
            tempo_restante (float): tempo restante para executar suas ações.

        Returns:
            bool: True se é necessário volta para base, False caso contrário.
        """
        caminho_encontrado_atual = self.encontra_melhor_caminho_a_star(
            problema.grafo_posicoes,
            chave_posicao_atual
        )
        if caminho_encontrado_atual:
            # Verifica se o tempo é suficiente para voltar com uma taxa de sobre de +2.0
            if abs(tempo_restante - caminho_encontrado_atual['0:0']['custo']) <= 1.5:
                self.trajeto_base = caminho_encontrado_atual
                self.ordem_trajeto = list(self.trajeto_base.keys())
                return True
        return False

    def escolhe_variacao_posicao(self) -> dict[str, int]:
        """Decide qual a variação da posição em cada eixo da posição do agente explorador.

        Returns:
            dict[str, int]: dicionário com o passo para linha e coluna.
        """
        chave_proxima_posicao = self.ordem_trajeto.pop()

        passo_linha = self.trajeto_base[chave_proxima_posicao]['linha']
        passo_coluna = self.trajeto_base[chave_proxima_posicao]['coluna']

        return {'linha': passo_linha, 'coluna': passo_coluna}

    def encontra_melhor_caminho_a_star(
            self,
            grafo_posicoes: dict[str, list[str]],
            chave_posicao_inicial: str
        ) -> dict[str, dict[str, int]]:
        """Encontra o melhor caminho de menor custo por meio do gráfico gerado do problema
            e a posição em que o agente se encontra.

        Args:
            chave_posicao_inicial (str): chave em str da posição.

        Returns:
            dict[str, dict[str, int]]: caminho com as chave das posições, passos e custos.
        """
        fronteira = PriorityQueue()
        fronteira.put(chave_posicao_inicial, 0)
        posicao_anterior = {}
        custo_ate_agora = {}
        posicao_anterior[chave_posicao_inicial] = None
        custo_ate_agora[chave_posicao_inicial] = 0

        while not fronteira.empty():
            posicao_atual: str = fronteira.get()

            if posicao_atual == '0:0':
                break

            for proxima_posicao in grafo_posicoes[posicao_atual]:
                est_atual_linha, est_atual_coluna = map(int, posicao_atual.split(':'))
                est_proximo_linha, est_proximo_coluna = map(int, proxima_posicao.split(':'))
                custo = 0
                if (
                    (abs(est_atual_linha - est_proximo_linha) == 1)
                    and (abs(est_atual_coluna - est_proximo_coluna) == 1)
                ):
                    custo = 1.5
                else:
                    custo = 1.0
                novo_custo = custo_ate_agora[posicao_atual] + custo

                if (
                    proxima_posicao not in custo_ate_agora
                    or novo_custo < custo_ate_agora[proxima_posicao]
                ):
                    custo_ate_agora[proxima_posicao] = novo_custo
                    prioridade = novo_custo + abs(est_proximo_linha) + abs(est_proximo_coluna)

                    fronteira.put(proxima_posicao, prioridade)

                    posicao_anterior[proxima_posicao] = posicao_atual

        caminho = {}
        posicao_atual = '0:0'
        while posicao_atual != chave_posicao_inicial:
            pos_anterior: str = posicao_anterior[posicao_atual]

            est_anterior_linha, est_anterior_coluna = map(int, pos_anterior.split(':'))
            est_atual_linha, est_atual_coluna = map(int, posicao_atual.split(':'))

            passo_linha = est_atual_linha - est_anterior_linha
            passo_coluna = est_atual_coluna - est_anterior_coluna

            caminho[posicao_atual] = {
                'linha': passo_linha,
                'coluna': passo_coluna,
                'custo': custo_ate_agora[posicao_atual]
            }
            posicao_atual = pos_anterior

        return caminho
