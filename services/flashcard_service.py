# services/flashcard_service.py
import sqlite3
from datetime import datetime, timedelta
from core.memory import DatabaseManager

class FlashcardService:
    def __init__(self):
        self.db_manager = DatabaseManager()

    def crear_mazo(self, nombre):
        """Crea un nuevo mazo de flashcards en la base de datos."""
        nombre = nombre.strip()
        if not nombre:
            return False, "El nombre del mazo no puede estar vacío."
        try:
            self.db_manager.cursor.execute('INSERT INTO mazos (nombre) VALUES (?)', (nombre,))
            self.db_manager.conn.commit()
            return True, "Mazo creado exitosamente."
        except sqlite3.IntegrityError:
            return False, "Ya existe un mazo con ese nombre."

    def obtener_todos_los_mazos(self):
        """
        Obtiene todos los mazos con el conteo de total de cartas, cartas pendientes
        y el porcentaje de maestría (cartas con repetitions >= 4).
        """
        self.db_manager.cursor.execute('''
            SELECT 
                m.id, 
                m.nombre,
                COUNT(f.id) as total_cartas,
                SUM(CASE WHEN f.due_date <= CURRENT_DATE THEN 1 ELSE 0 END) as cartas_pendientes,
                SUM(CASE WHEN f.repetitions >= 4 THEN 1 ELSE 0 END) as cartas_maestras
            FROM mazos m
            LEFT JOIN flashcards f ON m.id = f.mazo_id
            GROUP BY m.id, m.nombre
        ''')
        rows = self.db_manager.cursor.fetchall()
        
        mazos = []
        for r in rows:
            total = r[2] if r[2] else 0
            pendientes = r[3] if r[3] else 0
            maestras = r[4] if r[4] else 0
            
            # Cálculo del porcentaje de maestría
            porcentaje_maestria = 0
            if total > 0:
                porcentaje_maestria = int((maestras / total) * 100)
                
            mazos.append({
                'id': r[0],
                'nombre': r[1],
                'total_cartas': total,
                'cartas_pendientes': pendientes,
                'porcentaje_maestria': porcentaje_maestria
            })
        return mazos

    def obtener_mazo_por_id(self, mazo_id):
        self.db_manager.cursor.execute('SELECT id, nombre FROM mazos WHERE id = ?', (mazo_id,))
        row = self.db_manager.cursor.fetchone()
        if row:
            return {'id': row[0], 'nombre': row[1]}
        return None

    def eliminar_mazo(self, mazo_id):
        """Elimina un mazo y todas sus flashcards asociadas (por ON DELETE CASCADE)."""
        self.db_manager.cursor.execute('DELETE FROM mazos WHERE id = ?', (mazo_id,))
        self.db_manager.conn.commit()
        return True

    def crear_tarjeta(self, mazo_id, pregunta, respuesta, tags=""):
        """Crea una nueva flashcard para un mazo específico."""
        pregunta = pregunta.strip()
        respuesta = respuesta.strip()
        if not pregunta or not respuesta:
            return False, "La pregunta y la respuesta no pueden estar vacías."
        
        # Guardamos la fecha actual en formato YYYY-MM-DD
        hoy = datetime.now().strftime('%Y-%m-%d')
        
        self.db_manager.cursor.execute('''
            INSERT INTO flashcards (mazo_id, pregunta, respuesta, tags, due_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (mazo_id, pregunta, respuesta, tags, hoy))
        self.db_manager.conn.commit()
        return True, "Tarjeta creada exitosamente."

    def obtener_tarjetas_por_mazo(self, mazo_id):
        """Obtiene todas las tarjetas en un mazo."""
        self.db_manager.cursor.execute('''
            SELECT id, pregunta, respuesta, tags, due_date, interval, repetitions, ease_factor
            FROM flashcards
            WHERE mazo_id = ?
        ''', (mazo_id,))
        rows = self.db_manager.cursor.fetchall()
        
        tarjetas = []
        for r in rows:
            tarjetas.append({
                'id': r[0],
                'pregunta': r[1],
                'respuesta': r[2],
                'tags': r[3],
                'due_date': r[4],
                'interval': r[5],
                'repetitions': r[6],
                'ease_factor': r[7]
            })
        return tarjetas

    def obtener_tarjetas_pendientes_por_mazo(self, mazo_id):
        """Obtiene las tarjetas que están vencidas o vencen hoy."""
        self.db_manager.cursor.execute('''
            SELECT id, pregunta, respuesta, tags, due_date, interval, repetitions, ease_factor
            FROM flashcards
            WHERE mazo_id = ? AND due_date <= CURRENT_DATE
        ''', (mazo_id,))
        rows = self.db_manager.cursor.fetchall()
        
        tarjetas = []
        for r in rows:
            tarjetas.append({
                'id': r[0],
                'pregunta': r[1],
                'respuesta': r[2],
                'tags': r[3],
                'due_date': r[4],
                'interval': r[5],
                'repetitions': r[6],
                'ease_factor': r[7]
            })
        return tarjetas

    def eliminar_tarjeta(self, tarjeta_id):
        self.db_manager.cursor.execute('DELETE FROM flashcards WHERE id = ?', (tarjeta_id,))
        self.db_manager.conn.commit()
        return True

    def responder_tarjeta(self, tarjeta_id, calificacion):
        """
        Aplica el algoritmo SM-2 para actualizar la fecha de vencimiento de una tarjeta.
        calificacion: 0 (Otra vez), 1 (Difícil), 2 (Bien), 3 (Fácil)
        """
        # Obtener los datos actuales de la tarjeta
        self.db_manager.cursor.execute('''
            SELECT interval, repetitions, ease_factor FROM flashcards WHERE id = ?
        ''', (tarjeta_id,))
        row = self.db_manager.cursor.fetchone()
        if not row:
            return False, "Tarjeta no encontrada."

        interval = row[0]
        repetitions = row[1]
        ease_factor = row[2]

        # Mapeo de calificacion (0-3) a la escala de calidad original de SM-2 (0-5)
        # 0 (Otra vez) -> calidad 1
        # 1 (Difícil) -> calidad 2
        # 2 (Bien) -> calidad 4
        # 3 (Fácil) -> calidad 5
        if calificacion == 0:
            quality = 1
        elif calificacion == 1:
            quality = 2
        elif calificacion == 2:
            quality = 4
        else:
            quality = 5

        # Lógica SM-2
        if quality < 3:
            # Si el usuario responde incorrectamente o con mucha dificultad (Otra vez o Difícil)
            repetitions = 0
            interval = 1
        else:
            if repetitions == 0:
                interval = 1
            elif repetitions == 1:
                interval = 4  # en SM-2 estándar es 6, pero para aprendizaje rápido 4 es ideal
            else:
                interval = int(round(interval * ease_factor))
            
            repetitions += 1

        # Actualizar factor de facilidad (ease_factor)
        ease_factor = ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
        if ease_factor < 1.3:
            ease_factor = 1.3

        # Calcular nueva fecha de vencimiento
        hoy = datetime.now()
        nueva_fecha = hoy + timedelta(days=interval)
        nueva_fecha_str = nueva_fecha.strftime('%Y-%m-%d')

        # Actualizar en la BD
        self.db_manager.cursor.execute('''
            UPDATE flashcards
            SET interval = ?, repetitions = ?, ease_factor = ?, due_date = ?
            WHERE id = ?
        ''', (interval, repetitions, ease_factor, nueva_fecha_str, tarjeta_id))
        self.db_manager.conn.commit()

        return True, f"Repaso registrado. Próxima fecha: {nueva_fecha_str} (en {interval} días)"
