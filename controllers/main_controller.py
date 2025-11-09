from PyQt6.QtCore import QObject, pyqtSignal
from models.banco import Banco
from models.database import DatabaseManager
from models.entidades import (ClientePersona, ClienteEmpresa, 
                             CajaAhorro, CuentaCorriente, CuentaPlazoFijo)
from datetime import datetime
import csv

class MainController(QObject):
    """
    Controlador principal que coordina entre modelos y vistas
    Maneja la lógica de negocio y las operaciones del sistema
    """
    
    # Señales para actualizar la UI
    datos_actualizados = pyqtSignal()
    error_occurred = pyqtSignal(str)
    operacion_exitosa = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.banco = Banco()
        self.db = DatabaseManager()
        self.cargar_datos_iniciales()
    
    def cargar_datos_iniciales(self):
        """Carga los datos iniciales desde la base de datos"""
        try:
            # Cargar clientes
            clientes = self.db.cargar_clientes()
            for cliente in clientes:
                self.banco.alta_cliente(cliente)
            
            # Cargar cuentas
            self.db.cargar_cuentas(self.banco)
            
            self.datos_actualizados.emit()
            
        except Exception as e:
            self.error_occurred.emit(f"Error cargando datos: {str(e)}")
    
    # Operaciones con Clientes
    def alta_cliente(self, dni: str, nombre: str, tipo: str) -> bool:
        """Da de alta un nuevo cliente"""
        try:
            if not dni or not nombre:
                self.error_occurred.emit("DNI y Nombre son obligatorios")
                return False
            
            if tipo == "persona":
                cliente = ClientePersona(dni, nombre)
            else:
                cliente = ClienteEmpresa(dni, nombre)
            
            if self.banco.alta_cliente(cliente) and self.db.guardar_cliente(cliente):
                self.operacion_exitosa.emit(f"Cliente {nombre} agregado exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                self.error_occurred.emit("El cliente ya existe")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error al agregar cliente: {str(e)}")
            return False
    
    def baja_cliente(self, dni: str) -> bool:
        """Da de baja un cliente"""
        try:
            cliente = self.banco.buscar_cliente(dni)
            if not cliente:
                self.error_occurred.emit("Cliente no encontrado")
                return False
            
            # Verificar que el cliente no tenga cuentas
            cuentas_cliente = self.banco.obtener_cuentas_por_cliente(dni)
            if cuentas_cliente:
                self.error_occurred.emit("No se puede eliminar un cliente con cuentas activas")
                return False
            
            if self.banco.baja_cliente(dni) and self.db.eliminar_cliente(dni):
                self.operacion_exitosa.emit("Cliente eliminado exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                self.error_occurred.emit("Error al eliminar el cliente")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error al eliminar cliente: {str(e)}")
            return False
    
    def obtener_clientes(self):
        """Obtiene todos los clientes"""
        return self.banco.obtener_clientes()
    
    def obtener_cliente_por_dni(self, dni: str):
        """Busca un cliente por DNI"""
        return self.banco.buscar_cliente(dni)
    
    # Operaciones con Cuentas
    def alta_cuenta(self, numero: str, dni_titular: str, tipo: str, 
                   saldo_inicial: float = 0, **kwargs) -> bool:
        """Da de alta una nueva cuenta"""
        try:
            if not numero:
                self.error_occurred.emit("El número de cuenta es obligatorio")
                return False
            
            cliente = self.banco.buscar_cliente(dni_titular)
            if not cliente:
                self.error_occurred.emit("Cliente no encontrado")
                return False
            
            if tipo == "Caja Ahorro":
                cuenta = CajaAhorro(numero, cliente, saldo_inicial)
            elif tipo == "Cuenta Corriente":
                limite_descubierto = kwargs.get('limite_descubierto', 1000.0)
                cuenta = CuentaCorriente(numero, cliente, limite_descubierto, 
                                       self.banco.costo_mantenimiento_cc, saldo_inicial)
            elif tipo == "Plazo Fijo":
                plazo_dias = kwargs.get('plazo_dias', 30)
                cuenta = CuentaPlazoFijo(numero, cliente, saldo_inicial, 
                                       self.banco.tasa_interes_pf, plazo_dias)
            else:
                self.error_occurred.emit("Tipo de cuenta no válido")
                return False
            
            if self.banco.alta_cuenta(cuenta) and self.db.guardar_cuenta(cuenta):
                self.operacion_exitosa.emit(f"Cuenta {numero} creada exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                self.error_occurred.emit("La cuenta ya existe")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error al crear cuenta: {str(e)}")
            return False
    
    def baja_cuenta(self, numero: str) -> bool:
        """Da de baja una cuenta"""
        try:
            cuenta = self.banco.buscar_cuenta(numero)
            if not cuenta:
                self.error_occurred.emit("Cuenta no encontrada")
                return False
            
            if self.banco.baja_cuenta(numero) and self.db.eliminar_cuenta(numero):
                self.operacion_exitosa.emit("Cuenta eliminada exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                self.error_occurred.emit("Error al eliminar la cuenta")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error al eliminar cuenta: {str(e)}")
            return False
    
    def obtener_cuentas(self):
        """Obtiene todas las cuentas"""
        return self.banco.obtener_cuentas()
    
    def obtener_cuenta_por_numero(self, numero: str):
        """Busca una cuenta por número"""
        return self.banco.buscar_cuenta(numero)
    
    def obtener_cuentas_por_cliente(self, dni: str):
        """Obtiene las cuentas de un cliente"""
        return self.banco.obtener_cuentas_por_cliente(dni)
    
    # Operaciones Bancarias
    def depositar(self, numero_cuenta: str, monto: float) -> bool:
        """Realiza un depósito en una cuenta"""
        try:
            if monto <= 0:
                self.error_occurred.emit("El monto debe ser mayor a cero")
                return False
            
            cuenta = self.banco.buscar_cuenta(numero_cuenta)
            if not cuenta:
                self.error_occurred.emit("Cuenta no encontrada")
                return False
            
            if cuenta.depositar(monto):
                self.db.guardar_cuenta(cuenta)
                self.db.guardar_movimiento(numero_cuenta, "DEPOSITO", monto, cuenta.saldo)
                self.operacion_exitosa.emit(f"Depósito de ${monto:.2f} realizado exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                self.error_occurred.emit("Error al realizar el depósito")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error en depósito: {str(e)}")
            return False
    
    def extraer(self, numero_cuenta: str, monto: float) -> bool:
        """Realiza una extracción de una cuenta"""
        try:
            if monto <= 0:
                self.error_occurred.emit("El monto debe ser mayor a cero")
                return False
            
            cuenta = self.banco.buscar_cuenta(numero_cuenta)
            if not cuenta:
                self.error_occurred.emit("Cuenta no encontrada")
                return False
            
            if cuenta.extraer(monto):
                self.db.guardar_cuenta(cuenta)
                self.db.guardar_movimiento(numero_cuenta, "EXTRACCION", -monto, cuenta.saldo)
                self.operacion_exitosa.emit(f"Extracción de ${monto:.2f} realizada exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                self.error_occurred.emit("Fondos insuficientes para la extracción")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error en extracción: {str(e)}")
            return False
    
    def transferir(self, cuenta_origen: str, cuenta_destino: str, monto: float) -> bool:
        """Realiza una transferencia entre cuentas"""
        try:
            if monto <= 0:
                self.error_occurred.emit("El monto debe ser mayor a cero")
                return False
            
            if cuenta_origen == cuenta_destino:
                self.error_occurred.emit("No puede transferir a la misma cuenta")
                return False
            
            if self.banco.transferir(cuenta_origen, cuenta_destino, monto):
                # Actualizar ambas cuentas en la base de datos
                cuenta_origen_obj = self.banco.buscar_cuenta(cuenta_origen)
                cuenta_destino_obj = self.banco.buscar_cuenta(cuenta_destino)
                
                self.db.guardar_cuenta(cuenta_origen_obj)
                self.db.guardar_cuenta(cuenta_destino_obj)
                
                self.operacion_exitosa.emit(f"Transferencia de ${monto:.2f} realizada exitosamente")
                self.datos_actualizados.emit()
                return True
            else:
                self.error_occurred.emit("Fondos insuficientes para la transferencia")
                return False
                
        except Exception as e:
            self.error_occurred.emit(f"Error en transferencia: {str(e)}")
            return False
    
    def crear_plazo_fijo(self, cuenta_origen: str, capital: float, plazo_dias: int) -> str:
        """Crea un plazo fijo desde una cuenta origen"""
        try:
            if capital <= 0:
                self.error_occurred.emit("El capital debe ser mayor a cero")
                return ""
            
            cuenta_origen_obj = self.banco.buscar_cuenta(cuenta_origen)
            if not cuenta_origen_obj:
                self.error_occurred.emit("Cuenta origen no encontrada")
                return ""
            
            if capital > cuenta_origen_obj.saldo:
                self.error_occurred.emit("Fondos insuficientes en la cuenta origen")
                return ""
            
            # Extraer capital de la cuenta origen
            if not cuenta_origen_obj.extraer(capital):
                self.error_occurred.emit("No se pudo extraer el capital de la cuenta origen")
                return ""
            
            # Generar número de cuenta para el plazo fijo
            numero_pf = f"PF{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            # Crear cuenta a plazo fijo
            plazo_fijo = CuentaPlazoFijo(
                numero_pf, 
                cuenta_origen_obj.titular, 
                capital, 
                self.banco.tasa_interes_pf, 
                plazo_dias
            )
            
            # Registrar en el banco y base de datos
            if self.banco.alta_cuenta(plazo_fijo):
                self.db.guardar_cuenta(cuenta_origen_obj)
                self.db.guardar_cuenta(plazo_fijo)
                self.db.guardar_movimiento(cuenta_origen, "CREACION PF", -capital, cuenta_origen_obj.saldo)
                
                self.operacion_exitosa.emit(f"Plazo fijo {numero_pf} creado exitosamente")
                self.datos_actualizados.emit()
                return numero_pf
            else:
                # Revertir la extracción si falla la creación del plazo fijo
                cuenta_origen_obj.depositar(capital)
                self.error_occurred.emit("No se pudo crear el plazo fijo")
                return ""
                
        except Exception as e:
            self.error_occurred.emit(f"Error creando plazo fijo: {str(e)}")
            return ""
    
    # Informes y Estadísticas
    def generar_informe_general(self) -> dict:
        """Genera un informe general del banco"""
        try:
            informe = {
                'total_clientes': len(self.banco.obtener_clientes()),
                'clientes_persona': len(self.banco.obtener_clientes_persona()),
                'clientes_empresa': len(self.banco.obtener_clientes_empresa()),
                'total_cuentas': len(self.banco.obtener_cuentas()),
                'cajas_ahorro': len(self.banco.obtener_cajas_ahorro()),
                'cuentas_corriente': len(self.banco.obtener_cuentas_corriente()),
                'plazos_fijos': len(self.banco.obtener_cuentas_plazo_fijo()),
                'saldo_total': self.banco.saldo_total(),
                'saldo_cajas_ahorro': self.banco.saldo_total_cajas_ahorro(),
                'saldo_cuentas_corriente': self.banco.saldo_total_cuentas_corriente(),
                'saldo_plazos_fijos': self.banco.saldo_total_plazo_fijo(),
                'total_descubierto': self.banco.total_descubierto()
            }
            return informe
        except Exception as e:
            self.error_occurred.emit(f"Error generando informe: {str(e)}")
            return {}
    
    def generar_informe_plazos_fijos(self):
        """Genera informe detallado de plazos fijos"""
        return self.banco.obtener_cuentas_plazo_fijo()
    
    def obtener_movimientos(self, numero_cuenta: str = None, 
                          fecha_desde: datetime = None, 
                          fecha_hasta: datetime = None,
                          tipo_movimiento: str = None):
        """Obtiene movimientos con filtros opcionales"""
        try:
            movimientos = self.db.cargar_movimientos(numero_cuenta, fecha_desde, fecha_hasta)
            
            if tipo_movimiento:
                movimientos = [m for m in movimientos if m['tipo'] == tipo_movimiento]
            
            return movimientos
        except Exception as e:
            self.error_occurred.emit(f"Error obteniendo movimientos: {str(e)}")
            return []
    
    def exportar_movimientos_csv(self, movimientos, filename: str) -> bool:
        """Exporta movimientos a archivo CSV"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["Fecha", "Cuenta", "Tipo", "Monto", "Saldo Final"])
                
                for mov in movimientos:
                    writer.writerow([
                        mov['fecha'].strftime("%d/%m/%Y %H:%M"),
                        mov['numero_cuenta'],
                        mov['tipo'],
                        f"${mov['monto']:.2f}",
                        f"${mov['saldo_final']:.2f}"
                    ])
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error exportando CSV: {str(e)}")
            return False
    
    # Configuración de Parámetros
    def actualizar_parametros(self, tasa_interes: float, costo_mantenimiento: float, 
                             comision_transferencia: float) -> bool:
        """Actualiza los parámetros del sistema"""
        try:
            self.banco.tasa_interes_pf = tasa_interes
            self.banco.costo_mantenimiento_cc = costo_mantenimiento
            self.banco.comision_transferencia = comision_transferencia
            
            self.operacion_exitosa.emit("Parámetros actualizados exitosamente")
            return True
        except Exception as e:
            self.error_occurred.emit(f"Error actualizando parámetros: {str(e)}")
            return False
    
    def obtener_parametros(self) -> dict:
        """Obtiene los parámetros actuales del sistema"""
        return {
            'tasa_interes': self.banco.tasa_interes_pf,
            'costo_mantenimiento': self.banco.costo_mantenimiento_cc,
            'comision_transferencia': self.banco.comision_transferencia
        }
    
    # Métodos de utilidad
    def calcular_interes_plazo_fijo(self, capital: float, plazo_dias: int) -> float:
        """Calcula el interés de un plazo fijo"""
        tasa_anual = self.banco.tasa_interes_pf
        return capital * tasa_anual * plazo_dias / 365
    
    def verificar_disponibilidad_extraccion(self, numero_cuenta: str, monto: float) -> bool:
        """Verifica si se puede extraer un monto de una cuenta"""
        cuenta = self.banco.buscar_cuenta(numero_cuenta)
        if not cuenta:
            return False
        return cuenta.puede_extraer(monto)
    
    def obtener_comision_transferencia(self, cuenta_origen: str, cuenta_destino: str) -> float:
        """Calcula la comisión por transferencia entre cuentas"""
        cuenta_origen_obj = self.banco.buscar_cuenta(cuenta_origen)
        cuenta_destino_obj = self.banco.buscar_cuenta(cuenta_destino)
        
        if not cuenta_origen_obj or not cuenta_destino_obj:
            return 0.0
        
        if cuenta_origen_obj.titular.dni != cuenta_destino_obj.titular.dni:
            return self.banco.comision_transferencia
        else:
            return 0.0