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

function criarCardPresente(item) {
  const tags = item.tags.map((tag) => `<li>${tag}</li>`).join("");
  const temCompatibilidade =
    item.compatibilidade !== null && item.compatibilidade !== undefined;
  const selo = temCompatibilidade
    ? `<div class="selo-compatibilidade">${item.compatibilidade}%</div>`
    : "";

  return `
    <article class="cartao-presente">
      ${selo}
      <p class="categoria">${item.categoria}</p>
      <h3>${item.nome}</h3>
      <p class="preco">R$ ${item.preco.toFixed(2)}</p>
      <ul class="tags">${tags}</ul>
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
