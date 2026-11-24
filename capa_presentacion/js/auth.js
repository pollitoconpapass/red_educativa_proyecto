const Auth = (() => {
  const ESTUDIANTE = "ESTUDIANTE";
  const DOCENTE = "DOCENTE";

  function montar(modo = "login", correo = "") {
    document.title = "EduNet | Portal académico";
    const app = document.getElementById("app");
    app.innerHTML =
      modo === "registro" ? plantillaRegistro() : plantillaLogin(correo);

    if (modo === "registro") {
      conectarRegistro();
    } else {
      conectarLogin(correo);
      comprobarServidor();
    }
  }

  function marca() {
    return `<a class="marca" href="#"><span class="marca-signo">E</span>EduNet</a>`;
  }

  function plantillaLogin(correo) {
    return `<div class="auth">
      <section class="auth-marca" aria-label="EduNet">
        <div class="auth-marca-contenido">
          ${marca()}
          <div>
            <p class="auth-titular">Actividades, entregas y material del curso en un solo lugar.</p>
            <p class="auth-apoyo">Portal académico de la red educativa para estudiantes y docentes.</p>
          </div>
          <p class="auth-pie">Acceso con cuenta institucional</p>
        </div>
      </section>
      <main class="auth-panel" id="vista" tabindex="-1">
        <div class="auth-caja">
          <div class="auth-movil"><span class="marca-signo">E</span>EduNet</div>
          <header class="auth-cabecera">
            <h1>Iniciar sesión</h1>
            <p>Entra con el correo y la contraseña de tu cuenta.</p>
          </header>
          <form class="pila" id="form-login" novalidate>
            <div class="campo">
              <label for="correo">Correo</label>
              <input class="entrada" id="correo" name="correo" type="email" autocomplete="username" value="${ui.esc(correo)}" required />
              <p class="error-campo" data-error="correo" role="alert" hidden></p>
            </div>
            <div class="campo">
              <label for="clave">Contraseña</label>
              <input class="entrada" id="clave" name="clave" type="password" autocomplete="current-password" required />
              <p class="error-campo" data-error="clave" role="alert" hidden></p>
            </div>
            <p class="error-form" data-error="general" role="alert" hidden></p>
            <button class="btn btn-primario btn-bloque" type="submit">Entrar</button>
          </form>
          <p class="auth-cambio">¿No tienes cuenta? <button class="enlace" type="button" data-cambio="registro">Crear una cuenta</button></p>
          <p class="estado-servidor"><span class="punto"></span><span data-texto-servidor>Comprobando conexión con el servidor</span></p>
        </div>
      </main>
    </div>`;
  }

  function plantillaRegistro() {
    return `<div class="auth">
      <section class="auth-marca" aria-label="EduNet">
        <div class="auth-marca-contenido">
          ${marca()}
          <div>
            <p class="auth-titular">Un espacio común para el trabajo del curso.</p>
            <p class="auth-apoyo">Crea tu cuenta y empieza a recibir actividades, entregas y material.</p>
          </div>
          <p class="auth-pie">Registro abierto para estudiantes y docentes</p>
        </div>
      </section>
      <main class="auth-panel" id="vista" tabindex="-1">
        <div class="auth-caja">
          <div class="auth-movil"><span class="marca-signo">E</span>EduNet</div>
          <header class="auth-cabecera">
            <h1>Crear cuenta</h1>
            <p>Regístrate con tus datos académicos.</p>
          </header>
          <form class="pila" id="form-registro" novalidate>
            <div class="campo">
              <label for="nombre">Nombre completo</label>
              <input class="entrada" id="nombre" name="nombre" type="text" autocomplete="name" maxlength="150" required />
              <p class="error-campo" data-error="nombre" role="alert" hidden></p>
            </div>
            <div class="campo">
              <label for="correo">Correo</label>
              <input class="entrada" id="correo" name="correo" type="email" autocomplete="email" maxlength="150" required />
              <p class="error-campo" data-error="correo" role="alert" hidden></p>
            </div>
            <div class="campo">
              <label for="clave">Contraseña</label>
              <input class="entrada" id="clave" name="clave" type="password" autocomplete="new-password" minlength="8" required />
              <p class="ayuda">Mínimo 8 caracteres.</p>
              <p class="error-campo" data-error="clave" role="alert" hidden></p>
            </div>
            <div class="campo">
              <label for="rol">Rol</label>
              <select class="entrada" id="rol" name="rol">
                <option value="${ESTUDIANTE}">Estudiante</option>
                <option value="${DOCENTE}">Docente</option>
              </select>
            </div>
            <div class="campo" data-grupo="codigo">
              <label for="codigo">Código universitario</label>
              <input class="entrada" id="codigo" name="codigo_universitario" type="text" maxlength="50" />
              <p class="error-campo" data-error="codigo_universitario" role="alert" hidden></p>
            </div>
            <div class="campo" data-grupo="area" hidden>
              <label for="area">Área académica <span class="opcional">(opcional)</span></label>
              <input class="entrada" id="area" name="area_academica" type="text" maxlength="100" />
            </div>
            <p class="error-form" data-error="general" role="alert" hidden></p>
            <button class="btn btn-primario btn-bloque" type="submit">Crear cuenta</button>
          </form>
          <p class="auth-cambio">¿Ya tienes cuenta? <button class="enlace" type="button" data-cambio="login">Iniciar sesión</button></p>
        </div>
      </main>
    </div>`;
  }

  function marcarError(formulario, campo, mensaje) {
    const control = formulario.elements[campo];
    const caja = formulario.querySelector(`[data-error="${campo}"]`);
    if (control) control.setAttribute("aria-invalid", "true");
    if (caja) {
      caja.textContent = mensaje;
      caja.hidden = false;
    }
  }

  function limpiarErrores(formulario) {
    formulario.querySelectorAll("[data-error]").forEach((caja) => {
      caja.textContent = "";
      caja.hidden = true;
    });
    formulario.querySelectorAll('[aria-invalid="true"]').forEach((control) => {
      control.removeAttribute("aria-invalid");
    });
  }

  function correoValido(correo) {
    return /^\S+@\S+\.\S+$/.test(correo);
  }

  function conectarLogin(correo) {
    const formulario = document.getElementById("form-login");
    if (!formulario) return;

    formulario.addEventListener("input", (evento) => {
      const campo = evento.target.name;
      if (!campo) return;
      const caja = formulario.querySelector(`[data-error="${campo}"]`);
      if (caja) caja.hidden = true;
      evento.target.removeAttribute("aria-invalid");
    });

    formulario.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      limpiarErrores(formulario);

      const valorCorreo = formulario.correo.value.trim();
      const valorClave = formulario.clave.value;
      let valido = true;

      if (!valorCorreo) {
        marcarError(formulario, "correo", "Escribe tu correo.");
        valido = false;
      } else if (!correoValido(valorCorreo)) {
        marcarError(formulario, "correo", "Revisa el formato del correo.");
        valido = false;
      }
      if (!valorClave) {
        marcarError(formulario, "clave", "Escribe tu contraseña.");
        valido = false;
      }
      if (!valido) return;

      const boton = formulario.querySelector('button[type="submit"]');
      ui.ocupado(boton, "Entrando…");
      try {
        const datos = await api.login(valorCorreo, valorClave);
        guardarSesion({
          access_token: datos.access_token,
          id_usuario: datos.id_usuario,
          nombre: datos.nombre,
          rol: datos.rol,
        });
        App.iniciarSesion();
      } catch (fallo) {
        marcarError(formulario, "general", fallo.message);
      } finally {
        ui.liberar(boton);
      }
    });

    document.querySelectorAll("[data-cambio]").forEach((boton) => {
      boton.addEventListener("click", () => {
        const destino = boton.dataset.cambio;
        montar(destino, destino === "login" ? correo : "");
      });
    });
  }

  function conectarRegistro() {
    const formulario = document.getElementById("form-registro");
    if (!formulario) return;

    const grupoCodigo = formulario.querySelector('[data-grupo="codigo"]');
    const grupoArea = formulario.querySelector('[data-grupo="area"]');

    function actualizarRol() {
      const esEstudiante = formulario.rol.value === ESTUDIANTE;
      grupoCodigo.hidden = !esEstudiante;
      grupoArea.hidden = esEstudiante;
    }
    formulario.rol.addEventListener("change", actualizarRol);
    actualizarRol();

    formulario.addEventListener("input", (evento) => {
      const campo = evento.target.name;
      if (!campo) return;
      const caja = formulario.querySelector(`[data-error="${campo}"]`);
      if (caja) caja.hidden = true;
      evento.target.removeAttribute("aria-invalid");
    });

    formulario.addEventListener("submit", async (evento) => {
      evento.preventDefault();
      limpiarErrores(formulario);

      const nombre = formulario.nombre.value.trim();
      const correo = formulario.correo.value.trim();
      const clave = formulario.clave.value;
      const rol = formulario.rol.value;
      const codigo = formulario.codigo_universitario.value.trim();
      const area = formulario.area_academica.value.trim();
      let valido = true;

      if (nombre.length < 2) {
        marcarError(formulario, "nombre", "Escribe tu nombre completo.");
        valido = false;
      }
      if (!correo) {
        marcarError(formulario, "correo", "Escribe tu correo.");
        valido = false;
      } else if (!correoValido(correo)) {
        marcarError(formulario, "correo", "Revisa el formato del correo.");
        valido = false;
      }
      if (clave.length < 8) {
        marcarError(
          formulario,
          "clave",
          "La contraseña debe tener al menos 8 caracteres.",
        );
        valido = false;
      }
      if (rol === ESTUDIANTE && !codigo) {
        marcarError(
          formulario,
          "codigo_universitario",
          "El código es obligatorio para estudiantes.",
        );
        valido = false;
      }
      if (!valido) return;

      const boton = formulario.querySelector('button[type="submit"]');
      ui.ocupado(boton, "Creando cuenta…");
      try {
        await api.registro({
          nombre,
          correo,
          clave,
          rol,
          codigo_universitario: rol === ESTUDIANTE ? codigo : null,
          area_academica: rol === DOCENTE ? area || null : null,
        });
        ui.toast("Cuenta creada. Ahora inicia sesión.", "ok");
        montar("login", correo);
      } catch (fallo) {
        marcarError(formulario, "general", fallo.message);
      } finally {
        ui.liberar(boton);
      }
    });

    document.querySelectorAll("[data-cambio]").forEach((boton) => {
      boton.addEventListener("click", () => montar("login"));
    });
  }

  async function comprobarServidor() {
    const estado = document.querySelector(".estado-servidor");
    if (!estado) return;
    const punto = estado.querySelector(".punto");
    const texto = estado.querySelector("[data-texto-servidor]");
    try {
      await api.salud();
      punto.dataset.estado = "ok";
      texto.textContent = "Servidor disponible";
    } catch {
      punto.dataset.estado = "error";
      texto.textContent = `Sin conexión con ${window.EDUNET_API_URL}`;
    }
  }

  return { montar };
})();
