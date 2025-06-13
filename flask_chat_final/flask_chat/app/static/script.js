// Função para abrir janelas do chat (mantendo sua funcionalidade original)
function abrirJanela(papel) {
  window.open(
    '/' + papel,
    papel + '_janela',
    'width=500,height=700,resizable=yes,scrollbars=yes'
  );
}

// Animação dos ovos caindo
const eggEmojis = [
  '🥚', '🐣', '🐤', '🍳', '🥚', '🐓', '🐥', '🥚', '🍳', '🐣', 
  '🥚', '🐤', '🍳', '🐥'
];

function createEggParticle() {
  const container = document.getElementById('floating-eggs');
  const span = document.createElement('span');
  span.className = 'egg-particle';

  // Escolhe emoji aleatório relacionado a ovos
  span.textContent = eggEmojis[Math.floor(Math.random() * eggEmojis.length)];

  // Define posição horizontal aleatória
  span.style.left = Math.random() * 100 + 'vw';

  // Define tamanho aleatório entre 12 e 24 pixels
  const size = 12 + Math.random() * 12;
  span.style.fontSize = size + 'px';

  // Define duração da queda entre 6 e 12 segundos
  const duration = 6 + Math.random() * 6;
  span.style.animationDuration = duration + 's';

  container.appendChild(span);

  // Remove o elemento após a animação para não poluir DOM
  span.addEventListener('animationend', () => {
    span.remove();
  });
}

// Cria muitos ovos caindo ao longo do tempo
function startFallingEggs() {
  setInterval(() => {
    createEggParticle();
  }, 200); // A cada 200ms cria um novo
}

// Inicia a animação quando o DOM estiver carregado
document.addEventListener('DOMContentLoaded', () => {
  startFallingEggs();
});

function ouvirPiada() {
  fetch('/piada')
  .then(response => response.json())
  .then(data => {
      const piada = data.piada;
      const fala = new SpeechSynthesisUtterance(piada);
      fala.lang = 'pt-BR'; // voz em português
      window.speechSynthesis.speak(fala);
  })
  .catch(error => console.error('Erro ao buscar piada:', error));
}