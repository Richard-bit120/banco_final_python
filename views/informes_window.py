from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QComboBox, QPushButton, QTableWidget, QTableWidgetItem, 
                            QHeaderView, QMessageBox, QLabel, QTextEdit, QDateEdit,
                            QFileDialog, QDoubleSpinBox, QLineEdit)
from PyQt6.QtCore import QDate
from PyQt6.QtGui import QColor
from datetime import datetime
import csv
from models.entidades import CajaAhorro, CuentaCorriente, CuentaPlazoFijo

class InformeGeneralDialog(QDialog):
    def __init__(self, banco, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Informe General del Banco")
        self.setModal(True)
        self.resize(700, 600)
        
        layout = QVBoxLayout(self)
        
        # Área de texto para el informe
        self.texto_informe = QTextEdit()
        self.texto_informe.setReadOnly(True)
        layout.addWidget(self.texto_informe)
        
        # Botones
        buttons_layout = QHBoxLayout()
        actualizar_btn = QPushButton("Actualizar Informe")
        exportar_btn = QPushButton("Exportar a TXT")
        cerrar_btn = QPushButton("Cerrar")
        
        actualizar_btn.clicked.connect(self.generar_informe)
        exportar_btn.clicked.connect(self.exportar_informe)
        cerrar_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(actualizar_btn)
        buttons_layout.addWidget(exportar_btn)
        buttons_layout.addWidget(cerrar_btn)
        
        layout.addLayout(buttons_layout)
        
        # Generar informe inicial
        self.generar_informe()
    
    def generar_informe(self):
        """Genera el informe general del banco"""
        informe = "INFORME GENERAL DEL BANCO\n"
        informe += "=" * 60 + "\n\n"
        
        # Cajas de Ahorro
        cajas_ahorro = self.banco.obtener_cajas_ahorro()
        informe += f"CAJAS DE AHORRO ({len(cajas_ahorro)})\n"
        informe += "-" * 40 + "\n"
        total_ca = 0
        for ca in cajas_ahorro:
            informe += f"  {ca.numero} - {ca.titular.nombre}: ${ca.saldo:.2f}\n"
            total_ca += ca.saldo
        informe += f"TOTAL CA: ${total_ca:.2f}\n\n"
        
        # Cuentas Corrientes
        cuentas_corriente = self.banco.obtener_cuentas_corriente()
        informe += f"CUENTAS CORRIENTES ({len(cuentas_corriente)})\n"
        informe += "-" * 40 + "\n"
        total_cc = 0
        total_descubierto = 0
        for cc in cuentas_corriente:
            descubierto = f" (Descubierto: ${cc.descubierto_utilizado:.2f})" if cc.saldo < 0 else ""
            informe += f"  {cc.numero} - {cc.titular.nombre}: ${cc.saldo:.2f}{descubierto}\n"
            total_cc += cc.saldo
            if cc.saldo < 0:
                total_descubierto += abs(cc.saldo)
        informe += f"TOTAL CC: ${total_cc:.2f}\n"
        informe += f"TOTAL EN DESCUBIERTO: ${total_descubierto:.2f}\n\n"
        
        # Plazos Fijos
        plazos_fijos = self.banco.obtener_cuentas_plazo_fijo()
        informe += f"PLAZOS FIJOS ({len(plazos_fijos)})\n"
        informe += "-" * 40 + "\n"
        total_pf = 0
        for pf in plazos_fijos:
            informe += f"  {pf.numero} - {pf.titular.nombre}: ${pf.saldo:.2f}\n"
            total_pf += pf.saldo
        informe += f"TOTAL PF: ${total_pf:.2f}\n\n"
        
        # Clientes
        clientes_persona = self.banco.obtener_clientes_persona()
        clientes_empresa = self.banco.obtener_clientes_empresa()
        informe += "CLIENTES\n"
        informe += "-" * 40 + "\n"
        informe += f"CLIENTES PERSONA: {len(clientes_persona)}\n"
        informe += f"CLIENTES EMPRESA: {len(clientes_empresa)}\n"
        informe += f"TOTAL CLIENTES: {len(self.banco.obtener_clientes())}\n\n"
        
        # Totales generales
        saldo_total = self.banco.saldo_total()
        informe += "TOTALES GENERALES\n"
        informe += "-" * 40 + "\n"
        informe += f"SALDO TOTAL: ${saldo_total:.2f}\n"
        informe += f"TOTAL CUENTAS: {len(self.banco.obtener_cuentas())}\n"
        
        self.texto_informe.setPlainText(informe)
    
    def exportar_informe(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exportar Informe", "informe_general.txt", "Text Files (*.txt)"
        )
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.texto_informe.toPlainText())
                QMessageBox.information(self, "Éxito", "Informe exportado correctamente")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo exportar el informe: {str(e)}")

