from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Optional

class Cliente:
    """Clase base para todos los clientes del banco"""
    def __init__(self, dni: str, nombre: str, tipo: str = "persona"):
        self._dni = dni
        self._nombre = nombre
        self._tipo = tipo
    
    @property
    def dni(self) -> str:
        return self._dni
    
    @property
    def nombre(self) -> str:
        return self._nombre
    
    @property
    def tipo(self) -> str:
        return self._tipo
    
    def __str__(self):
        return f"{self.nombre} ({self.dni}) - {self.tipo}"

class ClientePersona(Cliente):
    """Cliente persona física"""
    def __init__(self, dni: str, nombre: str):
        super().__init__(dni, nombre, "persona")

class ClienteEmpresa(Cliente):
    """Cliente empresa"""
    def __init__(self, dni: str, nombre: str):
        super().__init__(dni, nombre, "empresa")

class CuentaBase(ABC):
    """Clase abstracta base para todas las cuentas"""
    def __init__(self, numero: str, titular: Cliente, saldo: float = 0.0):
        self._numero = numero
        self._titular = titular
        self._saldo = saldo
        self._movimientos = []
    
    @property
    def numero(self) -> str:
        return self._numero
    
    @property
    def titular(self) -> Cliente:
        return self._titular
    
    @property
    def saldo(self) -> float:
        return self._saldo
    
    def depositar(self, monto: float) -> bool:
        """Deposita un monto en la cuenta"""
        if monto <= 0:
            return False
        
        self._saldo += monto
        self._registrar_movimiento("DEPOSITO", monto)
        return True
    
    def extraer(self, monto: float) -> bool:
        """Extrae un monto de la cuenta si es posible"""
        if monto <= 0 or not self.puede_extraer(monto):
            return False
        
        self._saldo -= monto
        self._registrar_movimiento("EXTRACCION", -monto)
        return True
    
    def transferir(self, destino: 'CuentaBase', monto: float) -> bool:
        """Transfiere un monto a otra cuenta"""
        if monto <= 0 or not self.puede_extraer(monto):
            return False
        
        self._saldo -= monto
        destino.depositar(monto)
        self._registrar_movimiento(f"TRANSFERENCIA A {destino.numero}", -monto)
        destino._registrar_movimiento(f"TRANSFERENCIA DE {self.numero}", monto)
        return True
    
    def _registrar_movimiento(self, tipo: str, monto: float):
        """Registra un movimiento en la cuenta"""
        movimiento = {
            'fecha': datetime.now(),
            'tipo': tipo,
            'monto': monto,
            'saldo_final': self._saldo
        }
        self._movimientos.append(movimiento)
    
    @abstractmethod
    def puede_extraer(self, monto: float) -> bool:
        """Verifica si se puede extraer el monto"""
        pass
    
    @abstractmethod
    def costo_mantenimiento(self) -> float:
        """Calcula el costo de mantenimiento"""
        pass
    
    def obtener_movimientos(self, fecha_desde: datetime = None, fecha_hasta: datetime = None) -> List[dict]:
        """Obtiene movimientos filtrados por fecha"""
        movimientos_filtrados = self._movimientos
        
        if fecha_desde:
            movimientos_filtrados = [m for m in movimientos_filtrados if m['fecha'] >= fecha_desde]
        if fecha_hasta:
            movimientos_filtrados = [m for m in movimientos_filtrados if m['fecha'] <= fecha_hasta]
        
        return movimientos_filtrados

class CajaAhorro(CuentaBase):
    """Caja de ahorro que no permite saldo negativo"""
    def __init__(self, numero: str, titular: Cliente, saldo: float = 0.0):
        super().__init__(numero, titular, saldo)
    
    def puede_extraer(self, monto: float) -> bool:
        return self._saldo >= monto
    
    def costo_mantenimiento(self) -> float:
        costo_base = 0.0  # Sin costo para caja de ahorro
        if self.titular.tipo == "empresa":
            return costo_base * 0.9  # 10% de descuento
        return costo_base

class CuentaCorriente(CuentaBase):
    """Cuenta corriente con descubierto permitido"""
    def __init__(self, numero: str, titular: Cliente, limite_descubierto: float = 1000.0, 
                 costo_mantenimiento: float = 50.0, saldo: float = 0.0):
        super().__init__(numero, titular, saldo)
        self._limite_descubierto = limite_descubierto
        self._costo_mantenimiento_base = costo_mantenimiento
    
    def puede_extraer(self, monto: float) -> bool:
        return (self._saldo + self._limite_descubierto) >= monto
    
    def costo_mantenimiento(self) -> float:
        costo = self._costo_mantenimiento_base
        if self.titular.tipo == "empresa":
            costo *= 0.9  # 10% de descuento
        return costo
    
    @property
    def limite_descubierto(self) -> float:
        return self._limite_descubierto
    
    @property
    def descubierto_utilizado(self) -> float:
        return max(0, -self._saldo)

class CuentaPlazoFijo(CuentaBase):
    """Cuenta a plazo fijo con vencimiento"""
    def __init__(self, numero: str, titular: Cliente, capital: float, 
                 tasa_interes_anual: float = 0.10, plazo_dias: int = 30):
        super().__init__(numero, titular, capital)
        self._capital_inicial = capital
        self._tasa_interes_anual = tasa_interes_anual
        self._fecha_creacion = datetime.now()
        self._fecha_vencimiento = self._fecha_creacion + timedelta(days=plazo_dias)
        self._interes_acumulado = 0.0
    
    def puede_extraer(self, monto: float) -> bool:
        # No permite extracciones antes del vencimiento
        return datetime.now() >= self._fecha_vencimiento and self._saldo >= monto
    
    def costo_mantenimiento(self) -> float:
        return 0.0  # Sin costo de mantenimiento
    
    def acreditar_interes(self):
        """Acredita el interés mensual a la cuenta"""
        if datetime.now() >= self._fecha_vencimiento:
            # Calcular interés total
            meses = (self._fecha_vencimiento - self._fecha_creacion).days / 30.0
            interes = self._capital_inicial * self._tasa_interes_anual * meses / 12
            self._saldo = self._capital_inicial + interes
            self._interes_acumulado = interes
    
    @property
    def fecha_creacion(self) -> datetime:
        return self._fecha_creacion
    
    @property
    def fecha_vencimiento(self) -> datetime:
        return self._fecha_vencimiento
    
    @property
    def tasa_interes(self) -> float:
        return self._tasa_interes_anual
    
    @property
    def interes_calculado(self) -> float:
        return self._interes_acumulado
    
    @property
    def capital_inicial(self) -> float:
        return self._capital_inicial