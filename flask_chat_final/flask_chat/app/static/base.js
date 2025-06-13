// Função para controlar requisitos do formulário
function setRequisito(ativo) {
    document.getElementById("campoMensagem").required = ativo;
  }
  
  function validarFormulario(form) {
    return true;
  }
  
  // Socket.IO e funcionalidades do chat
  document.addEventListener("DOMContentLoaded", () => {
    const socket = io();
    const historico = document.getElementById("historico");
    const campo = document.getElementById("campoMensagem");
  
    socket.on("nova_mensagem", data => {
      const texto = data.html;
      let cor = "#374151";
      if (texto.includes("[USUÁRIO]")) cor = "red";
      if (texto.includes("[ATENDENTE]")) cor = "blue";
      const novaLinha = `<div style="color:${cor}">${texto}</div>`;
      historico.innerHTML += novaLinha;
      historico.scrollTop = historico.scrollHeight;
    });
  
    // Foco e limpeza após envio
    document.getElementById("formulario").addEventListener("submit", () => {
      setTimeout(() => {
        campo.value = "";
        campo.focus();
      }, 100);
    });
  
    document.querySelectorAll("button").forEach(btn => {
      btn.addEventListener("click", () => {
        setTimeout(() => campo.focus(), 100);
      });
    });
  
    window.onload = () => campo.focus();

    // Animação dos ovos caindo (mais sutil para não atrapalhar o chat)
    const eggEmojis = ['🥚', '🍳', '🐣'];
    
    function createEggParticle() {
      const container = document.getElementById('floating-eggs');
      const span = document.createElement('span');
      span.className = 'egg-particle';
      
      span.textContent = eggEmojis[Math.floor(Math.random() * eggEmojis.length)];
      span.style.left = Math.random() * 100 + 'vw';
      span.style.fontSize = (8 + Math.random() * 8) + 'px';
      span.style.animationDuration = (8 + Math.random() * 8) + 's';
      
      container.appendChild(span);
      
      span.addEventListener('animationend', () => {
        span.remove();
      });
    }
    
    // Menos ovos caindo para não atrapalhar o chat
    setInterval(() => {
      createEggParticle();
    }, 800);
  });