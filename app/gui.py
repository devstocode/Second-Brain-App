# app/gui.py
import customtkinter as ctk
from services.brain_service import BrainService

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class VentanaPrincipal(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Second Brain AI")
        self.geometry("900x600")

        self.cerebro = BrainService()

        # Variables Pomodoro
        self.tiempo_inicial = 25 * 60
        self.segundos_restantes = self.tiempo_inicial
        self.corriendo = False

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # --- 1. BARRA LATERAL ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="NeuroCore AI",
                                       font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_pomodoro = ctk.CTkButton(self.sidebar_frame, text="⏱️ Pomodoro", command=self.mostrar_pomodoro)
        self.btn_pomodoro.grid(row=1, column=0, padx=20, pady=10)

        self.btn_cuaderno = ctk.CTkButton(self.sidebar_frame, text="📓 Cuaderno", command=self.mostrar_cuaderno)
        self.btn_cuaderno.grid(row=2, column=0, padx=20, pady=10)

        self.btn_buscador = ctk.CTkButton(self.sidebar_frame, text="🧠 Buscador IA", command=self.mostrar_buscador)
        self.btn_buscador.grid(row=3, column=0, padx=20, pady=10)

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

        self.caja_texto = ctk.CTkTextbox(self.frame_cuaderno, width=500, height=200)
        self.caja_texto.pack(pady=10)

        self.combo_categoria = ctk.CTkComboBox(self.frame_cuaderno,
                                               values=["Programación", "Matemáticas", "Historia", "General"])
        self.combo_categoria.pack(pady=10)

        self.btn_guardar_apunte = ctk.CTkButton(self.frame_cuaderno, text="💾 Guardar", command=self.guardar_apunte)
        self.btn_guardar_apunte.pack(pady=20)

        # BOTÓN PARA BORRAR
        self.btn_borrar_apunte = ctk.CTkButton(self.frame_cuaderno, text="🗑️ Borrar", command=self.borrar_apunte,
                                               fg_color="#c93434", hover_color="#992626")
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

        self.btn_buscar = ctk.CTkButton(self.frame_buscador, text="🔍 Buscar con IA", command=self.realizar_busqueda)
        self.btn_buscar.pack(pady=10)

        self.resultado_texto = ctk.CTkTextbox(self.frame_buscador, width=600, height=200, state="disabled")
        self.resultado_texto.pack(pady=20)

        self.mostrar_pomodoro()

    # --- NAVEGACIÓN ---
    def ocultar_todos_los_frames(self):
        self.frame_pomodoro.grid_forget()
        self.frame_cuaderno.grid_forget()
        self.frame_buscador.grid_forget()

    def mostrar_pomodoro(self):
        self.ocultar_todos_los_frames()
        self.frame_pomodoro.grid(row=0, column=1, sticky="nsew")

    def mostrar_cuaderno(self):
        self.ocultar_todos_los_frames()
        self.frame_cuaderno.grid(row=0, column=1, sticky="nsew")

    def mostrar_buscador(self):
        self.ocultar_todos_los_frames()
        self.frame_buscador.grid(row=0, column=1, sticky="nsew")

    # --- FUNCIONES ---
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
        """Lee los minutos ingresados y actualiza el reloj."""
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
