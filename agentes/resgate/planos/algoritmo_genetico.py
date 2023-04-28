from random import choice, random, randint
from copy import deepcopy
from operator import add
from functools import reduce
from tqdm import tqdm
from agentes.utils.problema import Problema

class Individuo:
    def __init__(
            self,
            caminhos: dict[str, dict[str, list[tuple[str, int]]]],
            tempo_restante: float,
            max_subcaminhos: int
        ) -> None:
        self.tempo_restante: float = tempo_restante
        self.max_subcaminhos: int = max_subcaminhos
        self.qtd_subcaminhos: int = 0
        self.pontuacao: int = 0
        self.caminhos = caminhos
        self.caminhos_possiveis = []
        self.ja_visitados = []

        # GENES E INFORMAÇÕES CARACTERÍSTICAS
        self.genes: dict[str, list[tuple[str, str]] | int] = {
            'trajeto': [], # [(origem, destino1), (destino1, destino2), ..., (destino2, origem)]
            'peso_gravidade': 0,
            'peso_custo': 0
        }

        self.parametros_possiveis = {
            'peso_custo': [
                0.05, 0.1,
                0.15, 0.2,
                0.25, 0.3,
                0.35
            ],
            'peso_gravidade': [
                0.95, 0.9,
                0.85, 0.8,
                0.75, 0.7,
                0.65
            ]
        }

    def __str__(self) -> str:
        """Retorna o objeto representado por meio de uma saída de texto.

        Returns:
            str: indivíduo no formato para ser representado na saída de texto.
        """
        return f"Tamanho: {self.qtd_subcaminhos}\nGenes: {str(self.genes)}"

    def set_caracteristicas(self, caracteristicas: dict[str, float]) -> None:
        """Define as características de peso do indivíduo.

        Args:
            caracteristicas (dict[str, float]): dicionário com os pesos para função de fitness.
        """
        self.genes['peso_gravidade'] = caracteristicas['peso_gravidade']
        self.genes['peso_custo'] = caracteristicas['peso_custo']

    def set_trajeto(self, trajeto: list[tuple[str, str]]) -> None:
        """Atribui a sequência de sub-caminhos para um indivíduo.

        Args:
            trajeto (list[tuple[str, str]]): lista de sub-caminhos a ser atribuída.
        """
        self.genes['trajeto'] = trajeto

    def avalia_individuo(self, vitimas: dict[str, list[str]]):
        """Efetua a avaliação de um indivíduo, (aplica sua função de fitness).

        Args:
            vitimas (dict[str, list[str]]): as vítimas conhecidas no ambiente.
        """
        pontuacoes = []
        ordem_salvamento = self.qtd_subcaminhos + 1
        vitimas_salvas = {}

        for origem, destino in self.genes['trajeto']:
            if destino in vitimas and destino not in vitimas_salvas:
                gravidade = int(vitimas[destino][-1])
                gravidade_normalizada = ((4 - gravidade) + 1) * ordem_salvamento
                vitimas_salvas[destino] = deepcopy(vitimas[destino])
                self.tempo_restante -= 1
            else:
                gravidade_normalizada = 0
            ordem_salvamento -= 1

            custo_subcaminho = self.__obtem_custo_caminho(origem, destino)
            pontuacao_subcaminho = (
                (self.genes['peso_gravidade'] * gravidade_normalizada)
                / (self.genes['peso_custo'] * custo_subcaminho)
            )

            pontuacoes.append(pontuacao_subcaminho)

        self.pontuacao = sum(pontuacoes)

        cont = 0
        penalidade = 0
        for ordem, percurso in enumerate(self.genes['trajeto']):
            if percurso[0] == ['0:0'] or percurso[1] == ['0:0']:
                penalidade += self.qtd_subcaminhos - ordem + 1
                cont += 1

        if cont > 2:
            self.pontuacao -= penalidade

    def gera_individuo_aleatorio(self):
        """Gera indivíduos aleatórios de acordo com algumas condições.

        1. A origem do primeiro sub-caminho de todo individuo deve ser a posição da base
            dos agentes.
        2. O destino do  ́ultimo sub-caminho de todo individuo deve ser a posição da base
            dos agentes.
        3. A posição conhecida de uma vítima deve aparecer uma  ́unica vez como destino e
            outra vez como origem em sub-caminhos distintos.
        4. A origem do sub-caminho seguinte deve ser a posição da vítima que foi o destino
            do  ́ultimo sub-caminho.
        5. O custo combinado de todos os sub-caminhos realizados deve ser inferior ao
            tempo disponível.
        """
        chave_posicao_atual = '0:0'

        while self.__tem_caminho_possivel_no_tempo(chave_posicao_atual):
            if len(self.genes['trajeto']) >= self.max_subcaminhos:
                break

            if len(self.caminhos_possiveis) > 1:
                destino_escolhido = choice(self.caminhos_possiveis)
                if destino_escolhido == '0:0':
                    for caminhozinho in self.caminhos_possiveis:
                        if (
                            caminhozinho != "0:0"
                            and self.__eh_possivel_ir_e_voltar(chave_posicao_atual, caminhozinho)
                        ):
                            if '0:0' in self.caminhos_possiveis:
                                self.caminhos_possiveis.remove('0:0')
                            while destino_escolhido == '0:0':
                                destino_escolhido = choice(self.caminhos_possiveis)
                            break

                self.genes['trajeto'].append([chave_posicao_atual, destino_escolhido])
                self.tempo_restante -= self.__obtem_custo_caminho(
                    chave_origem = chave_posicao_atual,
                    chave_destino = destino_escolhido
                )
                chave_posicao_atual = destino_escolhido
                self.qtd_subcaminhos += 1
                if chave_posicao_atual != '0:0':
                    self.ja_visitados.append(destino_escolhido)
            elif '0:0' in self.caminhos_possiveis:
                if (self.__eh_possivel_ir_e_voltar(
                        origem = chave_posicao_atual,
                        destino = '0:0'
                    )
                ):
                    self.genes['trajeto'].append([chave_posicao_atual, "0:0"])
                    self.tempo_restante -= self.__obtem_custo_caminho(
                        chave_origem = chave_posicao_atual,
                        chave_destino = '0:0'
                    )
                    self.qtd_subcaminhos += 1
            else:
                break

            self.caminhos_possiveis = []
        self.genes['peso_custo'] = choice([
            0.05, 0.1,
            0.15, 0.2,
            0.25, 0.3,
            0.35
        ])
        self.genes['peso_gravidade'] = 1 - self.genes['peso_custo']

    def __tem_caminho_possivel_no_tempo(self, chave_origem: str) -> bool:
        """Retorna se ainda há algum sub-caminho possível para realizar.

        Leva em consideração a ida até o destino e a volta até a base dos agentes.

        Args:
            chave_origem (str): origem de partida do sub-caminho.

        Returns:
            bool: True se é possível ir até o sub-caminho e voltar até a base dos agentes,
                False caso contrário.
        """
        for destino in self.caminhos[chave_origem]:
            if (
                self.__eh_possivel_ir_e_voltar(chave_origem, destino)
                and destino not in self.ja_visitados
            ):
                self.caminhos_possiveis.append(destino)

        if self.caminhos_possiveis:
            return True
        return False

    def __eh_possivel_ir_e_voltar(self, origem: str, destino: str) -> bool:
        """Retorna se, partindo de determinada origem, é possível chegar até o destino
            e, deste destino, retornar até a base dos agentes.

        Args:
            origem (str): origem do sub-caminho.
            destino (str): destino do sub-caminho.

        Returns:
            bool: True se é possível ir até o destino e voltar até a base dos agentes,
                False caso contrário.
        """
        if destino == origem:
            return True
        custo_ida = self.__obtem_custo_caminho(origem, destino)
        custo_volta_base = self.__obtem_custo_caminho(destino, '0:0')
        if (custo_ida + custo_volta_base) <= self.tempo_restante:
            return True
        return False

    def __obtem_custo_caminho(self, chave_origem: str, chave_destino: str) -> float:
        """Retorna o custo de tempo para realizar o sub-caminho pretendido.

        Args:
            chave_origem (str): origem do sub-caminho.
            chave_destino (str): destino do sub-caminho.

        Returns:
            float: custo de tempo para realizar o sub-caminho.
        """
        if chave_origem == chave_destino:
            return 0

        custo = 0
        percurso = self.caminhos[chave_origem][chave_destino]

        custo = sum(posicao[1] for posicao in percurso)

        return custo

