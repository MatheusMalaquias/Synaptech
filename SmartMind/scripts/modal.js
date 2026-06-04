const modal = document.querySelector('#modal');
const modalDetails = document.querySelector('#modalDetails');
const closeBtn = document.querySelector('#closeModal');

export function openModal(tool) {
  modal.classList.remove('hidden');

  modalDetails.innerHTML = `
    <h2>${tool.name}</h2>
    <p>${tool.description}</p>
    <p>Category: ${tool.category}</p>
    <p>Rating: ${tool.rating}</p>
  `;
}

closeBtn.addEventListener('click', () => {
  modal.classList.add('hidden');
});