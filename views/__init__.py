# Paquete de vistas
from .main_window import MainWindow
from .clientes_window import (AltaClienteDialog, ListaClientesDialog)
from .cuentas_window import (AltaCuentaDialog, ListaCuentasDialog)
from .movimientos_window import (DepositoDialog, ExtraccionDialog, 
                                TransferenciaDialog, PlazoFijoDialog)
from .informes_window import (InformeGeneralDialog, InformePlazoFijoDialog, 
                             InformeMovimientosDialog, ConfiguracionDialog)

__all__ = [
    'MainWindow',
    'AltaClienteDialog', 'ListaClientesDialog',
    'AltaCuentaDialog', 'ListaCuentasDialog',
    'DepositoDialog', 'ExtraccionDialog', 'TransferenciaDialog', 'PlazoFijoDialog',
    'InformeGeneralDialog', 'InformePlazoFijoDialog', 'InformeMovimientosDialog', 'ConfiguracionDialog'
]