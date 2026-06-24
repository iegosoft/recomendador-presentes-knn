# Arquitetura do Sistema

## Visão geral

O sistema é uma aplicação web de página única (SPA simples) composta por três camadas:

```
┌─────────────────────────────────────────────────────┐
│                   NAVEGADOR (Frontend)               │
│  HTML/CSS/JS  →  Formulário de perfil                │
│                  Cards de resultado                  │
│                  fetch('/api/recomendar', {...})      │
└─────────────────────────┬───────────────────────────┘
                          │ HTTP JSON
┌─────────────────────────▼───────────────────────────┐
│                  SERVIDOR (Flask)                    │
│  app.py        GET /          → index.html           │
│                POST /api/recomendar → JSON           │
│                GET /health    → {"status":"ok"}      │
│                Validação de entrada                  │
└─────────────────────────┬───────────────────────────┘
                          │ chamada Python
┌─────────────────────────▼───────────────────────────┐
│              MOTOR DE RECOMENDAÇÃO                   │
│  recommender.py  GiftRecommender                     │
│                  - Filtros (idade, gênero, orçamento)│
│                  - Vetorização multi-hot             │
│                  - KNN (scikit-learn, cosine)        │
│                  - Coeficiente de Sobreposição       │
│                  - Deduplicação + Diversidade        │
└─────────────────────────┬───────────────────────────┘
                          │ pandas DataFrame
┌─────────────────────────▼───────────────────────────┐
│                    DADOS                             │
│  data/presentes.csv  — 1.512 itens                  │
└─────────────────────────────────────────────────────┘
```

## Estrutura de pastas

```
recomendador-presentes-knn/
│
├── app.py                    # Servidor Flask + API REST
├── recommender.py            # Motor de recomendação (KNN + cosseno)
│
├── data/
│   └── presentes.csv         # Catálogo com 1.512 itens
│
├── scripts/
│   └── gerar_dataset.py      # Gerador do catálogo (executado uma vez)
│
├── templates/
│   └── index.html            # Interface HTML
│
├── static/
│   ├── css/style.css         # Estilos (paleta e-commerce, cards)
│   └── js/app.js             # Lógica frontend (fetch, render)
│
├── tests/
│   ├── test_app.py           # 12 testes de integração da API
│   └── test_recommender.py   # 12 testes unitários do motor
│
├── documentacao/             # Esta documentação
│
├── requirements.txt          # Dependências de produção
├── requirements-dev.txt      # Dependências de desenvolvimento (+ pytest)
└── .github/
    └── workflows/
        └── testes.yml        # Pipeline de CI (GitHub Actions)
```

## Fluxo de uma requisição de recomendação

```
1. Usuário preenche o formulário no navegador
   └─ Campos: idade, gênero, orçamento, ocasião, interesses (checkboxes)

2. JavaScript coleta os dados e faz:
   POST /api/recomendar
   Content-Type: application/json
   Body: {"idade": 28, "genero": "Feminino", "orcamento": 200,
          "ocasiao": "Aniversário", "interesses": ["leitura", "cafe"]}

3. Flask (app.py) recebe a requisição
   └─ Valida todos os campos (_validar_dados)
   └─ Chama recomendador.recomendar(...)

4. GiftRecommender (recommender.py) executa o pipeline:
   └─ Filtra por idade e gênero (pandas)
   └─ Filtra por orçamento (progressivo)
   └─ Vetoriza o perfil (numpy multi-hot)
   └─ KNN com cosseno (scikit-learn) → candidatos
   └─ Calcula compatibilidade (coeficiente de sobreposição)
   └─ Deduplica variantes
   └─ Seleciona com diversidade por categoria
   └─ Retorna lista de até 6 itens

5. Flask retorna:
   HTTP 200
   {"resultados": [{id, nome, categoria, preco, tags, compatibilidade}, ...]}

6. JavaScript renderiza os cards de resultado na tela
```

## Inicialização da aplicação

Quando o servidor inicia, o `GiftRecommender` é instanciado uma única vez no escopo global (`app.py`, linha 15). Durante a inicialização:
- O CSV é lido e carregado em um `DataFrame` pandas
- Os campos de tags e ocasiões são parseados de strings para listas Python
- A **matriz de vetores multi-hot** de todos os 1.512 itens é pré-computada como um array NumPy 1512×19

Essa pré-computação acontece apenas na inicialização. A cada requisição, apenas os filtros de idade/gênero/orçamento são aplicados para reduzir o conjunto antes de passar para o KNN.
