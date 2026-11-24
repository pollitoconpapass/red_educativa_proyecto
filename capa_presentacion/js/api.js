const CLAVE_SESION = "edunet.sesion.v1";

class ErrorApi extends Error {
  constructor(mensaje, estado) {
    super(mensaje);
    this.name = "ErrorApi";
    this.estado = estado;
  }
}

function obtenerSesion() {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_SESION)) || null;
  } catch {
    return null;
  }
}

function guardarSesion(sesion) {
  localStorage.setItem(CLAVE_SESION, JSON.stringify(sesion));
}

function limpiarSesion() {
  localStorage.removeItem(CLAVE_SESION);
}

function mensajeDeError(cuerpo, estado) {
  const detalle = cuerpo && cuerpo.detail;
  if (typeof detalle === "string") return detalle;
  if (Array.isArray(detalle) && detalle.length) {
    return detalle
      .map((fallo) => {
        const campo = Array.isArray(fallo.loc)
          ? fallo.loc.slice(-1)[0]
          : "campo";
        return `${campo}: ${fallo.msg}`;
      })
      .join(". ");
  }
  return estado
    ? `La API respondió con un error ${estado}.`
    : "Error inesperado.";
}

async function solicitar(ruta, opciones = {}) {
  const {
    metodo = "GET",
    cuerpo,
    formulario,
    descarga = false,
    tiempoMaximo = 0,
  } = opciones;
  const sesion = obtenerSesion();
  const cabeceras = {};
  let payload;

  if (sesion && sesion.access_token) {
    cabeceras.Authorization = `Bearer ${sesion.access_token}`;
  }
  if (formulario) {
    payload = formulario;
  } else if (cuerpo !== undefined) {
    cabeceras["Content-Type"] = "application/json";
    payload = JSON.stringify(cuerpo);
  }

  const opcionesFetch = { method: metodo, headers: cabeceras, body: payload };
  if (tiempoMaximo && typeof AbortSignal.timeout === "function") {
    opcionesFetch.signal = AbortSignal.timeout(tiempoMaximo);
  }

  let respuesta;
  try {
    respuesta = await fetch(window.EDUNET_API_URL + ruta, opcionesFetch);
  } catch {
    throw new ErrorApi(
      "No se pudo conectar con la API. Revisa que el servidor esté en marcha.",
      0,
    );
  }

  if (respuesta.status === 401 && !ruta.startsWith("/auth/")) {
    limpiarSesion();
    window.dispatchEvent(new CustomEvent("sesion-expirada"));
  }

  if (!respuesta.ok) {
    let cuerpoError = null;
    try {
      cuerpoError = await respuesta.json();
    } catch {
      cuerpoError = null;
    }
    throw new ErrorApi(
      mensajeDeError(cuerpoError, respuesta.status),
      respuesta.status,
    );
  }

  if (descarga) return respuesta;
  if (respuesta.status === 204) return null;
  return respuesta.json();
}

function nombreDesdeCabecera(respuesta, respaldo) {
  const cabecera = respuesta.headers.get("Content-Disposition") || "";
  const coincidencia = cabecera.match(/filename\*?=(?:UTF-8'')?"?([^";]+)"?/i);
  if (!coincidencia) return respaldo || "documento";
  try {
    return decodeURIComponent(coincidencia[1]);
  } catch {
    return coincidencia[1];
  }
}

const api = {
  salud: () => solicitar("/health", { tiempoMaximo: 5000 }),

  login: (correo, clave) =>
    solicitar("/auth/login", { metodo: "POST", cuerpo: { correo, clave } }),

  registro: (datos) =>
    solicitar("/auth/registro", { metodo: "POST", cuerpo: datos }),

  actividadesEstudiante: () => solicitar("/estudiante/actividades"),

  entregasEstudiante: () => solicitar("/estudiante/entregas"),

  entregar: (idActividad, archivo) => {
    const datos = new FormData();
    datos.append("archivo", archivo);
    return solicitar(
      `/estudiante/actividades/${encodeURIComponent(idActividad)}/entrega`,
      {
        metodo: "POST",
        formulario: datos,
      },
    );
  },

  actividadesDocente: () => solicitar("/docente/actividades"),

  crearActividad: (titulo, fechaLimite) =>
    solicitar("/docente/actividades", {
      metodo: "POST",
      cuerpo: { titulo, fecha_limite: fechaLimite || null },
    }),

  entregasDocente: (idActividad) =>
    solicitar(
      `/docente/actividades/${encodeURIComponent(idActividad)}/entregas`,
    ),

  materialDocente: () => solicitar("/docente/material"),

  subirMaterial: (archivo) => {
    const datos = new FormData();
    datos.append("archivo", archivo);
    return solicitar("/docente/material", {
      metodo: "POST",
      formulario: datos,
    });
  },

  auditoria: (idUsuario, limite) => {
    const parametros = new URLSearchParams();
    if (idUsuario) parametros.set("id_usuario", idUsuario);
    parametros.set("limite", limite);
    return solicitar(`/auditoria?${parametros.toString()}`);
  },

  async descargar(idDocumento, nombreSugerido) {
    const respuesta = await solicitar(
      `/documentos/${encodeURIComponent(idDocumento)}/descarga`,
      { descarga: true },
    );
    const blob = await respuesta.blob();
    const nombre = nombreDesdeCabecera(respuesta, nombreSugerido);
    const url = URL.createObjectURL(blob);
    const enlace = document.createElement("a");
    enlace.href = url;
    enlace.download = nombre;
    document.body.append(enlace);
    enlace.click();
    enlace.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  },
};
