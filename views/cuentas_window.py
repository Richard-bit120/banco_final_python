from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QComboBox, QPushButton, QTableWidget,
                            QTableWidgetItem, QHeaderView, QMessageBox,
                            QLabel, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from models.entidades import CajaAhorro, CuentaCorriente, CuentaPlazoFijo

class AltaCuentaDialog(QDialog):
    def __init__(self, banco, db, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Alta de Cuenta")
        self.setModal(True)
        self.setFixedSize(500, 300)
        
        layout = QFormLayout(self)
        
        self.numero_input = QLineEdit()
        self.cliente_combo = QComboBox()
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItems(["Caja Ahorro", "Cuenta Corriente", "Plazo Fijo"])
        self.saldo_input = QDoubleSpinBox()
        self.saldo_input.setMinimum(0)
        self.saldo_input.setMaximum(1000000)
        self.saldo_input.setValue(0)
        
        # Conectar señal para mostrar/ocultar campos según tipo
        self.tipo_combo.currentTextChanged.connect(self.actualizar_campos)
        
        # Campos específicos para cuenta corriente
        self.limite_descubierto_input = QDoubleSpinBox()
        self.limite_descubierto_input.setMinimum(0)
        self.limite_descubierto_input.setMaximum(10000)
        self.limite_descubierto_input.setValue(1000)
        self.limite_descubierto_input.setVisible(False)
        
        # Campos específicos para plazo fijo
        self.plazo_dias_input = QComboBox()
        self.plazo_dias_input.addItems(["30", "60", "90", "180", "365"])
        self.plazo_dias_input.setVisible(False)
        
        # Actualizar combo de clientes
        self.actualizar_clientes()
        
        layout.addRow("Número Cuenta:", self.numero_input)
        layout.addRow("Cliente:", self.cliente_combo)
        layout.addRow("Tipo Cuenta:", self.tipo_combo)
        layout.addRow("Saldo Inicial:", self.saldo_input)
        layout.addRow("Límite Descubierto:", self.limite_descubierto_input)
        layout.addRow("Plazo (días):", self.plazo_dias_input)
        
        buttons_layout = QHBoxLayout()
        guardar_btn = QPushButton("Guardar")
        cancelar_btn = QPushButton("Cancelar")
        
        guardar_btn.clicked.connect(self.guardar_cuenta)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(guardar_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def actualizar_clientes(self):
        self.cliente_combo.clear()
        for cliente in self.banco.obtener_clientes():
            self.cliente_combo.addItem(f"{cliente.nombre} ({cliente.dni})", cliente.dni)
    
    def actualizar_campos(self, tipo):
        """Muestra/oculta campos según el tipo de cuenta"""
        if tipo == "Cuenta Corriente":
            self.limite_descubierto_input.setVisible(True)
            self.plazo_dias_input.setVisible(False)
        elif tipo == "Plazo Fijo":
            self.limite_descubierto_input.setVisible(False)
            self.plazo_dias_input.setVisible(True)
        else:  # Caja Ahorro
            self.limite_descubierto_input.setVisible(False)
            self.plazo_dias_input.setVisible(False)
    
    def guardar_cuenta(self):
        numero = self.numero_input.text().strip()
        dni_cliente = self.cliente_combo.currentData()
        tipo = self.tipo_combo.currentText()
        saldo = self.saldo_input.value()
        
        if not numero or not dni_cliente:
            QMessageBox.warning(self, "Error", "Número y Cliente son obligatorios")
            return
        
        cliente = self.banco.buscar_cliente(dni_cliente)
        if not cliente:
            QMessageBox.warning(self, "Error", "Cliente no encontrado")
            return
        
        if tipo == "Caja Ahorro":
            cuenta = CajaAhorro(numero, cliente, saldo)
        elif tipo == "Cuenta Corriente":
            limite = self.limite_descubierto_input.value()
            cuenta = CuentaCorriente(numero, cliente, limite, self.banco.costo_mantenimiento_cc, saldo)
        else:  # Plazo Fijo
            plazo_dias = int(self.plazo_dias_input.currentText())
            cuenta = CuentaPlazoFijo(numero, cliente, saldo, self.banco.tasa_interes_pf, plazo_dias)
        
        if self.banco.alta_cuenta(cuenta) and self.db.guardar_cuenta(cuenta):
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "La cuenta ya existe")

class ListaCuentasDialog(QDialog):
    def __init__(self, banco, db, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Lista de Cuentas")
        self.setModal(True)
        self.resize(800, 500)
        
        layout = QVBoxLayout(self)
        
        # Filtros
        filtros_layout = QHBoxLayout()
        self.filtro_tipo = QComboBox()
        self.filtro_tipo.addItems(["Todos", "Caja Ahorro", "Cuenta Corriente", "Plazo Fijo"])
        self.filtro_tipo.currentTextChanged.connect(self.cargar_cuentas)
        
        filtros_layout.addWidget(QLabel("Filtrar por tipo:"))
        filtros_layout.addWidget(self.filtro_tipo)
        filtros_layout.addStretch()
        
        layout.addLayout(filtros_layout)
        
        # Tabla de cuentas
        self.tabla_cuentas = QTableWidget()
        self.tabla_cuentas.setColumnCount(6)
        self.tabla_cuentas.setHorizontalHeaderLabels([
            "Número", "Titular", "Tipo", "Saldo", "Límite", "Estado"
        ])
        layout.addWidget(self.tabla_cuentas)
        
        # Botones
        buttons_layout = QHBoxLayout()
        movimientos_btn = QPushButton("Ver Movimientos")
        eliminar_btn = QPushButton("Eliminar")
        cerrar_btn = QPushButton("Cerrar")
        
        movimientos_btn.clicked.connect(self.ver_movimientos)
        eliminar_btn.clicked.connect(self.eliminar_cuenta)
        cerrar_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(movimientos_btn)
        buttons_layout.addWidget(eliminar_btn)
        buttons_layout.addWidget(cerrar_btn)
        
        layout.addLayout(buttons_layout)
        
        self.cargar_cuentas()
    
    def cargar_cuentas(self):
        tipo_filtro = self.filtro_tipo.currentText()
        
        if tipo_filtro == "Caja Ahorro":
            cuentas = self.banco.obtener_cajas_ahorro()
        elif tipo_filtro == "Cuenta Corriente":
            cuentas = self.banco.obtener_cuentas_corriente()
        elif tipo_filtro == "Plazo Fijo":
            cuentas = self.banco.obtener_cuentas_plazo_fijo()
        else:
            cuentas = self.banco.obtener_cuentas()
        
        self.tabla_cuentas.setRowCount(len(cuentas))
        
        for i, cuenta in enumerate(cuentas):
            self.tabla_cuentas.setItem(i, 0, QTableWidgetItem(cuenta.numero))
            self.tabla_cuentas.setItem(i, 1, QTableWidgetItem(cuenta.titular.nombre))
            
            tipo = "CA" if isinstance(cuenta, CajaAhorro) else "CC" if isinstance(cuenta, CuentaCorriente) else "PF"
            self.tabla_cuentas.setItem(i, 2, QTableWidgetItem(tipo))
            self.tabla_cuentas.setItem(i, 3, QTableWidgetItem(f"${cuenta.saldo:.2f}"))
            
            # Información específica por tipo
            if isinstance(cuenta, CuentaCorriente):
                self.tabla_cuentas.setItem(i, 4, QTableWidgetItem(f"${cuenta.limite_descubierto:.2f}"))
                estado = "En descubierto" if cuenta.saldo < 0 else "Normal"
            elif isinstance(cuenta, CuentaPlazoFijo):
                self.tabla_cuentas.setItem(i, 4, QTableWidgetItem("N/A"))
                estado = "Vencido" if cuenta.fecha_vencimiento else "Activo"
            else:
                self.tabla_cuentas.setItem(i, 4, QTableWidgetItem("N/A"))
                estado = "Normal"
            
            self.tabla_cuentas.setItem(i, 5, QTableWidgetItem(estado))
        
        self.tabla_cuentas.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def ver_movimientos(self):
        fila = self.tabla_cuentas.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Seleccione una cuenta para ver movimientos")
            return
        
        numero_cuenta = self.tabla_cuentas.item(fila, 0).text()
        # Aquí podrías abrir un diálogo específico para movimientos de esta cuenta
        QMessageBox.information(self, "Movimientos", f"Mostrar movimientos de cuenta {numero_cuenta}")
    
    def eliminar_cuenta(self):
        fila = self.tabla_cuentas.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Error", "Seleccione una cuenta para eliminar")
            return
        
        numero = self.tabla_cuentas.item(fila, 0).text()
        titular = self.tabla_cuentas.item(fila, 1).text()
        
        respuesta = QMessageBox.question(
            self, "Confirmar", 
            f"¿Está seguro de eliminar la cuenta {numero} de {titular}?"
        )
        
        if respuesta == QMessageBox.StandardButton.Yes:
            if self.banco.baja_cuenta(numero) and self.db.eliminar_cuenta(numero):
                self.cargar_cuentas()
                QMessageBox.information(self, "Éxito", "Cuenta eliminada correctamente")
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar la cuenta")
                
class EditarCuentaDialog(QDialog):
    def __init__(self, cuenta, banco, db, parent=None):
        super().__init__(parent)
        self.cuenta = cuenta
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Editar Cuenta")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QFormLayout(self)
        
        self.numero_input = QLineEdit(self.cuenta.numero)
        self.numero_input.setReadOnly(True)
        
        self.titular_label = QLabel(f"{self.cuenta.titular.nombre} ({self.cuenta.titular.dni})")
        
        # Campos específicos según tipo de cuenta
        if isinstance(self.cuenta, CuentaCorriente):
            self.limite_input = QDoubleSpinBox()
            self.limite_input.setMinimum(0)
            self.limite_input.setMaximum(10000)
            self.limite_input.setValue(self.cuenta.limite_descubierto)
            layout.addRow("Límite Descubierto:", self.limite_input)
        
        layout.addRow("Número:", self.numero_input)
        layout.addRow("Titular:", self.titular_label)
        
        buttons_layout = QHBoxLayout()
        guardar_btn = QPushButton("Guardar")
        cancelar_btn = QPushButton("Cancelar")
        
        guardar_btn.clicked.connect(self.guardar_cambios)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(guardar_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def guardar_cambios(self):
        try:
            if isinstance(self.cuenta, CuentaCorriente):
                self.cuenta._limite_descubierto = self.limite_input.value()
            
            # Actualizar en la base de datos
            if self.db.guardar_cuenta(self.cuenta):
                QMessageBox.information(self, "Éxito", "Cuenta actualizada correctamente")
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "No se pudo actualizar la cuenta")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al actualizar: {str(e)}")