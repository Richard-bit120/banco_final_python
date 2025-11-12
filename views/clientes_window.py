from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QComboBox, QPushButton, QTableWidget,
                            QTableWidgetItem, QHeaderView, QMessageBox,
                            QLabel, QSplitter)
from PyQt6.QtCore import Qt
from models.entidades import ClientePersona, ClienteEmpresa, CuentaCorriente

class AltaClienteDialog(QDialog):
    def __init__(self, banco, db, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Alta de Cliente")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QFormLayout(self)
        
        self.dni_input = QLineEdit()
        self.nombre_input = QLineEdit()
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["persona", "empresa"])
        
        layout.addRow("DNI:", self.dni_input)
        layout.addRow("Nombre:", self.nombre_input)
        layout.addRow("Tipo:", self.tipo_combo)
        
        buttons_layout = QHBoxLayout()
        guardar_btn = QPushButton("Guardar")
        cancelar_btn = QPushButton("Cancelar")
        
        guardar_btn.clicked.connect(self.guardar_cliente)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(guardar_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def guardar_cliente(self):
        dni = self.dni_input.text().strip()
        nombre = self.nombre_input.text().strip()
        tipo = self.tipo_combo.currentText()
        
        if not dni or not nombre:
            QMessageBox.warning(self, "Error", "DNI y Nombre son obligatorios")
            return
        
        if tipo == "persona":
            cliente = ClientePersona(dni, nombre)
        else:
            cliente = ClienteEmpresa(dni, nombre)
        
        if self.banco.alta_cliente(cliente) and self.db.guardar_cliente(cliente):
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "El cliente ya existe")

class ListaClientesDialog(QDialog):
    def __init__(self, banco, db, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Lista de Clientes")
        self.setModal(True)
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # Estadísticas
        stats_layout = QHBoxLayout()
        total_clientes = len(self.banco.obtener_clientes())
        clientes_persona = len(self.banco.obtener_clientes_persona())
        clientes_empresa = len(self.banco.obtener_clientes_empresa())
        
        stats_layout.addWidget(QLabel(f"Total: {total_clientes}"))
        stats_layout.addWidget(QLabel(f"Personas: {clientes_persona}"))
        stats_layout.addWidget(QLabel(f"Empresas: {clientes_empresa}"))
        layout.addLayout(stats_layout)
        
        # Tabla de clientes
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(3)
        self.tabla_clientes.setHorizontalHeaderLabels(["DNI", "Nombre", "Tipo"])
        layout.addWidget(self.tabla_clientes)
        
        # Botones
        buttons_layout = QHBoxLayout()
        editar_btn = QPushButton("Editar")
        eliminar_btn = QPushButton("Eliminar")
        cerrar_btn = QPushButton("Cerrar")
        
        editar_btn.clicked.connect(self.editar_cliente)
        eliminar_btn.clicked.connect(self.eliminar_cliente)
        cerrar_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(editar_btn)
        buttons_layout.addWidget(eliminar_btn)
        buttons_layout.addWidget(cerrar_btn)
        
        layout.addLayout(buttons_layout)
        
        self.cargar_clientes()
    
    def cargar_clientes(self):
        clientes = self.banco.obtener_clientes()
        self.tabla_clientes.setRowCount(len(clientes))
        
        for i, cliente in enumerate(clientes):
            self.tabla_clientes.setItem(i, 0, QTableWidgetItem(cliente.dni))
            self.tabla_clientes.setItem(i, 1, QTableWidgetItem(cliente.nombre))
            self.tabla_clientes.setItem(i, 2, QTableWidgetItem(cliente.tipo))
        
        self.tabla_clientes.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def editar_cliente(self):
        fila = self.tabla_clientes.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Seleccione un cliente para editar")
            return
    
        dni = self.tabla_clientes.item(fila, 0).text()
        cliente = self.banco.buscar_cliente(dni)
    
        if cliente:
            dialog = EditarClienteDialog(cliente, self.banco, self.db, self)
            if dialog.exec():
                self.cargar_clientes()
                QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
        else:
            QMessageBox.warning(self, "Error", "Cliente no encontrado")
    
    def eliminar_cliente(self):
        fila = self.tabla_clientes.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Seleccione un cliente para eliminar")
            return
        
        dni = self.tabla_clientes.item(fila, 0).text()
        nombre = self.tabla_clientes.item(fila, 1).text()
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de eliminar al cliente {nombre} ({dni})?"
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            if self.banco.baja_cliente(dni) and self.db.eliminar_cliente(dni):
                self.cargar_clientes()
                QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el cliente (puede tener cuentas activas)")

class EditarClienteDialog(QDialog):
    def __init__(self, cliente, banco, db, parent=None):
        super().__init__(parent)
        self.cliente = cliente
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Editar Cliente")
        self.setModal(True)
        
        layout = QFormLayout(self)
        
        self.dni_input = QLineEdit(self.cliente.dni)
        self.dni_input.setReadOnly(True)
        self.nombre_input = QLineEdit(self.cliente.nombre)
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["persona", "empresa"])
        self.tipo_combo.setCurrentText(self.cliente.tipo)
        
        layout.addRow("DNI:", self.dni_input)
        layout.addRow("Nombre:", self.nombre_input)
        layout.addRow("Tipo:", self.tipo_combo)
        
        buttons_layout = QHBoxLayout()
        guardar_btn = QPushButton("Guardar")
        cancelar_btn = QPushButton("Cancelar")
        
        guardar_btn.clicked.connect(self.guardar_cambios)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(guardar_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def guardar_cambios(self):
        nombre = self.nombre_input.text().strip()
        tipo = self.tipo_combo.currentText()
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        # Actualizar cliente (en una implementación real, necesitaríamos métodos de actualización)
        QMessageBox.information(self, "Editar", "Funcionalidad de edición completa")
        self.accept()
        
class EditarClienteDialog(QDialog):
    def __init__(self, cliente, banco, db, parent=None):
        super().__init__(parent)
        self.cliente = cliente
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Editar Cliente")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QFormLayout(self)
        
        self.dni_input = QLineEdit(self.cliente.dni)
        self.dni_input.setReadOnly(True)
        self.nombre_input = QLineEdit(self.cliente.nombre)
        
        layout.addRow("DNI:", self.dni_input)
        layout.addRow("Nombre:", self.nombre_input)
        
        buttons_layout = QHBoxLayout()
        guardar_btn = QPushButton("Guardar")
        cancelar_btn = QPushButton("Cancelar")
        
        guardar_btn.clicked.connect(self.guardar_cambios)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(guardar_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def guardar_cambios(self):
        nombre = self.nombre_input.text().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            return
        
        try:
            # Actualizar el nombre del cliente
            self.cliente._nombre = nombre
            
            # Actualizar en la base de datos
            if self.db.guardar_cliente(self.cliente):
                QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar el cliente")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al actualizar: {str(e)}")