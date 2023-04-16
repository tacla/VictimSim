from agentes.utils.problema import Problema

class PlanoRetornoBase:
    def __init__(self) -> None:
        self.problema = Problema()

    def verifica_retorno_base(self) -> None:
        return False