from __future__ import annotations
from typing import Optional, NoReturn
from graphviz import Digraph
from pathlib import Path

class NoArvore:
    """
    Representa um nó de uma árvore de álgebra relacional.

    Atributos:
        conteudo (str): Texto que representa a operação relacional ou tabela.
        filho_esquerda (Optional[NoArvore]): Subárvore à esquerda.
        filho_direita (Optional[NoArvore]): Subárvore à direita.
    """
    def __init__(self, conteudo: str):
        self.conteudo: str = conteudo
        self.filho_esquerda: Optional[NoArvore] = None
        self.filho_direita: Optional[NoArvore] = None


class Arvore:
    """
    Representa uma árvore de álgebra relacional e permite reconstrução da expressão.

    Atributos:
        raiz (Optional[NoArvore]): Nó raiz da árvore.
    """
    def __init__(self):
        self.raiz: Optional[NoArvore] = None

    def reconstruir_algebra_relacional(self) -> Optional[str]:
        """
        Reconstrói a expressão de álgebra relacional a partir da árvore.

        Retorna:
            Optional[str]: String formatada com a expressão relacional.
        """
        if self.raiz is None:
            return None
        return self._percorrer(self.raiz)

    def _percorrer(self, no: NoArvore, nivel: int = 0) -> str:
        """
        Percorre a árvore recursivamente para construir a expressão relacional.

        Args:
            no (NoArvore): Nó atual.
            nivel (int): Nível de indentação (para formatação).

        Retorna:
            str: Parte da expressão relacional.
        """
        indent = "   " * nivel

        if no.filho_esquerda is None and no.filho_direita is None:
            return f"{indent}{no.conteudo}\n"

        if self._is_select(no) and self._is_select(no.filho_esquerda):
            return self._combinar_selects(no, nivel)

        if self._is_join(no):
            return self._renderizar_join(no, nivel)
        if self._is_produto_cartesiano(no):
            return self._renderizar_produto_cartesiano(no, nivel)

        expressao = f"{indent}{no.conteudo}(\n"
        if no.filho_esquerda:
            expressao += self._percorrer(no.filho_esquerda, nivel + 1)
        if no.filho_direita:
            expressao += self._percorrer(no.filho_direita, nivel + 1)
        expressao += f"{indent})\n"
        return expressao

    def _is_select(self, no: Optional[NoArvore]) -> bool:
        """Verifica se o nó representa uma operação de seleção (𝛔)."""
        return no is not None and no.conteudo.startswith("𝛔[")

    def _is_join(self, no: Optional[NoArvore]) -> bool:
        """Verifica se o nó representa uma operação de junção (⨝)."""
        return no is not None and no.conteudo.startswith("⨝[")

    def _is_produto_cartesiano(self, no: Optional[NoArvore]) -> bool:
        """Verifica se o nó representa um produto cartesiano (X)."""
        return no is not None and no.conteudo.strip() == "X"

    def _extrair_condicao(self, conteudo: str) -> str:
        """
        Extrai a condição de uma operação de seleção.

        Args:
            conteudo (str): Conteúdo como "𝛔[cond]"

        Retorna:
            str: Condição interna, sem o operador.
        """
        return conteudo[2:-1]

    def _combinar_selects(self, no: NoArvore, nivel: int) -> str:
        """
        Junta seleções aninhadas em uma única seleção com conjunção lógica.

        Args:
            no (NoArvore): Nó que contém seleção aninhada.
            nivel (int): Nível de indentação.

        Retorna:
            str: Expressão formatada da seleção combinada.
        """
        indent = "   " * nivel
        cond1 = self._extrair_condicao(no.conteudo)
        filho = no.filho_esquerda
        cond2 = self._extrair_condicao(filho.conteudo)

        combinada = f"({cond1}) ^ ({cond2})"
        novo_no = filho.filho_esquerda

        if self._is_select(novo_no):
            novo_combinado = NoArvore(f"𝛔[{combinada}]")
            novo_combinado.filho_esquerda = novo_no
            return self._percorrer(novo_combinado, nivel)

        expressao = f"{indent}𝛔[{combinada}](\n"
        if novo_no:
            expressao += self._percorrer(novo_no, nivel + 1)
        if filho.filho_direita:
            expressao += self._percorrer(filho.filho_direita, nivel + 1)
        expressao += f"{indent})\n"
        return expressao

    def _renderizar_join(self, no: NoArvore, nivel: int) -> str:
        """
        Renderiza a operação de junção como string formatada.

        Args:
            no (NoArvore): Nó com junção.
            nivel (int): Nível de indentação.

        Retorna:
            str: Expressão da junção.
        """
        indent = "   " * nivel
        condicao = no.conteudo
        expressao = f"{indent}(\n"
        expressao += self._percorrer(no.filho_esquerda, nivel + 1)
        expressao += f"{indent}) {condicao} (\n"
        expressao += self._percorrer(no.filho_direita, nivel + 1)
        expressao += f"{indent})\n"
        return expressao

    def _renderizar_produto_cartesiano(self, no: NoArvore, nivel: int) -> str:
        """
        Renderiza o produto cartesiano como string formatada.

        Args:
            no (NoArvore): Nó com operação X.
            nivel (int): Nível de indentação.

        Retorna:
            str: Expressão do produto cartesiano.
        """
        indent = "   " * nivel
        expressao = f"{indent}(\n"
        expressao += self._percorrer(no.filho_esquerda, nivel + 1)
        expressao += f"{indent}) X (\n"
        expressao += self._percorrer(no.filho_direita, nivel + 1)
        expressao += f"{indent})\n"
        return expressao


