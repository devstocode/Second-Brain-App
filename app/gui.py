# app/gui.py
import customtkinter as ctk
import tkinter as tk
from services.brain_service import BrainService
import math

# ── Paleta de colores ──────────────────────────────────────────────────────────
LIGHT = {
    "bg":          "#F3F4F6",
    "sidebar":     "#FFFFFF",
    "surface":     "#FFFFFF",
    "surface2":    "#F8F9FA",
    "border":      "#E5E7EB",
    "primary":     "#1A73E8",
    "primary_h":   "#1557B0",
    "on_primary":  "#FFFFFF",
    "text":        "#1F2937",
    "text2":       "#6B7280",
    "success":     "#188038",
    "danger":      "#D93025",
    "danger_h":    "#B02314",
    "active_item": "#E8F0FE",
    "active_text": "#1A73E8",
    "timer_ring":  "#1A73E8",
    "timer_track": "#E8EAED",
}
DARK = {
    "bg":          "#0F1117",
    "sidebar":     "#1C1E26",
    "surface":     "#1C1E26",
    "surface2":    "#252730",
    "border":      "#2D2F3A",
    "primary":     "#8AB4F8",
    "primary_h":   "#AFC8FF",
    "on_primary":  "#0F1117",
    "text":        "#E8EAED",
    "text2":       "#9AA0A6",
    "success":     "#81C995",
    "danger":      "#F28B82",
    "danger_h":    "#EE675C",
    "active_item": "#1E3050",
    "active_text": "#8AB4F8",
    "timer_ring":  "#8AB4F8",
    "timer_track": "#2D2F3A",
}


def c(key):
    """Shortcut – devuelve el color correcto según el tema activo."""
    return _THEME[key]


_THEME = LIGHT.copy()


# ── Animación de fade ──────────────────────────────────────────────────────────
def fade_in(widget, alpha=0.0, step=0.08):
    if alpha < 1.0:
        try:
            widget.attributes("-alpha", alpha)
            widget.after(16, lambda: fade_in(widget, alpha + step))
        except Exception:
            pass
    else:
        widget.attributes("-alpha", 1.0)


# ── Widget Canvas circular para el temporizador ────────────────────────────────
class RingTimer(tk.Canvas):
    """Canvas con anillo SVG-style para el Pomodoro."""

    def __init__(self, master, size=260, **kwargs):
        super().__init__(master, width=size, height=size,
                         highlightthickness=0, **kwargs)
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        self.r = (size // 2) - 18
        self._draw(1.0)

    def _draw(self, fraction):
        self.delete("all")
        s = self.size
        cx, cy, r = self.cx, self.cy, self.r
        # pista
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                         outline=c("timer_track"), width=12)
        # arco activo
        if fraction > 0:
            extent = fraction * 360
            start = 90
            x0, y0, x1, y1 = cx - r, cy - r, cx + r, cy + r
            self.create_arc(x0, y0, x1, y1,
                            start=start, extent=-extent,
                            outline=c("timer_ring"), width=12,
                            style="arc")

    def update_ring(self, fraction):
        self._draw(fraction)

    def refresh_colors(self):
        self._draw_last = getattr(self, "_last_frac", 1.0)
        self._draw(self._draw_last)

    def update_ring(self, fraction):
        self._last_frac = fraction
        self._draw(fraction)


