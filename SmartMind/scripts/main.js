const container = document.querySelector("#class-schedule-container");
const modal = document.querySelector("#class-details-modal");
const closeBtn = document.querySelector("#modal-close-button");

const menuButton = document.querySelector("#menu-button");
const navMenu = document.querySelector("#nav-menu");

if (menuButton && navMenu) {
    menuButton.addEventListener("click", () => {
        navMenu.classList.toggle("open");
        menuButton.classList.toggle("open");
    });
}

const yearSpan = document.querySelector("#current-year");
const lastModified = document.querySelector("#last-modified");

if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
}

if (lastModified) {
    lastModified.textContent = document.lastModified;
}

const visitDisplay = document.querySelector("#visits");

if (visitDisplay) {
    let visits = localStorage.getItem("visits");

    if (!visits) {
        visits = 1;
    } else {
        visits = Number(visits) + 1;
    }

    localStorage.setItem("visits", visits);
    visitDisplay.textContent = visits;
}

if (container) {
    loadTools();
}

async function loadTools() {
    try {
        const response = await fetch("data/tools.json");

        if (!response.ok) {
            throw new Error("Erro ao carregar JSON");
        }

        const tools = await response.json();

        tools.forEach(tool => {
            const card = document.createElement("div");
            card.classList.add("class-card");

            card.innerHTML = `
                <h3>${tool.name}</h3>
            `;

            card.addEventListener("click", () => {
                openModal(tool);
            });

            container.appendChild(card);
        });

    } catch (error) {
        console.error("Erro ao carregar JSON:", error);
    }
}

function openModal(tool) {
    document.querySelector("#modal-title").textContent = tool.name;
    document.querySelector("#modal-img").src = tool.image;
    document.querySelector("#modal-img").alt = tool.name;
    document.querySelector("#modal-instructor").textContent = tool.category;
    document.querySelector("#modal-schedule").textContent = "Rating: " + tool.rating;
    document.querySelector("#modal-description").textContent = tool.description;

    modal.showModal();
}

if (closeBtn) {
    closeBtn.addEventListener("click", () => {
        modal.close();
    });
}

if (modal) {
    modal.addEventListener("click", (e) => {
        if (e.target === modal) {
            modal.close();
        }
    });
}