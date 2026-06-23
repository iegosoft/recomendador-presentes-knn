import pytest

from recommender import MIN_COMPATIBILIDADE, OCASIAO_SEM_PREFERENCIA, GiftRecommender


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


def test_selecionar_com_diversidade_respeita_limite_quando_possivel():
    # teste unitario e deterministico do algoritmo de diversidade, sem
    # depender do catalogo real nem da ordem de empate do NearestNeighbors
    # (que pode variar entre plataformas quando varios itens tem
    # compatibilidade exatamente igual).
    pool = [
        {"id": 1, "categoria": "A", "preco": 10, "compatibilidade": 95.0},
        {"id": 2, "categoria": "A", "preco": 10, "compatibilidade": 90.0},
        {"id": 3, "categoria": "A", "preco": 10, "compatibilidade": 85.0},
        {"id": 4, "categoria": "B", "preco": 10, "compatibilidade": 84.0},
        {"id": 5, "categoria": "B", "preco": 10, "compatibilidade": 83.0},
        {"id": 6, "categoria": "C", "preco": 10, "compatibilidade": 82.0},
        {"id": 7, "categoria": "D", "preco": 10, "compatibilidade": 81.0},
    ]

    selecionados = GiftRecommender._selecionar_com_diversidade(pool, top_n=4)

    contagem_por_categoria = {}
    for item in selecionados:
        contagem_por_categoria[item["categoria"]] = contagem_por_categoria.get(item["categoria"], 0) + 1

    assert len(selecionados) == 4
    assert max(contagem_por_categoria.values()) <= 2


def test_selecionar_com_diversidade_relaxa_limite_se_necessario():
    # quando nao ha itens suficientes de outras categorias, o limite por
    # categoria deve ser relaxado em vez de devolver menos itens do que
    # poderia.
    pool = [
        {"id": 1, "categoria": "A", "preco": 10, "compatibilidade": 95.0},
        {"id": 2, "categoria": "A", "preco": 10, "compatibilidade": 90.0},
        {"id": 3, "categoria": "A", "preco": 10, "compatibilidade": 85.0},
    ]

    selecionados = GiftRecommender._selecionar_com_diversidade(pool, top_n=4)

    assert len(selecionados) == 3
    assert [item["id"] for item in selecionados] == [1, 2, 3]


def test_diversidade_espalha_resultados_entre_categorias(recomendador):
    # teste de ponta a ponta, mais permissivo: confirma que a diversidade
    # melhora a distribuicao sem depender da ordem exata de empate entre
    # itens com compatibilidade igual (que varia entre plataformas).
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

    assert len(contagem_por_categoria) >= 3
    assert max(contagem_por_categoria.values()) < len(resultados)


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


def test_nenhuma_recomendacao_fica_abaixo_do_piso_de_compatibilidade(recomendador):
    resultados, _ = recomendador.recomendar(
        idade=28,
        genero="Feminino",
        orcamento=200,
        ocasiao="Natal",
        interesses=["leitura", "cafe"],
    )
    assert len(resultados) > 0
    assert all(item["compatibilidade"] >= MIN_COMPATIBILIDADE for item in resultados)


def test_sem_correspondencia_confiavel_devolve_lista_vazia_em_vez_de_lixo(recomendador):
    # idade 15 com orcamento de R$ 50 nao tem nenhum item de tecnologia ou
    # esportes que caiba no orcamento (o mais barato do catalogo custa mais
    # que isso mesmo com a tolerancia maxima); o sistema deve admitir que nao
    # tem um presente confiavel em vez de sugerir algo sem relacao com os
    # interesses so para preencher a lista.
    resultados, orcamento_ampliado = recomendador.recomendar(
        idade=15,
        genero="Masculino",
        orcamento=50,
        ocasiao="Natal",
        interesses=["tecnologia", "esportes"],
    )
    assert resultados == []
    assert orcamento_ampliado is False


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
