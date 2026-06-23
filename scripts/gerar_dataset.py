"""Expande data/presentes.csv aplicando variacoes de edicao/preco sobre os
itens-base ja curados, em vez de inventar itens novos sem tags coerentes.
Rode com: python scripts/gerar_dataset.py
"""

import csv

CAMINHO_SAIDA = "data/presentes.csv"

SEEDS = [
    ("Fone de ouvido bluetooth", "Tecnologia", 150, 12, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "tecnologia;musica;jogos;fitness"),
    ("Smartwatch fitness", "Tecnologia", 650, 16, 65, "Unissex", "Aniversário;Natal;Formatura", "tecnologia;fitness;esportes;bem-estar"),
    ("Caixa de som portátil", "Tecnologia", 220, 12, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "tecnologia;musica;viagem;jogos"),
    ("Câmera instantânea", "Tecnologia", 350, 14, 60, "Unissex", "Aniversário;Natal;Formatura", "tecnologia;fotografia;viagem;arte"),
    ("Drone com câmera", "Tecnologia", 900, 16, 50, "Masculino", "Aniversário;Natal", "tecnologia;fotografia;viagem;jogos"),
    ("Console portátil de videogame", "Tecnologia", 1300, 10, 40, "Unissex", "Aniversário;Natal", "tecnologia;jogos;viagem"),
    ("Box coleção ficção científica", "Livros", 180, 14, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "leitura;arte;tecnologia"),
    ("Livro de poesia contemporânea", "Livros", 60, 16, 99, "Feminino", "Aniversário;Amigo Secreto;Dia dos Namorados", "leitura;arte;musica"),
    ("Romance best-seller", "Livros", 55, 14, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "leitura;arte"),
    ("Livro de receitas gourmet", "Livros", 90, 18, 99, "Unissex", "Aniversário;Natal;Dia das Mães", "leitura;culinaria;vinho;cafe"),
    ("Biografia inspiradora", "Livros", 70, 18, 99, "Masculino", "Aniversário;Dia dos Pais;Formatura", "leitura;bem-estar;arte"),
    ("Guia de viagem ilustrado", "Livros", 85, 16, 99, "Unissex", "Aniversário;Formatura", "leitura;viagem;fotografia;arte"),
    ("Carteira de couro", "Moda", 180, 18, 99, "Masculino", "Aniversário;Dia dos Pais;Natal", "moda;artesanato"),
    ("Bolsa transversal", "Moda", 220, 16, 99, "Feminino", "Aniversário;Dia das Mães;Natal", "moda;viagem;artesanato"),
    ("Óculos de sol clássico", "Moda", 150, 16, 99, "Unissex", "Aniversário;Natal;Formatura", "moda;viagem;fotografia"),
    ("Cachecol de lã", "Moda", 95, 14, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "moda;artesanato"),
    ("Relógio analógico", "Moda", 400, 18, 99, "Masculino", "Aniversário;Natal;Formatura", "moda;artesanato"),
    ("Conjunto de brincos", "Moda", 130, 14, 99, "Feminino", "Aniversário;Dia dos Namorados;Natal", "moda;beleza;artesanato"),
    ("Kit de skincare", "Beleza & Bem-estar", 160, 16, 99, "Feminino", "Aniversário;Dia das Mães;Natal", "beleza;bem-estar;moda"),
    ("Difusor de aromaterapia", "Beleza & Bem-estar", 130, 18, 99, "Unissex", "Aniversário;Natal;Dia das Mães", "bem-estar;decoracao;beleza"),
    ("Perfume importado", "Beleza & Bem-estar", 250, 18, 99, "Unissex", "Aniversário;Dia dos Namorados;Natal", "beleza;moda;viagem"),
    ("Kit de barbearia", "Beleza & Bem-estar", 170, 18, 99, "Masculino", "Aniversário;Dia dos Pais;Natal", "beleza;bem-estar;moda"),
    ("Vela aromática artesanal", "Beleza & Bem-estar", 70, 16, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "bem-estar;artesanato;decoracao"),
    ("Massageador elétrico", "Beleza & Bem-estar", 220, 18, 99, "Unissex", "Aniversário;Dia das Mães;Dia dos Pais", "bem-estar;fitness;tecnologia"),
    ("Tapete de yoga", "Esportes & Fitness", 110, 14, 99, "Unissex", "Aniversário;Natal;Amigo Secreto", "fitness;bem-estar;esportes"),
    ("Garrafa térmica esportiva", "Esportes & Fitness", 80, 12, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "fitness;esportes;viagem;cafe"),
    ("Kit de halteres ajustáveis", "Esportes & Fitness", 350, 16, 99, "Masculino", "Aniversário;Natal;Dia dos Pais", "fitness;esportes;bem-estar"),
    ("Bicicleta urbana", "Esportes & Fitness", 1800, 14, 60, "Unissex", "Aniversário;Natal;Formatura", "esportes;fitness;viagem;bem-estar"),
    ("Bola de futebol oficial", "Esportes & Fitness", 130, 8, 99, "Masculino", "Aniversário;Natal;Amigo Secreto", "esportes;jogos;fitness"),
    ("Relógio para corrida com GPS", "Esportes & Fitness", 700, 16, 65, "Unissex", "Aniversário;Natal;Formatura", "fitness;tecnologia;esportes;viagem"),
    ("Jogo de tabuleiro estratégico", "Jogos", 150, 10, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "jogos;arte;leitura"),
    ("Quebra-cabeça 1000 peças", "Jogos", 70, 10, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "jogos;arte;decoracao"),
    ("Console de videogame de mesa", "Jogos", 900, 10, 50, "Unissex", "Aniversário;Natal", "jogos;tecnologia;musica"),
    ("Conjunto de cartas colecionáveis", "Jogos", 120, 10, 40, "Masculino", "Aniversário;Amigo Secreto;Natal", "jogos;arte;artesanato"),
    ("Jogo de xadrez de madeira", "Jogos", 160, 12, 99, "Unissex", "Aniversário;Natal;Formatura", "jogos;artesanato;decoracao"),
    ("Controle sem fio para videogame", "Jogos", 280, 12, 60, "Unissex", "Aniversário;Natal;Amigo Secreto", "jogos;tecnologia;musica"),
    ("Máquina de café expresso", "Culinária", 600, 18, 99, "Unissex", "Aniversário;Natal;Dia das Mães", "culinaria;cafe;tecnologia;decoracao"),
    ("Kit de facas profissionais", "Culinária", 350, 18, 99, "Unissex", "Aniversário;Natal;Casamento", "culinaria;artesanato;decoracao"),
    ("Tábua de queijos artesanal", "Culinária", 130, 18, 99, "Unissex", "Aniversário;Natal;Casamento", "culinaria;artesanato;vinho;decoracao"),
    ("Kit para preparo de drinks", "Culinária", 180, 18, 99, "Masculino", "Aniversário;Natal;Amigo Secreto", "culinaria;vinho;decoracao"),
    ("Conjunto de taças para vinho", "Culinária", 150, 18, 99, "Unissex", "Aniversário;Casamento;Natal", "culinaria;vinho;decoracao;arte"),
    ("Panela de ferro fundido", "Culinária", 280, 18, 99, "Unissex", "Casamento;Natal;Dia das Mães", "culinaria;artesanato;decoracao"),
    ("Guitarra acústica iniciante", "Música", 700, 12, 99, "Unissex", "Aniversário;Natal;Formatura", "musica;arte"),
    ("Vinil de edição especial", "Música", 140, 16, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "musica;decoracao;arte"),
    ("Teclado musical portátil", "Música", 550, 10, 99, "Unissex", "Aniversário;Natal;Formatura", "musica;tecnologia"),
    ("Fone de ouvido para estúdio", "Música", 450, 16, 99, "Unissex", "Aniversário;Natal;Formatura", "musica;tecnologia;arte"),
    ("Ukulele decorado", "Música", 250, 10, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "musica;arte;artesanato;viagem"),
    ("Caixa de som retrô vintage", "Música", 320, 16, 99, "Unissex", "Aniversário;Natal", "musica;tecnologia;decoracao;arte"),
    ("Kit de pintura em tela", "Arte & Artesanato", 130, 12, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "arte;decoracao;artesanato"),
    ("Conjunto de canetas para caligrafia", "Arte & Artesanato", 90, 14, 99, "Unissex", "Aniversário;Amigo Secreto;Formatura", "arte;artesanato;leitura"),
    ("Kit de cerâmica para iniciantes", "Arte & Artesanato", 160, 14, 99, "Feminino", "Aniversário;Natal;Amigo Secreto", "arte;artesanato;decoracao"),
    ("Caderno de desenho artesanal", "Arte & Artesanato", 60, 12, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "arte;artesanato;leitura"),
    ("Kit de bordado", "Arte & Artesanato", 80, 14, 99, "Feminino", "Aniversário;Amigo Secreto;Natal", "artesanato;moda;decoracao"),
    ("Quadro decorativo pintado à mão", "Arte & Artesanato", 200, 16, 99, "Unissex", "Aniversário;Casamento;Natal", "arte;decoracao;artesanato"),
    ("Mala de viagem rígida", "Viagem", 450, 16, 99, "Unissex", "Aniversário;Natal;Formatura", "viagem;moda"),
    ("Travesseiro de pescoço para viagem", "Viagem", 60, 12, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "viagem;bem-estar"),
    ("Kit de organizadores de bagagem", "Viagem", 90, 14, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "viagem;moda"),
    ("Garrafa térmica para trilhas", "Viagem", 95, 14, 99, "Unissex", "Aniversário;Natal;Amigo Secreto", "viagem;esportes;fitness"),
    ("Mochila para notebook e viagem", "Viagem", 220, 14, 99, "Unissex", "Aniversário;Natal;Formatura", "viagem;tecnologia;moda"),
    ("Mapa-múndi de raspar", "Viagem", 110, 14, 99, "Unissex", "Aniversário;Natal;Amigo Secreto", "viagem;decoracao;arte"),
    ("Cama acolchoada para pets", "Pets", 130, 12, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "pets;decoracao;bem-estar"),
    ("Comedouro automático para pets", "Pets", 220, 16, 99, "Unissex", "Aniversário;Natal", "pets;tecnologia;bem-estar"),
    ("Brinquedo interativo para cães", "Pets", 70, 12, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "pets;jogos;fitness"),
    ("Coleira personalizada", "Pets", 60, 12, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "pets;artesanato;moda"),
    ("Casinha decorativa para gatos", "Pets", 180, 14, 99, "Unissex", "Aniversário;Natal", "pets;decoracao;artesanato"),
    ("Kit de higiene para pets", "Pets", 90, 14, 99, "Unissex", "Aniversário;Amigo Secreto;Natal", "pets;bem-estar"),
    ("Difusor de aromas com luz", "Casa & Decoração", 120, 16, 99, "Unissex", "Aniversário;Natal;Casamento", "decoracao;bem-estar;beleza"),
    ("Conjunto de almofadas decorativas", "Casa & Decoração", 140, 16, 99, "Unissex", "Casamento;Natal;Chá de Bebê", "decoracao;artesanato"),
    ("Vaso decorativo de cerâmica", "Casa & Decoração", 100, 16, 99, "Unissex", "Casamento;Aniversário;Natal", "decoracao;arte;jardinagem"),
    ("Kit de jardinagem para apartamento", "Casa & Decoração", 95, 16, 99, "Unissex", "Aniversário;Natal;Dia das Mães", "jardinagem;decoracao;bem-estar"),
    ("Luminária de mesa minimalista", "Casa & Decoração", 160, 16, 99, "Unissex", "Aniversário;Casamento;Natal", "decoracao;tecnologia"),
    ("Jogo de toalhas de banho", "Casa & Decoração", 130, 16, 99, "Unissex", "Casamento;Chá de Bebê;Natal", "decoracao;bem-estar"),
]