class ArvoreDrawer:
    """
    Gera uma visualização gráfica de uma árvore de álgebra relacional usando Graphviz.

    Atributos:
        DIRETORIO_IMAGEM (Path): Diretório onde as imagens serão salvas.
        FORMATO_IMAGEM (str): Formato da imagem a ser gerada.
    """
    DIRETORIO_IMAGEM: Path = Path.cwd() / "img"
    FORMATO_IMAGEM: str = "png"
    
    def __init__(self, arvore: Arvore):
        self.arvore = arvore
        self.dot = Digraph(format=self.FORMATO_IMAGEM)
        self.node_count = 0

    def desenhar(self, nome_imagem: str) -> None | NoReturn:
        """
        Gera e salva uma imagem da árvore relacional.

        Args:
            nome_imagem (str): Nome do arquivo de saída (sem extensão).

        Raises:
            ValueError: Se a árvore estiver vazia.
        """
        if not self.arvore.raiz:
            raise ValueError("A árvore está vazia.")
        
        self.DIRETORIO_IMAGEM.mkdir(parents=True, exist_ok=True)
        self.node_count = 0
        self._desenhar_no(self.arvore.raiz)
        self.dot.render(filename=(self.DIRETORIO_IMAGEM / nome_imagem), cleanup=True)
        print(f"✅ Árvore desenhada com sucesso em: {self.DIRETORIO_IMAGEM / nome_imagem}.{self.FORMATO_IMAGEM}")

    def _desenhar_no(self, no: NoArvore) -> str:
        """
        Cria os nós e arestas do grafo recursivamente.

        Args:
            no (NoArvore): Nó atual da árvore.

        Retorna:
            str: Identificador do nó no grafo.
        """
        id_atual = f"node{self.node_count}"
        self.node_count += 1

        conteudo_legivel = (
            no.conteudo
            .replace("𝝿", "π")
            .replace("𝛔", "σ")
            .replace("⨝", "X")
        )

        self.dot.node(id_atual, label=conteudo_legivel)

        if no.filho_esquerda:
            id_esq = self._desenhar_no(no.filho_esquerda)
            self.dot.edge(id_atual, id_esq)

        if no.filho_direita:
            id_dir = self._desenhar_no(no.filho_direita)
            self.dot.edge(id_atual, id_dir)

        return id_atual


if __name__ == "__main__":
    '''
𝝿[C.Nome, E.CEP, P.Status](
   𝛔[(C.TipoCliente = 4) ∧ (E.UF = "SP")](
        (
          Cliente[C] ⨝[C.idCliente = P.Cliente_idCliente] Pedido[P]
        ) ⨝[C.idCliente = E.Cliente_idCliente] Endereco[E]
   )
)
    '''
    
    """
    Exemplo de uso:
    - Cria uma árvore representando uma consulta relacional.
    - Reconstrói e imprime a expressão.
    - Gera uma imagem da árvore.
    """
    arvore = Arvore()

    arvore.raiz = NoArvore("𝝿[C.Nome, E.CEP, P.Status]")
    arvore.raiz.filho_esquerda = NoArvore("𝛔[C.TipoCliente = 4]")
    arvore.raiz.filho_esquerda.filho_esquerda = NoArvore("𝛔[E.UF = \"SP\"]")
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda = NoArvore("⨝[C.idCliente = E.Cliente_idCliente]")
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda.filho_esquerda = NoArvore("⨝[C.idCliente = P.Cliente_idCliente]")
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda.filho_esquerda.filho_esquerda = NoArvore("Cliente[C]")
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda.filho_esquerda.filho_direita = NoArvore("Pedido[P]")
    arvore.raiz.filho_esquerda.filho_esquerda.filho_esquerda.filho_direita = NoArvore("Endereco[E]")

    print(arvore.reconstruir_algebra_relacional())

    drawer: ArvoreDrawer = ArvoreDrawer(arvore)
    drawer.desenhar("arvore_inicial")