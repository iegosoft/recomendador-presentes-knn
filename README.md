# Recomendador de Presentes

Aplicação web em Flask que recomenda presentes com base no perfil de quem
vai receber (idade, gênero, orçamento, ocasião e interesses), usando
similaridade de cosseno e KNN sobre um catálogo de produtos.

## Como instalar

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Como rodar

```bash
python app.py
```

A aplicação fica disponível em `http://localhost:5000`.

## Como rodar os testes

```bash
pytest
```

## Estrutura de pastas

```
data/             dataset simulado de presentes (presentes.csv)
templates/        template HTML da interface (index.html)
static/css/       estilos da interface
static/js/        lógica de front-end (fetch para a API)
scripts/          scripts utilitários descartáveis
tests/            testes automatizados (pytest)
recommender.py    motor de recomendação (classe GiftRecommender)
app.py            aplicação Flask e rotas
```

## Como o algoritmo funciona

A recomendação acontece em duas fases bem separadas: primeiro **filtros
rígidos** eliminam itens incompatíveis, depois um **ranqueamento por
similaridade** ordena o que sobrou pelo quanto combina com o perfil
informado.

### 1. Filtros rígidos

Antes de qualquer cálculo de similaridade, o catálogo é reduzido aos itens
que:

- estão dentro da faixa de idade do destinatário;
- são compatíveis com o gênero informado (itens `Unissex` sempre passam);
- cabem no orçamento.

O filtro de orçamento usa uma tolerância progressiva: tenta primeiro sem
margem nenhuma, depois com 15% e por fim com 30% de margem, parando na
primeira faixa que devolve uma quantidade razoável de itens. Isso evita
tanto recomendar algo fora do orçamento sem necessidade quanto devolver
uma lista vazia quando só faltavam alguns reais para encaixar um item bom.

### 2. Ranqueamento por similaridade de cosseno (KNN)

Cada presente do catálogo é representado por um vetor multi-hot: uma
posição para cada tag do vocabulário e uma posição para cada ocasião,
marcadas com 1 quando o presente tem aquela característica. O perfil
informado no formulário é convertido para o mesmo formato de vetor a
partir dos interesses e da ocasião escolhidos. Quando a ocasião escolhida
é "Sem ocasião específica", a parte do vetor referente a ocasião fica
zerada e só os interesses contam.

Com os itens já filtrados e vetorizados, o `NearestNeighbors` do
scikit-learn (`metric="cosine"`) encontra os vizinhos mais próximos do
vetor de perfil, e a distância de cosseno é convertida em porcentagem de
compatibilidade (`(1 - distância) * 100`).

**Por que cosseno e não distância euclidiana:** os vetores aqui são
multi-hot e esparsos — o que importa é a *proporção* de características em
comum, não o quão "longe" os pontos estão em valor absoluto. Dois
presentes com 2 tags em comum entre 3 tags cada são muito mais parecidos
entre si do que um presente com 2 tags e outro com 10 tags que também
compartilham 2 — mas a distância euclidiana penalizaria esse segundo caso
pelo simples fato de o vetor ser "maior". Cosseno mede o ângulo entre os
vetores, ignorando magnitude, o que é exatamente a noção de similaridade
que faz sentido para conjuntos de características como tags e ocasiões.

Se o vetor de perfil resultar todo zerado (nenhum interesse ou ocasião
reconhecida no vocabulário), o sistema cai num fallback: em vez de KNN,
ordena os itens filtrados pela proximidade ao orçamento informado, sem
gerar erro.
