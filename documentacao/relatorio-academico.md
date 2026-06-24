# Sistema de Recomendação de Presentes Baseado em Conteúdo com Similaridade de Cosseno e K-Vizinhos Mais Próximos (KNN)

---

**Disciplina:** Álgebra Linear
**Professor:** Fernando Soares

**Discentes:**
- Ariane Nascimento Andrade
- Josielle Santos da Silva
- Juliane Vitória de Souza Silva
- Mauricio Carvalho de Castro
- Iêgo Sérgio Costa de Souza

---

## Sumário

1. [Introdução](#1-introdução)
2. [Objetivos](#2-objetivos)
3. [Fundamentação Teórica](#3-fundamentação-teórica)
   - 3.1 Sistemas de Recomendação
   - 3.2 Espaço Vetorial e Representação dos Dados
   - 3.3 Produto Interno e Norma de Vetores
   - 3.4 Similaridade de Cosseno
   - 3.5 K-Vizinhos Mais Próximos (KNN)
   - 3.6 Coeficiente de Sobreposição
4. [Metodologia e Implementação](#4-metodologia-e-implementação)
   - 4.1 Arquitetura do Sistema
   - 4.2 O Dataset
   - 4.3 Pipeline de Recomendação
   - 4.4 Parâmetros do Modelo
5. [Tecnologias Utilizadas](#5-tecnologias-utilizadas)
6. [Interface do Sistema](#6-interface-do-sistema)
7. [Testes Automatizados](#7-testes-automatizados)
8. [Resultados e Discussão](#8-resultados-e-discussão)
9. [Conclusão](#9-conclusão)
10. [Referências](#10-referências)

---

## 1. Introdução

Escolher um presente adequado para outra pessoa é uma tarefa subjetiva e, muitas vezes, difícil. A falta de conhecimento sobre os interesses, faixa etária e preferências do destinatário torna essa escolha ainda mais desafiadora. Com o avanço das técnicas de recuperação de informação e aprendizado de máquina, tornou-se possível automatizar parcialmente esse processo por meio de **sistemas de recomendação**.

Este trabalho apresenta o desenvolvimento de um sistema web de recomendação de presentes que aplica, de forma direta, conceitos estudados na disciplina de **Álgebra Linear**: representação de dados como vetores em espaço multidimensional, produto interno entre vetores e a **similaridade de cosseno** como medida de ângulo entre vetores. O algoritmo de busca utilizado é o **K-Vizinhos Mais Próximos (KNN)**, que encontra os itens do catálogo matematicamente mais próximos do perfil informado pelo usuário.

A proposta une fundamentos matemáticos rigorosos com uma implementação prática e funcional, demonstrando que a álgebra linear não é apenas teoria abstrata, mas uma ferramenta concreta utilizada diariamente em sistemas modernos de inteligência artificial.

---

## 2. Objetivos

### Objetivo Geral

Desenvolver um sistema web de recomendação de presentes que utilize a similaridade de cosseno como métrica de distância dentro do algoritmo KNN para sugerir itens personalizados a partir do perfil de um destinatário.

### Objetivos Específicos

- Representar itens e perfis de usuário como vetores em um espaço vetorial de 19 dimensões utilizando **multi-hot encoding**
- Aplicar o produto interno (dot product) e a norma de vetores no cálculo das métricas de similaridade
- Implementar o algoritmo **K-Nearest Neighbors** com métrica cosseno para busca por similaridade
- Desenvolver uma interface web acessível que permita ao usuário informar o perfil do destinatário e visualizar os presentes recomendados com seus percentuais de compatibilidade
- Testar e validar o sistema com um catálogo de 1.512 produtos e 24 testes automatizados

---

## 3. Fundamentação Teórica

### 3.1 Sistemas de Recomendação

Sistemas de recomendação são algoritmos que filtram informações para sugerir itens relevantes a um usuário. Existem três abordagens principais:

| Abordagem | Princípio | Limitação |
|---|---|---|
| **Filtragem Colaborativa** | Recomenda com base no comportamento de usuários similares | Exige histórico de uso; problema do "cold start" |
| **Filtragem Baseada em Conteúdo** | Compara atributos dos itens com o perfil do usuário | Depende de uma boa descrição dos itens |
| **Híbrida** | Combina colaborativa e baseada em conteúdo | Maior complexidade de implementação |

Este projeto utiliza **Filtragem Baseada em Conteúdo** (Content-Based Filtering). Essa escolha é adequada ao contexto: não há histórico de compras nem avaliações de outros usuários disponíveis — apenas o perfil de quem vai receber o presente e os atributos de cada item do catálogo.

### 3.2 Espaço Vetorial e Representação dos Dados

O primeiro passo do modelo é transformar dados qualitativos em representações numéricas que possam ser manipuladas matematicamente. Para isso, é definido um **vocabulário fixo de 19 tags** (interesses):

```
tecnologia, fitness, viagem, musica, fotografia, arte,
jogos, leitura, culinaria, moda, beleza, bem-estar,
esportes, cafe, vinho, artesanato, decoracao, jardinagem, pets
```

Cada tag ocupa uma posição fixa nesse vocabulário. Um item ou perfil é representado como um **vetor binário de 19 dimensões**, onde cada componente é 1 se aquela tag está presente ou 0 se não está. Essa técnica é chamada de **multi-hot encoding**:

**Exemplo — "Tapete de yoga" (tags: fitness, bem-estar, esportes):**

```
v_item = (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0)
              ^fitness                    ^bem-estar ^esportes
```

**Exemplo — perfil do usuário (interesses: fitness, esportes):**

```
v_perfil = (0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0)
                ^fitness                          ^esportes
```

Com isso, tanto o perfil do destinatário quanto cada item do catálogo existem no **mesmo espaço vetorial ℝ¹⁹**, o que permite aplicar diretamente as operações de álgebra linear para medir a proximidade entre eles.

### 3.3 Produto Interno e Norma de Vetores

Dois conceitos fundamentais de álgebra linear são utilizados diretamente nas fórmulas do sistema:

**Produto interno (dot product):**

Dados dois vetores **a** e **b** em ℝⁿ:

```
a · b = Σ aᵢ × bᵢ   (para i = 1 até n)
```

Para vetores binários como os deste projeto, `a · b` conta quantas tags os dois vetores têm em comum — ou seja, a **interseção** dos conjuntos de interesses.

**Norma euclidiana:**

```
‖v‖ = √(v · v) = √(Σ vᵢ²)
```

Para vetores binários, `‖v‖²` = `v · v` é simplesmente o **número de tags** presentes no vetor (pois cada componente é 0 ou 1, e 1² = 1).

Ambas as operações são implementadas com NumPy: `np.dot(a, b)` para o produto interno.

### 3.4 Similaridade de Cosseno

A **similaridade de cosseno** mede o **ângulo entre dois vetores** no espaço multidimensional. Ela responde à pergunta: *esses dois vetores apontam na mesma direção?*

A fórmula é derivada diretamente da definição de produto interno com ângulo:

```
a · b = ‖a‖ × ‖b‖ × cos(θ)
```

Isolando o cosseno:

```
         a · b
cos(θ) = ───────
         ‖a‖ × ‖b‖
```

O resultado varia de **0** (vetores perpendiculares — nenhuma similaridade) a **1** (vetores paralelos — similaridade total). Para o cálculo de distância usada pelo KNN, utiliza-se `d = 1 - cos(θ)`, de modo que menor distância corresponde a maior similaridade.

**Por que cosseno e não distância euclidiana?**

A distância euclidiana mede o comprimento do segmento entre dois pontos no espaço. No contexto de vetores binários de tags, dois itens poderiam ter muitas tags em comum mas também muitas tags diferentes, resultando em uma distância euclidiana grande — mesmo sendo, semanticamente, muito similares. O cosseno captura a **direção** (interesses compartilhados) e é insensível à **magnitude** (quantidade de tags), o que o torna mais adequado para esse tipo de representação.

**Conexão com a disciplina:** a similaridade de cosseno é a aplicação direta da fórmula do ângulo entre vetores estudada em álgebra linear. O produto interno `a · b` e as normas `‖a‖`, `‖b‖` são os mesmos operadores do conteúdo da disciplina, aplicados a vetores em ℝ¹⁹.

### 3.5 K-Vizinhos Mais Próximos (KNN)

O **K-Nearest Neighbors (KNN)** é um algoritmo não-paramétrico de busca por similaridade. Em vez de criar um modelo com pesos ajustados durante um treino, ele simplesmente procura, em um conjunto de pontos conhecidos, quais são os **K pontos mais próximos** de um ponto de consulta.

Neste projeto:
- Os **pontos do espaço** são os vetores de tags de cada item do catálogo (matriz N × 19, onde N = número de itens após filtragem)
- O **ponto de consulta** é o vetor de interesses do perfil do destinatário
- A **métrica de distância** é a distância cosseno: `d = 1 - cos(θ)`

O KNN é implementado com `sklearn.neighbors.NearestNeighbors(metric="cosine")`. A cada requisição, o algoritmo:
1. Constrói a matriz de vetores dos itens candidatos (após filtros de idade, gênero e orçamento)
2. Recebe o vetor do perfil como ponto de consulta
3. Retorna os K itens com menor distância cosseno ao perfil

O valor de K é definido como `top_n × MULTIPLICADOR_POOL` (com `MULTIPLICADOR_POOL = 20`), retornando um pool amplo de candidatos que é depois filtrado pela métrica de compatibilidade e pela seleção de diversidade.

### 3.6 Coeficiente de Sobreposição (Szymkiewicz-Simpson)

Após o KNN identificar os candidatos mais próximos, o sistema calcula a **compatibilidade exibida ao usuário**. Para isso, não é usado o cosseno diretamente, mas o **Coeficiente de Sobreposição**:

```
              |A ∩ B|
overlap(A,B) = ───────────
              min(|A|, |B|)
```

Onde `|A|` e `|B|` são os tamanhos dos conjuntos de tags do item e do perfil, respectivamente, e `|A ∩ B|` é o número de tags em comum (o produto interno dos vetores binários).

**Por que não usar o cosseno diretamente como porcentagem exibida?**

O cosseno simétrico penaliza itens com tags extras. Um item com 10 tags, compartilhando 2 com o perfil, pontuaria pior do que um item com apenas essas 2 tags — mesmo sendo uma excelente opção.

**Por que não usar cobertura pura (overlap / |perfil|)?**

A cobertura pura cria um problema diferente: quanto mais interesses o usuário selecionar, mais difícil fica qualquer item atingir boa pontuação, pois o denominador cresce com o número de interesses escolhidos. Usuários que selecionam interesses de categorias muito diferentes (ex: tecnologia, culinária, viagem, leitura, pets) receberiam sempre lista vazia, pois nenhum produto cobre 5 categorias ao mesmo tempo.

**O Coeficiente de Sobreposição resolve os dois problemas:**

Ao dividir pelo *menor* dos dois conjuntos, um item focado que atende integralmente o que ele se propõe recebe 100% de compatibilidade — independente de quantos outros interesses o usuário selecionou. Isso reflete com precisão a semântica desejada: um presente é bom se é perfeito para *algum* dos seus interesses, não necessariamente para todos ao mesmo tempo.

---

## 4. Metodologia e Implementação

### 4.1 Arquitetura do Sistema

O sistema é composto por três camadas:

```
┌─────────────────────────────────────────────────┐
│              NAVEGADOR (Frontend)               │
│  HTML5 + CSS3 + JavaScript                      │
│  Formulário de perfil → fetch → cards resultado │
└──────────────────────┬──────────────────────────┘
                       │ POST /api/recomendar (JSON)
┌──────────────────────▼──────────────────────────┐
│              SERVIDOR (Flask / Python)          │
│  Validação de entrada → GiftRecommender         │
│  GET /  →  interface HTML                       │
│  GET /health  →  {"status": "ok"}               │
└──────────────────────┬──────────────────────────┘
                       │ chamada Python
┌──────────────────────▼──────────────────────────┐
│         MOTOR DE RECOMENDAÇÃO (recommender.py)  │
│  Filtros rígidos → Multi-hot → KNN → Cosseno    │
│  Coeficiente de Sobreposição → Diversidade      │
└──────────────────────┬──────────────────────────┘
                       │ pandas DataFrame
┌──────────────────────▼──────────────────────────┐
│              DADOS (data/presentes.csv)         │
│  1.512 itens · 12 categorias · 19 tags          │
└─────────────────────────────────────────────────┘
```

### 4.2 O Dataset

O catálogo de presentes contém **1.512 itens** gerados a partir de **72 produtos-base** por meio de variações sistemáticas:

- **3 estilos**: Vintage, Industrial, Minimalista
- **7 faixas de preço**: Linha Popular (×0,27) até Edição Limitada (×1,65)
- **Total**: 72 × 3 × 7 = **1.512 itens**

Cada item possui: nome, categoria (12 categorias), preço (de R$ 15 a R$ ~2.970), faixa etária, gênero, ocasiões aplicáveis e tags de interesse.

### 4.3 Pipeline de Recomendação

O algoritmo executa as seguintes etapas em sequência para cada requisição:

**Etapa 1 — Filtros Rígidos**

Filtra o catálogo por faixa etária, gênero e orçamento do destinatário. Se o orçamento for muito restritivo, o sistema tenta tolerâncias progressivas de 0%, 15% e 30%.

**Etapa 2 — Vetorização do Perfil**

Converte a lista de interesses selecionados em um vetor multi-hot de 19 dimensões:

```python
perfil_tags = np.array([1.0 if tag in interesses else 0.0
                        for tag in TAGS_VOCABULARIO])
```

**Etapa 3 — Busca KNN com Cosseno**

Monta a matriz de vetores dos candidatos (N × 19) e executa a busca pelos K mais próximos:

```python
modelo = NearestNeighbors(metric="cosine", n_neighbors=tamanho_pool)
modelo.fit(matriz_candidatos)
_, posicoes = modelo.kneighbors([perfil_tags])
```

**Etapa 4 — Cálculo do Coeficiente de Sobreposição**

Para cada candidato retornado pelo KNN:

```python
sobreposicao = np.dot(vetor_item, perfil_tags)          # |A ∩ B|
norma_item   = np.dot(vetor_item, vetor_item)           # |A|
menor        = min(norma_perfil, norma_item)            # min(|A|, |B|)
compatibilidade = (sobreposicao / menor) * 100
```

Itens com compatibilidade abaixo de **58%** são descartados.

**Etapa 5 — Deduplicação**

Remove variantes duplicadas do mesmo produto (mesmo conjunto de tags e categoria), mantendo apenas a variante com preço mais próximo do orçamento.

**Etapa 6 — Seleção com Diversidade**

Seleciona até 6 itens limitando no máximo 2 por categoria, garantindo variedade nas sugestões. O limite é relaxado progressivamente se não houver itens suficientes.

### 4.4 Parâmetros do Modelo

| Parâmetro | Valor | Justificativa |
|---|---|---|
| Dimensão do espaço vetorial | 19 | Uma dimensão por tag/interesse disponível |
| `MULTIPLICADOR_POOL` | 20 | KNN retorna pool amplo antes do corte de compatibilidade |
| `MIN_COMPATIBILIDADE` | 58% | Piso mínimo para evitar resultados sem relação com o perfil |
| `BONUS_OCASIAO` | +5% | Bônus quando o item serve para a ocasião informada |
| `TOLERANCIAS_ORCAMENTO` | [0%, 15%, 30%] | Flexibiliza o orçamento progressivamente |
| `MAX_ITENS_POR_CATEGORIA` | 2 | Garante diversidade de categorias nos resultados |
| `top_n` (padrão) | 6 | Número máximo de presentes recomendados |

---

## 5. Tecnologias Utilizadas

| Camada | Tecnologia | Versão | Uso no projeto |
|---|---|---|---|
| Linguagem | Python | 3.14 | Toda a lógica do backend |
| Servidor web | Flask | 3.1.3 | API REST e roteamento |
| Algoritmo KNN | scikit-learn | 1.9.0 | `NearestNeighbors(metric="cosine")` |
| Álgebra vetorial | NumPy | 2.5.0 | Vetores multi-hot e dot product |
| Dados tabulares | pandas | 3.0.3 | Carregamento e filtragem do CSV |
| Testes | pytest | 8.4.2 | 24 testes automatizados |
| CI/CD | GitHub Actions | — | Execução automática dos testes |
| Frontend | HTML5 / CSS3 / JS | — | Interface web responsiva |
| Fontes | Google Fonts | — | Poppins (títulos) + Inter (corpo) |

---

## 6. Interface do Sistema

A interface foi desenvolvida com estilo visual inspirado em plataformas de e-commerce modernas, usando uma paleta roxa/amarela e cards com gradientes por categoria.

### 6.1 Tela Inicial — Formulário de Perfil

*[RESERVADO PARA CAPTURA DE TELA — Formulário com campos: idade, gênero, orçamento, ocasião e interesses (chips selecionáveis)]*

---

### 6.2 Tela de Resultados — Cards de Recomendação

*[RESERVADO PARA CAPTURA DE TELA — Grid de cards mostrando produtos recomendados com nome, categoria, preço e % de compatibilidade]*

---

### 6.3 Aba "Sobre o Projeto"

*[RESERVADO PARA CAPTURA DE TELA — Aba com informações da disciplina, professor e equipe de desenvolvimento]*

---

### 6.4 Exemplo de Uso — Recomendação Completa

*[RESERVADO PARA CAPTURA DE TELA — Formulário preenchido + resultado exibido na mesma tela ou em sequência]*

---

## 7. Testes Automatizados

O projeto possui **24 testes automatizados** divididos em dois módulos, executados automaticamente pelo GitHub Actions a cada alteração no código.

### tests/test_app.py — Testes de integração da API (12 testes)

| Teste | O que verifica |
|---|---|
| `test_index_retorna_200` | Página inicial carrega corretamente |
| `test_health_retorna_ok` | Endpoint `/health` responde `{"status": "ok"}` |
| `test_recomendar_retorna_lista` | API retorna lista de resultados válida |
| `test_recomendar_sem_body_retorna_400` | Requisição sem corpo retorna 400 |
| `test_idade_invalida_retorna_400` | Validação de idade fora do intervalo |
| `test_genero_invalido_retorna_400` | Validação de gênero desconhecido |
| `test_interesse_invalido_retorna_400` | Validação de tag não existente no vocabulário |
| `test_rota_api_nao_encontrada_retorna_json` | 404 em rotas `/api/` retorna JSON |
| *(e outros)* | |

### tests/test_recommender.py — Testes unitários do motor (12 testes)

| Teste | O que verifica |
|---|---|
| `test_recomendacao_basica` | Resultado não vazio para perfil simples |
| `test_compatibilidade_entre_0_e_100` | Compatibilidade sempre no intervalo válido |
| `test_diversidade_limite_por_categoria` | No máximo 2 itens da mesma categoria |
| `test_remover_variantes_duplicadas` | Deduplicação elimina variantes com mesmas tags |
| `test_fallback_por_orcamento` | Fallback quando perfil não tem tags válidas |
| `test_selecionar_com_diversidade_relaxa_limite` | Relaxamento do limite de categoria quando necessário |
| *(e outros)* | |

---

## 8. Resultados e Discussão

### Qualidade das recomendações

O sistema demonstrou ser capaz de recomendar presentes relevantes para uma ampla variedade de perfis. A escolha do **Coeficiente de Sobreposição** como métrica de compatibilidade exibida foi fundamental para resolver um problema que as métricas mais simples não conseguiam solucionar:

- Quando o usuário selecionava interesses de categorias muito diferentes (ex: tecnologia, culinária, pets e leitura), a métrica de cobertura pura (`overlap / |perfil|`) produzia resultados vazios, pois nenhum produto cobre todos os 5 interesses simultaneamente
- O Coeficiente de Sobreposição resolve isso ao dividir pelo *menor* dos dois conjuntos: um item que atende plenamente 2 dos seus 5 interesses selecionados recebe 100% de compatibilidade, independente dos outros 3

### Diversidade dos resultados

O mecanismo de seleção com diversidade por categoria garante que os 6 presentes sugeridos não venham todos da mesma categoria, tornando as recomendações mais úteis e variadas.

### Transparência

Cada recomendação exibe o percentual de compatibilidade calculado, tornando o sistema transparente e interpretável — o usuário pode entender por que determinado presente foi sugerido.

### Limitações

- O sistema utiliza apenas dados fornecidos pelo usuário na sessão (não há perfil persistente ou histórico)
- As recomendações são limitadas ao catálogo pré-definido de 1.512 itens
- A ocasião é tratada apenas como bônus (+5%), não como filtro rígido, para não restringir demais os resultados

---

## 9. Conclusão

Este projeto demonstrou na prática como conceitos fundamentais de **álgebra linear** — produto interno, norma de vetores, ângulo entre vetores e similaridade de cosseno — estão diretamente presentes nos algoritmos de inteligência artificial utilizados em sistemas reais de recomendação.

O sistema desenvolvido vai além de uma demonstração teórica: é uma aplicação web funcional com API REST, interface amigável, catálogo de 1.512 itens, 24 testes automatizados e pipeline de integração contínua — mostrando que os mesmos fundamentos matemáticos estudados na disciplina de Álgebra Linear são a base de tecnologias amplamente utilizadas na indústria de tecnologia.

A principal contribuição técnica do projeto foi a escolha e justificativa do **Coeficiente de Sobreposição** como métrica de compatibilidade, em substituição ao cosseno simétrico e à cobertura pura, resolvendo de forma elegante o problema de resultados vazios para perfis com interesses diversificados.

---

## 10. Referências

MANNING, Christopher D.; RAGHAVAN, Prabhakar; SCHÜTZE, Hinrich. **Introduction to Information Retrieval**. Cambridge University Press, 2008.

RICCI, Francesco; ROKACH, Lior; SHAPIRA, Bracha. **Recommender Systems Handbook**. Springer, 2011.

STRANG, Gilbert. **Introduction to Linear Algebra**. 5. ed. Wellesley-Cambridge Press, 2016.

PEDREGOSA, Fabian et al. **Scikit-learn: Machine Learning in Python**. Journal of Machine Learning Research, v. 12, p. 2825–2830, 2011.

SZYMKIEWICZ, D. Une contribution statistique à la géographie floristique. **Acta Societatis Botanicorum Poloniae**, v. 5, n. 3, p. 249–265, 1934. *(Coeficiente de Sobreposição)*
