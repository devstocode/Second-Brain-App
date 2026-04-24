# app/main.py
import sys
import os

# Esto ayuda a que Python encuentre las carpetas core y services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importamos nuestra nueva clase gráfica
from app.gui import VentanaPrincipal

if __name__ == "__main__":
    # Creamos el objeto ventana y lo mantenemos abierto (mainloop)
    app = VentanaPrincipal()
    app.mainloop()