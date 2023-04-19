class Estado:
    """Esta classe representa um estado do problema para os agentes, ou seja,
        é um par ordenado que indica uma posição no espaço do ambiente.
    """

    def __init__(self, linha: int = 0, coluna: int = 0) -> None:
        """Define um par ordenado (x, y) como a posição do agente,
            isto é, um estado do problema.

        Args:
            linha (int): valor da posição da linha.
            coluna (int): valor da posição da coluna.
        """
        self.linha = linha
        self.coluna = coluna

    def get_chave_posicao(self):
        """Retorna a posição que o estado representa, no formato das chaves dos dicionários.

        Returns:
            str: chave da posicao que este estado representa.
        """
        return str(self.linha) + ':' + str(self.coluna)

    def __str__(self) -> str:
        return f"({self.linha}, {self.coluna})"