class AlgoritmoGenetico:
    def __init__(
            self,
            probabilidade_eventos: dict[str, float],
            caminhos: dict[str, dict[str, list[tuple[str, int]]]],
            vitimas: dict[str, list[str]],
            tempo_disponivel: float
        ) -> None:
        self.probabilidade_eventos = probabilidade_eventos
        self.caminhos = caminhos
        self.vitimas = vitimas
        self.tempo_disponivel = tempo_disponivel
        self.max_subcaminhos = len(self.vitimas.keys()) + 1

    def aplica_mutacao(self, individuo: Individuo) -> Individuo:
        """Aplica a mutação em uma das características mutáveis do indivíduo.

        Args:
            individuo (Individuo): indivíduo a ser mutado.

        Returns:
            Individuo: Indivíduo com a mutação aplicada.
        """
        # Escolhe um parâmetro aleatório dentro dos parâmetros possíveis.
        parametro_mutacao = choice(list(individuo.parametros_possiveis.keys()))

        # Faz a mutacao em cima do parâmetro escolhido
        individuo.genes[parametro_mutacao] = choice(
            individuo.parametros_possiveis[parametro_mutacao]
        )
        if 'gravidade' in parametro_mutacao:
            individuo.genes['peso_custo'] = 1 - individuo.genes[parametro_mutacao]
        else:
            individuo.genes['peso_gravidade'] = 1 - individuo.genes[parametro_mutacao]

        return individuo

    def crossover(self, pai: Individuo, mae: Individuo) -> list[Individuo]:
        """Efetua o crossover das características de dois Indivíduos para geração de outro.

        Args:
            pai (Individuo): objeto Individuo considerado pai.
            mae (Individuo): objeto Individuo considerado mae.

        Returns:
            list[Individuo]: uma lista contendo dois indivíduos criados pelo pai e mae passados.
        """
        filhos = []
        # Loop que representa a quantidade de filhos a serem gerados.
        for _ in range(2):
            caracteristicas_filho = {}

            # Escolhe aleatoriamente características para o filho.
            for param in pai.parametros_possiveis:
                caracteristicas_filho[param] = choice([mae.genes[param], pai.genes[param]])

            # Gera um filho com uma nova sequência de sub-caminhos aleatório
            filho = Individuo(self.caminhos, self.tempo_disponivel, self.max_subcaminhos)
            filho.gera_individuo_aleatorio()

            # Atribui as características de peso dos pais para a função de fitness do filho
            filho.set_caracteristicas(caracteristicas_filho)

            # Avalia a pontuação deste indivíduo
            filho.avalia_individuo(self.vitimas)

            # Se a pontuação do filho for menor que a dos pais, descarta o trajeto do filho
            if filho.pontuacao < pai.pontuacao and filho.pontuacao < mae.pontuacao:
                trajeto = mae.genes['trajeto']
                if pai.pontuacao > mae.pontuacao:
                    trajeto = pai.genes['trajeto']

                # Atribui o trajeto com maior pontuação entre os pais
                filho.set_trajeto(trajeto)

            # Chance de mutação dos parâmetros de modo aleatório.
            if self.probabilidade_eventos['chance_mutacao'] > random():
                filho = self.aplica_mutacao(filho)

            # Insere o filho gerado na lista de filhos destes pais
            filhos.append(filho)

        return filhos

    def faz_evolucao(self, populacao: list[Individuo]) -> list[Individuo]:
        """Realiza a evolução dos indivíduos de uma população.

        Args:
            populacao (list[Individuo]): lista de indivíduos da população.

        Returns:
             list[Individuo]: lista de indivíduos (população) evoluída.
        """
        # Obtém a pontuacao para cada um dos individuos da população
        pontuacao_individuos = [
            {'pontuacao': individuo.pontuacao, 'individuo': individuo}
            for individuo in populacao
        ]

        # Ordena as pontuações de forma crescente
        individuos_ordenados = [
            x['individuo'] for x in sorted(
                pontuacao_individuos,
                key = lambda x: x['pontuacao'],
                reverse = True
            )
        ]

        # Seleciona a quantidade que deve ser mantida para a próxima geração
        qtd_individuos_mantidos = int(
            self.probabilidade_eventos['percentagem_retencao_populacao']
            * int(len(individuos_ordenados))
        )

        # Os individuos geradores serão todos aqueles que foram mantidos
        individuos_geradores = individuos_ordenados[:qtd_individuos_mantidos]

        # Aleatoriamente mantém alguns daqueles que foram descartados
        for individuo in individuos_ordenados[qtd_individuos_mantidos:]:
            if self.probabilidade_eventos['chace_selecao_aleatoria'] > random():
                individuos_geradores.append(individuo)

        # Quantidade de crianças que devem ser geradas
        qtd_individuos_geradores = len(individuos_geradores)
        qtd_individuos_desejada = len(populacao) - qtd_individuos_geradores
        individuos_filhos = []

        print("GERANDO FILHOS PARA GERAÇÃO SEGUINTE")
        barra_progresso = tqdm(total = qtd_individuos_desejada)
        # Cria os filhos com as características dos individuos remanescentes.
        while len(individuos_filhos) < qtd_individuos_desejada:
            # Seleciona dois individuos geradores aleatórios.
            pos_individuo_pai = randint(0, qtd_individuos_geradores-1)
            pos_individuo_mae = randint(0, qtd_individuos_geradores-1)

            # Verifica se os individuos são diferentes
            if pos_individuo_pai != pos_individuo_mae:
                individuo_pai = individuos_geradores[pos_individuo_pai]
                individuo_mae = individuos_geradores[pos_individuo_mae]

                # Cruza os individuos selecionados e retorna os filhos.
                filhos = self.crossover(individuo_pai, individuo_mae)

                # Acrescenta um filho por vez até a quantidade desejada.
                for filho in filhos:
                    if len(individuos_filhos) < qtd_individuos_desejada:
                        individuos_filhos.append(filho)
                        barra_progresso.update(1)
        barra_progresso.close()
        # Inclui os filhos gerados na nova população
        individuos_geradores.extend(individuos_filhos)

        # Retorna a população evoluída
        return individuos_geradores

    def gera_populacao_aleatoria(self, qtd_individuos: int) -> list[Individuo]:
        """Gera uma população de indivíduos com trajetos aleatorios.

        Args:
            qtd_individuos (int): quantidade de indivíduos para gerar a população.

        Returns:
            list[Individuo]: lista de indivíduos aleatórios gerados.
        """
        populacao_gerada = []
        print("GERANDO INDIVIDUOS ALEATÓRIOS")
        barra_progresso = tqdm(total = qtd_individuos)
        for _ in range(qtd_individuos):
            individuo = Individuo(self.caminhos, self.tempo_disponivel, self.max_subcaminhos)
            individuo.gera_individuo_aleatorio()
            populacao_gerada.append(individuo)
            individuo = None
            barra_progresso.update(1)

        barra_progresso.close()

        return populacao_gerada

