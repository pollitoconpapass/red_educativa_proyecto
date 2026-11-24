const Estudiante = (() => {
  function vencida(fechaLimite) {
    if (!fechaLimite) return false;
    const fecha = new Date(fechaLimite);
    return !Number.isNaN(fecha.getTime()) && fecha.getTime() < Date.now();
  }

  function estadoActividad(actividad) {
    if (actividad.id_entrega) return { texto: "Entregada", clase: "badge-ok" };
    if (vencida(actividad.fecha_limite))
      return { texto: "Vencida", clase: "badge-alerta" };
    return { texto: "Pendiente", clase: "badge-pendiente" };
  }

  function filaActividad(actividad) {
    const estado = estadoActividad(actividad);
    const reemplaza = Boolean(actividad.id_entrega);
    return `<li class="actividad">
      <div class="actividad-cuerpo">
        <div class="actividad-cab">
          <h3 class="actividad-titulo">${ui.esc(actividad.titulo)}</h3>
          <span class="badge ${estado.clase}">${estado.texto}</span>
        </div>
        <dl class="meta">
          <div><dt>Docente</dt><dd>${ui.esc(actividad.docente)}</dd></div>
          <div><dt>Límite</dt><dd>${ui.fecha(actividad.fecha_limite) || "Sin límite"}</dd></div>
          <div><dt>Mi entrega</dt><dd>${actividad.id_entrega ? ui.fecha(actividad.fecha_entrega) : "Sin subir"}</dd></div>
        </dl>
      </div>
      <button class="btn ${reemplaza ? "btn-suave" : "btn-primario"}" type="button"
        data-accion="entregar"
        data-id="${actividad.id_actividad}"
        data-titulo="${ui.esc(actividad.titulo)}"
        data-reemplaza="${reemplaza ? "1" : "0"}">
        ${reemplaza ? "Reemplazar" : "Subir entrega"}
      </button>
    </li>`;
  }

  async function actividades(contenedor) {
    await ui.conDatos(contenedor, api.actividadesEstudiante, (lista) => {
      const entregadas = lista.filter(
        (actividad) => actividad.id_entrega,
      ).length;
      const pendientes = lista.filter(
        (actividad) =>
          !actividad.id_entrega && !vencida(actividad.fecha_limite),
      ).length;
      const fueraDeFecha = lista.filter(
        (actividad) => !actividad.id_entrega && vencida(actividad.fecha_limite),
      ).length;

      return `<div class="vista-cab">
          <div>
            <h2>Actividades publicadas</h2>
            <p>La fecha límite es informativa: puedes entregar fuera de plazo.</p>
          </div>
        </div>
        <div class="metricas">
          <div class="metrica"><strong>${lista.length}</strong><span>Actividades</span></div>
          <div class="metrica"><strong>${pendientes}</strong><span>Pendientes</span></div>
          <div class="metrica"><strong>${entregadas}</strong><span>Entregadas</span></div>
          <div class="metrica"><strong>${fueraDeFecha}</strong><span>Fuera de fecha</span></div>
        </div>
        ${
          lista.length
            ? `<ul class="lista-actividades">${lista.map(filaActividad).join("")}</ul>`
            : ui.vacio(
                "No hay actividades publicadas",
                "Cuando un docente cree una actividad, aparecerá en esta lista.",
              )
        }`;
    });
  }

  async function entregas(contenedor) {
    await ui.conDatos(contenedor, api.entregasEstudiante, (lista) => {
      return `<div class="vista-cab">
          <div>
            <h2>Mis entregas</h2>
            <p>Descarga una copia de los archivos que ya subiste.</p>
          </div>
        </div>
        ${
          lista.length
            ? `<ul class="lista-documentos">${lista
                .map(
                  (entrega) => `<li class="documento">
                    <div class="documento-cuerpo">
                      <h3 class="documento-nombre">${ui.esc(entrega.nombre_archivo)}</h3>
                      <p class="documento-contexto">${ui.esc(entrega.actividad)}</p>
                      <dl class="meta">
                        <div><dt>Tamaño</dt><dd>${ui.tamano(entrega.tamano_bytes)}</dd></div>
                        <div><dt>Subida</dt><dd>${ui.fecha(entrega.fecha_entrega)}</dd></div>
                      </dl>
                    </div>
                    <button class="btn btn-suave btn-sm" type="button"
                      data-accion="descargar"
                      data-id="${entrega.id_documento}"
                      data-nombre="${ui.esc(entrega.nombre_archivo)}">Descargar</button>
                  </li>`,
                )
                .join("")}</ul>`
            : ui.vacio(
                "Aún no tienes entregas",
                "Sube tu primer archivo desde la sección de actividades.",
              )
        }`;
    });
  }

  function abrirEntrega(datos) {
    const esReemplazo = datos.reemplaza === "1";

    ui.abrirModal({
      titulo: esReemplazo ? "Reemplazar entrega" : "Subir entrega",
      cuerpo: `<form class="pila" id="form-entrega" novalidate>
          <p class="nota">Actividad: <strong>${ui.esc(datos.titulo)}</strong></p>
          ${
            esReemplazo
              ? '<p class="aviso">El archivo anterior se reemplazará. El docente verá solo el nuevo.</p>'
              : ""
          }
          <div class="campo">
            <label class="archivo" for="archivo-entrega">
              <span class="archivo-nombre" data-nombre-archivo>Selecciona un archivo</span>
              <span class="archivo-nota">Máximo 10 MB por archivo.</span>
              <input id="archivo-entrega" name="archivo" type="file" required />
            </label>
            <p class="error-campo" data-error="archivo" role="alert" hidden></p>
          </div>
          <p class="error-campo" data-error="general" role="alert" hidden></p>
          <div class="modal-acciones">
            <button class="btn btn-primario" type="submit">${esReemplazo ? "Reemplazar" : "Subir"}</button>
            <button class="btn btn-suave" type="button" data-accion="cerrar-modal">Cancelar</button>
          </div>
        </form>`,
      alMontar(raiz) {
        const formulario = raiz.querySelector("#form-entrega");
        const entrada = formulario.querySelector('input[type="file"]');
        const errorArchivo = formulario.querySelector('[data-error="archivo"]');
        const errorGeneral = formulario.querySelector('[data-error="general"]');

        entrada.addEventListener("change", () => {
          formulario.querySelector("[data-nombre-archivo]").textContent =
            entrada.files[0] ? entrada.files[0].name : "Selecciona un archivo";
          errorArchivo.hidden = true;
        });

        formulario.addEventListener("submit", async (evento) => {
          evento.preventDefault();
          errorArchivo.hidden = true;
          errorGeneral.hidden = true;

          const archivo = entrada.files[0];
          if (!archivo) {
            errorArchivo.textContent =
              "Selecciona un archivo antes de continuar.";
            errorArchivo.hidden = false;
            return;
          }
          if (!archivo.size) {
            errorArchivo.textContent = "El archivo está vacío.";
            errorArchivo.hidden = false;
            return;
          }
          if (archivo.size > 10 * 1024 * 1024) {
            errorArchivo.textContent = "El archivo supera el límite de 10 MB.";
            errorArchivo.hidden = false;
            return;
          }

          const boton = formulario.querySelector('button[type="submit"]');
          ui.ocupado(boton, "Subiendo…");
          try {
            const resultado = await api.entregar(Number(datos.id), archivo);
            ui.cerrarModal();
            ui.toast(
              resultado.reemplazada
                ? "Entrega reemplazada."
                : "Entrega subida.",
              "ok",
            );
            App.recargar();
          } catch (fallo) {
            errorGeneral.textContent = fallo.message;
            errorGeneral.hidden = false;
          } finally {
            ui.liberar(boton);
          }
        });
      },
    });
  }

  return { actividades, entregas, abrirEntrega };
})();