# ── Ventana principal ──────────────────────────────────────────────────────────
class VentanaPrincipal(ctk.CTk):

    NAV_ITEMS = [
        ("pomodoro",  "⏱",  "Enfoque"),
        ("cuaderno",  "📓", "Cuaderno"),
        ("buscador",  "🧠", "Buscador IA"),
    ]

    def __init__(self):
        super().__init__()
        self.title("NeuroCore AI")
        self.geometry("1000x660")
        self.minsize(820, 560)

        self._dark_mode = False
        self.cerebro = BrainService()

        # Pomodoro state
        self.tiempo_inicial = 25 * 60
        self.segundos_restantes = self.tiempo_inicial
        self.corriendo = False

        self._build_layout()
        self._nav_to("pomodoro")
        self.after(50, lambda: fade_in(self))

    # ── Layout base ───────────────────────────────────────────────────────────
    def _build_layout(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.configure(fg_color=c("bg"))

        self._build_sidebar()
        self._build_pomodoro()
        self._build_cuaderno()
        self._build_buscador()

    # ── Sidebar ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0,
                                    fg_color=c("sidebar"),
                                    border_width=1, border_color=c("border"))
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_rowconfigure(5, weight=1)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(28, 8))
        ctk.CTkLabel(logo_frame, text="◈", font=("Segoe UI", 26),
                     text_color=c("primary")).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(logo_frame, text="NeuroCore",
                     font=ctk.CTkFont("Segoe UI", 17, "bold"),
                     text_color=c("text")).pack(side="left")

        # Separador
        sep = ctk.CTkFrame(self.sidebar, height=1, fg_color=c("border"))
        sep.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 12))

        # Botones de navegación
        self._nav_buttons = {}
        for idx, (key, icon, label) in enumerate(self.NAV_ITEMS, start=2):
            btn = self._make_nav_btn(key, icon, label)
            btn.grid(row=idx, column=0, sticky="ew", padx=12, pady=3)
            self._nav_buttons[key] = btn

        # Separador inferior + toggle modo
        sep2 = ctk.CTkFrame(self.sidebar, height=1, fg_color=c("border"))
        sep2.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 12))

        self.toggle_mode_btn = ctk.CTkButton(
            self.sidebar,
            text="☾  Modo oscuro",
            font=ctk.CTkFont("Segoe UI", 13),
            fg_color="transparent",
            hover_color=c("active_item"),
            text_color=c("text2"),
            anchor="w",
            corner_radius=10,
            height=40,
            command=self._toggle_dark_mode,
        )
        self.toggle_mode_btn.grid(row=7, column=0, sticky="ew", padx=12, pady=(0, 20))

    def _make_nav_btn(self, key, icon, label):
        return ctk.CTkButton(
            self.sidebar,
            text=f"  {icon}   {label}",
            font=ctk.CTkFont("Segoe UI", 14),
            fg_color="transparent",
            hover_color=c("active_item"),
            text_color=c("text2"),
            anchor="w",
            corner_radius=10,
            height=44,
            command=lambda k=key: self._nav_to(k),
        )

    def _nav_to(self, key):
        self._active = key
        for k, btn in self._nav_buttons.items():
            if k == key:
                btn.configure(fg_color=c("active_item"),
                               text_color=c("active_text"))
            else:
                btn.configure(fg_color="transparent",
                               text_color=c("text2"))

        for frame in (self.frame_pomodoro, self.frame_cuaderno, self.frame_buscador):
            frame.grid_forget()

        target = {
            "pomodoro": self.frame_pomodoro,
            "cuaderno": self.frame_cuaderno,
            "buscador": self.frame_buscador,
        }[key]
        target.grid(row=0, column=1, sticky="nsew")

    # ── Pomodoro ──────────────────────────────────────────────────────────────
    def _build_pomodoro(self):
        self.frame_pomodoro = ctk.CTkFrame(self, corner_radius=0,
                                           fg_color=c("bg"))
        self.frame_pomodoro.grid_columnconfigure(0, weight=1)

        # Encabezado
        hdr = ctk.CTkFrame(self.frame_pomodoro, fg_color=c("surface"),
                            corner_radius=0,
                            border_width=1, border_color=c("border"))
        hdr.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(hdr, text="Zona de enfoque",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color=c("text")).pack(side="left", padx=28, pady=18)

        # Tarjeta central
        card = ctk.CTkFrame(self.frame_pomodoro, fg_color=c("surface"),
                             corner_radius=18,
                             border_width=1, border_color=c("border"))
        card.grid(row=1, column=0, padx=60, pady=40, sticky="n")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(padx=48, pady=36)

        # Ring timer
        self.ring_bg = c("bg")
        self.ring_canvas = RingTimer(inner, size=260, bg=c("bg"))
        self.ring_canvas.pack()

        # Tiempo encima del canvas
        self.label_reloj = ctk.CTkLabel(inner, text="25:00",
                                        font=ctk.CTkFont("Segoe UI", 54, "bold"),
                                        text_color=c("text"))
        self.label_reloj.place(in_=self.ring_canvas,
                               relx=0.5, rely=0.5, anchor="center")

        # Subtítulo estado
        self.label_estado = ctk.CTkLabel(inner, text="Listo para comenzar",
                                         font=ctk.CTkFont("Segoe UI", 13),
                                         text_color=c("text2"))
        self.label_estado.pack(pady=(10, 0))

        # Botones
        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(pady=18)

        self.btn_inicio = ctk.CTkButton(
            btn_row, text="  ▶  Iniciar", width=140, height=44,
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            fg_color=c("primary"), hover_color=c("primary_h"),
            text_color=c("on_primary"), corner_radius=22,
            command=self.alternar_cronometro,
        )
        self.btn_inicio.grid(row=0, column=0, padx=8)

        self.btn_reiniciar = ctk.CTkButton(
            btn_row, text="↺  Reiniciar", width=130, height=44,
            font=ctk.CTkFont("Segoe UI", 14),
            fg_color=c("surface2"), hover_color=c("border"),
            text_color=c("text2"), corner_radius=22,
            border_width=1, border_color=c("border"),
            command=self.reiniciar_cronometro,
        )
        self.btn_reiniciar.grid(row=0, column=1, padx=8)

        # Config de tiempo
        cfg = ctk.CTkFrame(inner, fg_color=c("surface2"),
                            corner_radius=12,
                            border_width=1, border_color=c("border"))
        cfg.pack(pady=(0, 4))
        ctk.CTkLabel(cfg, text="Minutos:",
                     font=ctk.CTkFont("Segoe UI", 13),
                     text_color=c("text2")).pack(side="left", padx=(16, 6), pady=12)
        self.entrada_tiempo = ctk.CTkEntry(cfg, width=56, height=32,
                                           justify="center",
                                           font=ctk.CTkFont("Segoe UI", 13),
                                           fg_color=c("surface"),
                                           border_color=c("border"),
                                           text_color=c("text"))
        self.entrada_tiempo.insert(0, "25")
        self.entrada_tiempo.pack(side="left", padx=4, pady=12)
        ctk.CTkButton(cfg, text="Aplicar", width=72, height=32,
                      font=ctk.CTkFont("Segoe UI", 13),
                      fg_color=c("primary"), hover_color=c("primary_h"),
                      text_color=c("on_primary"), corner_radius=8,
                      command=self.aplicar_tiempo).pack(side="left", padx=(4, 16), pady=12)

    # ── Cuaderno ──────────────────────────────────────────────────────────────
    def _build_cuaderno(self):
        self.frame_cuaderno = ctk.CTkFrame(self, corner_radius=0,
                                           fg_color=c("bg"))
        self.frame_cuaderno.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(self.frame_cuaderno, fg_color=c("surface"),
                            corner_radius=0,
                            border_width=1, border_color=c("border"))
        hdr.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(hdr, text="Cuaderno de apuntes",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color=c("text")).pack(side="left", padx=28, pady=18)

        card = ctk.CTkFrame(self.frame_cuaderno, fg_color=c("surface"),
                             corner_radius=18,
                             border_width=1, border_color=c("border"))
        card.grid(row=1, column=0, padx=60, pady=36, sticky="n")
        card.grid_columnconfigure(0, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=32)

        ctk.CTkLabel(inner, text="Escribe tu apunte",
                     font=ctk.CTkFont("Segoe UI", 14, "bold"),
                     text_color=c("text")).pack(anchor="w", pady=(0, 6))

        self.caja_texto = ctk.CTkTextbox(inner, width=520, height=190,
                                         font=ctk.CTkFont("Segoe UI", 14),
                                         fg_color=c("surface2"),
                                         border_color=c("border"),
                                         border_width=1,
                                         text_color=c("text"),
                                         corner_radius=10)
        self.caja_texto.pack(fill="x", pady=(0, 14))

        ctk.CTkLabel(inner, text="Categoría",
                     font=ctk.CTkFont("Segoe UI", 13),
                     text_color=c("text2")).pack(anchor="w", pady=(0, 4))

        self.combo_categoria = ctk.CTkComboBox(
            inner,
            values=["Programación", "Matemáticas", "Historia", "General"],
            width=220, height=36,
            font=ctk.CTkFont("Segoe UI", 13),
            fg_color=c("surface2"),
            border_color=c("border"),
            text_color=c("text"),
            button_color=c("border"),
            dropdown_fg_color=c("surface"),
            corner_radius=8,
        )
        self.combo_categoria.pack(anchor="w", pady=(0, 18))

        btn_row = ctk.CTkFrame(inner, fg_color="transparent")
        btn_row.pack(anchor="w")

        self.btn_guardar_apunte = ctk.CTkButton(
            btn_row, text="  💾  Guardar", width=130, height=42,
            font=ctk.CTkFont("Segoe UI", 14, "bold"),
            fg_color=c("primary"), hover_color=c("primary_h"),
            text_color=c("on_primary"), corner_radius=21,
            command=self.guardar_apunte,
        )
        self.btn_guardar_apunte.grid(row=0, column=0, padx=(0, 10))

        self.btn_borrar_apunte = ctk.CTkButton(
            btn_row, text="  🗑  Borrar", width=120, height=42,
            font=ctk.CTkFont("Segoe UI", 14),
            fg_color="transparent",
            hover_color="#FEE2E2",
            text_color=c("danger"),
            border_width=1, border_color=c("danger"),
            corner_radius=21,
            command=self.borrar_apunte,
        )
        self.btn_borrar_apunte.grid(row=0, column=1)

        self.label_mensaje = ctk.CTkLabel(inner, text="",
                                          font=ctk.CTkFont("Segoe UI", 13))
        self.label_mensaje.pack(anchor="w", pady=(14, 0))

    # ── Buscador ──────────────────────────────────────────────────────────────
    def _build_buscador(self):
        self.frame_buscador = ctk.CTkFrame(self, corner_radius=0,
                                           fg_color=c("bg"))
        self.frame_buscador.grid_columnconfigure(0, weight=1)

        hdr = ctk.CTkFrame(self.frame_buscador, fg_color=c("surface"),
                            corner_radius=0,
                            border_width=1, border_color=c("border"))
        hdr.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(hdr, text="Buscador inteligente",
                     font=ctk.CTkFont("Segoe UI", 22, "bold"),
                     text_color=c("text")).pack(side="left", padx=28, pady=18)

        card = ctk.CTkFrame(self.frame_buscador, fg_color=c("surface"),
                             corner_radius=18,
                             border_width=1, border_color=c("border"))
        card.grid(row=1, column=0, padx=60, pady=36, sticky="nsew")
        self.frame_buscador.grid_rowconfigure(1, weight=1)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=36, pady=32)

        # Barra de búsqueda estilo Google
        search_row = ctk.CTkFrame(inner, fg_color=c("surface2"),
                                   corner_radius=30,
                                   border_width=1, border_color=c("border"),
                                   height=50)
        search_row.pack(fill="x", pady=(0, 18))
        search_row.pack_propagate(False)

        ctk.CTkLabel(search_row, text="🔍",
                     font=("Segoe UI", 16),
                     text_color=c("text2")).pack(side="left", padx=(18, 0))

        self.entrada_busqueda = ctk.CTkEntry(
            search_row,
            placeholder_text="Pregúntale a tu cerebro...",
            font=ctk.CTkFont("Segoe UI", 14),
            fg_color="transparent",
            border_width=0,
            text_color=c("text"),
        )
        self.entrada_busqueda.pack(side="left", fill="x", expand=True, padx=10)
        self.entrada_busqueda.bind("<Return>", lambda e: self.realizar_busqueda())

        self.btn_buscar = ctk.CTkButton(
            search_row, text="Buscar", width=90, height=36,
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            fg_color=c("primary"), hover_color=c("primary_h"),
            text_color=c("on_primary"), corner_radius=24,
            command=self.realizar_busqueda,
        )
        self.btn_buscar.pack(side="right", padx=8, pady=7)

        ctk.CTkLabel(inner, text="Resultados",
                     font=ctk.CTkFont("Segoe UI", 13, "bold"),
                     text_color=c("text2")).pack(anchor="w", pady=(0, 6))

        self.resultado_texto = ctk.CTkTextbox(
            inner, height=260,
            font=ctk.CTkFont("Segoe UI", 13),
            fg_color=c("surface2"),
            border_color=c("border"),
            border_width=1,
            text_color=c("text"),
            corner_radius=12,
            state="disabled",
        )
        self.resultado_texto.pack(fill="both", expand=True)

    # ── Modo oscuro / claro ───────────────────────────────────────────────────
    def _toggle_dark_mode(self):
        self._dark_mode = not self._dark_mode
        _THEME.clear()
        _THEME.update(DARK if self._dark_mode else LIGHT)

        ctk.set_appearance_mode("dark" if self._dark_mode else "light")

        label = "☀  Modo claro" if self._dark_mode else "☾  Modo oscuro"
        self.toggle_mode_btn.configure(text=label)

        self._rebuild()

    def _rebuild(self):
        """Destruye y reconstruye todos los widgets con los nuevos colores."""
        self.configure(fg_color=c("bg"))
        for widget in self.winfo_children():
            widget.destroy()
        self._build_layout()
        self._nav_to(getattr(self, "_active", "pomodoro"))
        # Restaurar estado del timer
        mins = self.tiempo_inicial // 60
        segs = self.tiempo_inicial % 60
        self.label_reloj.configure(
            text=f"{self.segundos_restantes // 60:02d}:{self.segundos_restantes % 60:02d}"
        )

    # ── Lógica Pomodoro ───────────────────────────────────────────────────────
    def alternar_cronometro(self):
        if not self.corriendo:
            self.corriendo = True
            self.btn_inicio.configure(text="  ⏸  Pausar",
                                      fg_color=c("danger"),
                                      hover_color=c("danger_h"))
            self.label_estado.configure(text="En sesión de enfoque...")
            self._contar()
        else:
            self.corriendo = False
            self.btn_inicio.configure(text="  ▶  Reanudar",
                                      fg_color=c("primary"),
                                      hover_color=c("primary_h"))
            self.label_estado.configure(text="En pausa")

    def _contar(self):
        if self.corriendo and self.segundos_restantes > 0:
            self.segundos_restantes -= 1
            m = self.segundos_restantes // 60
            s = self.segundos_restantes % 60
            self.label_reloj.configure(text=f"{m:02d}:{s:02d}")
            fraccion = self.segundos_restantes / self.tiempo_inicial
            self.ring_canvas.update_ring(fraccion)
            self.after(1000, self._contar)
        elif self.segundos_restantes == 0:
            self.corriendo = False
            self.label_estado.configure(text="✓ ¡Sesión completada!")
            self.btn_inicio.configure(text="  ▶  Iniciar",
                                      fg_color=c("primary"),
                                      hover_color=c("primary_h"))

    def reiniciar_cronometro(self):
        self.corriendo = False
        self.segundos_restantes = self.tiempo_inicial
        m = self.tiempo_inicial // 60
        self.label_reloj.configure(text=f"{m:02d}:00")
        self.ring_canvas.update_ring(1.0)
        self.btn_inicio.configure(text="  ▶  Iniciar",
                                   fg_color=c("primary"),
                                   hover_color=c("primary_h"))
        self.label_estado.configure(text="Listo para comenzar")

    def aplicar_tiempo(self):
        try:
            mins = int(self.entrada_tiempo.get())
            if mins > 0:
                self.tiempo_inicial = mins * 60
                self.segundos_restantes = self.tiempo_inicial
                self.label_reloj.configure(text=f"{mins:02d}:00")
                self.ring_canvas.update_ring(1.0)
                self.corriendo = False
                self.btn_inicio.configure(text="  ▶  Iniciar",
                                           fg_color=c("primary"),
                                           hover_color=c("primary_h"))
                self.label_estado.configure(text="Listo para comenzar")
        except ValueError:
            pass

    # ── Lógica Cuaderno ───────────────────────────────────────────────────────
    def guardar_apunte(self):
        texto = self.caja_texto.get("0.0", "end").strip()
        cat = self.combo_categoria.get()
        if texto:
            self.cerebro.guardar_en_el_cerebro(texto, cat)
            self.caja_texto.delete("0.0", "end")
            self.label_mensaje.configure(text="✓  Apunte guardado correctamente",
                                         text_color=c("success"))
            self.after(2500, lambda: self.label_mensaje.configure(text=""))

    def borrar_apunte(self):
        texto = self.caja_texto.get("0.0", "end").strip()
        if texto:
            self.cerebro.eliminar_apunte(texto)
            self.caja_texto.delete("0.0", "end")
            self.label_mensaje.configure(text="🗑  Apunte eliminado",
                                         text_color=c("danger"))
            self.after(2500, lambda: self.label_mensaje.configure(text=""))

    # ── Lógica Buscador ───────────────────────────────────────────────────────
    def realizar_busqueda(self):
        consulta = self.entrada_busqueda.get().strip()
        if not consulta:
            return

        resultados = self.cerebro.buscar_con_ia(consulta)
        self.resultado_texto.configure(state="normal")
        self.resultado_texto.delete("0.0", "end")

        if not resultados:
            self.resultado_texto.insert("end",
                "Sin resultados. Prueba con otros términos.")
        else:
            for res in resultados:
                header = f"📌  [{res['categoria']}]   Similitud: {res['score']:.2f}\n"
                self.resultado_texto.insert("end", header)
                self.resultado_texto.insert("end", res['texto'] + "\n\n")

        self.resultado_texto.configure(state="disabled")
