const App = (() => {
  const ROLES = {
    ESTUDIANTE: [
      {
        id: "actividades",
        texto: "Actividades",
        vista: Estudiante.actividades,
      },
      { id: "entregas", texto: "Mis entregas", vista: Estudiante.entregas },
    ],
    DOCENTE: [
      { id: "actividades", texto: "Actividades", vista: Docente.actividades },
      { id: "material", texto: "Material", vista: Docente.material },
      { id: "auditoria", texto: "Auditoría", vista: Docente.auditoria },
    ],
  };

  let ultimaExpiracion = 0;

  function iniciar() {
    document.addEventListener("click", manejarClic);
    document.addEventListener("keydown", manejarTeclado);
    window.addEventListener("hashchange", manejarHash);
    window.addEventListener("sesion-expirada", manejarExpiracion);

    if (obtenerSesion()) {
      montarShell();
    } else {
      Auth.montar("login");
    }
  }

  function montarShell() {
    const sesion = obtenerSesion();
    const elementos = sesion ? ROLES[sesion.rol] : null;
    if (!sesion || !elementos) {
      limpiarSesion();
      Auth.montar("login");
      return;
    }

    const inicial = (sesion.nombre || "?").trim().charAt(0).toUpperCase();
    const rol = sesion.rol === "DOCENTE" ? "Docente" : "Estudiante";

    document.getElementById("app").innerHTML = `<div class="shell">
      <aside class="sidebar" aria-label="Navegación principal">
        <a class="marca" href="#/${elementos[0].id}"><span class="marca-signo">E</span>EduNet</a>
        <nav>
          <ul class="sidebar-nav">
            ${elementos
              .map(
                (elemento) =>
                  `<li><a class="nav-enlace" data-nav="${elemento.id}" href="#/${elemento.id}">${elemento.texto}</a></li>`,
              )
              .join("")}
          </ul>
        </nav>
        <div class="sidebar-pie">
          <div class="usuario">
            <span class="avatar" aria-hidden="true">${ui.esc(inicial)}</span>
            <div>
              <p class="usuario-nombre">${ui.esc(sesion.nombre)}</p>
              <p class="usuario-rol">${rol}</p>
            </div>
          </div>
          <button class="btn-salir" type="button" data-accion="cerrar-sesion">Cerrar sesión</button>
          <a class="sidebar-doc" href="${ui.esc(window.EDUNET_API_URL)}/docs" target="_blank" rel="noopener">Documentación de la API</a>
        </div>
      </aside>
      <div class="shell-main">
        <header class="topbar">
          <div class="contenedor topbar-interior">
            <button class="btn-menu" type="button" data-accion="abrir-menu" aria-label="Abrir menú" aria-expanded="false" aria-controls="sidebar">
              <span></span><span></span><span></span>
            </button>
            <h1 id="titulo-vista">Portal</h1>
          </div>
        </header>
        <main class="vista" id="vista" tabindex="-1"></main>
      </div>
    </div>
    <button class="menu-fondo" type="button" data-accion="cerrar-menu" aria-label="Cerrar menú" hidden></button>`;

    pintarRuta();
  }

  function pintarRuta() {
    const sesion = obtenerSesion();
    const elementos = sesion ? ROLES[sesion.rol] : null;
    if (!elementos) return;

    const solicitada = location.hash.replace(/^#\/?/, "");
    const elemento =
      elementos.find((item) => item.id === solicitada) || elementos[0];

    if (solicitada !== elemento.id) {
      history.replaceState(null, "", `#/${elemento.id}`);
    }

    const titulo = document.getElementById("titulo-vista");
    if (!titulo) return;

    titulo.textContent = elemento.texto;
    document.title = `${elemento.texto} | EduNet`;

    document.querySelectorAll("[data-nav]").forEach((enlace) => {
      const activo = enlace.dataset.nav === elemento.id;
      enlace.classList.toggle("activo", activo);
      if (activo) enlace.setAttribute("aria-current", "page");
      else enlace.removeAttribute("aria-current");
    });

    cerrarMenu();
    window.scrollTo(0, 0);
    elemento.vista(document.getElementById("vista"));
  }

  function iniciarSesion() {
    const sesion = obtenerSesion();
    const elementos = sesion ? ROLES[sesion.rol] : null;
    if (!elementos) {
      limpiarSesion();
      Auth.montar("login");
      return;
    }
    history.replaceState(null, "", `#/${elementos[0].id}`);
    montarShell();
  }

  function cerrarSesion() {
    ui.cerrarModal();
    limpiarSesion();
    document.body.classList.remove("menu-abierto");
    history.replaceState(null, "", location.pathname + location.search);
    Auth.montar("login");
    ui.toast("Sesión cerrada.", "ok");
  }

  function manejarExpiracion() {
    if (obtenerSesion()) return;
    const ahora = Date.now();
    if (ahora - ultimaExpiracion < 1500) return;
    ultimaExpiracion = ahora;

    ui.cerrarModal();
    document.body.classList.remove("menu-abierto");
    history.replaceState(null, "", location.pathname + location.search);
    Auth.montar("login");
    ui.toast("Tu sesión expiró. Vuelve a iniciar sesión.", "alerta");
  }

  function abrirMenu() {
    document.body.classList.add("menu-abierto");
    const fondo = document.querySelector(".menu-fondo");
    if (fondo) fondo.hidden = false;
    const boton = document.querySelector('[data-accion="abrir-menu"]');
    if (boton) boton.setAttribute("aria-expanded", "true");
  }

  function cerrarMenu() {
    document.body.classList.remove("menu-abierto");
    const fondo = document.querySelector(".menu-fondo");
    if (fondo) fondo.hidden = true;
    const boton = document.querySelector('[data-accion="abrir-menu"]');
    if (boton) boton.setAttribute("aria-expanded", "false");
  }

  async function descargar(elemento) {
    ui.ocupado(elemento, "Descargando…");
    try {
      await api.descargar(Number(elemento.dataset.id), elemento.dataset.nombre);
    } catch (fallo) {
      ui.toast(fallo.message, "error");
    } finally {
      ui.liberar(elemento);
    }
  }

  const acciones = {
    "cerrar-modal": () => ui.cerrarModal(),
    "abrir-menu": abrirMenu,
    "cerrar-menu": cerrarMenu,
    "cerrar-sesion": cerrarSesion,
    "nueva-actividad": () => Docente.nuevaActividad(),
    entregar: (elemento) => Estudiante.abrirEntrega(elemento.dataset),
    "entregas-actividad": (elemento) => Docente.verEntregas(elemento.dataset),
    descargar: (elemento) => descargar(elemento),
  };

  function manejarClic(evento) {
    if (!(evento.target instanceof Element)) return;
    if (evento.target.closest(".nav-enlace, .sidebar .marca")) cerrarMenu();

    const origen = evento.target.closest("[data-accion]");
    if (!origen) return;
    const accion = acciones[origen.dataset.accion];
    if (!accion) return;
    evento.preventDefault();
    accion(origen);
  }

  function manejarTeclado(evento) {
    if (
      evento.key === "Escape" &&
      document.body.classList.contains("menu-abierto")
    ) {
      cerrarMenu();
    }
  }

  function manejarHash() {
    if (obtenerSesion()) pintarRuta();
  }

  return { iniciar, iniciarSesion, recargar: pintarRuta };
})();

document.addEventListener("DOMContentLoaded", App.iniciar);