class Otimizador:
    def __init__(
            self,
            n_populacao: int,
            n_geracoes: int,
            probabilidade_eventos: dict[str, float],
            tempo_disponivel: float
        ) -> None:
        self.probabilidade_eventos = probabilidade_eventos
        self.n_populacao = n_populacao
        self.n_geracoes = n_geracoes

        self.tempo_disponivel = tempo_disponivel

        self.melhor_individuo_ = None
        self.melhor_pontuacao_ = -9999999

    def evoluir(
            self,
            problema: Problema,
            caminhos_possiveis: dict[str, dict[str, list[tuple[str, int]]]]
        ) -> None:
        """Faz a evolução dos indivíduos, isto é, a otimização por meio de algoritmo genético.

        Args:
            problema (Problema): instância do problema a ser resolvido.

            caminhos_possiveis (dict[str, dict[str, list[tuple[str, int]]]]): dicionário de
                caminhos possíveis entre todas as combinações de posições de interesse.
        """
        algoritmo_genetico = AlgoritmoGenetico(
            self.probabilidade_eventos,
            caminhos_possiveis,
            problema.sinais_vitais_vitimas,
            self.tempo_disponivel
        )
        print(f"numero de vítimas para salvar: {len(problema.sinais_vitais_vitimas)}")
        populacao = algoritmo_genetico.gera_populacao_aleatoria(self.n_populacao)

        for geracao in range(1, self.n_geracoes + 1):
            print(f"Geração {geracao} de {self.n_geracoes}")

            # Faz a avaliação da população da geração atual
            self.avalia_populacao(populacao, problema.sinais_vitais_vitimas)

            # Obtém a pontuação média da população atual
            pontuacao_media = self.get_pontuacao_media(populacao)

            print(f"Media da geração {geracao}: {round(pontuacao_media, 2)}")

            # Ordena os individuos pela pontuação de modo decrescente.
            populacao = sorted(
                populacao,
                key = lambda x: x.pontuacao,
                reverse = True
            )

            print(f"{populacao[0].pontuacao} -> {populacao[0].genes['trajeto']}")
            # Salva dados do melhor individuo
            if self.melhor_pontuacao_ < populacao[0].pontuacao:
                self.melhor_individuo_ = deepcopy(populacao[0])
                # self.melhores_parametros_ = self.melhor_estimador_.get_params()
                self.melhor_pontuacao_ = self.melhor_individuo_.pontuacao

            # Evolui a geração, exceto se for a última geração.
            if geracao != self.n_geracoes:
                # Faz a evolução da populacao
                populacao = algoritmo_genetico.faz_evolucao(populacao)

        # Descreve o top 5 indivíduos no terminal
        self.__print_modelos(populacao[:5])

    def avalia_populacao(self, populacao: list[Individuo], vitimas: dict[str, list[str]]):
        """Faz a avaliação de acordo com a função de fitness dos indivíduos para cada indivíduo.

        Args:
            populacao (list[Individuo]): lista de indivíduos.
            vitimas (dict[str, list[str]]): posição e sinais vitais das vítimas.
        """
        barra_progresso = tqdm(total=len(populacao))

        for individuo in populacao:
            individuo.avalia_individuo(vitimas)
            barra_progresso.update(1)

        barra_progresso.close()

    def get_pontuacao_media(self, populacao: list[Individuo]) -> float:
        """Calcula a pontuação média de uma população.

        Args:
            populacao (list[Individuo]): indivíduos da população.

        Returns:
            float: pontuação média da população.
        """
        somatorio_pontuacao = 0

        somatorio_pontuacao = reduce(add, (individuo.pontuacao for individuo in populacao))

        return round(somatorio_pontuacao/float((len(populacao))), 2)

    def __print_modelos(self, populacao: list[Individuo]) -> None:
        """Descreve a lista dos indivíduos da população.

        Parameters:
            modelos (list): População dos modelos.
        """
        print('='*80)
        for individuo in populacao:
            print(f"{individuo.pontuacao} -> {individuo.genes['trajeto']}")
