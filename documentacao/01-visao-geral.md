# Visão Geral do Projeto

## Título

**Sistema de Recomendação de Presentes Baseado em Conteúdo com Similaridade de Cosseno e K-Vizinhos Mais Próximos (KNN)**

## Objetivo

O sistema tem como objetivo sugerir presentes personalizados a partir de um perfil de destinatário — informações como faixa etária, gênero, orçamento, ocasião e interesses pessoais. Em vez de perguntar o que a pessoa quer ganhar, ele infere quais itens do catálogo têm maior afinidade com quem vai recebê-los.

A proposta resolve um problema real: escolher um presente sem conhecer bem a pessoa é difícil e subjetivo. Com um modelo baseado em conteúdo, o sistema consegue comparar matematicamente o perfil do destinatário com cada item do catálogo e ranquear os mais compatíveis.

## Tipo de sistema de recomendação

Existem três abordagens principais para sistemas de recomendação:

| Abordagem | Como funciona | Limitação |
|---|---|---|
| Filtragem Colaborativa | Compara o comportamento de usuários semelhantes | Precisa de histórico de uso ("cold start problem") |
| Filtragem Baseada em Conteúdo | Compara atributos do item com o perfil do usuário | Depende de uma boa descrição dos itens |
| Híbrida | Combina as duas abordagens | Maior complexidade de implementação |

Este projeto utiliza **Filtragem Baseada em Conteúdo** (Content-Based Filtering). A escolha é justificada pelo contexto: não há histórico de compras nem avaliações de outros usuários — apenas o perfil de quem vai receber o presente e os atributos de cada item do catálogo.

## Contexto acadêmico

O projeto aplica conceitos de múltiplas áreas:

- **Álgebra Linear**: representação de dados como vetores em espaço multidimensional, produto interno (dot product), norma de vetores
- **Geometria Analítica**: similaridade de cosseno como medida de ângulo entre vetores
- **Aprendizado de Máquina**: K-Vizinhos Mais Próximos (KNN) como algoritmo de busca por similaridade
- **Engenharia de Software**: API REST com Flask, testes automatizados, CI/CD com GitHub Actions
- **Ciência de Dados**: codificação de atributos categóricos, filtragem e ranqueamento de resultados
