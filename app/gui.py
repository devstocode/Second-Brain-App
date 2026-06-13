# app/gui.py
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from services.brain_service import BrainService
from services.flashcard_service import FlashcardService
import time

ctk.set_appearance_mode("Dark")  # Forzamos modo oscuro premium
ctk.set_default_color_theme("blue")

# Colores que imitan perfectamente la armonía de tus capturas
COLOR_BG_PRINCIPAL = "#242424" # Fondo gris oscuro general
COLOR_BG_TARJETA = "#2d2d2d"   # Tarjetas (elevadas y más claras que el fondo principal)
COLOR_BG_SUBTARJETA = "#1a1a1a"# Entradas de texto e insets (más oscuras que el fondo principal)
COLOR_BORDE = "#3f3f3f"         # Borde gris medio
COLOR_AZUL = "#1f6aa5"          # Azul de tus botones "Guardar"
COLOR_AZUL_HOVER = "#144e78"
COLOR_ROJO = "#c93434"          # Rojo de tus botones "Borrar"
COLOR_ROJO_HOVER = "#992626"
COLOR_VERDE = "#2e7d32"         # Verde para nivel alto
COLOR_VERDE_HOVER = "#1b5e20"
COLOR_AMBER = "#e65100"         # Naranja para nivel medio
COLOR_AMBER_HOVER = "#bf360c"


