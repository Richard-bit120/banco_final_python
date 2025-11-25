from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTabWidget, QMessageBox,
                            QTableWidget, QTableWidgetItem, QHeaderView,
                            QMenuBar, QMenu, QStatusBar)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
from models.entidades import CajaAhorro, CuentaCorriente, CuentaPlazoFijo

class MainWindow(QMainWindow):
    """Ventana principal del sistema bancario"""
    
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("Sistema Bancario")
        self.setGeometry(100, 100, 500, 350)
        
        # Crear menú principal
        self.crear_menu()
        
        # Crear widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        layout = QVBoxLayout(central_widget)
        
        # Título
        titulo = QLabel("SISTEMA BANCARIO 11/11/2025 - PROGRAMACION 1")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 10px;")
        layout.addWidget(titulo)
        
        # Widget de pestañas
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Pestaña de resumen
        self.crear_tab_resumen()
        
        # Barra de estado
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Sistema listo")
        
        # Actualizar datos iniciales
        self.actualizar_resumen()
    
    def crear_menu(self):
        """Crea el menú principal"""
        menubar = self.menuBar()
        
        # Menú Archivo
        archivo_menu = menubar.addMenu('Archivo')
        salir_action = QAction('Salir', self)
        salir_action.triggered.connect(self.close)
        archivo_menu.addAction(salir_action)
        
        # Menú Clientes
        clientes_menu = menubar.addMenu('Clientes')
        alta_cliente_action = QAction('Alta Cliente', self)
        alta_cliente_action.triggered.connect(self.mostrar_alta_cliente)
        clientes_menu.addAction(alta_cliente_action)
        
        listar_clientes_action = QAction('Listar Clientes', self)
        listar_clientes_action.triggered.connect(self.mostrar_clientes)
        clientes_menu.addAction(listar_clientes_action)
        
        # Menú Cuentas
        cuentas_menu = menubar.addMenu('Cuentas')
        alta_cuenta_action = QAction('Alta Cuenta', self)
        alta_cuenta_action.triggered.connect(self.mostrar_alta_cuenta)
        cuentas_menu.addAction(alta_cuenta_action)
        
        listar_cuentas_action = QAction('Listar Cuentas', self)
        listar_cuentas_action.triggered.connect(self.mostrar_cuentas)
        cuentas_menu.addAction(listar_cuentas_action)
        
        # Menú Movimientos
        movimientos_menu = menubar.addMenu('Movimientos')
        deposito_action = QAction('Depósito', self)
        deposito_action.triggered.connect(self.mostrar_deposito)
        movimientos_menu.addAction(deposito_action)
        
        extraccion_action = QAction('Extracción', self)
        extraccion_action.triggered.connect(self.mostrar_extraccion)
        movimientos_menu.addAction(extraccion_action)
        
        transferencia_action = QAction('Transferencia', self)
        transferencia_action.triggered.connect(self.mostrar_transferencia)
        movimientos_menu.addAction(transferencia_action)
        
        plazo_fijo_action = QAction('Plazo Fijo', self)
        plazo_fijo_action.triggered.connect(self.mostrar_plazo_fijo)
        movimientos_menu.addAction(plazo_fijo_action)
        
        # Menú Informes
        informes_menu = menubar.addMenu('Informes')
        informe_general_action = QAction('Informe General', self)
        informe_general_action.triggered.connect(self.mostrar_informe_general)
        informes_menu.addAction(informe_general_action)
        
        informe_plazo_fijo_action = QAction('Informe Plazo Fijo', self)
        informe_plazo_fijo_action.triggered.connect(self.mostrar_informe_plazo_fijo)
        informes_menu.addAction(informe_plazo_fijo_action)
        
        informe_movimientos_action = QAction('Informe Movimientos', self)
        informe_movimientos_action.triggered.connect(self.mostrar_informe_movimientos)
        informes_menu.addAction(informe_movimientos_action)
        
        # Menú Parámetros
        parametros_menu = menubar.addMenu('Parámetros')
        config_action = QAction('Configurar Parámetros', self)
        config_action.triggered.connect(self.mostrar_configuracion)
        parametros_menu.addAction(config_action)
    
    def crear_tab_resumen(self):
        """Crea la pestaña de resumen"""
        tab_resumen = QWidget()
        layout = QVBoxLayout(tab_resumen)
        
        # Estadísticas rápidas
        stats_layout = QHBoxLayout()
        
        # Total clientes
        self.clientes_frame = self.crear_stat_frame("Total Clientes", "0")
        stats_layout.addWidget(self.clientes_frame)
        
        # Total cuentas
        self.cuentas_frame = self.crear_stat_frame("Total Cuentas", "0")
        stats_layout.addWidget(self.cuentas_frame)
        
        # Saldo total
        self.saldo_frame = self.crear_stat_frame("Saldo Total", "$0.00")
        stats_layout.addWidget(self.saldo_frame)
        
        layout.addLayout(stats_layout)
        
        # Tabla de últimas cuentas
        layout.addWidget(QLabel("Últimas Cuentas:"))
        self.tabla_cuentas = QTableWidget()
        self.tabla_cuentas.setColumnCount(4)
        self.tabla_cuentas.setHorizontalHeaderLabels(["Número", "Titular", "Tipo", "Saldo"])
        layout.addWidget(self.tabla_cuentas)
        
        self.tabs.addTab(tab_resumen, "Resumen")
    
    def crear_stat_frame(self, titulo: str, valor: str) -> QWidget:
        """Crea un frame de estadística"""
        frame = QWidget()
        frame.setStyleSheet("border: 1px solid gray; padding: 10px; border-radius: 5px;")
        layout = QVBoxLayout(frame)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_valor = QLabel(valor)
        lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_valor.setStyleSheet("font-size: 14pt; font-weight: bold;")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)
        
        return frame
    
    def actualizar_stat_frame(self, frame: QWidget, valor: str):
        """Actualiza el valor de un frame de estadística"""
        layout = frame.layout()
        if layout and layout.itemAt(1):
            layout.itemAt(1).widget().setText(valor)
    
    def actualizar_resumen(self):
        """Actualiza la información del resumen usando el controlador"""
        try:
            informe = self.controller.generar_informe_general()
            
            # Actualizar estadísticas
            self.actualizar_stat_frame(self.clientes_frame, str(informe['total_clientes']))
            self.actualizar_stat_frame(self.cuentas_frame, str(informe['total_cuentas']))
            self.actualizar_stat_frame(self.saldo_frame, f"${informe['saldo_total']:.2f}")
            
            # Actualizar tabla de cuentas
            self.actualizar_tabla_cuentas()
            
        except Exception as e:
            self.mostrar_error(f"Error actualizando resumen: {str(e)}")
    
    def actualizar_tabla_cuentas(self):
        """Actualiza la tabla de cuentas"""
        cuentas = self.controller.obtener_cuentas()[:10]  # Últimas 10 cuentas
        
        self.tabla_cuentas.setRowCount(len(cuentas))
        
        for i, cuenta in enumerate(cuentas):
            self.tabla_cuentas.setItem(i, 0, QTableWidgetItem(cuenta.numero))
            self.tabla_cuentas.setItem(i, 1, QTableWidgetItem(cuenta.titular.nombre))
            
            tipo = "CA" if isinstance(cuenta, CajaAhorro) else "CC" if isinstance(cuenta, CuentaCorriente) else "PF"
            self.tabla_cuentas.setItem(i, 2, QTableWidgetItem(tipo))
            self.tabla_cuentas.setItem(i, 3, QTableWidgetItem(f"${cuenta.saldo:.2f}"))
        
        self.tabla_cuentas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error"""
        QMessageBox.warning(self, "Error", mensaje)
        self.status_bar.showMessage(f"Error: {mensaje}")
    
    def mostrar_exito(self, mensaje: str):
        """Muestra un mensaje de éxito"""
        QMessageBox.information(self, "Éxito", mensaje)
        self.status_bar.showMessage(mensaje)
    
    # Métodos para mostrar diálogos
    def mostrar_alta_cliente(self):
        from .clientes_window import AltaClienteDialog
        dialog = AltaClienteDialog(self.controller.banco, self.controller.db, self)
        if dialog.exec():
            self.actualizar_resumen()
    
    def mostrar_clientes(self):
        from .clientes_window import ListaClientesDialog
        dialog = ListaClientesDialog(self.controller.banco, self.controller.db, self)
        dialog.exec()
    
    def mostrar_alta_cuenta(self):
        from .cuentas_window import AltaCuentaDialog
        dialog = AltaCuentaDialog(self.controller.banco, self.controller.db, self)
        if dialog.exec():
            self.actualizar_resumen()
    
    def mostrar_cuentas(self):
        from .cuentas_window import ListaCuentasDialog
        dialog = ListaCuentasDialog(self.controller.banco, self.controller.db, self)
        dialog.exec()
    
    def mostrar_deposito(self):
        from .movimientos_window import DepositoDialog
        dialog = DepositoDialog(self.controller.banco, self.controller.db, self)
        if dialog.exec():
            self.actualizar_resumen()
    
    def mostrar_extraccion(self):
        from .movimientos_window import ExtraccionDialog
        dialog = ExtraccionDialog(self.controller.banco, self.controller.db, self)
        if dialog.exec():
            self.actualizar_resumen()
    
    def mostrar_transferencia(self):
        from .movimientos_window import TransferenciaDialog
        dialog = TransferenciaDialog(self.controller.banco, self.controller.db, self)
        if dialog.exec():
            self.actualizar_resumen()
    
    def mostrar_plazo_fijo(self):
        from .movimientos_window import PlazoFijoDialog
        dialog = PlazoFijoDialog(self.controller.banco, self.controller.db, self)
        if dialog.exec():
            self.actualizar_resumen()
    
    def mostrar_informe_general(self):
        from .informes_window import InformeGeneralDialog
        dialog = InformeGeneralDialog(self.controller.banco, self)
        dialog.exec()
    
    def mostrar_informe_plazo_fijo(self):
        from .informes_window import InformePlazoFijoDialog
        dialog = InformePlazoFijoDialog(self.controller.banco, self)
        dialog.exec()
    
    def mostrar_informe_movimientos(self):
        from .informes_window import InformeMovimientosDialog
        dialog = InformeMovimientosDialog(self.controller.banco, self.controller.db, self)
        dialog.exec()
    
    def mostrar_configuracion(self):
        from .informes_window import ConfiguracionDialog
        dialog = ConfiguracionDialog(self.controller.banco, self)
        if dialog.exec():
            self.actualizar_resumen()