const Docente = (() => {
  const ACCIONES = {
    LOGIN: ["Inicio de sesión", "badge-neutro"],
    REGISTRO: ["Registro", "badge-neutro"],
    ACTIVIDAD_CREADA: ["Actividad creada", "badge-pendiente"],
    MATERIAL_SUBIDO: ["Material subido", "badge-pendiente"],
    ENTREGA_SUBIDA: ["Entrega subida", "badge-ok"],
    ENTREGA_REEMPLAZADA: ["Entrega reemplazada", "badge-ok"],
    DESCARGA: ["Descarga", "badge-neutro"],
  };

  function filaActividad(actividad) {
    const total = Number(actividad.total_entregas) || 0;
    return `<li class="actividad">
      <div class="actividad-cuerpo">
        <div class="actividad-cab">
          <h3 class="actividad-titulo">${ui.esc(actividad.titulo)}</h3>
          <span class="badge ${total ? "badge-pendiente" : "badge-neutro"}">${total} ${total === 1 ? "entrega" : "entregas"}</span>
        </div>
        <dl class="meta">
          <div><dt>Límite</dt><dd>${ui.fecha(actividad.fecha_limite) || "Sin límite"}</dd></div>
        </dl>
      </div>
      <button class="btn btn-suave btn-sm" type="button"
        data-accion="entregas-actividad"
        data-id="${actividad.id_actividad}"
        data-titulo="${ui.esc(actividad.titulo)}">Ver entregas</button>
    </li>`;
  }

  async function actividades(contenedor) {
    await ui.conDatos(contenedor, api.actividadesDocente, (lista) => {
      const totalEntregas = lista.reduce(
        (suma, actividad) => suma + (Number(actividad.total_entregas) || 0),
        0,
      );
      return `<div class="vista-cab">
          <div>
            <h2>Tus actividades</h2>
            <p>Crea actividades y revisa las entregas de tus estudiantes.</p>
          </div>
          <button class="btn btn-primario" type="button" data-accion="nueva-actividad">Nueva actividad</button>
        </div>
        <div class="metricas">
          <div class="metrica"><strong>${lista.length}</strong><span>Actividades</span></div>
          <div class="metrica"><strong>${totalEntregas}</strong><span>Entregas recibidas</span></div>
        </div>
        ${
          lista.length
            ? `<ul class="lista-actividades">${lista.map(filaActividad).join("")}</ul>`
            : ui.vacio(
                "Todavía no has creado actividades",
                "Usa el botón Nueva actividad para publicar la primera.",
              )
        }`;
    });
  }

  function nuevaActividad() {
    ui.abrirModal({
      titulo: "Nueva actividad",
      cuerpo: `<form class="pila" id="form-actividad" novalidate>
          <div class="campo">
            <label for="titulo-actividad">Título</label>
            <input class="entrada" id="titulo-actividad" name="titulo" type="text" maxlength="200" required />
            <p class="error-campo" data-error="titulo" role="alert" hidden></p>
          </div>
          <div class="campo">
            <label for="limite-actividad">Fecha límite <span class="opcional">(opcional)</span></label>
            <input class="entrada" id="limite-actividad" name="fecha_limite" type="datetime-local" />
            <p class="ayuda">Es informativa: no se bloquean las entregas fuera de plazo.</p>
          </div>
          <p class="error-campo" data-error="general" role="alert" hidden></p>
          <div class="modal-acciones">
            <button class="btn btn-primario" type="submit">Crear actividad</button>
            <button class="btn btn-suave" type="button" data-accion="cerrar-modal">Cancelar</button>
          </div>
        </form>`,
      alMontar(raiz) {
        const formulario = raiz.querySelector("#form-actividad");
        const errorTitulo = formulario.querySelector('[data-error="titulo"]');
        const errorGeneral = formulario.querySelector('[data-error="general"]');

        formulario.addEventListener("submit", async (evento) => {
          evento.preventDefault();
          errorTitulo.hidden = true;
          errorGeneral.hidden = true;

          const titulo = formulario.titulo.value.trim();
          if (!titulo) {
            errorTitulo.textContent = "Escribe un título para la actividad.";
            errorTitulo.hidden = false;
            formulario.titulo.focus();
            return;
          }

          const boton = formulario.querySelector('button[type="submit"]');
          ui.ocupado(boton, "Creando…");
          try {
            await api.crearActividad(titulo, formulario.fecha_limite.value);
            ui.cerrarModal();
            ui.toast("Actividad creada.", "ok");
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

  function verEntregas(datos) {
    const cuerpo = ui.abrirModal({
      titulo: `Entregas de ${datos.titulo}`,
      cuerpo: ui.esqueleto(3),
    });

    async function cargar() {
      cuerpo.innerHTML = ui.esqueleto(3);
      try {
        const lista = await api.entregasDocente(Number(datos.id));
        if (!cuerpo.isConnected) return;

        cuerpo.innerHTML = lista.length
          ? `<ul class="lista-documentos">${lista
              .map(
                (entrega) => `<li class="documento">
                  <div class="documento-cuerpo">
                    <h3 class="documento-nombre">${ui.esc(entrega.estudiante)}</h3>
                    <p class="documento-contexto">Código ${ui.esc(entrega.codigo_universitario)}</p>
                    <dl class="meta">
                      <div><dt>Archivo</dt><dd>${ui.esc(entrega.nombre_archivo)}</dd></div>
                      <div><dt>Tamaño</dt><dd>${ui.tamano(entrega.tamano_bytes)}</dd></div>
                      <div><dt>Fecha</dt><dd>${ui.fecha(entrega.fecha_entrega)}</dd></div>
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
              "Sin entregas por ahora",
              "Los estudiantes verán esta actividad y podrán subir su archivo.",
            );
      } catch (fallo) {
        if (!cuerpo.isConnected) return;
        cuerpo.innerHTML = `<div class="estado">
          <p class="estado-titulo">No se pudieron cargar las entregas</p>
          <p class="estado-texto">${ui.esc(fallo.message)}</p>
          <button class="btn btn-suave" type="button" data-reintentar>Reintentar</button>
        </div>`;
        cuerpo
          .querySelector("[data-reintentar]")
          .addEventListener("click", cargar);
      }
    }

    cargar();
  }

  function filaMaterial(documento) {
    return `<li class="documento">
      <div class="documento-cuerpo">
        <h3 class="documento-nombre">${ui.esc(documento.nombre_archivo)}</h3>
        <dl class="meta">
          <div><dt>Publicado</dt><dd>${ui.fecha(documento.fecha_publicacion)}</dd></div>
          <div><dt>Tamaño</dt><dd>${ui.tamano(documento.tamano_bytes)}</dd></div>
        </dl>
      </div>
      <button class="btn btn-suave btn-sm" type="button"
        data-accion="descargar"
        data-id="${documento.id_documento}"
        data-nombre="${ui.esc(documento.nombre_archivo)}">Descargar</button>
    </li>`;
  }

  function material(contenedor) {
    contenedor.innerHTML = `<div class="vista-cab">
        <div>
          <h2>Material del curso</h2>
          <p>Lo que publiques aquí queda disponible para todos los estudiantes.</p>
        </div>
      </div>
      <form class="panel-carga" id="form-material" novalidate>
        <h3>Publicar un archivo</h3>
        <div class="campo">
          <label class="archivo" for="archivo-material">
            <span class="archivo-nombre" data-nombre-archivo>Selecciona un archivo</span>
            <span class="archivo-nota">Máximo 10 MB por archivo.</span>
            <input id="archivo-material" name="archivo" type="file" required />
          </label>
          <p class="error-campo" data-error="archivo" role="alert" hidden></p>
        </div>
        <p class="error-campo" data-error="general" role="alert" hidden></p>
        <div class="form-acciones">
          <button class="btn btn-primario" type="submit">Publicar</button>
        </div>
      </form>
      <div id="lista-material"></div>`;

    const formulario = contenedor.querySelector("#form-material");
    const entrada = formulario.querySelector('input[type="file"]');
    const errorArchivo = formulario.querySelector('[data-error="archivo"]');
    const errorGeneral = formulario.querySelector('[data-error="general"]');

    entrada.addEventListener("change", () => {
      formulario.querySelector("[data-nombre-archivo]").textContent = entrada
        .files[0]
        ? entrada.files[0].name
        : "Selecciona un archivo";
      errorArchivo.hidden = true;
    });

    formulario.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      errorArchivo.hidden = true;
      errorGeneral.hidden = true;

      const archivo = entrada.files[0];
      if (!archivo) {
        errorArchivo.textContent = "Selecciona un archivo antes de continuar.";
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
      ui.ocupado(boton, "Publicando…");
      try {
        await api.subirMaterial(archivo);
        ui.toast("Material publicado.", "ok");
        App.recargar();
      } catch (fallo) {
        errorGeneral.textContent = fallo.message;
        errorGeneral.hidden = false;
      } finally {
        ui.liberar(boton);
      }
    });

    ui.conDatos(
      contenedor.querySelector("#lista-material"),
      api.materialDocente,
      (lista) => {
        return lista.length
          ? `<ul class="lista-documentos">${lista.map(filaMaterial).join("")}</ul>`
          : ui.vacio(
              "Todavía no has publicado material",
              "El primer archivo que subas aparecerá en esta lista.",
            );
      },
    );
  }

  function pintarAuditoria(lista) {
    if (!lista.length) {
      return ui.vacio(
        "No hay registros para estos filtros",
        "Prueba con otro ID de usuario o un límite mayor.",
      );
    }

    return `<div class="tabla-scroll">
        <table class="tabla">
          <thead>
            <tr>
              <th scope="col">Fecha</th>
              <th scope="col">Usuario</th>
              <th scope="col">Acción</th>
              <th scope="col">Entidad</th>
              <th scope="col">ID</th>
            </tr>
          </thead>
          <tbody>
            ${lista
              .map((registro) => {
                const accion = ACCIONES[registro.accion] || [
                  registro.accion,
                  "badge-neutro",
                ];
                return `<tr>
                  <td class="num">${ui.fecha(registro.fecha)}</td>
                  <td>${ui.esc(registro.usuario)} <span class="mono">#${registro.id_usuario}</span></td>
                  <td><span class="badge ${accion[1]}">${ui.esc(accion[0])}</span></td>
                  <td class="mono">${ui.esc(registro.entidad)}</td>
                  <td class="num">${registro.id_entidad ?? "No aplica"}</td>
                </tr>`;
              })
              .join("")}
          </tbody>
        </table>
      </div>
      <p class="tabla-nota">Registros devueltos: ${lista.length}.</p>`;
  }

  function auditoria(contenedor) {
    contenedor.innerHTML = `<div class="vista-cab">
        <div>
          <h2>Registro de actividad</h2>
          <p>Últimas acciones guardadas por la API, de la más reciente a la más antigua.</p>
        </div>
      </div>
      <form class="filtros" id="form-auditoria" novalidate>
        <div class="campo">
          <label for="filtro-usuario">ID de usuario</label>
          <input class="entrada" id="filtro-usuario" name="id_usuario" type="number" min="1" step="1" placeholder="Todos" />
        </div>
        <div class="campo">
          <label for="filtro-limite">Límite</label>
          <select class="entrada" id="filtro-limite" name="limite">
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100" selected>100</option>
            <option value="250">250</option>
            <option value="500">500</option>
          </select>
        </div>
        <button class="btn btn-suave" type="submit">Aplicar</button>
        <p class="error-campo" data-error="filtro" role="alert" hidden></p>
      </form>
      <div id="resultado-auditoria"></div>`;

    const formulario = contenedor.querySelector("#form-auditoria");
    const resultado = contenedor.querySelector("#resultado-auditoria");
    const errorFiltro = formulario.querySelector('[data-error="filtro"]');

    function cargar() {
      errorFiltro.hidden = true;
      const idUsuario = formulario.id_usuario.value.trim();
      const limite = formulario.limite.value;

      if (
        idUsuario &&
        (!Number.isInteger(Number(idUsuario)) || Number(idUsuario) < 1)
      ) {
        errorFiltro.textContent =
          "El ID de usuario debe ser un número mayor que cero.";
        errorFiltro.hidden = false;
        return;
      }

      ui.conDatos(
        resultado,
        () => api.auditoria(idUsuario, limite),
        pintarAuditoria,
      );
    }

    formulario.addEventListener("submit", (evento) => {
      evento.preventDefault();
      cargar();
    });

    cargar();
  }

  return { actividades, nuevaActividad, verEntregas, material, auditoria };
})();
