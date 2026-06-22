import pytest

from recommender import OCASIAO_SEM_PREFERENCIA, GiftRecommender


@pytest.fixture(scope="module")
def recomendador():
    return GiftRecommender()


def test_filtra_por_idade_e_genero(recomendador):
    candidatos = recomendador._filtrar_por_idade_e_genero(idade=10, genero="Masculino")
    assert (candidatos["idade_min"] <= 10).all()
    assert (candidatos["idade_max"] >= 10).all()
    assert candidatos["genero"].isin(["Masculino", "Unissex"]).all()


def test_recomendacoes_vem_ordenadas_por_compatibilidade(recomendador):
    resultados, _ = recomendador.recomendar(
        idade=28,
        genero="Feminino",
        orcamento=200,
        ocasiao="Aniversário",
        interesses=["leitura", "cafe"],
    )
    assert len(resultados) > 0
    compatibilidades = [item["compatibilidade"] for item in resultados]
    assert compatibilidades == sorted(compatibilidades, reverse=True)


def test_orcamento_muito_baixo_nao_gera_falsa_ampliacao(recomendador):
    resultados, orcamento_ampliado = recomendador.recomendar(
        idade=28,
        genero="Feminino",
        orcamento=1,
        ocasiao="Aniversário",
        interesses=["leitura"],
    )
    assert resultados == []
    assert orcamento_ampliado is False


def test_fallback_quando_perfil_fica_zerado(recomendador):
    resultados, _ = recomendador.recomendar(
        idade=35,
        genero="Masculino",
        orcamento=150,
        ocasiao=OCASIAO_SEM_PREFERENCIA,
        interesses=["tag-inexistente"],
    )
    assert len(resultados) > 0
    assert all(item["compatibilidade"] is None for item in resultados)


def test_diversidade_espalha_resultados_entre_categorias(recomendador):
    # "decoracao" aparece em itens de varias categorias (Casa & Decoracao,
    # Pets, Culinaria, Musica, Arte & Artesanato, Jogos...). Sem diversidade,
    # uma lista de 8 itens tenderia a ficar dominada so por Casa & Decoracao,
    # que tem o maior numero de produtos com essa tag no catalogo.
    resultados, _ = recomendador.recomendar(
        idade=28,
        genero="Unissex",
        orcamento=1000,
        ocasiao=OCASIAO_SEM_PREFERENCIA,
        interesses=["decoracao"],
        top_n=8,
    )
    contagem_por_categoria = {}
    for item in resultados:
        contagem_por_categoria[item["categoria"]] = contagem_por_categoria.get(item["categoria"], 0) + 1

    assert len(contagem_por_categoria) >= 4
    assert max(contagem_por_categoria.values()) <= 3


def test_remove_variantes_de_preco_do_mesmo_produto_do_pool(recomendador):
    # cada produto-base do catalogo tem 7 variantes de preco com as mesmas
    # tags (Linha Essencial, Edicao Padrao, Versao Pro etc.) que empatam
    # exatamente na compatibilidade; nao deveriam dominar os resultados.
    resultados, _ = recomendador.recomendar(
        idade=28,
        genero="Unissex",
        orcamento=2000,
        ocasiao="Natal",
        interesses=["tecnologia"],
        top_n=6,
    )
    nomes_base = [item["nome"].split(" – ")[0] for item in resultados]
    assert len(nomes_base) == len(set(nomes_base))


def test_tipos_dos_resultados_sao_nativos(recomendador):
    resultados, _ = recomendador.recomendar(
        idade=28,
        genero="Feminino",
        orcamento=300,
        ocasiao="Natal",
        interesses=["musica"],
    )
    item = resultados[0]
    assert isinstance(item["id"], int)
    assert isinstance(item["preco"], float)
    assert isinstance(item["compatibilidade"], float)
