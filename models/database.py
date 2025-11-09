import sqlite3
from datetime import datetime
from typing import List, Dict, Any
from .entidades import Cliente, ClientePersona, ClienteEmpresa, CuentaBase, CajaAhorro, CuentaCorriente, CuentaPlazoFijo
from .banco import Banco  # Importación añadida

class DatabaseManager:
    """Gestor de base de datos SQLite para el sistema bancario"""
    
    def __init__(self, db_path: str = "sistema_bancario.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Inicializa la base de datos con las tablas necesarias"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Tabla de clientes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clientes (
                    dni TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    tipo TEXT NOT NULL
                )
            ''')
            
            # Tabla de cuentas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cuentas (
                    numero TEXT PRIMARY KEY,
                    dni_titular TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    saldo REAL NOT NULL,
                    limite_descubierto REAL,
                    costo_mantenimiento REAL,
                    capital_inicial REAL,
                    tasa_interes REAL,
                    fecha_creacion TEXT,
                    fecha_vencimiento TEXT,
                    FOREIGN KEY (dni_titular) REFERENCES clientes (dni)
                )
            ''')
            
            # Tabla de movimientos
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS movimientos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    numero_cuenta TEXT NOT NULL,
                    fecha TEXT NOT NULL,
                    tipo TEXT NOT NULL,
                    monto REAL NOT NULL,
                    saldo_final REAL NOT NULL,
                    FOREIGN KEY (numero_cuenta) REFERENCES cuentas (numero)
                )
            ''')
            
            conn.commit()
    
    # Métodos para clientes
    def guardar_cliente(self, cliente: Cliente) -> bool:
        """Guarda un cliente en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT OR REPLACE INTO clientes (dni, nombre, tipo) VALUES (?, ?, ?)',
                    (cliente.dni, cliente.nombre, cliente.tipo)
                )
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def cargar_clientes(self) -> List[Cliente]:
        """Carga todos los clientes de la base de datos"""
        clientes = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT dni, nombre, tipo FROM clientes')
                for row in cursor.fetchall():
                    dni, nombre, tipo = row
                    if tipo == "persona":
                        clientes.append(ClientePersona(dni, nombre))
                    else:
                        clientes.append(ClienteEmpresa(dni, nombre))
        except sqlite3.Error:
            pass
        return clientes
    
    def eliminar_cliente(self, dni: str) -> bool:
        """Elimina un cliente de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM clientes WHERE dni = ?', (dni,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    # Métodos para cuentas
    def guardar_cuenta(self, cuenta: CuentaBase) -> bool:
        """Guarda una cuenta en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Determinar tipo de cuenta y parámetros específicos
                tipo_cuenta = ""
                limite_descubierto = None
                costo_mantenimiento = None
                capital_inicial = None
                tasa_interes = None
                fecha_creacion = None
                fecha_vencimiento = None
                
                if isinstance(cuenta, CajaAhorro):
                    tipo_cuenta = "CA"
                elif isinstance(cuenta, CuentaCorriente):
                    tipo_cuenta = "CC"
                    limite_descubierto = cuenta.limite_descubierto
                    costo_mantenimiento = cuenta.costo_mantenimiento()
                elif isinstance(cuenta, CuentaPlazoFijo):
                    tipo_cuenta = "PF"
                    capital_inicial = cuenta.capital_inicial
                    tasa_interes = cuenta.tasa_interes
                    fecha_creacion = cuenta.fecha_creacion.isoformat()
                    fecha_vencimiento = cuenta.fecha_vencimiento.isoformat()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO cuentas 
                    (numero, dni_titular, tipo, saldo, limite_descubierto, costo_mantenimiento, 
                     capital_inicial, tasa_interes, fecha_creacion, fecha_vencimiento)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    cuenta.numero, cuenta.titular.dni, tipo_cuenta, cuenta.saldo,
                    limite_descubierto, costo_mantenimiento, capital_inicial,
                    tasa_interes, fecha_creacion, fecha_vencimiento
                ))
                
                conn.commit()
                return True
        except sqlite3.Error:
            return False
    
    def cargar_cuentas(self, banco: Banco) -> List[CuentaBase]:  # CORREGIDO: Banco ahora está importado
        """Carga todas las cuentas de la base de datos"""
        cuentas = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT c.numero, c.dni_titular, c.tipo, c.saldo, c.limite_descubierto,
                           c.costo_mantenimiento, c.capital_inicial, c.tasa_interes,
                           c.fecha_creacion, c.fecha_vencimiento, cl.nombre, cl.tipo as cliente_tipo
                    FROM cuentas c
                    JOIN clientes cl ON c.dni_titular = cl.dni
                ''')
                
                for row in cursor.fetchall():
                    (numero, dni_titular, tipo_cuenta, saldo, limite_descubierto,
                     costo_mantenimiento, capital_inicial, tasa_interes,
                     fecha_creacion, fecha_vencimiento, nombre_cliente, tipo_cliente) = row
                    
                    # Crear cliente
                    if tipo_cliente == "persona":
                        cliente = ClientePersona(dni_titular, nombre_cliente)
                    else:
                        cliente = ClienteEmpresa(dni_titular, nombre_cliente)
                    
                    # Crear cuenta según tipo
                    if tipo_cuenta == "CA":
                        cuenta = CajaAhorro(numero, cliente, saldo)
                    elif tipo_cuenta == "CC":
                        cuenta = CuentaCorriente(numero, cliente, limite_descubierto or 1000.0, 
                                               costo_mantenimiento or 50.0, saldo)
                    elif tipo_cuenta == "PF":
                        fecha_creacion_dt = datetime.fromisoformat(fecha_creacion)
                        fecha_vencimiento_dt = datetime.fromisoformat(fecha_vencimiento)
                        # Calcular días de plazo
                        plazo_dias = (fecha_vencimiento_dt - fecha_creacion_dt).days
                        cuenta = CuentaPlazoFijo(numero, cliente, capital_inicial or saldo,
                                               tasa_interes or 0.10, plazo_dias)
                        cuenta._fecha_creacion = fecha_creacion_dt
                        cuenta._fecha_vencimiento = fecha_vencimiento_dt
                    
                    cuentas.append(cuenta)
                    banco.alta_cuenta(cuenta)
                    
        except sqlite3.Error as e:
            print(f"Error cargando cuentas: {e}")
        
        return cuentas
    
    def eliminar_cuenta(self, numero: str) -> bool:
        """Elimina una cuenta de la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM cuentas WHERE numero = ?', (numero,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False
    
    # Métodos para movimientos
    def guardar_movimiento(self, numero_cuenta: str, tipo: str, monto: float, saldo_final: float):
        """Guarda un movimiento en la base de datos"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO movimientos (numero_cuenta, fecha, tipo, monto, saldo_final)
                    VALUES (?, ?, ?, ?, ?)
                ''', (numero_cuenta, datetime.now().isoformat(), tipo, monto, saldo_final))
                conn.commit()
        except sqlite3.Error:
            pass
    
    def cargar_movimientos(self, numero_cuenta: str = None, fecha_desde: datetime = None, 
                          fecha_hasta: datetime = None) -> List[Dict[str, Any]]:
        """Carga movimientos con filtros opcionales"""
        movimientos = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                query = '''
                    SELECT numero_cuenta, fecha, tipo, monto, saldo_final 
                    FROM movimientos 
                    WHERE 1=1
                '''
                params = []
                
                if numero_cuenta:
                    query += ' AND numero_cuenta = ?'
                    params.append(numero_cuenta)
                
                if fecha_desde:
                    query += ' AND fecha >= ?'
                    params.append(fecha_desde.isoformat())
                
                if fecha_hasta:
                    query += ' AND fecha <= ?'
                    params.append(fecha_hasta.isoformat())
                
                query += ' ORDER BY fecha DESC'
                
                cursor.execute(query, params)
                
                for row in cursor.fetchall():
                    numero_cuenta, fecha_str, tipo, monto, saldo_final = row
                    movimientos.append({
                        'numero_cuenta': numero_cuenta,
                        'fecha': datetime.fromisoformat(fecha_str),
                        'tipo': tipo,
                        'monto': monto,
                        'saldo_final': saldo_final
                    })
                    
        except sqlite3.Error:
            pass
        
        return movimientos