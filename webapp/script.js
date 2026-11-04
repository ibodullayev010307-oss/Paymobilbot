const packages = [
[60, 11500],
[120, 22000],
[180, 36000],
[325, 56000],
[660, 112000],
[720, 123000],
[1320, 224000],
[1800, 278000],
[2125, 335000],
[3850, 563000],
[5650, 842500],
[8100, 1096000],
[16200, 2170000],
[24300, 3255000],
[32400, 4340000],
[40500, 5430000],
[64800, 8680000],
[81000, 10850000]
];

let selectedPackage = null;

const container = document.getElementById("packages");
const continueBtn = document.getElementById("continueBtn");

function formatPrice(price) {
return price.toLocaleString("uz-UZ") + " so'm";
}

packages.forEach(([uc, price]) => {
const card = document.createElement("div");

card.className = "package";

card.innerHTML = `
    <div class="uc">💎 ${uc.toLocaleString("uz-UZ")} UC</div>
    <div class="price">${formatPrice(price)}</div>
`;

card.addEventListener("click", () => {
    document.querySelectorAll(".package").forEach(item => {
        item.classList.remove("selected");
    });

    card.classList.add("selected");

    selectedPackage = {
        uc: uc,
        price: price
    };

    continueBtn.disabled = false;
});

container.appendChild(card);

});

continueBtn.addEventListener("click", () => {
if (!selectedPackage) return;

localStorage.setItem(
    "selectedPackage",
    JSON.stringify(selectedPackage)
);

window.location.href = "player.html";

});
