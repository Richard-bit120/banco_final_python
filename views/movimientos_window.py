from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLineEdit, QComboBox, QPushButton, QMessageBox,
                            QLabel, QDoubleSpinBox, QDateEdit, QTextEdit)
from PyQt6.QtCore import QDate
from datetime import datetime, timedelta
from models.entidades import CuentaPlazoFijo

class DepositoDialog(QDialog):
    def __init__(self, banco, db, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Depósito")
        self.setModal(True)
        self.setFixedSize(400, 200)
        
        layout = QFormLayout(self)
        
        self.cuenta_combo = QComboBox()
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setMinimum(0.01)
        self.monto_input.setMaximum(1000000)
        self.monto_input.setValue(100)
        
        self.actualizar_cuentas()
        
        layout.addRow("Cuenta:", self.cuenta_combo)
        layout.addRow("Monto:", self.monto_input)
        
        # Información de saldo actual
        self.saldo_label = QLabel("Saldo actual: $0.00")
        layout.addRow(self.saldo_label)
        
        # Conectar señal para actualizar saldo cuando cambie la cuenta
        self.cuenta_combo.currentIndexChanged.connect(self.actualizar_saldo)
        self.actualizar_saldo()  # Actualizar inicialmente
        
        buttons_layout = QHBoxLayout()
        depositar_btn = QPushButton("Depositar")
        cancelar_btn = QPushButton("Cancelar")
        
        depositar_btn.clicked.connect(self.realizar_deposito)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(depositar_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def actualizar_cuentas(self):
        self.cuenta_combo.clear()
        for cuenta in self.banco.obtener_cuentas():
            self.cuenta_combo.addItem(f"{cuenta.numero} - {cuenta.titular.nombre}", cuenta.numero)
    
    def actualizar_saldo(self):
        numero_cuenta = self.cuenta_combo.currentData()
        if numero_cuenta:
            cuenta = self.banco.buscar_cuenta(numero_cuenta)
            if cuenta:
                self.saldo_label.setText(f"Saldo actual: ${cuenta.saldo:.2f}")
    
    def realizar_deposito(self):
        numero_cuenta = self.cuenta_combo.currentData()
        monto = self.monto_input.value()
        
        if not numero_cuenta:
            QMessageBox.warning(self, "Error", "Seleccione una cuenta")
            return
        
        if self.banco.depositar(numero_cuenta, monto):
            cuenta = self.banco.buscar_cuenta(numero_cuenta)
            self.db.guardar_cuenta(cuenta)
            self.db.guardar_movimiento(numero_cuenta, "DEPOSITO", monto, cuenta.saldo)
            QMessageBox.information(self, "Éxito", f"Depósito de ${monto:.2f} realizado correctamente")
            self.actualizar_saldo()
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo realizar el depósito")

class ExtraccionDialog(QDialog):
    def __init__(self, banco, db, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Extracción")
        self.setModal(True)
        self.setFixedSize(400, 250)
        
        layout = QFormLayout(self)
        
        self.cuenta_combo = QComboBox()
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setMinimum(0.01)
        self.monto_input.setMaximum(1000000)
        self.monto_input.setValue(100)
        
        self.actualizar_cuentas()
        
        layout.addRow("Cuenta:", self.cuenta_combo)
        layout.addRow("Monto:", self.monto_input)
        
        # Información de cuenta
        self.saldo_label = QLabel("Saldo actual: $0.00")
        self.limite_label = QLabel("Límite disponible: $0.00")
        
        layout.addRow(self.saldo_label)
        layout.addRow(self.limite_label)
        
        # Conectar señal para actualizar información cuando cambie la cuenta
        self.cuenta_combo.currentIndexChanged.connect(self.actualizar_info_cuenta)
        self.actualizar_info_cuenta()  # Actualizar inicialmente
        
        buttons_layout = QHBoxLayout()
        extraer_btn = QPushButton("Extraer")
        cancelar_btn = QPushButton("Cancelar")
        
        extraer_btn.clicked.connect(self.realizar_extraccion)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(extraer_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def actualizar_cuentas(self):
        self.cuenta_combo.clear()
        for cuenta in self.banco.obtener_cuentas():
            self.cuenta_combo.addItem(f"{cuenta.numero} - {cuenta.titular.nombre}", cuenta.numero)
    
    def actualizar_info_cuenta(self):
        numero_cuenta = self.cuenta_combo.currentData()
        if numero_cuenta:
            cuenta = self.banco.buscar_cuenta(numero_cuenta)
            if cuenta:
                self.saldo_label.setText(f"Saldo actual: ${cuenta.saldo:.2f}")
                
                if hasattr(cuenta, 'limite_descubierto'):
                    limite_disponible = cuenta.saldo + cuenta.limite_descubierto
                    self.limite_label.setText(f"Límite disponible: ${limite_disponible:.2f}")
                    self.limite_label.setVisible(True)
                else:
                    self.limite_label.setVisible(False)
    
    def realizar_extraccion(self):
        numero_cuenta = self.cuenta_combo.currentData()
        monto = self.monto_input.value()
        
        if not numero_cuenta:
            QMessageBox.warning(self, "Error", "Seleccione una cuenta")
            return
        
        if self.banco.extraer(numero_cuenta, monto):
            cuenta = self.banco.buscar_cuenta(numero_cuenta)
            self.db.guardar_cuenta(cuenta)
            self.db.guardar_movimiento(numero_cuenta, "EXTRACCION", -monto, cuenta.saldo)
            QMessageBox.information(self, "Éxito", f"Extracción de ${monto:.2f} realizada correctamente")
            self.actualizar_info_cuenta()
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo realizar la extracción (fondos insuficientes)")

class TransferenciaDialog(QDialog):
    def __init__(self, banco, db, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Transferencia")
        self.setModal(True)
        self.setFixedSize(500, 300)
        
        layout = QFormLayout(self)
        
        self.cuenta_origen_combo = QComboBox()
        self.cuenta_destino_combo = QComboBox()
        self.monto_input = QDoubleSpinBox()
        self.monto_input.setMinimum(0.01)
        self.monto_input.setMaximum(1000000)
        self.monto_input.setValue(100)
        
        self.actualizar_cuentas()
        
        layout.addRow("Cuenta Origen:", self.cuenta_origen_combo)
        layout.addRow("Cuenta Destino:", self.cuenta_destino_combo)
        layout.addRow("Monto:", self.monto_input)
        
        # Información de comisión
        self.comision_label = QLabel("Comisión por transferencia a terceros: $0.00")
        layout.addRow(self.comision_label)
        
        # Conectar señales para actualizar información
        self.cuenta_origen_combo.currentIndexChanged.connect(self.actualizar_comision)
        self.cuenta_destino_combo.currentIndexChanged.connect(self.actualizar_comision)
        self.actualizar_comision()
        
        buttons_layout = QHBoxLayout()
        transferir_btn = QPushButton("Transferir")
        cancelar_btn = QPushButton("Cancelar")
        
        transferir_btn.clicked.connect(self.realizar_transferencia)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(transferir_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def actualizar_cuentas(self):
        self.cuenta_origen_combo.clear()
        self.cuenta_destino_combo.clear()
        
        for cuenta in self.banco.obtener_cuentas():
            self.cuenta_origen_combo.addItem(f"{cuenta.numero} - {cuenta.titular.nombre}", cuenta.numero)
            self.cuenta_destino_combo.addItem(f"{cuenta.numero} - {cuenta.titular.nombre}", cuenta.numero)
    
    def actualizar_comision(self):
        cuenta_origen_num = self.cuenta_origen_combo.currentData()
        cuenta_destino_num = self.cuenta_destino_combo.currentData()
        
        if cuenta_origen_num and cuenta_destino_num:
            cuenta_origen = self.banco.buscar_cuenta(cuenta_origen_num)
            cuenta_destino = self.banco.buscar_cuenta(cuenta_destino_num)
            
            if cuenta_origen and cuenta_destino:
                if cuenta_origen.titular.dni != cuenta_destino.titular.dni:
                    comision = self.banco.comision_transferencia
                    self.comision_label.setText(f"Comisión por transferencia a terceros: ${comision:.2f}")
                    self.comision_label.setStyleSheet("color: red;")
                else:
                    self.comision_label.setText("Transferencia entre cuentas propias - Sin comisión")
                    self.comision_label.setStyleSheet("color: green;")
    
    def realizar_transferencia(self):
        cuenta_origen_num = self.cuenta_origen_combo.currentData()
        cuenta_destino_num = self.cuenta_destino_combo.currentData()
        monto = self.monto_input.value()
        
        if not cuenta_origen_num or not cuenta_destino_num:
            QMessageBox.warning(self, "Error", "Seleccione ambas cuentas")
            return
        
        if cuenta_origen_num == cuenta_destino_num:
            QMessageBox.warning(self, "Error", "No puede transferir a la misma cuenta")
            return
        
        if self.banco.transferir(cuenta_origen_num, cuenta_destino_num, monto):
            # Actualizar cuentas en la base de datos
            cuenta_origen = self.banco.buscar_cuenta(cuenta_origen_num)
            cuenta_destino = self.banco.buscar_cuenta(cuenta_destino_num)
            
            self.db.guardar_cuenta(cuenta_origen)
            self.db.guardar_cuenta(cuenta_destino)
            
            QMessageBox.information(self, "Éxito", f"Transferencia de ${monto:.2f} realizada correctamente")
            self.accept()
        else:
            QMessageBox.warning(self, "Error", "No se pudo realizar la transferencia (fondos insuficientes)")

class PlazoFijoDialog(QDialog):
    def __init__(self, banco, db, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Crear Plazo Fijo")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QFormLayout(self)
        
        self.cuenta_origen_combo = QComboBox()
        self.plazo_dias_combo = QComboBox()
        self.plazo_dias_combo.addItems(["30", "60", "90", "180", "365"])
        self.capital_input = QDoubleSpinBox()
        self.capital_input.setMinimum(100)
        self.capital_input.setMaximum(1000000)
        self.capital_input.setValue(1000)
        
        self.actualizar_cuentas()
        
        layout.addRow("Cuenta de Origen:", self.cuenta_origen_combo)
        layout.addRow("Plazo (días):", self.plazo_dias_combo)
        layout.addRow("Capital:", self.capital_input)
        
        # Información del plazo fijo
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        layout.addRow("Resumen:", self.info_text)
        
        # Conectar señales para actualizar información
        self.cuenta_origen_combo.currentIndexChanged.connect(self.actualizar_info)
        self.plazo_dias_combo.currentIndexChanged.connect(self.actualizar_info)
        self.capital_input.valueChanged.connect(self.actualizar_info)
        self.actualizar_info()
        
        buttons_layout = QHBoxLayout()
        crear_btn = QPushButton("Crear Plazo Fijo")
        cancelar_btn = QPushButton("Cancelar")
        
        crear_btn.clicked.connect(self.crear_plazo_fijo)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(crear_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def actualizar_cuentas(self):
        self.cuenta_origen_combo.clear()
        for cuenta in self.banco.obtener_cuentas():
            # Solo mostrar cuentas que no sean plazos fijos y tengan saldo suficiente
            if not hasattr(cuenta, 'fecha_vencimiento'):
                self.cuenta_origen_combo.addItem(f"{cuenta.numero} - {cuenta.titular.nombre}", cuenta.numero)
    
    def actualizar_info(self):
        cuenta_origen_num = self.cuenta_origen_combo.currentData()
        plazo_dias = int(self.plazo_dias_combo.currentText())
        capital = self.capital_input.value()
        
        if cuenta_origen_num:
            cuenta_origen = self.banco.buscar_cuenta(cuenta_origen_num)
            if cuenta_origen:
                saldo_disponible = cuenta_origen.saldo
                tasa_anual = self.banco.tasa_interes_pf
                
                info = f"Saldo disponible en cuenta origen: ${saldo_disponible:.2f}\n"
                info += f"Capital a invertir: ${capital:.2f}\n"
                info += f"Plazo: {plazo_dias} días\n"
                info += f"Tasa de interés anual: {tasa_anual*100:.2f}%\n"
                
                # Calcular interés
                interes = capital * tasa_anual * plazo_dias / 365
                total = capital + interes
                
                info += f"Interés estimado: ${interes:.2f}\n"
                info += f"Total al vencimiento: ${total:.2f}\n\n"
                
                if capital > saldo_disponible:
                    info += "❌ Fondos insuficientes en la cuenta origen"
                else:
                    info += "✅ Fondos suficientes disponibles"
                
                self.info_text.setPlainText(info)
    
    def crear_plazo_fijo(self):
        cuenta_origen_num = self.cuenta_origen_combo.currentData()
        plazo_dias = int(self.plazo_dias_combo.currentText())
        capital = self.capital_input.value()
        
        if not cuenta_origen_num:
            QMessageBox.warning(self, "Error", "Seleccione una cuenta origen")
            return
        
        cuenta_origen = self.banco.buscar_cuenta(cuenta_origen_num)
        if not cuenta_origen:
            QMessageBox.warning(self, "Error", "Cuenta origen no encontrada")
            return
        
        if capital > cuenta_origen.saldo:
            QMessageBox.warning(self, "Error", "Fondos insuficientes en la cuenta origen")
            return
        
        # Extraer capital de la cuenta origen
        if not cuenta_origen.extraer(capital):
            QMessageBox.warning(self, "Error", "No se pudo extraer el capital de la cuenta origen")
            return
        
        # Generar número de cuenta para el plazo fijo
        numero_pf = f"PF{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # CORRECCIÓN: Crear cuenta a plazo fijo (ahora importada correctamente)
        plazo_fijo = CuentaPlazoFijo(
            numero_pf, 
            cuenta_origen.titular, 
            capital, 
            self.banco.tasa_interes_pf, 
            plazo_dias
        )
        
        # Registrar en el banco y base de datos
        if self.banco.alta_cuenta(plazo_fijo):
            self.db.guardar_cuenta(cuenta_origen)
            self.db.guardar_cuenta(plazo_fijo)
            self.db.guardar_movimiento(cuenta_origen_num, "CREACION PF", -capital, cuenta_origen.saldo)
            
            QMessageBox.information(
                self, 
                "Éxito", 
                f"Plazo fijo creado exitosamente\n"
                f"Número: {numero_pf}\n"
                f"Capital: ${capital:.2f}\n"
                f"Vencimiento: {plazo_fijo.fecha_vencimiento.strftime('%d/%m/%Y')}"
            )
            self.accept()
        else:
            # Revertir la extracción si falla la creación del plazo fijo
            cuenta_origen.depositar(capital)
            QMessageBox.warning(self, "Error", "No se pudo crear el plazo fijo")