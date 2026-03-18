import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    MYSQL_HOST = os.getenv('MYSQL_HOST')
    MYSQL_USER = os.getenv('MYSQL_USER')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE')
    MYSQL_PORT = int(os.getenv('MYSQL_PORT'))

    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"

    THRESHOLDS = {
        'flow': {
            
            'sensor_min': 1.0,      # L/min - minimum mesurable fiable
            'sensor_max': 30.0,     # L/min - maximum supporté
            
            # Pompe éteinte
            'pompe_off_max': 0.2,     # Débit résiduel acceptable (bruit électronique)
            'leak_min': 0.3,          # Seuil de détection de fuite
            
            # Pompe allumée
            'debit_normal': 2.0,      # Valeur de référence
            
            # Plage normale : entre 1.4 et 2.6 L/min (2.0 ± 30%)
            'pompe_on_min': 1.4,       # 30% en dessous de la normale
            'pompe_on_max': 2.6,       # 30% au-dessus de la normale
            
            # Seuils critiques
            'critical_min': 0.8,       # En dessous = pompe bouchée ou défaillante
            'critical_max': 4.0,       # Au dessus = tuyau débranché (2× la normale)
        }
    }