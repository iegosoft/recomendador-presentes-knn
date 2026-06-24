const form = document.getElementById("form-recomendacao");
const mensagemErro = document.getElementById("mensagem-erro");
const gridResultados = document.getElementById("grid-resultados");
const resultadosTitulo = document.getElementById("resultados-titulo");
const avisoOrcamento = document.getElementById("aviso-orcamento");
const estadoVazio = document.getElementById("estado-vazio");

form.addEventListener("submit", async (evento) => {
  evento.preventDefault();
  esconderMensagens();

  const dados = coletarDados();

  if (dados.interesses.length === 0) {
    mostrarErro("Selecione pelo menos um interesse.");
    return;
  }

  try {
    const resposta = await fetch("/api/recomendar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(dados),
    });

    const corpo = await resposta.json();

    if (!resposta.ok) {
      mostrarErro(corpo.erro || "Não foi possível buscar recomendações.");
      return;
    }

    renderizarResultados(corpo);
  } catch (erro) {
    mostrarErro("Erro de conexão. Tente novamente.");
  }
});

function coletarDados() {
  const interesses = Array.from(
    form.querySelectorAll('input[name="interesses"]:checked')
  ).map((input) => input.value);

  return {
    idade: Number(form.idade.value),
    genero: form.genero.value,
    orcamento: Number(form.orcamento.value),
    ocasiao: form.ocasiao.value,
    interesses,
  };
}

function renderizarResultados(corpo) {
  const resultados = corpo.resultados || [];

  resultadosTitulo.hidden = false;

  if (corpo.aviso) {
    avisoOrcamento.hidden = false;
    avisoOrcamento.textContent = corpo.aviso;
  }

  if (resultados.length === 0) {
    estadoVazio.hidden = false;
    gridResultados.innerHTML = "";
    return;
  }

  gridResultados.innerHTML = resultados.map(criarCardPresente).join("");
}

const VISUAL_POR_CATEGORIA = {
  "Tecnologia": { emoji: "💻", cores: ["#6c2bd9", "#9b6cf2"] },
  "Livros": { emoji: "📚", cores: ["#1d6fa5", "#5fb3e0"] },
  "Moda": { emoji: "👗", cores: ["#d9266c", "#f06ba0"] },
  "Beleza & Bem-estar": { emoji: "💆", cores: ["#e0a02b", "#f5cd6b"] },
  "Esportes & Fitness": { emoji: "🏋️", cores: ["#1f9d6c", "#5fd99b"] },
  "Jogos": { emoji: "🎮", cores: ["#7c3aed", "#b794f6"] },
  "Culinária": { emoji: "🍳", cores: ["#d9601f", "#f5a35e"] },
  "Música": { emoji: "🎵", cores: ["#c0265a", "#ef6f9c"] },
  "Arte & Artesanato": { emoji: "🎨", cores: ["#1d8a99", "#5fcdde"] },
  "Viagem": { emoji: "✈️", cores: ["#2563eb", "#7ba6f7"] },
  "Pets": { emoji: "🐾", cores: ["#a0522d", "#d29b6e"] },
  "Casa & Decoração": { emoji: "🏠", cores: ["#5a3ea1", "#9b85d6"] },
};

function criarCardPresente(item) {
  const tags = item.tags.map((tag) => `<li>${tag}</li>`).join("");
  const temCompatibilidade =
    item.compatibilidade !== null && item.compatibilidade !== undefined;
  const etiqueta = temCompatibilidade
    ? `<span class="etiqueta-compatibilidade">${item.compatibilidade}% de afinidade</span>`
    : "";

  const visual = VISUAL_POR_CATEGORIA[item.categoria] || { emoji: "🎁", cores: ["#6c2bd9", "#9b6cf2"] };
  const fundoCapa = `linear-gradient(135deg, ${visual.cores[0]}, ${visual.cores[1]})`;

  return `
    <article class="cartao-presente">
      <div class="cartao-capa" style="background: ${fundoCapa}">
        ${visual.emoji}
        ${etiqueta}
      </div>
      <div class="cartao-corpo">
        <p class="categoria">${item.categoria}</p>
        <h3>${item.nome}</h3>
        <p class="preco">R$ ${item.preco.toFixed(2)}</p>
        <ul class="tags">${tags}</ul>
      </div>
    </article>
  `;
}

function mostrarErro(texto) {
  mensagemErro.hidden = false;
  mensagemErro.textContent = texto;
}

function esconderMensagens() {
  mensagemErro.hidden = true;
  avisoOrcamento.hidden = true;
  estadoVazio.hidden = true;
}

// ── Troca de abas ────────────────────────────────────────
document.querySelectorAll(".aba-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const alvo = btn.dataset.aba;

    document.querySelectorAll(".aba-btn").forEach((b) => {
      b.classList.remove("aba-ativa");
      b.setAttribute("aria-selected", "false");
    });
    document.querySelectorAll(".painel-aba").forEach((p) => {
      p.hidden = true;
    });

    btn.classList.add("aba-ativa");
    btn.setAttribute("aria-selected", "true");
    document.getElementById(`painel-${alvo}`).hidden = false;
  });
});
