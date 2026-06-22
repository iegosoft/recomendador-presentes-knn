import pytest

from app import app as flask_app


@pytest.fixture
def cliente():
    flask_app.testing = True
    return flask_app.test_client()


def test_pagina_inicial_renderiza_formulario(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200
    assert b"form-recomendacao" in resposta.data


def test_health_retorna_ok(cliente):
    resposta = cliente.get("/health")
    assert resposta.status_code == 200
    assert resposta.get_json() == {"status": "ok"}


def test_rota_inexistente_da_api_retorna_404_json(cliente):
    resposta = cliente.get("/api/rota-que-nao-existe")
    assert resposta.status_code == 404
    assert "erro" in resposta.get_json()


def test_recomendar_sem_corpo_json_retorna_400(cliente):
    resposta = cliente.post("/api/recomendar")
    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_recomendar_caso_valido(cliente):
    resposta = cliente.post(
        "/api/recomendar",
        json={
            "idade": 28,
            "genero": "Feminino",
            "orcamento": 200,
            "ocasiao": "Natal",
            "interesses": ["leitura", "cafe"],
        },
    )
    corpo = resposta.get_json()
    assert resposta.status_code == 200
    assert len(corpo["resultados"]) > 0


def test_recomendar_sem_interesses_retorna_400(cliente):
    resposta = cliente.post(
        "/api/recomendar",
        json={"idade": 28, "genero": "Feminino", "orcamento": 200, "ocasiao": "Natal", "interesses": []},
    )
    assert resposta.status_code == 400
    assert "erro" in resposta.get_json()


def test_recomendar_orcamento_baixo_sem_aviso_falso(cliente):
    resposta = cliente.post(
        "/api/recomendar",
        json={"idade": 28, "genero": "Feminino", "orcamento": 1, "ocasiao": "Natal", "interesses": ["leitura"]},
    )
    corpo = resposta.get_json()
    assert resposta.status_code == 200
    assert corpo["resultados"] == []
    assert "aviso" not in corpo


def test_recomendar_idade_fora_de_qualquer_faixa(cliente):
    # 105 e uma idade valida (dentro do limite de 1-120 aceito pela API), mas
    # nenhum item do catalogo tem idade_max tao alta - deve devolver lista
    # vazia, sem erro.
    resposta = cliente.post(
        "/api/recomendar",
        json={"idade": 105, "genero": "Feminino", "orcamento": 200, "ocasiao": "Natal", "interesses": ["leitura"]},
    )
    corpo = resposta.get_json()
    assert resposta.status_code == 200
    assert corpo["resultados"] == []


def test_recomendar_idade_invalida_retorna_400(cliente):
    resposta = cliente.post(
        "/api/recomendar",
        json={"idade": -5, "genero": "Feminino", "orcamento": 200, "ocasiao": "Natal", "interesses": ["leitura"]},
    )
    assert resposta.status_code == 400


def test_recomendar_genero_invalido_retorna_400(cliente):
    resposta = cliente.post(
        "/api/recomendar",
        json={"idade": 28, "genero": "Outro", "orcamento": 200, "ocasiao": "Natal", "interesses": ["leitura"]},
    )
    assert resposta.status_code == 400


def test_recomendar_ocasiao_invalida_retorna_400(cliente):
    resposta = cliente.post(
        "/api/recomendar",
        json={"idade": 28, "genero": "Feminino", "orcamento": 200, "ocasiao": "Reveillon", "interesses": ["leitura"]},
    )
    assert resposta.status_code == 400


def test_recomendar_interesse_invalido_retorna_400(cliente):
    resposta = cliente.post(
        "/api/recomendar",
        json={
            "idade": 28,
            "genero": "Feminino",
            "orcamento": 200,
            "ocasiao": "Natal",
            "interesses": ["interesse-que-nao-existe"],
        },
    )
    assert resposta.status_code == 400
