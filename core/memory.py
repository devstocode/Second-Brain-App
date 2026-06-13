import sqlite3
from app.config import Config

class DatabaseManager:
    def __init__(self):
        # Usamos la ruta que definimos en el archivo de configuración
        self.conn = sqlite3.connect(Config.DB_PATH)
        self.conn.execute("PRAGMA foreign_keys = ON;")
        self.cursor = self.conn.cursor()
        self._crear_tablas()

    def _crear_tablas(self):
        # Creamos la tabla si no existe (id, contenido del estudio, y categoría)
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS recuerdos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                contenido TEXT NOT NULL,
                categoria TEXT
            )
        ''')
        # Tabla de Mazos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS mazos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
        ''')
        # Tabla de Flashcards con algoritmo de repetición espaciada
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mazo_id INTEGER NOT NULL,
                pregunta TEXT NOT NULL,
                respuesta TEXT NOT NULL,
                tags TEXT,
                due_date TEXT DEFAULT CURRENT_DATE,
                interval INTEGER DEFAULT 1,
                repetitions INTEGER DEFAULT 0,
                ease_factor REAL DEFAULT 2.5,
                FOREIGN KEY (mazo_id) REFERENCES mazos(id) ON DELETE CASCADE
            )
        ''')
        self.conn.commit()

    def guardar(self, texto, categoria="General"):
        self.cursor.execute('INSERT INTO recuerdos (contenido, categoria) VALUES (?, ?)', (texto, categoria))
        self.conn.commit()

    def obtener_todos(self):
        self.cursor.execute('SELECT * FROM recuerdos')
        return self.cursor.fetchall()

    def eliminar_apunte(self, contenido_texto):
        """Elimina un apunte de la base de datos buscando su contenido exacto."""
        # Ejecutamos el borrado en la tabla 'recuerdos' buscando en la columna 'contenido'
        self.cursor.execute("DELETE FROM recuerdos WHERE contenido = ?", (contenido_texto,))
        self.conn.commit()