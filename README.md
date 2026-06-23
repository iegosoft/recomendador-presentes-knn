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

Para desenvolver (com `pytest`), instale as dependências de desenvolvimento
em vez disso:

```bash
pip install -r requirements-dev.txt
```

## Como rodar

```bash
python app.py
```

A aplicação fica disponível em `http://localhost:5000`.

### Variáveis de ambiente

| Variável      | Padrão      | Descrição                                  |
|---------------|-------------|---------------------------------------------|
| `FLASK_DEBUG` | `false`     | `true` ativa o modo debug do Flask (recarga automática e depurador interativo — nunca use em produção) |
| `HOST`        | `127.0.0.1` | endereço em que o servidor escuta           |
| `PORT`        | `5000`      | porta em que o servidor escuta              |

### Rodando em produção

O servidor embutido do Flask (`python app.py`) é só para desenvolvimento.
Em produção, sirva a aplicação com um servidor WSGI como o
[Gunicorn](https://gunicorn.org/):

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

O endpoint `GET /health` devolve `{"status": "ok"}` e pode ser usado como
healthcheck por um orquestrador (Docker, Kubernetes, etc.).

## Como rodar os testes

```bash
pytest
```

O workflow em `.github/workflows/testes.yml` roda essa mesma suíte
automaticamente em cada push e pull request para `main`.

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
margem nenhuma, depois com 15% e por fim com 30% de margem. A tolerância
só avança se a faixa de preço atual não tiver **nenhum item com
compatibilidade aceitável** (ver seção 3) — não basta existir algum item
qualquer dentro do preço. Essa distinção importa: a versão antiga parava
de ampliar a busca assim que encontrava 3 itens baratos de qualquer tipo,
e podia acabar recomendando algo sem nenhuma relação com os interesses só
porque cabia no orçamento original.

### 2. Ranqueamento por cobertura do perfil (KNN + cosseno)

Cada presente do catálogo é representado por um vetor multi-hot com uma
posição para cada tag do vocabulário (a ocasião **não** entra nesse
vetor — ver por quê mais abaixo). O perfil informado no formulário é
convertido para o mesmo formato a partir dos interesses escolhidos.

O `NearestNeighbors` do scikit-learn (`metric="cosine"`) busca, entre os
itens já filtrados, um pool de candidatos bem maior do que o número de
resultados exibidos (6x). Esse pool é só a busca inicial — a porcentagem
de compatibilidade exibida **não** é a similaridade de cosseno simétrica.
Cosseno padrão (e qualquer métrica que penalize o item por ter
características extras, como o coeficiente de Dice) faz um item com 10
tags compartilhando 2 com o perfil pontuar pior do que um item com só
essas 2 tags — o que deixava presentes genuinamente bons com porcentagens
baixas e arbitrárias. Em vez disso, a compatibilidade exibida é a
**cobertura do perfil**: que fração das tags escolhidas pelo usuário
aquele item realmente tem — `dot(perfil, item) / dot(perfil, perfil)`. Um
item que tem todas as tags escolhidas marca 100%, independente de quantas
outras características ele também tenha.

A ocasião conta como um **bônus** de 5 pontos (`BONUS_OCASIAO`) quando o
item também serve para a ocasião escolhida, em vez de entrar no mesmo
vetor dos interesses. Ela foi deliberadamente tirada do vetor principal:
a maioria dos itens do catálogo serve para várias ocasiões ao mesmo
tempo, e colocar isso no mesmo cálculo de cobertura/cosseno fazia esse
"servir para várias ocasiões" ser tratado como característica extra
irrelevante, inflando a base de comparação do item e empurrando a
compatibilidade pra baixo de forma artificial — inclusive em casos
simples de 1 ou 2 interesses, que deveriam pontuar alto sem dificuldade.

### 3. Piso mínimo de confiança

Nenhuma recomendação é exibida com menos de 58% de compatibilidade
(`MIN_COMPATIBILIDADE` em `recommender.py`). Itens abaixo disso são
descartados antes mesmo de chegar à etapa de diversidade — o sistema
prefere devolver uma lista menor (ou vazia, com o estado correspondente
no front-end) a preencher os resultados com presentes de baixa relação
com o que foi pedido só para completar a grade. O valor foi calibrado pra
não ficar rigoroso demais: cobrir 2 de 3 interesses escolhidos já dá 66,7%
de cobertura e passa do piso, mas cobrir só 1 de 3 (33,3%) ainda fica de
fora — o sistema não finge uma confiança que não tem.

### 4. Diversidade e desempate

Pegar só os itens mais parecidos do pool, sem mais nada, tende a devolver
uma lista dominada por uma única categoria, porque itens da mesma
categoria tendem a compartilhar tags — e o catálogo tem várias variantes
de preço do mesmo produto-base com tags idênticas, que empatam
perfeitamente em compatibilidade entre si. Por isso, antes da seleção
final: variantes do mesmo produto-base (mesma categoria e mesmas tags) são
reduzidas a uma só, mantendo a mais próxima do orçamento; depois, a
seleção limita em 2 o número de itens por categoria
(`MAX_ITENS_POR_CATEGORIA`), relaxando esse limite progressivamente só se
não houver itens suficientes de outras categorias para preencher a lista
(em vez de descartar o limite por completo). Quando duas opções têm
exatamente a mesma compatibilidade, o desempate é pela proximidade do
preço ao orçamento informado. O resultado final é sempre reordenado por
compatibilidade antes de ser devolvido.

### 5. Fallback para perfil sem correspondência

Se o vetor de perfil (interesses) resultar todo zerado, o sistema não
tenta calcular cobertura — cai num fallback que ordena os itens filtrados
pela proximidade ao orçamento informado, sem gerar erro. Na prática isso
só acontece chamando `GiftRecommender.recomendar` diretamente com tags
fora do vocabulário, já que a API valida os interesses antes de chegar
aqui.
