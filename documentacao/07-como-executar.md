# Como Instalar e Executar

## Pré-requisitos

- Python 3.10 ou superior
- Git

## Instalação

```bash
# Clone o repositório
git clone https://github.com/iegosoft/recomendador-presentes-knn.git
cd recomendador-presentes-knn

# Instale as dependências
pip install -r requirements.txt
```

## Executar o servidor

```bash
python app.py
```

Acesse `http://127.0.0.1:5000` no navegador.

### Variáveis de ambiente opcionais

| Variável | Padrão | Descrição |
|---|---|---|
| `FLASK_DEBUG` | `false` | Ativa o modo debug do Flask (`true` ou `false`) |
| `HOST` | `127.0.0.1` | Endereço de rede em que o servidor escuta |
| `PORT` | `5000` | Porta do servidor |

**Exemplo com debug ativo:**
```bash
FLASK_DEBUG=true python app.py
```

## Executar os testes

```bash
# Instale também as dependências de desenvolvimento
pip install -r requirements-dev.txt

# Execute todos os testes
pytest

# Execute com saída detalhada
pytest -v
```

O projeto conta com 24 testes automatizados divididos em dois módulos:
- `tests/test_app.py` — testes de integração da API Flask
- `tests/test_recommender.py` — testes unitários do motor de recomendação

## Regenerar o catálogo

O arquivo `data/presentes.csv` já está incluso no repositório. Caso queira regerá-lo:

```bash
python scripts/gerar_dataset.py
```

Isso recria o catálogo com 1.512 itens a partir dos 72 produtos-base definidos em `scripts/gerar_dataset.py`.

## Testar a API manualmente

Com o servidor rodando, envie uma requisição de teste via terminal:

```bash
curl -s -X POST http://127.0.0.1:5000/api/recomendar \
  -H "Content-Type: application/json" \
  -d '{"idade": 28, "genero": "Feminino", "orcamento": 200, "ocasiao": "Aniversário", "interesses": ["leitura", "cafe", "decoracao"]}' \
  | python -m json.tool
```

## CI/CD — Integração Contínua

Os testes rodam automaticamente no GitHub Actions a cada push e pull request. A configuração está em `.github/workflows/testes.yml`. O pipeline instala as dependências e executa `pytest` em um ambiente Ubuntu com Python 3.14.
