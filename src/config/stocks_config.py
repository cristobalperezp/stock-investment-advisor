"""
Configuración normalizada de acciones chilenas
Basado en analyst_2.ipynb y sistema de investment_analyzer
"""

# Lista completa de acciones chilenas por sectores (basada en analyst_2.ipynb)
CHILEAN_STOCKS_BY_SECTOR = {
    # Banca y Servicios Financieros
    "Banca": [
        "BSANTANDER.SN",  # Banco Santander Chile
        "BCI.SN",         # Banco de Crédito e Inversiones  
        "CHILE.SN",       # Banco de Chile
        "BICECORP.SN",     # Bice Corp
        "ITAU.SN",         # Itaú Corpbanca
        "BCI.SN"         # Banco de Crédito e Inversiones (repetido para asegurar inclusión)
    ],
    
    # Retail y Consumo
    "Retail": [
        "FALABELLA.SN",   # Falabella
        "RIPLEY.SN",      # Ripley
        "CENCOSUD.SN",    # Cencosud
        "FORUS.SN",       # Forus
        "SMU.SN",         # SMU
        "TRICOT.SN"       # Tricot
    ],
    
    # Energía y Servicios Públicos
    "Energía y Utilities": [
        "ENELCHILE.SN",   # Enel Chile
        "COLBUN.SN",      # Colbún
        "AGUAS-A.SN",     # Aguas Andinas
        "GASCO.SN",       # Gasco
        "COPEC.SN",        # Copec
        "ECL.SN"          # Engie Chile
    ],
    
    # Embotellados y Bebidas
    "Embotellados": [
        "EMBONOR-B.SN",   # Embotelladora Andina
        "CONCHATORO.SN",  # Concha y Toro
        "CCU.SN"          # CCU
    ],
    
    # AFP y Seguros
    "AFP": [
        "HABITAT.SN",     # AFP Habitat
        "PROVIDA.SN",     # AFP Provida
        "PLANVITAL.SN"    # AFP PlanVital
    ],
    
    # Inmobiliario
    "Inmobiliario": [
        "CENCOMALLS.SN",  # Cencosud Shopping
        "MALLPLAZA.SN",   # Mall Plaza
        "PARAUCO.SN"      # Parauco
    ],
    
    # Transporte y Logística
    "Transporte": [
        "LTM.SN"          # LATAM Airlines
    ],
    
    # Minería y Materiales
    "Minería": [
        "SQM-B.SN"        # SQM
    ],
    
    # Forestal y Papel
    "Forestal": [
        "CMPC.SN"         # CMPC
    ]
}

# Lista plana de todas las acciones (para compatibilidad)
ALL_CHILEAN_STOCKS = []
for sector_stocks in CHILEAN_STOCKS_BY_SECTOR.values():
    ALL_CHILEAN_STOCKS.extend(sector_stocks)

# Mapeo de símbolos a nombres para display
STOCK_NAMES = {
    # Banca
    "BSANTANDER.SN": "Banco Santander Chile",
    "BCI.SN": "BCI - Banco de Crédito e Inversiones", 
    "CHILE.SN": "Banco de Chile",
    "BICECORP.SN": "Bice Corp",
    "ITAU.SN": "Itaú Corpbanca",
    "BCI.SN": "Banco de Crédito e Inversiones",  # Repetido para asegurar inclusión
    
    # Retail
    "FALABELLA.SN": "Falabella",
    "RIPLEY.SN": "Ripley",
    "CENCOSUD.SN": "Cencosud", 
    "FORUS.SN": "Forus",
    "SMU.SN": "SMU",
    "TRICOT.SN": "Tricot",
    
    # Energía
    "ENELCHILE.SN": "Enel Chile",
    "COLBUN.SN": "Colbún", 
    "AGUAS-A.SN": "Aguas Andinas",
    "GASCO.SN": "Gasco",
    "COPEC.SN": "Empresas Copec",
    "ECL.SN": "Engie Chile",
    
    # Embotellados
    "EMBONOR-B.SN": "Embotelladora Andina",
    "CONCHATORO.SN": "Concha y Toro",
    "CCU.SN": "CCU",
    
    # AFP
    "HABITAT.SN": "AFP Habitat", 
    "PROVIDA.SN": "AFP Provida",
    "PLANVITAL.SN": "AFP PlanVital",
    
    # Inmobiliario
    "CENCOMALLS.SN": "Cencosud Shopping",
    "MALLPLAZA.SN": "Mall Plaza", 
    "PARAUCO.SN": "Parauco",
    
    # Transporte
    "LTM.SN": "LATAM Airlines",
    
    # Minería
    "SQM-B.SN": "SQM",
    
    # Forestal
    "CMPC.SN": "CMPC"
}

# Configuración por defecto para análisis
DEFAULT_ANALYSIS_CONFIG = {
    "top_stocks_count": 5,        # Número de acciones TOP a analizar
    "budget": 5000000,            # Presupuesto por defecto en CLP
    "min_stocks": 3,              # Mínimo de acciones para diversificación
    "max_stocks": 10,             # Máximo de acciones a considerar
    "investment_horizon": "medium", # corto, medium, largo
    "risk_level": "moderado"      # conservador, moderado, agresivo
}

def get_stocks_by_sector(sector: str = None):
    """
    Obtiene acciones por sector
    Args:
        sector: Nombre del sector (opcional, si None devuelve todos)
    Returns:
        Lista de tickers o dict de sectores
    """
    if sector:
        return CHILEAN_STOCKS_BY_SECTOR.get(sector, [])
    return CHILEAN_STOCKS_BY_SECTOR

def get_stock_name(ticker: str) -> str:
    """
    Obtiene el nombre display de una acción
    Args:
        ticker: Símbolo del ticker
    Returns:
        Nombre de la empresa
    """
    return STOCK_NAMES.get(ticker, ticker.replace(".SN", ""))

def get_sector_for_stock(ticker: str) -> str:
    """
    Obtiene el sector de una acción específica
    Args:
        ticker: Símbolo del ticker
    Returns:
        Nombre del sector
    """
    for sector, stocks in CHILEAN_STOCKS_BY_SECTOR.items():
        if ticker in stocks:
            return sector
    return "Otros"
