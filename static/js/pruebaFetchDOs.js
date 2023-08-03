document.getElementById("botonSiete").addEventListener("click", async () => {
    try {
      const response = await fetch('/validacion/');
      const data = await response.text();
      document.getElementById("contenedor").innerHTML = data;
    } catch (error) {
      console.error("Error:", error);
    }
  });

  document.getElementById("botonOcho").addEventListener("click", async () => {
    try {
      const response = await fetch('/crearDenuncia/');
      const data = await response.text();
      console.log("hola mundo")
      document.getElementById("contenedor").innerHTML = data;
    } catch (error) {
      console.error("Error:", error);
    }
  });

  document.getElementById("botonNueve").addEventListener("click", async () => {
    try {
      const response = await fetch('/crearCat/');
      const data = await response.text();
      document.getElementById("contenedor").innerHTML = data;
    } catch (error) {
      console.error("Error:", error);
    }
  });