VARIACOES = [
    ("Linha Popular", 0.27),
    ("Linha Econômica", 0.40),
    ("Linha Essencial", 0.55),
    ("Versão Compacta", 0.75),
    ("Edição Padrão", 1.00),
    ("Linha Premium", 1.30),
    ("Edição Limitada", 1.65),
]

# palavras de estilo invariaveis em genero (nao mudam com o substantivo:
# "industrial"/"industrial", "vintage"/"vintage", "minimalista"/"minimalista"),
# pra multiplicar a variedade de nomes sem gerar erro de concordancia
# gramatical em portugues (o que aconteceria com adjetivos tipo "moderno").
ESTILOS = ["Vintage", "Industrial", "Minimalista"]


def gerar_linhas():
    linha_id = 1
    for nome, categoria, preco, idade_min, idade_max, genero, ocasiao, tags in SEEDS:
        for estilo in ESTILOS:
            for rotulo, multiplicador in VARIACOES:
                yield {
                    "id": linha_id,
                    "nome": f"{nome} {estilo} – {rotulo}",
                    "categoria": categoria,
                    "preco": round(preco * multiplicador),
                    "idade_min": idade_min,
                    "idade_max": idade_max,
                    "genero": genero,
                    "ocasiao": ocasiao,
                    "tags": tags,
                }
                linha_id += 1


if __name__ == "__main__":
    linhas = list(gerar_linhas())
    with open(CAMINHO_SAIDA, "w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=["id", "nome", "categoria", "preco", "idade_min", "idade_max", "genero", "ocasiao", "tags"],
        )
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"Gerado {CAMINHO_SAIDA} com {len(linhas)} itens.")
