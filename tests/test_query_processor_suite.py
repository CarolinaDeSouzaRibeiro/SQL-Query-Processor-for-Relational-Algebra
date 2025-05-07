import unittest
from parser import process_sql_query
from arvores_construcao_otimizacao import (
    converter_algebra_em_arvore,
    otimizar_selects,
    otimizar_projecoes,
    No,
    Arvore
)

# Valid queries from docs/exemplos_consultas.txt
VALID_QUERIES = [
    "SELECT nome, email FROM Cliente",
    "select NOME, EmAiL FrOm CLIENTE",
    "SELECT * FROM TipoCliente",
    "SELECT Nome FROM Produto WHERE Preco > 50.00",
    "SELECT Nome FROM Cliente WHERE Email = 'teste@mail.com'",
    "SELECT idProduto, QuantEstoque FROM Produto WHERE Preco < 100 AND QuantEstoque >= 10",
    "SELECT Nome FROM Cliente WHERE idCliente < 5",
    "SELECT p.idPedido FROM Pedido p INNER JOIN Cliente c ON p.Cliente_idCliente = c.idCliente WHERE p.DataPedido > c.DataRegistro",
    "SELECT Cliente.Nome, Pedido.DataPedido FROM Cliente INNER JOIN Pedido ON Cliente.idCliente = Pedido.Cliente_idCliente",
    "SELECT c.Nome, p.DataPedido FROM Cliente c INNER JOIN Pedido p ON c.idCliente = p.Cliente_idCliente",
    "SELECT c.Nome, p.idPedido FROM Cliente AS c INNER JOIN Pedido AS p ON c.idCliente = p.Cliente_idCliente WHERE p.ValorTotalPedido > 100.0",
    "SELECT * FROM Categoria C INNER JOIN Produto P ON C.idCategoria = P.Categoria_idCategoria",
    "SELECT Ped.idPedido, Prod.Nome, Itens.Quantidade FROM Pedido Ped INNER JOIN Pedido_has_Produto Itens ON Ped.idPedido = Itens.Pedido_idPedido INNER JOIN Produto Prod ON Itens.Produto_idProduto = Prod.idProduto",
    "SELECT Ped.idPedido, Prod.Nome FROM Pedido Ped INNER JOIN Pedido_has_Produto Itens ON Ped.idPedido = Itens.Pedido_idPedido INNER JOIN Produto Prod ON Itens.Produto_idProduto = Prod.idProduto WHERE Ped.Cliente_idCliente = 10 AND Itens.Quantidade > 1",
    "SELECT c.Nome, p.DataPedido FROM Cliente c INNER JOIN Pedido p ON p.Cliente_idCliente = c.idCliente",
    "SELECT P.Nome FROM Produto P INNER JOIN Categoria C ON P.Categoria_idCategoria = idCategoria",
    "SELECT P.Nome FROM Produto P INNER JOIN Categoria C ON idCategoria = C.idCategoria",
    "SELECT P.Nome FROM Produto P INNER JOIN Categoria C ON idCategoria = idCategoria",
]

# Invalid queries from docs/exemplos_consultas.txt
INVALID_QUERIES = [
    "SELECT nome FROM Clientes",
    "SELECT c.nome FROM Cliente c INNER JOIN Pedidos_Invalidos p ON c.idCliente = p.cliente_id",
    "SELECT nome, sobrenome FROM Cliente",
    "SELECT nome FROM Cliente WHERE apelido = 'Jo'",
    "SELECT c.nome FROM Cliente c INNER JOIN Pedido p ON c.id = p.Cliente_idCliente",
    "SELECT c.nome FROM Cliente c INNER JOIN Pedido c ON c.idCliente = c.Cliente_idCliente",
    "SELECT x.nome FROM Cliente c WHERE c.idCliente = 1",
    "SELECT c.nome FROM Cliente c WHERE x.idCliente = 1",
    "SELECT Descricao FROM Produto P INNER JOIN Categoria C ON P.Categoria_idCategoria = C.idCategoria",
    "SELECT P.Nome FROM Produto P INNER JOIN Categoria C ON P.Categoria_idCategoria = C.idCategoria WHERE Descricao = 'Teste'",
    "SELECT c1.Nome FROM Cliente c1 INNER JOIN Cliente c2 ON c1.TipoCliente_idTipoCliente = TipoCliente_idTipoCliente",
    "SELECT nome FROM Produto WHERE Preco && 10",
    "SELECT nome FROM Cliente INNER JOIN Pedido",
    "SELECT c.nome FROM Cliente c INNER JOIN Pedido p ON",
    "SELECT FROM nome clientes WHERE id = 1",
]

class TestQueryProcessorSuite(unittest.TestCase):
    def test_valid_queries(self):
        for sql in VALID_QUERIES:
            with self.subTest(sql=sql):
                ra = process_sql_query(sql)
                self.assertIsInstance(ra, str, f"Expected string output for valid query: {sql}\nGot: {ra}")

    def test_invalid_queries(self):
        for sql in INVALID_QUERIES:
            with self.subTest(sql=sql):
                ra = process_sql_query(sql)
                self.assertTrue(isinstance(ra, Exception) or 'Erro' in str(ra), f"Expected error for invalid query: {sql}\nGot: {ra}")

    def test_optimization_selection_pushdown(self):
        # Use a valid query with WHERE and JOIN
        sql = "SELECT p.idPedido FROM Pedido p INNER JOIN Cliente c ON p.Cliente_idCliente = c.idCliente WHERE p.DataPedido > c.DataRegistro"
        ra = process_sql_query(sql)
        arvore = converter_algebra_em_arvore(ra)
        arvore_opt = otimizar_selects(arvore)
        join_node = arvore_opt.raiz
        self.assertIn(join_node.get_operacao(), ["JOIN", "PRODUCT"])
        # At least one child should be a SELECT node
        left = join_node.filho_esq
        right = join_node.filho_dir
        self.assertTrue(
            (left and left.get_operacao() == "SELECT") or (right and right.get_operacao() == "SELECT"),
            "Expected at least one SELECT node as child after selection pushdown."
        )

    def test_tree_structure_basic(self):
        # Use a simple valid query
        sql = "SELECT nome, email FROM Cliente"
        ra = process_sql_query(sql)
        arvore = converter_algebra_em_arvore(ra)
        self.assertIsInstance(arvore, Arvore)
        self.assertIsInstance(arvore.raiz, No)
        self.assertEqual(arvore.raiz.get_operacao(), "PROJECT")
        self.assertEqual(arvore.raiz.filho_esq.get_operacao(), "TABLE")

    @staticmethod
    def _normalize(s):
        return ' '.join(str(s).replace("\n", " ").replace("\t", " ").split())

if __name__ == "__main__":
    unittest.main() 