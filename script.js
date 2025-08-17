// Animación simple para el formulario
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector("form");
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    alert("¡Gracias por contactarnos! Te responderemos pronto.");
    form.reset();
  });
});