class InformePlazoFijoDialog(QDialog):
    def __init__(self, banco, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Informe de Plazos Fijos")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Tabla de plazos fijos
        self.tabla_plazos_fijos = QTableWidget()
        self.tabla_plazos_fijos.setColumnCount(8)
        self.tabla_plazos_fijos.setHorizontalHeaderLabels([
            "Número", "Cliente", "Fecha Creación", "Fecha Vencimiento", 
            "Capital", "Tasa Interés", "Interés Calculado", "Total"
        ])
        layout.addWidget(self.tabla_plazos_fijos)
        
        # Botones
        buttons_layout = QHBoxLayout()
        actualizar_btn = QPushButton("Actualizar")
        exportar_btn = QPushButton("Exportar a CSV")
        cerrar_btn = QPushButton("Cerrar")
        
        actualizar_btn.clicked.connect(self.cargar_plazos_fijos)
        exportar_btn.clicked.connect(self.exportar_csv)
        cerrar_btn.clicked.connect(self.accept)
        
        buttons_layout.addWidget(actualizar_btn)
        buttons_layout.addWidget(exportar_btn)
        buttons_layout.addWidget(cerrar_btn)
        
        layout.addLayout(buttons_layout)
        
        # Cargar datos iniciales
        self.cargar_plazos_fijos()
    
    def cargar_plazos_fijos(self):
        plazos_fijos = self.banco.obtener_cuentas_plazo_fijo()
        self.tabla_plazos_fijos.setRowCount(len(plazos_fijos))
        
        for i, pf in enumerate(plazos_fijos):
            self.tabla_plazos_fijos.setItem(i, 0, QTableWidgetItem(pf.numero))
            self.tabla_plazos_fijos.setItem(i, 1, QTableWidgetItem(pf.titular.nombre))
            self.tabla_plazos_fijos.setItem(i, 2, QTableWidgetItem(pf.fecha_creacion.strftime("%d/%m/%Y")))
            self.tabla_plazos_fijos.setItem(i, 3, QTableWidgetItem(pf.fecha_vencimiento.strftime("%d/%m/%Y")))
            self.tabla_plazos_fijos.setItem(i, 4, QTableWidgetItem(f"${pf.capital_inicial:.2f}"))
            self.tabla_plazos_fijos.setItem(i, 5, QTableWidgetItem(f"{pf.tasa_interes*100:.2f}%"))
            self.tabla_plazos_fijos.setItem(i, 6, QTableWidgetItem(f"${pf.interes_calculado:.2f}"))
            self.tabla_plazos_fijos.setItem(i, 7, QTableWidgetItem(f"${pf.saldo:.2f}"))
        
        self.tabla_plazos_fijos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def exportar_csv(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV", "plazos_fijos.csv", "CSV Files (*.csv)"
        )
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    # Escribir encabezados
                    headers = []
                    for col in range(self.tabla_plazos_fijos.columnCount()):
                        headers.append(self.tabla_plazos_fijos.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    # Escribir datos
                    for row in range(self.tabla_plazos_fijos.rowCount()):
                        fila = []
                        for col in range(self.tabla_plazos_fijos.columnCount()):
                            item = self.tabla_plazos_fijos.item(row, col)
                            fila.append(item.text() if item else "")
                        writer.writerow(fila)
                
                QMessageBox.information(self, "Éxito", "Datos exportados correctamente")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo exportar: {str(e)}")

class InformeMovimientosDialog(QDialog):
    def __init__(self, banco, db, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.db = db
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Informe de Movimientos")
        self.setModal(True)
        self.resize(900, 600)
        
        layout = QVBoxLayout(self)
        
        # Filtros
        filtros_layout = QHBoxLayout()
        
        self.cuenta_combo = QComboBox()
        self.cuenta_combo.addItem("Todas las cuentas", None)
        for cuenta in self.banco.obtener_cuentas():
            self.cuenta_combo.addItem(f"{cuenta.numero} - {cuenta.titular.nombre}", cuenta.numero)
        
        self.tipo_combo = QComboBox()
        self.tipo_combo.addItem("Todos los tipos", None)
        self.tipo_combo.addItem("Depósito", "DEPOSITO")
        self.tipo_combo.addItem("Extracción", "EXTRACCION")
        self.tipo_combo.addItem("Transferencia", "TRANSFERENCIA")
        self.tipo_combo.addItem("Comisión", "COMISION")
        self.tipo_combo.addItem("Plazo Fijo", "CREACION PF")
        
        self.fecha_desde = QDateEdit()
        self.fecha_desde.setDate(QDate.currentDate().addDays(-30))
        self.fecha_desde.setCalendarPopup(True)
        
        self.fecha_hasta = QDateEdit()
        self.fecha_hasta.setDate(QDate.currentDate())
        self.fecha_hasta.setCalendarPopup(True)
        
        filtros_layout.addWidget(QLabel("Cuenta:"))
        filtros_layout.addWidget(self.cuenta_combo)
        filtros_layout.addWidget(QLabel("Tipo:"))
        filtros_layout.addWidget(self.tipo_combo)
        filtros_layout.addWidget(QLabel("Desde:"))
        filtros_layout.addWidget(self.fecha_desde)
        filtros_layout.addWidget(QLabel("Hasta:"))
        filtros_layout.addWidget(self.fecha_hasta)
        
        layout.addLayout(filtros_layout)
        
        # Botón filtrar
        filtrar_btn = QPushButton("Filtrar")
        filtrar_btn.clicked.connect(self.filtrar_movimientos)
        layout.addWidget(filtrar_btn)
        
        # Tabla de movimientos
        self.tabla_movimientos = QTableWidget()
        self.tabla_movimientos.setColumnCount(5)
        self.tabla_movimientos.setHorizontalHeaderLabels(["Fecha", "Cuenta", "Tipo", "Monto", "Saldo Final"])
        layout.addWidget(self.tabla_movimientos)
        
        # Botón exportar
        exportar_btn = QPushButton("Exportar a CSV")
        exportar_btn.clicked.connect(self.exportar_csv)
        layout.addWidget(exportar_btn)
        
        # Cargar movimientos iniciales
        self.filtrar_movimientos()
    
    def filtrar_movimientos(self):
        cuenta = self.cuenta_combo.currentData()
        tipo = self.tipo_combo.currentData()
        fecha_desde = self.fecha_desde.date().toPyDate()
        fecha_hasta = self.fecha_hasta.date().toPyDate()
        
        movimientos = self.db.cargar_movimientos(cuenta, fecha_desde, fecha_hasta)
        
        if tipo:
            movimientos = [m for m in movimientos if m['tipo'] == tipo]
        
        self.tabla_movimientos.setRowCount(len(movimientos))
        
        for i, mov in enumerate(movimientos):
            self.tabla_movimientos.setItem(i, 0, QTableWidgetItem(mov['fecha'].strftime("%d/%m/%Y %H:%M")))
            self.tabla_movimientos.setItem(i, 1, QTableWidgetItem(mov['numero_cuenta']))
            self.tabla_movimientos.setItem(i, 2, QTableWidgetItem(mov['tipo']))
            
            monto_item = QTableWidgetItem(f"${mov['monto']:.2f}")
            if mov['monto'] < 0:
                # CORRECCIÓN: Usar QColor en lugar de Qt.GlobalColor
                monto_item.setForeground(QColor(255, 0, 0))  # Rojo
            else:
                monto_item.setForeground(QColor(0, 100, 0))  # Verde oscuro
            self.tabla_movimientos.setItem(i, 3, monto_item)
            
            self.tabla_movimientos.setItem(i, 4, QTableWidgetItem(f"${mov['saldo_final']:.2f}"))
        
        self.tabla_movimientos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    
    def exportar_csv(self):
        filename, _ = QFileDialog.getSaveFileName(
            self, "Exportar CSV", "movimientos.csv", "CSV Files (*.csv)"
        )
        if filename:
            try:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Fecha", "Cuenta", "Tipo", "Monto", "Saldo Final"])
                    
                    for row in range(self.tabla_movimientos.rowCount()):
                        fila = []
                        for col in range(self.tabla_movimientos.columnCount()):
                            item = self.tabla_movimientos.item(row, col)
                            fila.append(item.text() if item else "")
                        writer.writerow(fila)
                
                QMessageBox.information(self, "Éxito", "Datos exportados correctamente")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo exportar: {str(e)}")

class ConfiguracionDialog(QDialog):
    def __init__(self, banco, parent=None):
        super().__init__(parent)
        self.banco = banco
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Configuración de Parámetros")
        self.setModal(True)
        self.setFixedSize(400, 300)
        
        layout = QFormLayout(self)
        
        # Tasa de interés para plazos fijos
        self.tasa_interes_input = QDoubleSpinBox()
        self.tasa_interes_input.setMinimum(0.01)
        self.tasa_interes_input.setMaximum(1.0)
        self.tasa_interes_input.setSingleStep(0.01)
        self.tasa_interes_input.setValue(self.banco.tasa_interes_pf)
        self.tasa_interes_input.setSuffix(" % anual")
        
        # Costo de mantenimiento para cuentas corrientes
        self.costo_mantenimiento_input = QDoubleSpinBox()
        self.costo_mantenimiento_input.setMinimum(0)
        self.costo_mantenimiento_input.setMaximum(1000)
        self.costo_mantenimiento_input.setValue(self.banco.costo_mantenimiento_cc)
        self.costo_mantenimiento_input.setPrefix("$ ")
        
        # Comisión por transferencias
        self.comision_transferencia_input = QDoubleSpinBox()
        self.comision_transferencia_input.setMinimum(0)
        self.comision_transferencia_input.setMaximum(500)
        self.comision_transferencia_input.setValue(self.banco.comision_transferencia)
        self.comision_transferencia_input.setPrefix("$ ")
        
        layout.addRow("Tasa de Interés Plazo Fijo:", self.tasa_interes_input)
        layout.addRow("Costo Mantenimiento C.Corriente:", self.costo_mantenimiento_input)
        layout.addRow("Comisión Transferencia Terceros:", self.comision_transferencia_input)
        
        # Botones
        buttons_layout = QHBoxLayout()
        guardar_btn = QPushButton("Guardar")
        cancelar_btn = QPushButton("Cancelar")
        
        guardar_btn.clicked.connect(self.guardar_configuracion)
        cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(guardar_btn)
        buttons_layout.addWidget(cancelar_btn)
        
        layout.addRow(buttons_layout)
    
    def guardar_configuracion(self):
        try:
            self.banco.tasa_interes_pf = self.tasa_interes_input.value()
            self.banco.costo_mantenimiento_cc = self.costo_mantenimiento_input.value()
            self.banco.comision_transferencia = self.comision_transferencia_input.value()
            
            QMessageBox.information(self, "Éxito", "Parámetros actualizados correctamente")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudieron actualizar los parámetros: {str(e)}")