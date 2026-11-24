const ui = (() => {
  const formatoFecha = new Intl.DateTimeFormat("es-PE", {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });

  function esc(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, (caracter) => {
      const mapa = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;",
      };
      return mapa[caracter];
    });
  }

  function fecha(valor) {
    if (!valor) return "";
    const fechaObjeto = new Date(valor);
    if (Number.isNaN(fechaObjeto.getTime())) return "";
    return formatoFecha.format(fechaObjeto).replace(/\./g, "");
  }

  function tamano(bytes) {
    if (!Number.isFinite(bytes)) return "";
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024)
      return `${(bytes / 1024).toFixed(1).replace(".", ",")} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1).replace(".", ",")} MB`;
  }

  function toast(mensaje, tipo = "ok") {
    const region = document.getElementById("toast-region");
    if (!region) return;
    const aviso = document.createElement("div");
    aviso.className = "toast";
    aviso.dataset.tipo = tipo;
    aviso.textContent = mensaje;
    region.append(aviso);
    while (region.children.length > 3) region.firstElementChild.remove();
    window.setTimeout(() => aviso.remove(), 4500);
  }

  function esqueleto(filas = 4) {
    return `<div class="esqueleto" aria-hidden="true">${Array.from(
      { length: filas },
      () => '<div class="esqueleto-fila"></div>',
    ).join("")}</div>
    <p class="solo-lectores" role="status">Cargando información</p>`;
  }

  function vacio(titulo, texto) {
    return `<div class="estado">
      <p class="estado-titulo">${esc(titulo)}</p>
      <p class="estado-texto">${esc(texto)}</p>
    </div>`;
  }

  function error(mensaje) {
    return `<div class="estado">
      <p class="estado-titulo">No se pudo cargar la información</p>
      <p class="estado-texto">${esc(mensaje)}</p>
      <button class="btn btn-suave" type="button" data-reintentar>Reintentar</button>
    </div>`;
  }

  async function conDatos(contenedor, cargar, pintar) {
    async function ejecutar() {
      contenedor.innerHTML = esqueleto(4);
      try {
        const datos = await cargar();
        if (!contenedor.isConnected) return;
        contenedor.innerHTML = pintar(datos);
      } catch (fallo) {
        if (!contenedor.isConnected) return;
        contenedor.innerHTML = error(fallo.message);
        contenedor
          .querySelector("[data-reintentar]")
          .addEventListener("click", ejecutar);
      }
    }
    await ejecutar();
  }

  function ocupado(boton, texto) {
    boton.dataset.textoOriginal = boton.textContent;
    boton.textContent = texto;
    boton.disabled = true;
  }

  function liberar(boton) {
    if (boton.dataset.textoOriginal) {
      boton.textContent = boton.dataset.textoOriginal;
      delete boton.dataset.textoOriginal;
    }
    boton.disabled = false;
  }

  let ultimoEnfocado = null;
  let manejarTeclado = null;

  function abrirModal({ titulo, cuerpo, alMontar }) {
    cerrarModal();
    ultimoEnfocado = document.activeElement;

    const raiz = document.getElementById("modal-root");
    raiz.innerHTML = `<div class="modal-fondo">
      <div class="modal" role="dialog" aria-modal="true" aria-labelledby="modal-titulo">
        <header class="modal-cab">
          <h2 id="modal-titulo">${esc(titulo)}</h2>
          <button class="btn-cerrar" type="button" data-accion="cerrar-modal" aria-label="Cerrar">&times;</button>
        </header>
        <div class="modal-cuerpo" data-modal-cuerpo>${cuerpo}</div>
      </div>
    </div>`;

    const fondo = raiz.querySelector(".modal-fondo");
    fondo.addEventListener("click", (evento) => {
      if (evento.target === fondo) cerrarModal();
    });

    manejarTeclado = (evento) => {
      if (evento.key === "Escape") {
        cerrarModal();
        return;
      }
      if (evento.key !== "Tab") return;

      const enfocables = raiz.querySelectorAll(
        'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
      );
      if (!enfocables.length) return;
      const primero = enfocables[0];
      const ultimo = enfocables[enfocables.length - 1];

      if (evento.shiftKey && document.activeElement === primero) {
        evento.preventDefault();
        ultimo.focus();
      } else if (!evento.shiftKey && document.activeElement === ultimo) {
        evento.preventDefault();
        primero.focus();
      }
    };
    document.addEventListener("keydown", manejarTeclado);
    document.body.classList.add("con-modal");

    const cuerpoEl = raiz.querySelector("[data-modal-cuerpo]");
    if (alMontar) alMontar(cuerpoEl);

    if (!raiz.contains(document.activeElement)) {
      const primerEnfocable = raiz.querySelector(
        'input:not([type="file"]), select, textarea, button:not(.btn-cerrar), a[href]',
      );
      (primerEnfocable || raiz.querySelector(".btn-cerrar")).focus();
    }

    return cuerpoEl;
  }

  function cerrarModal() {
    const raiz = document.getElementById("modal-root");
    if (!raiz.firstChild) return;
    raiz.innerHTML = "";
    document.body.classList.remove("con-modal");
    if (manejarTeclado) {
      document.removeEventListener("keydown", manejarTeclado);
      manejarTeclado = null;
    }
    if (ultimoEnfocado && document.contains(ultimoEnfocado)) {
      ultimoEnfocado.focus();
    }
    ultimoEnfocado = null;
  }

  return {
    esc,
    fecha,
    tamano,
    toast,
    esqueleto,
    vacio,
    conDatos,
    ocupado,
    liberar,
    abrirModal,
    cerrarModal,
  };
})();
