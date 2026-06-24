# Tecnologias Utilizadas

## Backend

### Python 3.14
Linguagem principal do projeto. Utilizado para o motor de recomendação, o servidor web e os scripts de geração de dados.

### Flask 3.1.3
Framework web minimalista para Python. Responsável por:
- Servir a interface HTML (`GET /`)
- Expor a API de recomendação (`POST /api/recomendar`)
- Lidar com erros HTTP (404, 500) com respostas JSON quando o caminho começa com `/api/`
- Endpoint de saúde (`GET /health`) para monitoramento

### scikit-learn 1.9.0
Biblioteca de aprendizado de máquina do Python. Utilizada especificamente para o algoritmo **KNN** através da classe `sklearn.neighbors.NearestNeighbors`. A métrica configurada é `"cosine"`, o que faz com que a busca pelos vizinhos mais próximos use a distância cosseno internamente.

### pandas 3.0.3
Biblioteca para manipulação de dados tabulares. Usada para:
- Carregar e indexar o catálogo de presentes (`data/presentes.csv`)
- Aplicar filtros de idade, gênero e orçamento sobre o DataFrame
- Converter campos multivalorados separados por `;` em listas Python

### NumPy 2.5.0
Biblioteca de computação numérica. Usada para:
- Representar vetores de tags como arrays de ponto flutuante (`np.ndarray`)
- Calcular o produto interno (dot product) entre vetores: `np.dot(a, b)`
- Montar a matriz de vetores de todos os itens do catálogo

## Frontend

### HTML5 + CSS3 + JavaScript (vanilla)
A interface foi construída sem frameworks frontend adicionais:
- **HTML5**: formulário de perfil, renderização dinâmica dos cards de resultado
- **CSS3**: variáveis CSS, gradientes, animações de hover, layout responsivo com grid
- **JavaScript**: coleta os dados do formulário, chama a API via `fetch`, renderiza os cards de resultado dinamicamente

### Google Fonts (Poppins + Inter)
- **Poppins**: títulos e destaques (estilo e-commerce)
- **Inter**: corpo do texto e campos de formulário

## Qualidade e infraestrutura

### pytest 8.4.2
Framework de testes para Python. O projeto conta com 24 testes automatizados cobrindo:
- Respostas corretas da API (HTTP 200, 400, 404)
- Comportamento do motor de recomendação (diversidade, deduplicação, fallback por orçamento)
- Casos extremos (perfil sem interesses válidos, orçamento muito restritivo)

### GitHub Actions (CI/CD)
Pipeline de integração contínua configurado em `.github/workflows/testes.yml`. Executa automaticamente todos os testes via `pytest` em cada push e pull request, garantindo que nenhuma alteração quebre o sistema antes de ser incorporada à branch principal.

## Resumo

| Camada | Tecnologia | Versão |
|---|---|---|
| Linguagem | Python | 3.14 |
| Servidor web | Flask | 3.1.3 |
| Algoritmo KNN | scikit-learn | 1.9.0 |
| Manipulação de dados | pandas | 3.0.3 |
| Álgebra vetorial | NumPy | 2.5.0 |
| Testes | pytest | 8.4.2 |
| CI/CD | GitHub Actions | — |
| Frontend | HTML5 / CSS3 / JS | — |
| Fontes | Google Fonts (Poppins, Inter) | — |
