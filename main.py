import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow
from controllers.main_controller import MainController

def main():
    """Función principal de la aplicación"""
    app = QApplication(sys.argv)
    
    # Crear el controlador principal
    controller = MainController()
    
    # Crear y mostrar la ventana principal, pasando el controlador
    window = MainWindow(controller)
    window.show()
    
    # Conectar señales del controlador a la ventana
    controller.datos_actualizados.connect(window.actualizar_resumen)
    controller.error_occurred.connect(window.mostrar_error)
    controller.operacion_exitosa.connect(window.mostrar_exito)
    
    # Ejecutar la aplicación
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
    
    