class CanvasCircularProgress(ctk.CTkCanvas):
    """Componente premium para dibujar porcentaje de maestría en un círculo."""
    def __init__(self, parent, percentage, size=65, **kwargs):
        bg = parent.cget("fg_color")
        if isinstance(bg, (list, tuple)):
            bg_color = bg[1] if len(bg) > 1 else bg[0]
        else:
            bg_color = bg if bg else COLOR_BG_TARJETA
            
        if bg_color == "transparent":
            bg_color = COLOR_BG_TARJETA

        super().__init__(parent, width=size, height=size, bg=bg_color, highlightthickness=0, **kwargs)
        self.percentage = int(percentage)
        self.size = size
        self.draw()

    def draw(self):
        self.delete("all")
        ring_bg = "#333333" # Gris oscuro
        
        if self.percentage >= 80:
            ring_fg = "#10b981"  # Verde esmeralda
        elif self.percentage >= 50:
            ring_fg = COLOR_AMBER  # Naranja
        else:
            ring_fg = COLOR_AZUL  # Azul
            
        padding = 5
        self.create_oval(padding, padding, self.size - padding, self.size - padding, outline=ring_bg, width=4)
        
        angle = (self.percentage / 100.0) * 360
        if angle > 0:
            self.create_arc(padding, padding, self.size - padding, self.size - padding, 
                            start=90, extent=-angle, outline=ring_fg, width=4, style="arc")
            
        self.create_text(self.size // 2, self.size // 2, text=f"{self.percentage}%", 
                         fill="#f1f5f9", font=("Arial", 10, "bold"))


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Second Brain AI - Neural Architect")
        self.geometry("980x680")

        self.cerebro = BrainService()
        self.servicio_flashcards = FlashcardService()

        # Variables Pomodoro
        self.tiempo_inicial = 25 * 60
        self.segundos_restantes = self.tiempo_inicial
        self.corriendo = False

        # Variables de control de Flashcards
        self.active_mazo_id = None
        self.active_tarjetas_estudio = []
        self.idx_tarjeta_actual = 0
        self.revelado = False
        self.editing_tarjeta_id = None
        
        # Timer de estudio
        self.study_start_time = 0
        self.study_timer_running = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- 1. BARRA LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="NeuroCore AI",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_pomodoro = ctk.CTkButton(self.sidebar_frame, text="⏱️ Pomodoro", command=self.mostrar_pomodoro)
        self.btn_pomodoro.grid(row=1, column=0, padx=20, pady=10)

        self.btn_cuaderno = ctk.CTkButton(self.sidebar_frame, text="📓 Cuaderno", command=self.mostrar_cuaderno)
        self.btn_cuaderno.grid(row=2, column=0, padx=20, pady=10)

        self.btn_buscador = ctk.CTkButton(self.sidebar_frame, text="🧠 Buscador IA", command=self.mostrar_buscador)
        self.btn_buscador.grid(row=3, column=0, padx=20, pady=10)

        # Usamos el emoji de carpeta simple en español
        self.btn_flashcards = ctk.CTkButton(self.sidebar_frame, text="📁 Flashcards", command=self.mostrar_flashcards)
        self.btn_flashcards.grid(row=4, column=0, padx=20, pady=10)

        self.lbl_ver = ctk.CTkLabel(self.sidebar_frame, text="v1.2.0", font=("Arial", 10), text_color="#64748b")
        self.lbl_ver.grid(row=6, column=0, padx=20, pady=10, sticky="w")

        # --- 2. ÁREAS DE TRABAJO ---

        # Habitación A: POMODORO
        self.frame_pomodoro = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.label_titulo_p = ctk.CTkLabel(self.frame_pomodoro, text="ZONA DE ENFOQUE", font=("Arial", 24, "bold"))
        self.label_titulo_p.pack(pady=(50, 20))
        self.label_reloj = ctk.CTkLabel(self.frame_pomodoro, text="25:00", font=("Arial", 80, "bold"))
        self.label_reloj.pack(pady=30)

        self.frame_botones_p = ctk.CTkFrame(self.frame_pomodoro, fg_color="transparent")
        self.frame_botones_p.pack(pady=20)

        self.btn_inicio = ctk.CTkButton(self.frame_botones_p, text="Iniciar", command=self.alternar_cronometro)
        self.btn_inicio.grid(row=0, column=0, padx=10)
        self.btn_reiniciar = ctk.CTkButton(self.frame_botones_p, text="Reiniciar", command=self.reiniciar_cronometro,
                                           fg_color="gray")
        self.btn_reiniciar.grid(row=0, column=1, padx=10)

        # --- CONFIGURACIÓN DE TIEMPO ---
        self.frame_config_p = ctk.CTkFrame(self.frame_pomodoro, fg_color="transparent")
        self.frame_config_p.pack(pady=20)

        self.label_minutos = ctk.CTkLabel(self.frame_config_p, text="Minutos:")
        self.label_minutos.grid(row=0, column=0, padx=5)

        self.entrada_tiempo = ctk.CTkEntry(self.frame_config_p, width=60, justify="center")
        self.entrada_tiempo.insert(0, "25")
        self.entrada_tiempo.grid(row=0, column=1, padx=5)

        self.btn_aplicar_tiempo = ctk.CTkButton(self.frame_config_p, text="Aplicar", width=70,
                                                command=self.aplicar_tiempo)
        self.btn_aplicar_tiempo.grid(row=0, column=2, padx=5)

        # Habitación B: CUADERNO
        self.frame_cuaderno = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.label_titulo_c = ctk.CTkLabel(self.frame_cuaderno, text="NUEVO APUNTE", font=("Arial", 24, "bold"))
        self.label_titulo_c.pack(pady=(50, 20))

        self.caja_texto = ctk.CTkTextbox(self.frame_cuaderno, width=500, height=200, fg_color=COLOR_BG_SUBTARJETA)
        self.caja_texto.pack(pady=10)

        self.combo_categoria = ctk.CTkComboBox(self.frame_cuaderno,
                                               values=["Programación", "Matemáticas", "Historia", "General"])
        self.combo_categoria.pack(pady=10)

        self.btn_guardar_apunte = ctk.CTkButton(self.frame_cuaderno, text="💾 Guardar", command=self.guardar_apunte, fg_color=COLOR_AZUL, hover_color=COLOR_AZUL_HOVER)
        self.btn_guardar_apunte.pack(pady=20)

        self.btn_borrar_apunte = ctk.CTkButton(self.frame_cuaderno, text="🗑️ Borrar", command=self.borrar_apunte,
                                               fg_color=COLOR_ROJO, hover_color=COLOR_ROJO_HOVER)
        self.btn_borrar_apunte.pack(pady=(0, 20))

        self.label_mensaje = ctk.CTkLabel(self.frame_cuaderno, text="")
        self.label_mensaje.pack()

        # Habitación C: BUSCADOR IA
        self.frame_buscador = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.label_titulo_b = ctk.CTkLabel(self.frame_buscador, text="BUSCADOR INTELIGENTE", font=("Arial", 24, "bold"))
        self.label_titulo_b.pack(pady=(50, 20))

        self.entrada_busqueda = ctk.CTkEntry(self.frame_buscador, placeholder_text="Pregúntale a tu cerebro...",
                                             width=400)
        self.entrada_busqueda.pack(pady=10)

        self.btn_buscar = ctk.CTkButton(self.frame_buscador, text="🔍 Buscar con IA", command=self.realizar_busqueda, fg_color=COLOR_AZUL, hover_color=COLOR_AZUL_HOVER)
        self.btn_buscar.pack(pady=10)

        self.resultado_texto = ctk.CTkTextbox(self.frame_buscador, width=600, height=200, state="disabled", fg_color=COLOR_BG_SUBTARJETA)
        self.resultado_texto.pack(pady=20)

        # Habitación D: FLASHCARDS (UNIFICADA)
        self.frame_flashcards = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.frame_flashcards.grid_columnconfigure(0, weight=1)
        self.frame_flashcards.grid_rowconfigure(0, weight=1)

        # Sub-estructuras internas de Flashcards
        self.subframe_biblioteca = ctk.CTkFrame(self.frame_flashcards, fg_color="transparent")
        self.subframe_detalles_mazo = ctk.CTkFrame(self.frame_flashcards, fg_color="transparent")
        self.subframe_crear_tarjeta = ctk.CTkFrame(self.frame_flashcards, fg_color="transparent")
        self.subframe_estudiar = ctk.CTkFrame(self.frame_flashcards, fg_color="transparent")

        self.crear_elementos_biblioteca()
        self.crear_elementos_detalles_mazo()
        self.crear_elementos_crear_tarjeta()
        self.crear_elementos_estudiar()

        # Mostrar página por defecto
        self.mostrar_pomodoro()

    # --- NAVEGACIÓN PRINCIPAL ---
    def ocultar_todos_los_frames(self):
        self.frame_pomodoro.grid_forget()
        self.frame_cuaderno.grid_forget()
        self.frame_buscador.grid_forget()
        self.frame_flashcards.grid_forget()
        self.unbind("<space>")
        self.study_timer_running = False

    def mostrar_pomodoro(self):
        self.ocultar_todos_los_frames()
        self.frame_pomodoro.grid(row=0, column=1, sticky="nsew")

    def mostrar_cuaderno(self):
        self.ocultar_todos_los_frames()
        self.frame_cuaderno.grid(row=0, column=1, sticky="nsew")

    def mostrar_buscador(self):
        self.ocultar_todos_los_frames()
        self.frame_buscador.grid(row=0, column=1, sticky="nsew")

    def mostrar_flashcards(self):
        self.ocultar_todos_los_frames()
        self.frame_flashcards.grid(row=0, column=1, sticky="nsew")
        self.mostrar_subframe_biblioteca()

    # --- NAVEGACIÓN INTERNA FLASHCARDS ---
    def ocultar_todos_los_subframes(self):
        self.subframe_biblioteca.grid_forget()
        self.subframe_detalles_mazo.grid_forget()
        self.subframe_crear_tarjeta.grid_forget()
        self.subframe_estudiar.grid_forget()
        self.unbind("<space>")
        self.study_timer_running = False

    def mostrar_subframe_biblioteca(self):
        self.ocultar_todos_los_subframes()
        self.subframe_biblioteca.grid(row=0, column=0, sticky="nsew")
        self.actualizar_biblioteca_mazos()

    def mostrar_subframe_detalles_mazo(self, mazo_id):
        self.ocultar_todos_los_subframes()
        self.subframe_detalles_mazo.grid(row=0, column=0, sticky="nsew")
        self.cargar_detalles_mazo(mazo_id)

    def mostrar_subframe_crear_tarjeta(self, mazo_id=None, tarjeta_id=None):
        self.ocultar_todos_los_subframes()
        self.subframe_crear_tarjeta.grid(row=0, column=0, sticky="nsew")
        self.cargar_creador_tarjetas(mazo_id, tarjeta_id)

    def mostrar_subframe_estudiar(self, mazo_id):
        self.ocultar_todos_los_subframes()
        self.subframe_estudiar.grid(row=0, column=0, sticky="nsew")
        self.iniciar_sesion_estudio(mazo_id)

    # ==========================================
    # --- VISTA 1: BIBLIOTECA (YOUR LIBRARY) ---
    # ==========================================
    def crear_elementos_biblioteca(self):
        self.subframe_biblioteca.grid_columnconfigure(0, weight=1)
        self.subframe_biblioteca.grid_rowconfigure(1, weight=1)

        # Header al estilo "Tu Biblioteca"
        header_frame = ctk.CTkFrame(self.subframe_biblioteca, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))

        lbl_titulo = ctk.CTkLabel(header_frame, text="Tu Biblioteca", font=("Arial", 22, "bold"))
        lbl_titulo.pack(side="left")

        # Botón "+" azul a la derecha
        btn_nuevo_mazo = ctk.CTkButton(header_frame, text="+ Nuevo Mazo", width=100, height=32, font=("Arial", 12, "bold"),
                                       fg_color=COLOR_AZUL, hover_color=COLOR_AZUL_HOVER, command=self.crear_nuevo_mazo_dialog)
        btn_nuevo_mazo.pack(side="right", padx=5)

        # Subtítulo y buscador de mazos
        subtitle_frame = ctk.CTkFrame(self.subframe_biblioteca, fg_color="transparent")
        subtitle_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 10))

        lbl_sub = ctk.CTkLabel(subtitle_frame, text="Selecciona un mazo para comenzar tu sesión de estudio.", font=("Arial", 12), text_color="#94a3b8")
        lbl_sub.pack(side="left")

        # Filtros pills debajo del subtítulo
        filter_frame = ctk.CTkFrame(self.subframe_biblioteca, fg_color="transparent")
        filter_frame.grid(row=2, column=0, sticky="ew", padx=30, pady=(5, 10))

        pills = ["Todos los Mazos", "Requiere Repaso", "Dominados"]
        for p in pills:
            btn_pill = ctk.CTkButton(filter_frame, text=p, width=100, height=24, font=("Arial", 10), fg_color="#1c1e24", text_color="#94a3b8", hover_color="#333333")
            btn_pill.pack(side="left", padx=3)

        # Contenedor con scroll para los mazos en cuadrícula
        self.scroll_biblioteca = ctk.CTkScrollableFrame(self.subframe_biblioteca, fg_color="transparent")
        self.scroll_biblioteca.grid(row=3, column=0, sticky="nsew", padx=30, pady=(0, 20))
        self.subframe_biblioteca.grid_rowconfigure(3, weight=1)

    def crear_nuevo_mazo_dialog(self):
        dialog = ctk.CTkInputDialog(text="Introduce el nombre del nuevo mazo:", title="Crear Mazo")
        nombre_mazo = dialog.get_input()
        if nombre_mazo:
            exito, mensaje = self.servicio_flashcards.crear_mazo(nombre_mazo)
            if exito:
                self.actualizar_biblioteca_mazos()
            else:
                messagebox.showerror("Error", mensaje)

    def actualizar_biblioteca_mazos(self):
        for widget in self.scroll_biblioteca.winfo_children():
            widget.destroy()

        mazos = self.servicio_flashcards.obtener_todos_los_mazos()

        if not mazos:
            lbl_vacio = ctk.CTkLabel(self.scroll_biblioteca, text="No tienes ningún mazo. ¡Crea uno para comenzar!",
                                     font=("Arial", 14, "italic"), text_color="#64748b")
            lbl_vacio.pack(pady=50)
            return

        self.scroll_biblioteca.grid_columnconfigure(0, weight=1)
        self.scroll_biblioteca.grid_columnconfigure(1, weight=1)

        for i, mazo in enumerate(mazos):
            row = i // 2
            col = i % 2

            card = ctk.CTkFrame(self.scroll_biblioteca, corner_radius=12, border_width=1, border_color=COLOR_BORDE,
                                fg_color=COLOR_BG_TARJETA, height=160)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            card.grid_columnconfigure(1, weight=1)

            # Badge superior en Español
            badge_text = "Dominado" if mazo['porcentaje_maestria'] >= 80 else ("Por Repasar" if mazo['cartas_pendientes'] > 0 else "Neuroanatomía")
            badge_color = "#064e3b" if mazo['porcentaje_maestria'] >= 80 else ("#7f1d1d" if mazo['cartas_pendientes'] > 0 else "#2a2a2a")
            badge_text_color = "#10b981" if mazo['porcentaje_maestria'] >= 80 else ("#ef4444" if mazo['cartas_pendientes'] > 0 else "#94a3b8")

            lbl_badge = ctk.CTkLabel(card, text=badge_text, font=("Arial", 10, "bold"), fg_color=badge_color, text_color=badge_text_color, corner_radius=4)
            lbl_badge.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

            # Tres puntos menú de opciones (Editar y Eliminar)
            lbl_dots = ctk.CTkLabel(card, text="•••", font=("Arial", 12), text_color="#64748b", cursor="hand2")
            lbl_dots.grid(row=0, column=1, padx=15, pady=(15, 5), sticky="e")

            # Menú contextual para Editar/Eliminar mazo
            menu = tk.Menu(self, tearoff=0, bg=COLOR_BG_TARJETA, fg="#f8fafc", activebackground=COLOR_AZUL, activeforeground="#f8fafc", bd=1)
            menu.add_command(label="Editar Nombre", command=lambda m_id=mazo['id'], m_name=mazo['nombre']: self.editar_nombre_mazo_dialog(m_id, m_name))
            menu.add_command(label="Eliminar Mazo", command=lambda m_id=mazo['id']: self.confirmar_eliminar_mazo(m_id))

            # Bind para abrir el menú con clic izquierdo sobre los tres puntos
            lbl_dots.bind("<Button-1>", lambda event, m=menu: m.tk_popup(event.x_root, event.y_root))

            # Título del mazo
            lbl_name = ctk.CTkLabel(card, text=mazo['nombre'], font=("Arial", 16, "bold"), anchor="w", text_color="#f8fafc")
            lbl_name.grid(row=1, column=0, columnspan=2, padx=15, pady=2, sticky="w")

            # Indicador de maestria circular (canvas customizado)
            prog = CanvasCircularProgress(card, percentage=mazo['porcentaje_maestria'], size=60)
            prog.grid(row=2, column=0, rowspan=2, padx=15, pady=(5, 15), sticky="w")

            # Estadísticas en Español
            lbl_stats = ctk.CTkLabel(card, text=f"🎴 {mazo['total_cartas']} Tarjetas Totales\n⏱️ {mazo['cartas_pendientes']} Pendientes Hoy", 
                                     font=("Arial", 11), justify="left", anchor="w", text_color="#94a3b8")
            lbl_stats.grid(row=2, column=1, padx=5, pady=(5, 0), sticky="w")

            # Botón de estudiar inferior
            btn_study = ctk.CTkButton(card, text="▶ Estudiar Ahora" if mazo['cartas_pendientes'] > 0 else "Repasar", 
                                      width=120, height=28, font=("Arial", 11, "bold"),
                                      fg_color=COLOR_AZUL, text_color="#f8fafc",
                                      hover_color=COLOR_AZUL_HOVER,
                                      command=lambda m_id=mazo['id']: self.mostrar_subframe_estudiar(m_id))
            btn_study.grid(row=3, column=1, padx=5, pady=(5, 15), sticky="w")

            # Vincular clic de navegación a detalles en toda la card
            # excepto en el botón de estudiar y en el menú de tres puntos
            def vincular_clicks_card(widget, m_id=mazo['id'], study_btn=btn_study, dots_lbl=lbl_dots):
                if widget == study_btn or widget == dots_lbl:
                    return
                try:
                    widget.configure(cursor="hand2")
                except Exception:
                    pass
                widget.bind("<Button-1>", lambda event, m_id=m_id: self.mostrar_subframe_detalles_mazo(m_id))
                for child in widget.winfo_children():
                    vincular_clicks_card(child, m_id, study_btn, dots_lbl)

            vincular_clicks_card(card)

    def editar_nombre_mazo_dialog(self, mazo_id, nombre_actual):
        dialog = ctk.CTkInputDialog(text=f"Introduce el nuevo nombre para el mazo '{nombre_actual}':", title="Editar Nombre Mazo")
        nuevo_nombre = dialog.get_input()
        if nuevo_nombre:
            exito, mensaje = self.servicio_flashcards.editar_mazo(mazo_id, nuevo_nombre)
            if exito:
                self.actualizar_biblioteca_mazos()
            else:
                messagebox.showerror("Error", mensaje)

    def confirmar_eliminar_mazo(self, mazo_id):
        if messagebox.askyesno("Eliminar Mazo", "¿Estás seguro de que quieres eliminar este mazo? Se borrarán todas sus flashcards."):
            self.servicio_flashcards.eliminar_mazo(mazo_id)
            self.actualizar_biblioteca_mazos()

    # ==========================================
    # --- VISTA 2: DECK DETAILS (DETALLES) ---
    # ==========================================
    def crear_elementos_detalles_mazo(self):
        self.subframe_detalles_mazo.grid_columnconfigure(0, weight=1)
        self.subframe_detalles_mazo.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self.subframe_detalles_mazo, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))

        btn_back = ctk.CTkButton(top_frame, text="← Biblioteca", width=80, height=28, fg_color="#2b2b2b", hover_color="#333333",
                                 command=self.mostrar_subframe_biblioteca)
        btn_back.pack(side="left")

        self.lbl_titulo_mazo_detalles = ctk.CTkLabel(top_frame, text="Mazo", font=("Arial", 20, "bold"))
        self.lbl_titulo_mazo_detalles.pack(side="left", padx=15)

        # Distribución de dos columnas
        content_frame = ctk.CTkFrame(self.subframe_detalles_mazo, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=(0, 20))
        content_frame.grid_columnconfigure(0, weight=1) 
        content_frame.grid_columnconfigure(1, weight=2) 
        content_frame.grid_rowconfigure(0, weight=1)

        # --- COLUMNA 1: ESTADÍSTICAS (LEFT) ---
        left_panel = ctk.CTkFrame(content_frame, fg_color=COLOR_BG_TARJETA, corner_radius=12, border_width=1, border_color=COLOR_BORDE)
        left_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)

        # AI Readiness Score card
        score_card = ctk.CTkFrame(left_panel, fg_color="transparent", height=140)
        score_card.pack(fill="x", padx=15, pady=15)

        lbl_score_title = ctk.CTkLabel(score_card, text="Preparación General (IA)", font=("Arial", 12), text_color="#94a3b8")
        lbl_score_title.pack(anchor="w", padx=15, pady=(15, 2))

        self.lbl_score_ai = ctk.CTkLabel(score_card, text="87%", font=("Arial", 28, "bold"), text_color="#f8fafc")
        self.lbl_score_ai.pack(anchor="w", padx=15, pady=2)

        self.prog_bar_ai = ctk.CTkProgressBar(score_card, width=180, height=6, progress_color=COLOR_AZUL, fg_color="#333333")
        self.prog_bar_ai.pack(anchor="w", padx=15, pady=10)

        # Due Now / New cards side-by-side stats
        stats_frame = ctk.CTkFrame(score_card, fg_color="transparent")
        stats_frame.pack(fill="x", padx=15, pady=(0, 15))

        self.lbl_due_now = ctk.CTkLabel(stats_frame, text="PENDIENTES\n42", font=("Arial", 11, "bold"), justify="left", text_color="#ef4444")
        self.lbl_due_now.pack(side="left")

        self.lbl_new_now = ctk.CTkLabel(stats_frame, text="NUEVAS\n15", font=("Arial", 11, "bold"), justify="left", text_color=COLOR_AZUL)
        self.lbl_new_now.pack(side="right")

        # Tags & Categories card
        tags_card = ctk.CTkFrame(left_panel, fg_color="transparent")
        tags_card.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        lbl_tags_title = ctk.CTkLabel(tags_card, text="Categorías y Etiquetas", font=("Arial", 12, "bold"), text_color="#f1f5f9")
        lbl_tags_title.pack(anchor="w", padx=15, pady=(15, 5))

        self.frame_tags_badg = ctk.CTkFrame(tags_card, fg_color="transparent")
        self.frame_tags_badg.pack(fill="both", expand=True, padx=15, pady=5)

        # --- COLUMNA 2: LISTA DE TARJETAS (RIGHT) ---
        right_panel = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        right_panel.grid_columnconfigure(0, weight=1)
        right_panel.grid_rowconfigure(1, weight=1)

        # Barra de búsqueda superior
        search_bar_frame = ctk.CTkFrame(right_panel, fg_color="transparent")
        search_bar_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))

        # Empaquetamos de derecha a izquierda para evitar que los botones se recorten en pantallas pequeñas
        btn_add_card = ctk.CTkButton(search_bar_frame, text="+ Añadir Tarjeta", width=180, height=32, font=("Arial", 12, "bold"),
                                     fg_color=COLOR_AZUL, hover_color=COLOR_AZUL_HOVER,
                                     command=lambda: self.mostrar_subframe_crear_tarjeta(self.active_mazo_id))
        btn_add_card.pack(side="right", padx=(10, 0))

        btn_filter = ctk.CTkButton(search_bar_frame, text="Filtrar", width=70, height=32, 
                                   fg_color="#2b2b2b", hover_color="#333333", border_width=1, border_color=COLOR_BORDE,
                                   command=self.filtrar_tarjetas)
        btn_filter.pack(side="right", padx=(5, 0))

        self.entry_buscar_tarjetas = ctk.CTkEntry(search_bar_frame, placeholder_text="Buscar en preguntas, respuestas o tags...", height=32, fg_color=COLOR_BG_SUBTARJETA, border_color=COLOR_BORDE)
        self.entry_buscar_tarjetas.pack(side="left", fill="x", expand=True)
        self.entry_buscar_tarjetas.bind("<KeyRelease>", lambda event: self.filtrar_tarjetas())

        # Scroll de tarjetas
        self.scroll_tarjetas = ctk.CTkScrollableFrame(right_panel, fg_color=COLOR_BG_TARJETA, corner_radius=12, border_width=1, border_color=COLOR_BORDE)
        self.scroll_tarjetas.grid(row=1, column=0, sticky="nsew")

    def cargar_detalles_mazo(self, mazo_id):
        self.active_mazo_id = mazo_id
        mazo_info = self.servicio_flashcards.obtener_mazo_por_id(mazo_id)
        if not mazo_info:
            return
        
        self.lbl_titulo_mazo_detalles.configure(text=mazo_info['nombre'])
        
        tarjetas = self.servicio_flashcards.obtener_tarjetas_por_mazo(mazo_id)
        pendientes = self.servicio_flashcards.obtener_tarjetas_pendientes_por_mazo(mazo_id)
        
        total = len(tarjetas)
        n_pendientes = len(pendientes)
        n_nuevas = sum(1 for t in tarjetas if t['repetitions'] == 0)
        suma_repasos = sum(min(t['repetitions'], 4) for t in tarjetas)
        
        porcentaje_maestria = int((suma_repasos / (total * 4)) * 100) if total > 0 else 0
        self.lbl_score_ai.configure(text=f"{porcentaje_maestria}%")
        self.prog_bar_ai.set(porcentaje_maestria / 100.0)
        
        self.lbl_due_now.configure(text=f"PENDIENTES\n{n_pendientes}")
        self.lbl_new_now.configure(text=f"NUEVAS\n{n_nuevas}")

        # Renderizar etiquetas en pills individuales
        for widget in self.frame_tags_badg.winfo_children():
            widget.destroy()

        tags_set = set()
        for t in tarjetas:
            if t['tags']:
                for tag in t['tags'].split(','):
                    if tag.strip():
                        tags_set.add(tag.strip())

        if tags_set:
            frame_pills = ctk.CTkFrame(self.frame_tags_badg, fg_color="transparent")
            frame_pills.pack(fill="both", expand=True)
            
            for idx, tag in enumerate(list(tags_set)[:6]):
                lbl_pill = ctk.CTkLabel(frame_pills, text=f" #{tag} ", font=("Arial", 10, "bold"), 
                                        fg_color="#2b2b2b", text_color=COLOR_AZUL, corner_radius=6)
                lbl_pill.pack(side="left", padx=2, pady=2)
        else:
            lbl_none = ctk.CTkLabel(self.frame_tags_badg, text="No hay etiquetas", font=("Arial", 11, "italic"), text_color="#64748b")
            lbl_none.pack(pady=5)

        self.filtrar_tarjetas()

    def filtrar_tarjetas(self):
        query = self.entry_buscar_tarjetas.get().lower()

        for widget in self.scroll_tarjetas.winfo_children():
            widget.destroy()

        tarjetas = self.servicio_flashcards.obtener_tarjetas_por_mazo(self.active_mazo_id)
        tarjetas_filtradas = []
        
        for t in tarjetas:
            if not query or query in t['pregunta'].lower() or query in t['respuesta'].lower() or (t['tags'] and query in t['tags'].lower()):
                tarjetas_filtradas.append(t)

        if not tarjetas_filtradas:
            lbl_vacia = ctk.CTkLabel(self.scroll_tarjetas, text="Ninguna tarjeta coincide.",
                                     font=("Arial", 12, "italic"), text_color="#64748b")
            lbl_vacia.pack(pady=30)
            return

        for t in tarjetas_filtradas:
            card_item = ctk.CTkFrame(self.scroll_tarjetas, fg_color=COLOR_BG_TARJETA, corner_radius=10, border_width=1, border_color=COLOR_BORDE)
            card_item.pack(fill="x", padx=15, pady=8)
            card_item.grid_columnconfigure(0, weight=1)

            # Determinar estado y color
            if t['repetitions'] == 0:
                due_status = "Nueva"
                status_color = "#38bdf8"
            else:
                from datetime import datetime
                try:
                    hoy_date = datetime.now().date()
                    due_date = datetime.strptime(t['due_date'], "%Y-%m-%d").date()
                    dias_restantes = (due_date - hoy_date).days
                except Exception:
                    dias_restantes = 0
                
                if dias_restantes <= 0:
                    due_status = "Vence Hoy"
                    status_color = "#ef4444"
                elif dias_restantes == 1:
                    due_status = "Vence Mañana"
                    status_color = "#ca8a04"
                else:
                    due_status = f"Vence en {dias_restantes} días"
                    status_color = "#94a3b8"

            # Fila de pregunta con viñeta coloreada según estado
            q_frame = ctk.CTkFrame(card_item, fg_color="transparent")
            q_frame.grid(row=0, column=0, padx=15, pady=(12, 4), sticky="w")

            lbl_dot = ctk.CTkLabel(q_frame, text="•", font=("Arial", 18), text_color=status_color)
            lbl_dot.pack(side="left", anchor="n", padx=(0, 5))

            lbl_q = ctk.CTkLabel(q_frame, text=t['pregunta'], font=("Arial", 13, "bold"), text_color="#f8fafc", anchor="w", justify="left", wraplength=420)
            lbl_q.pack(side="left", fill="x", expand=True)

            # Fila de respuesta directamente sobre el fondo de la tarjeta (sin contenedor oscuro tipo input)
            lbl_a = ctk.CTkLabel(card_item, text=t['respuesta'], font=("Arial", 12), text_color="#cbd5e1", anchor="w", justify="left", wraplength=440)
            lbl_a.grid(row=1, column=0, padx=30, pady=(4, 12), sticky="w")

            # Tag e info due en el pie de la tarjeta
            footer_item = ctk.CTkFrame(card_item, fg_color="transparent")
            footer_item.grid(row=2, column=0, columnspan=2, padx=15, pady=(0, 12), sticky="ew")

            t_tag = t['tags'].split(',')[0] if t['tags'] else "general"
            lbl_t = ctk.CTkLabel(footer_item, text=f" #{t_tag} ", font=("Arial", 10, "bold"), 
                                 fg_color="#202020", text_color="#60a5fa", corner_radius=6)
            lbl_t.pack(side="left")

            lbl_due = ctk.CTkLabel(footer_item, text=due_status, font=("Arial", 10, "bold"), text_color=status_color)
            lbl_due.pack(side="right")

            btn_edit_card = ctk.CTkButton(card_item, text="✏️", width=30, height=28, fg_color="transparent", hover_color="#3b3b3b", text_color="#94a3b8",
                                          command=lambda t_id=t['id']: self.mostrar_subframe_crear_tarjeta(self.active_mazo_id, t_id))
            btn_edit_card.grid(row=0, column=1, padx=(0, 15), pady=(12, 4), sticky="ne")

            btn_del = ctk.CTkButton(card_item, text="🗑️", width=30, height=28, fg_color="transparent", hover_color="#991b1b", text_color="#ef4444",
                                    command=lambda t_id=t['id']: self.eliminar_tarjeta_y_recargar(t_id))
            btn_del.grid(row=1, column=1, padx=(0, 15), pady=(4, 12), sticky="se")

    def eliminar_tarjeta_y_recargar(self, tarjeta_id):
        if messagebox.askyesno("Eliminar Tarjeta", "¿Seguro que quieres borrar esta tarjeta de estudio?"):
            self.servicio_flashcards.eliminar_tarjeta(tarjeta_id)
            self.cargar_detalles_mazo(self.active_mazo_id)

    # ===============================================
    # --- VISTA 3: CARD CREATOR (CREAR TARJETA) ---
    # ===============================================
    def crear_elementos_crear_tarjeta(self):
        self.subframe_crear_tarjeta.grid_columnconfigure(0, weight=1)
        self.subframe_crear_tarjeta.grid_rowconfigure(1, weight=1)

        top_frame = ctk.CTkFrame(self.subframe_crear_tarjeta, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))

        btn_back = ctk.CTkButton(top_frame, text="← Volver", width=80, height=28, fg_color="#2b2b2b", hover_color="#333333",
                                 command=lambda: self.mostrar_subframe_detalles_mazo(self.active_mazo_id))
        btn_back.pack(side="left")

        self.lbl_title_crear = ctk.CTkLabel(top_frame, text="NeuroCore Flashcards", font=("Arial", 20, "bold"))
        self.lbl_title_crear.pack(side="left", padx=15)

        lbl_deck = ctk.CTkLabel(top_frame, text="Mazo:")
        lbl_deck.pack(side="left", padx=(20, 5))
        self.opt_mazo_creacion = ctk.CTkOptionMenu(top_frame, values=[], width=150, height=28)
        self.opt_mazo_creacion.pack(side="left")

        self.btn_save_crear = ctk.CTkButton(top_frame, text="💾 Guardar Tarjeta", width=160, height=32, font=("Arial", 12, "bold"),
                                        fg_color=COLOR_AZUL, hover_color=COLOR_AZUL_HOVER,
                                        command=self.guardar_nueva_tarjeta)
        self.btn_save_crear.pack(side="right")

        form_frame = ctk.CTkFrame(self.subframe_crear_tarjeta, fg_color="transparent")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=5)
        form_frame.grid_columnconfigure(0, weight=1)
        form_frame.grid_columnconfigure(1, weight=1)
        form_frame.grid_rowconfigure(1, weight=1)

        tag_status_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        tag_status_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        self.entry_tags = ctk.CTkEntry(tag_status_frame, placeholder_text="+ Añadir Tag (ej: neuroanatomy)", width=200, height=28)
        self.entry_tags.pack(side="left")

        lbl_status_info = ctk.CTkLabel(tag_status_frame, text="👁️ Público  |  ⏱️ Autoguardado hace 2m", font=("Arial", 11), text_color="#64748b")
        lbl_status_info.pack(side="right")

        # Panel Izquierdo: Front (Question)
        front_frame = ctk.CTkFrame(form_frame, fg_color=COLOR_BG_TARJETA, corner_radius=12, border_width=1, border_color=COLOR_BORDE)
        front_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=5)
        front_frame.grid_columnconfigure(0, weight=1)
        front_frame.grid_rowconfigure(2, weight=1)

        front_header = ctk.CTkFrame(front_frame, fg_color="transparent")
        front_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))
        
        lbl_f = ctk.CTkLabel(front_header, text="Frente (Pregunta)", font=("Arial", 13, "bold"), text_color=COLOR_AZUL)
        lbl_f.pack(side="left")
        
        lbl_format_f = ctk.CTkLabel(front_header, text="B   I   <>   🖼️", font=("Arial", 11, "bold"), text_color="#64748b")
        lbl_format_f.pack(side="right")

        self.txt_pregunta = ctk.CTkTextbox(front_frame, font=("Arial", 13), fg_color=COLOR_BG_SUBTARJETA, border_width=1, border_color=COLOR_BORDE)
        self.txt_pregunta.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="nsew")

        # Panel Derecho: Back (Answer)
        back_frame = ctk.CTkFrame(form_frame, fg_color=COLOR_BG_TARJETA, corner_radius=12, border_width=1, border_color=COLOR_BORDE)
        back_frame.grid(row=1, column=1, sticky="nsew", padx=(10, 0), pady=5)
        back_frame.grid_columnconfigure(0, weight=1)
        back_frame.grid_rowconfigure(2, weight=1)

        back_header = ctk.CTkFrame(back_frame, fg_color="transparent")
        back_header.grid(row=0, column=0, sticky="ew", padx=15, pady=(15, 5))

        lbl_b = ctk.CTkLabel(back_header, text="Dorso (Respuesta)", font=("Arial", 13, "bold"), text_color="#10b981")
        lbl_b.pack(side="left")
        
        lbl_format_b = ctk.CTkLabel(back_header, text="B   I   •   <>   🖼️", font=("Arial", 11, "bold"), text_color="#64748b")
        lbl_format_b.pack(side="right")

        self.txt_respuesta = ctk.CTkTextbox(back_frame, font=("Arial", 13), fg_color=COLOR_BG_SUBTARJETA, border_width=1, border_color=COLOR_BORDE)
        self.txt_respuesta.grid(row=1, column=0, padx=15, pady=(5, 15), sticky="nsew")

        self.subframe_crear_tarjeta.grid_rowconfigure(2, weight=0)

    def cargar_creador_tarjetas(self, mazo_id=None, tarjeta_id=None):
        self.editing_tarjeta_id = tarjeta_id
        
        mazos = self.servicio_flashcards.obtener_todos_los_mazos()
        self.mazos_creacion_map = {m['nombre']: m['id'] for m in mazos}
        nombres = list(self.mazos_creacion_map.keys())

        if nombres:
            self.opt_mazo_creacion.configure(values=nombres)
            
            # Si estamos editando, cargamos la tarjeta existente
            if tarjeta_id:
                t_info = self.servicio_flashcards.obtener_tarjeta_por_id(tarjeta_id)
                if t_info:
                    self.lbl_title_crear.configure(text="✏️ Editar Tarjeta")
                    self.btn_save_crear.configure(text="💾 Guardar Cambios")
                    
                    self.txt_pregunta.delete("0.0", "end")
                    self.txt_pregunta.insert("0.0", t_info['pregunta'])
                    
                    self.txt_respuesta.delete("0.0", "end")
                    self.txt_respuesta.insert("0.0", t_info['respuesta'])
                    
                    self.entry_tags.delete(0, "end")
                    if t_info['tags']:
                        self.entry_tags.insert(0, t_info['tags'])
                        
                    # Seleccionar mazo correcto
                    for name, mid in self.mazos_creacion_map.items():
                        if mid == t_info['mazo_id']:
                            self.opt_mazo_creacion.set(name)
                            break
                    return

            # Modo creación de nueva tarjeta
            self.lbl_title_crear.configure(text="NeuroCore Flashcards")
            self.btn_save_crear.configure(text="💾 Guardar Tarjeta")
            
            if mazo_id:
                mazo_info = self.servicio_flashcards.obtener_mazo_por_id(mazo_id)
                if mazo_info and mazo_info['nombre'] in self.mazos_creacion_map:
                    self.opt_mazo_creacion.set(mazo_info['nombre'])
            else:
                self.opt_mazo_creacion.set(nombres[0])
                
        self.txt_pregunta.delete("0.0", "end")
        self.txt_respuesta.delete("0.0", "end")
        self.entry_tags.delete(0, "end")

    def guardar_nueva_tarjeta(self):
        mazo_name = self.opt_mazo_creacion.get()
        if not mazo_name or mazo_name not in self.mazos_creacion_map:
            messagebox.showerror("Error", "Debes crear un mazo primero.")
            return

        mazo_id = self.mazos_creacion_map[mazo_name]
        pregunta = self.txt_pregunta.get("0.0", "end").strip()
        respuesta = self.txt_respuesta.get("0.0", "end").strip()
        tags = self.entry_tags.get().strip()

        if not pregunta or not respuesta:
            messagebox.showerror("Campos vacíos", "La pregunta y la respuesta son obligatorias.")
            return

        if self.editing_tarjeta_id:
            # Modo Edición
            exito, mensaje = self.servicio_flashcards.actualizar_tarjeta(
                self.editing_tarjeta_id, mazo_id, pregunta, respuesta, tags
            )
            if exito:
                messagebox.showinfo("Actualizada", "¡Tarjeta actualizada correctamente!")
                # Volver a los detalles del mazo
                self.mostrar_subframe_detalles_mazo(self.active_mazo_id)
            else:
                messagebox.showerror("Error", mensaje)
        else:
            # Modo Nueva Tarjeta
            exito, mensaje = self.servicio_flashcards.crear_tarjeta(mazo_id, pregunta, respuesta, tags)
            if exito:
                self.txt_pregunta.delete("0.0", "end")
                self.txt_respuesta.delete("0.0", "end")
                self.entry_tags.delete(0, "end")
                messagebox.showinfo("Guardada", "¡Tarjeta agregada correctamente!")
            else:
                messagebox.showerror("Error", mensaje)

    # ==========================================
    # --- VISTA 4: STUDY SESSION (ESTUDIO) ---
    # ==========================================
    def crear_elementos_estudiar(self):
        self.subframe_estudiar.grid_columnconfigure(0, weight=1)
        self.subframe_estudiar.grid_rowconfigure(1, weight=1)

        # Fila superior de navegación
        top_frame = ctk.CTkFrame(self.subframe_estudiar, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 10))

        btn_back = ctk.CTkButton(top_frame, text="← Biblioteca", width=80, height=28, fg_color="#2b2b2b", hover_color="#333333",
                                 command=self.mostrar_subframe_biblioteca)
        btn_back.pack(side="left")

        self.lbl_study_title = ctk.CTkLabel(top_frame, text="Mazo de Repaso", font=("Arial", 18, "bold"))
        self.lbl_study_title.pack(side="left", padx=15)

        self.lbl_study_deck_sub = ctk.CTkLabel(top_frame, text="Mazo Activo", font=("Arial", 12), text_color="#64748b")
        self.lbl_study_deck_sub.pack(side="left", padx=5)

        # Reloj e indicador de tiempo (Timer de estudio)
        self.lbl_study_timer = ctk.CTkLabel(top_frame, text="⏱️ 00:00", font=("Arial", 13, "bold"), fg_color="#2b2b2b", text_color="#f8fafc", corner_radius=6)
        self.lbl_study_timer.pack(side="right")

        # Contenido principal
        study_content = ctk.CTkFrame(self.subframe_estudiar, fg_color="transparent")
        study_content.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        study_content.grid_columnconfigure(0, weight=1)
        
        # Corrección de pesos del Grid:
        study_content.grid_rowconfigure(1, weight=0) # Barra de progreso NO se expande
        study_content.grid_rowconfigure(2, weight=1) # Tarjeta de estudio SE expande para llenar el espacio

        # Fila de progreso
        progress_info_frame = ctk.CTkFrame(study_content, fg_color="transparent")
        progress_info_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        self.lbl_progreso_study = ctk.CTkLabel(progress_info_frame, text="Tarjeta 1 de 10", font=("Arial", 12))
        self.lbl_progreso_study.pack(side="left")

        # Estadísticas en Español
        self.lbl_study_counts = ctk.CTkLabel(progress_info_frame, text="0  •  0  •  0", font=("Arial", 12, "bold"), text_color=COLOR_AZUL)
        self.lbl_study_counts.pack(side="right")

        self.prog_bar_study = ctk.CTkProgressBar(study_content, height=6, progress_color=COLOR_AZUL, fg_color="#333333")
        self.prog_bar_study.grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # Tarjeta grande interactiva de estudio
        self.card_box = ctk.CTkFrame(study_content, fg_color=COLOR_BG_TARJETA, corner_radius=15, border_width=1, border_color=COLOR_BORDE)
        self.card_box.grid(row=2, column=0, sticky="nsew", pady=10)
        self.card_box.grid_columnconfigure(0, weight=1)
        self.card_box.grid_rowconfigure(1, weight=1)

        # Badge "Pregunta" y ojo
        lbl_badge_header = ctk.CTkFrame(self.card_box, fg_color="transparent")
        lbl_badge_header.grid(row=0, column=0, sticky="ew", padx=20, pady=15)
        
        self.lbl_badge = ctk.CTkLabel(lbl_badge_header, text="  Pregunta  ", font=("Arial", 10, "bold"), text_color=COLOR_AZUL, fg_color="#1a1c24", corner_radius=4)
        self.lbl_badge.pack(side="left")
        
        lbl_eye = ctk.CTkLabel(lbl_badge_header, text="👁️", font=("Arial", 12), text_color="#64748b")
        lbl_eye.pack(side="right")

        # Texto pregunta/respuesta
        text_container = ctk.CTkFrame(self.card_box, fg_color="transparent")
        text_container.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        text_container.grid_columnconfigure(0, weight=1)

        self.lbl_pregunta_study = ctk.CTkLabel(text_container, text="Pregunta", font=("Arial", 20, "bold"), wraplength=650)
        self.lbl_pregunta_study.pack(fill="x", expand=True, pady=15)

        self.sep_study = ctk.CTkFrame(text_container, height=1, fg_color="#333333")
        
        self.lbl_respuesta_study = ctk.CTkLabel(text_container, text="Respuesta", font=("Arial", 16), text_color="#10b981", wraplength=650)
        
        self.lbl_study_footer = ctk.CTkLabel(self.card_box, text="👆 Haz clic en la tarjeta o presiona ESPACIO para revelar la respuesta", font=("Arial", 11, "italic"), text_color="#64748b")
        self.lbl_study_footer.grid(row=2, column=0, pady=20)

        # Eventos para click recursivos en toda la tarjeta y sus elementos
        self.vincular_click_revelar(self.card_box)

        # Controles SM-2
        self.btn_panel_sm2 = ctk.CTkFrame(self.subframe_estudiar, fg_color="transparent")
        self.btn_panel_sm2.grid(row=2, column=0, padx=30, pady=(10, 20), sticky="ew")
        
        self.btn_panel_sm2.grid_columnconfigure(0, weight=1)
        self.btn_panel_sm2.grid_columnconfigure(1, weight=1)
        self.btn_panel_sm2.grid_columnconfigure(2, weight=1)
        self.btn_panel_sm2.grid_columnconfigure(3, weight=1)

        self.btn_again = ctk.CTkButton(self.btn_panel_sm2, text="Otra vez\n< 1m", height=40, font=("Arial", 12, "bold"), fg_color=COLOR_ROJO, hover_color=COLOR_ROJO_HOVER, command=lambda: self.calificar_tarjeta(0))
        self.btn_again.grid(row=0, column=0, padx=6, sticky="ew")

        self.btn_hard = ctk.CTkButton(self.btn_panel_sm2, text="Difícil\n12m", height=40, font=("Arial", 12, "bold"), fg_color=COLOR_AMBER, hover_color=COLOR_AMBER_HOVER, command=lambda: self.calificar_tarjeta(1))
        self.btn_hard.grid(row=0, column=1, padx=6, sticky="ew")

        self.btn_good = ctk.CTkButton(self.btn_panel_sm2, text="Bien\n1d", height=40, font=("Arial", 12, "bold"), fg_color=COLOR_AZUL, hover_color=COLOR_AZUL_HOVER, command=lambda: self.calificar_tarjeta(2))
        self.btn_good.grid(row=0, column=2, padx=6, sticky="ew")

        self.btn_easy = ctk.CTkButton(self.btn_panel_sm2, text="Fácil\n4d", height=40, font=("Arial", 12, "bold"), fg_color=COLOR_VERDE, hover_color=COLOR_VERDE_HOVER, command=lambda: self.calificar_tarjeta(3))
        self.btn_easy.grid(row=0, column=3, padx=6, sticky="ew")

    def vincular_click_revelar(self, widget):
        """Vincula recursivamente el evento de clic izquierdo a un widget y todos sus hijos."""
        widget.bind("<Button-1>", lambda event: self.revelar_respuesta())
        for child in widget.winfo_children():
            self.vincular_click_revelar(child)

    def iniciar_sesion_estudio(self, mazo_id):
        self.active_mazo_id = mazo_id
        mazo_info = self.servicio_flashcards.obtener_mazo_por_id(mazo_id)
        if mazo_info:
            self.lbl_study_title.configure(text=mazo_info['nombre'])
            self.lbl_study_deck_sub.configure(text=f"Mazo: {mazo_info['nombre']}")

        self.active_tarjetas_estudio = self.servicio_flashcards.obtener_tarjetas_pendientes_por_mazo(mazo_id)
        self.idx_tarjeta_actual = 0
        self.revelado = False

        self.study_start_time = time.time()
        self.study_timer_running = True
        self.actualizar_timer_estudio()

        self.bind("<space>", lambda event: self.revelar_respuesta())

        self.mostrar_siguiente_tarjeta()

    def actualizar_timer_estudio(self):
        if self.study_timer_running:
            duracion = int(time.time() - self.study_start_time)
            minutos = duracion // 60
            segundos = duracion % 60
            self.lbl_study_timer.configure(text=f"⏱️ {minutos:02d}:{segundos:02d}")
            self.after(1000, self.actualizar_timer_estudio)

    def mostrar_siguiente_tarjeta(self):
        self.revelado = False
        
        self.btn_panel_sm2.grid_remove()
        self.sep_study.pack_forget()
        self.lbl_respuesta_study.pack_forget()
        self.lbl_study_footer.grid()

        total_cards = len(self.active_tarjetas_estudio)

        tarjetas_mazo = self.servicio_flashcards.obtener_tarjetas_por_mazo(self.active_mazo_id)
        due_count = len(self.active_tarjetas_estudio) - self.idx_tarjeta_actual
        new_count = sum(1 for t in tarjetas_mazo if t['repetitions'] == 0)
        mastered_count = sum(1 for t in tarjetas_mazo if t['repetitions'] >= 4)
        
        self.lbl_study_counts.configure(text=f"{due_count}  •  {new_count}  •  {mastered_count}", text_color=COLOR_AZUL)

        if total_cards == 0 or self.idx_tarjeta_actual >= total_cards:
            # Finalizado
            self.lbl_pregunta_study.configure(text="🎉 ¡Felicidades!\nHas completado los repasos de hoy para este mazo.", text_color="#10b981")
            self.lbl_badge.configure(text="COMPLETADO", text_color="#10b981", fg_color="#064e3b")
            self.lbl_study_footer.grid_remove()
            self.prog_bar_study.set(1.0)
            self.lbl_progreso_study.configure(text="Progreso: 100%")
            self.unbind("<space>")
            self.study_timer_running = False
            return

        prog_val = self.idx_tarjeta_actual / total_cards
        self.prog_bar_study.set(prog_val)
        self.lbl_progreso_study.configure(text=f"Tarjeta {self.idx_tarjeta_actual + 1} de {total_cards}")

        card = self.active_tarjetas_estudio[self.idx_tarjeta_actual]
        self.lbl_pregunta_study.configure(text=card['pregunta'], text_color="#f1f5f9")
        self.lbl_badge.configure(text="Pregunta", text_color=COLOR_AZUL, fg_color="#1a1c24")

    def revelar_respuesta(self):
        if self.revelado or self.idx_tarjeta_actual >= len(self.active_tarjetas_estudio):
            return
            
        self.revelado = True
        card = self.active_tarjetas_estudio[self.idx_tarjeta_actual]
        
        self.sep_study.pack(fill="x", pady=15)
        self.lbl_respuesta_study.configure(text=card['respuesta'])
        self.lbl_respuesta_study.pack(fill="x", expand=True, pady=10)

        self.lbl_study_footer.grid_remove()
        self.btn_panel_sm2.grid()

    def calificar_tarjeta(self, calificacion):
        if self.idx_tarjeta_actual >= len(self.active_tarjetas_estudio):
            return

        card = self.active_tarjetas_estudio[self.idx_tarjeta_actual]
        self.servicio_flashcards.responder_tarjeta(card['id'], calificacion)

        self.idx_tarjeta_actual += 1
        self.mostrar_siguiente_tarjeta()

    # ==========================================
    # --- FUNCIONES DE OTRAS SECCIONES ---
    # ==========================================
    def alternar_cronometro(self):
        if not self.corriendo:
            self.corriendo = True
            self.btn_inicio.configure(text="Pausar", fg_color="red")
            self.contar()
        else:
            self.corriendo = False
            self.btn_inicio.configure(text="Reanudar", fg_color="#1f538d")

    def contar(self):
        if self.corriendo and self.segundos_restantes > 0:
            self.segundos_restantes -= 1
            minutos = self.segundos_restantes // 60
            segs = self.segundos_restantes % 60
            self.label_reloj.configure(text=f"{minutos:02d}:{segs:02d}")
            self.after(1000, self.contar)

    def reiniciar_cronometro(self):
        self.corriendo = False
        self.segundos_restantes = self.tiempo_inicial
        minutos = self.tiempo_inicial // 60
        self.label_reloj.configure(text=f"{minutos:02d}:00")
        self.btn_inicio.configure(text="Iniciar", state="normal", fg_color="#1f538d")

    def aplicar_tiempo(self):
        try:
            minutos = int(self.entrada_tiempo.get())
            if minutos > 0:
                self.tiempo_inicial = minutos * 60
                self.segundos_restantes = self.tiempo_inicial
                self.label_reloj.configure(text=f"{minutos:02d}:00")
                self.corriendo = False
                self.btn_inicio.configure(text="Iniciar", fg_color="#1f538d")
        except ValueError:
            print("Por favor ingresa un número válido")

    def guardar_apunte(self):
        texto = self.caja_texto.get("0.0", "end").strip()
        cat = self.combo_categoria.get()
        if texto:
            self.cerebro.guardar_en_el_cerebro(texto, cat)
            self.caja_texto.delete("0.0", "end")
            self.label_mensaje.configure(text="¡Guardado!", text_color="green")
            self.after(2000, lambda: self.label_mensaje.configure(text=""))

    def borrar_apunte(self):
        texto = self.caja_texto.get("0.0", "end").strip()
        if texto:
            self.cerebro.eliminar_apunte(texto)
            self.caja_texto.delete("0.0", "end")
            self.label_mensaje.configure(text="¡Apunte eliminado!", text_color="#c93434")
            self.after(2000, lambda: self.label_mensaje.configure(text=""))

    def realizar_busqueda(self):
        consulta = self.entrada_busqueda.get()
        if not consulta: return

        resultados = self.cerebro.buscar_con_ia(consulta)
        self.resultado_texto.configure(state="normal")
        self.resultado_texto.delete("0.0", "end")

        if not resultados:
            self.resultado_texto.insert("end", "No encontré nada relacionado en tu memoria.")
        else:
            for res in resultados:
                texto_res = f"📌 [{res['categoria']}] (Similitud: {res['score']:.2f})\n{res['texto']}\n\n"
                self.resultado_texto.insert("end", texto_res)

        self.resultado_texto.configure(state="disabled")
