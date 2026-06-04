import { openModal } from './modal.js';

const container = document.querySelector('#toolsContainer');

async function getTools() {
  try {
    const response = await fetch('../data/tools.json');
    const data = await response.json();
    displayTools(data);
  } catch (error) {
    console.error('Erro:', error);
  }
}

function displayTools(tools) {
  tools.forEach(tool => {
    const card = document.createElement('div');
    card.classList.add('card');

    card.innerHTML = `
      <h3>${tool.name}</h3>
      <p>${tool.category}</p>
      <p>⭐ ${tool.rating}</p>
    `;

    card.addEventListener('click', () => {
      openModal(tool);
    });

    container.appendChild(card);
  });
}

getTools();