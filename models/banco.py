from typing import List, Dict, Optional
from .entidades import Cliente, CuentaBase, CajaAhorro, CuentaCorriente, CuentaPlazoFijo

class Banco:
    """Clase que administra clientes y cuentas del sistema bancario"""
    
    def __init__(self):
        self._clientes: Dict[str, Cliente] = {}
        self._cuentas: Dict[str, CuentaBase] = {}
        self._comision_transferencia = 50.0
        self._tasa_interes_pf = 0.10
        self._costo_mantenimiento_cc = 50.0
    
    # Métodos para clientes
    def alta_cliente(self, cliente: Cliente) -> bool:
        """Da de alta un nuevo cliente"""
        if cliente.dni in self._clientes:
            return False
        self._clientes[cliente.dni] = cliente
        return True
    
    def baja_cliente(self, dni: str) -> bool:
        """Da de baja un cliente"""
        if dni not in self._clientes:
            return False
        
        # Verificar que el cliente no tenga cuentas activas
        cuentas_cliente = self.obtener_cuentas_por_cliente(dni)
        if cuentas_cliente:
            return False
        
        del self._clientes[dni]
        return True
    
    def buscar_cliente(self, dni: str) -> Optional[Cliente]:
        """Busca un cliente por DNI"""
        return self._clientes.get(dni)
    
    def obtener_clientes(self) -> List[Cliente]:
        """Obtiene todos los clientes"""
        return list(self._clientes.values())
    
    def obtener_clientes_persona(self) -> List[Cliente]:
        """Obtiene solo clientes persona"""
        return [c for c in self._clientes.values() if c.tipo == "persona"]
    
    def obtener_clientes_empresa(self) -> List[Cliente]:
        """Obtiene solo clientes empresa"""
        return [c for c in self._clientes.values() if c.tipo == "empresa"]
    
    # Métodos para cuentas
    def alta_cuenta(self, cuenta: CuentaBase) -> bool:
        """Da de alta una nueva cuenta"""
        if cuenta.numero in self._cuentas:
            return False
        self._cuentas[cuenta.numero] = cuenta
        return True
    
    def baja_cuenta(self, numero: str) -> bool:
        """Da de baja una cuenta"""
        if numero not in self._cuentas:
            return False
        del self._cuentas[numero]
        return True
    
    def buscar_cuenta(self, numero: str) -> Optional[CuentaBase]:
        """Busca una cuenta por número"""
        return self._cuentas.get(numero)
    
    def obtener_cuentas(self) -> List[CuentaBase]:
        """Obtiene todas las cuentas"""
        return list(self._cuentas.values())
    
    def obtener_cuentas_por_cliente(self, dni: str) -> List[CuentaBase]:
        """Obtiene las cuentas de un cliente"""
        return [c for c in self._cuentas.values() if c.titular.dni == dni]
    
    def obtener_cajas_ahorro(self) -> List[CajaAhorro]:
        """Obtiene todas las cajas de ahorro"""
        return [c for c in self._cuentas.values() if isinstance(c, CajaAhorro)]
    
    def obtener_cuentas_corriente(self) -> List[CuentaCorriente]:
        """Obtiene todas las cuentas corrientes"""
        return [c for c in self._cuentas.values() if isinstance(c, CuentaCorriente)]
    
    def obtener_cuentas_plazo_fijo(self) -> List[CuentaPlazoFijo]:
        """Obtiene todas las cuentas a plazo fijo"""
        return [c for c in self._cuentas.values() if isinstance(c, CuentaPlazoFijo)]
    
    # Operaciones bancarias
    def depositar(self, numero_cuenta: str, monto: float) -> bool:
        """Realiza un depósito en una cuenta"""
        cuenta = self.buscar_cuenta(numero_cuenta)
        if not cuenta:
            return False
        return cuenta.depositar(monto)
    
    def extraer(self, numero_cuenta: str, monto: float) -> bool:
        """Realiza una extracción de una cuenta"""
        cuenta = self.buscar_cuenta(numero_cuenta)
        if not cuenta:
            return False
        return cuenta.extraer(monto)
    
    def transferir(self, nro_origen: str, nro_destino: str, monto: float) -> bool:
        """Realiza una transferencia entre cuentas"""
        cuenta_origen = self.buscar_cuenta(nro_origen)
        cuenta_destino = self.buscar_cuenta(nro_destino)
        
        if not cuenta_origen or not cuenta_destino:
            return False
        
        # Verificar si las cuentas son de distintos titulares
        comision = 0.0
        if cuenta_origen.titular.dni != cuenta_destino.titular.dni:
            comision = self._comision_transferencia
        
        # Aplicar transferencia con comisión si corresponde
        if cuenta_origen.puede_extraer(monto + comision):
            if comision > 0:
                cuenta_origen.extraer(comision)
                cuenta_origen._registrar_movimiento("COMISION TRANSFERENCIA", -comision)
            
            return cuenta_origen.transferir(cuenta_destino, monto)
        
        return False
    
    # Métodos para informes
    def saldo_total(self) -> float:
        """Calcula el saldo total de todas las cuentas"""
        return sum(cuenta.saldo for cuenta in self._cuentas.values())
    
    def saldo_total_cajas_ahorro(self) -> float:
        """Calcula el saldo total de cajas de ahorro"""
        return sum(caja.saldo for caja in self.obtener_cajas_ahorro())
    
    def saldo_total_cuentas_corriente(self) -> float:
        """Calcula el saldo total de cuentas corrientes"""
        return sum(cc.saldo for cc in self.obtener_cuentas_corriente())
    
    def saldo_total_plazo_fijo(self) -> float:
        """Calcula el saldo total de plazos fijos"""
        return sum(pf.saldo for pf in self.obtener_cuentas_plazo_fijo())
    
    def total_descubierto(self) -> float:
        """Calcula el total en descubierto"""
        return sum(cc.descubierto_utilizado for cc in self.obtener_cuentas_corriente())
    
    # Parámetros configurables
    @property
    def comision_transferencia(self) -> float:
        return self._comision_transferencia
    
    @comision_transferencia.setter
    def comision_transferencia(self, valor: float):
        self._comision_transferencia = valor
    
    @property
    def tasa_interes_pf(self) -> float:
        return self._tasa_interes_pf
    
    @tasa_interes_pf.setter
    def tasa_interes_pf(self, valor: float):
        self._tasa_interes_pf = valor
    
    @property
    def costo_mantenimiento_cc(self) -> float:
        return self._costo_mantenimiento_cc
    
    @costo_mantenimiento_cc.setter
    def costo_mantenimiento_cc(self, valor: float):
        self._costo_mantenimiento_cc = valor