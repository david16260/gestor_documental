// ===============================
// CONFIGURACIÓN DE SESIÓN
// ===============================
const token = localStorage.getItem("access_token");
const usuarioActual = localStorage.getItem("usuario_nombre");

// Referencias DOM
const loginSection = document.getElementById("login-section");
const contentSection = document.getElementById("versiones-section") 
                    || document.getElementById("documentos-section") 
                    || document.getElementById("historial-section");
const usuarioHeader = document.getElementById("usuario-info-header");
const usuarioBody = document.getElementById("usuario-info");

// ===============================
// PÁGINAS PÚBLICAS Y PROTEGIDAS
// ===============================
const publicPages = ["/", "/forgot-password"];
const protectedPages = ["/documentos", "/versiones", "/historial"];
const currentPath = window.location.pathname;

// ===============================
// FUNCIONES
// ===============================
function mostrarContenido() {
    if (loginSection) loginSection.style.display = "none";
    if (contentSection) contentSection.style.display = "block";
    if (usuarioHeader) usuarioHeader.innerText = `Conectado como ${usuarioActual}`;
    if (usuarioBody) usuarioBody.innerHTML = `🔒 Sesión activa como: <strong>${usuarioActual}</strong>`;
}

function mostrarLogin() {
    if (loginSection) loginSection.style.display = "block";
    if (contentSection) contentSection.style.display = "none";
}

// ===============================
// VERIFICACIÓN DE SESIÓN
// ===============================
if (protectedPages.includes(currentPath)) {
    if (!token || !usuarioActual) {
        window.location.href = "/"; // Redirige al login
    } else {
        mostrarContenido();
    }
} else if (publicPages.includes(currentPath)) {
    if (token && usuarioActual && currentPath === "/") {
        window.location.href = "/dashboard"; // Redirige al dashboard
    }
}

// ===============================
// LOGIN
// ===============================
const loginForm = document.getElementById("login-form");
if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value.trim();
        const password = document.getElementById("password").value.trim();

        const formData = new FormData();
        formData.append("username", email);
        formData.append("password", password);

        try {
            const resp = await fetch("/auth/login", { method: "POST", body: formData });
            const data = await resp.json();

            if (resp.ok) {
                localStorage.setItem("access_token", data.access_token);
                localStorage.setItem("usuario_nombre", data.usuario);
                window.location.href = "/dashboard";
            } else {
                alert(data.detail || "Usuario o contraseña incorrecta");
            }
        } catch (err) {
            alert("Error de conexión: " + err);
        }
    });
}

// ===============================
// LOGOUT
// ===============================
const logoutBtns = document.querySelectorAll("#logout-btn");
logoutBtns.forEach(btn => {
    btn.addEventListener("click", () => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("usuario_nombre");
        window.location.href = "/";
    });
});

// ===============================
// OLVIDO DE CONTRASEÑA
// ===============================
const forgotForm = document.getElementById("forgot-form");
if (forgotForm) {
    forgotForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const email = document.getElementById("email").value.trim();

        try {
            const resp = await fetch("/auth/forgot-password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ email })
            });
            const data = await resp.json();

            if (resp.ok) {
                localStorage.setItem("reset_token", data.reset_token);
                alert("✅ Token generado. Redirigiendo a restablecer contraseña...");
                setTimeout(() => window.location.href = "/reset-password", 1000);
            } else {
                alert(data.detail || "Error al generar token");
            }
        } catch (err) {
            alert("❌ No se pudo conectar con el servidor: " + err);
        }
    });
}
