"""
Config yönetimi için yardımcı modül
JSON tabanlı config sistemi
"""

import json
import os

CONFIG_FILE = 'config.json'

DEFAULT_CONFIG = {
    'API_ID': '',
    'API_HASH': '',
    'PHONE_NUMBER': '',
    'GROUP_IDS': [],
    'SEARCH_KEYWORDS': [],
    'SEARCH_LINKS': [],
    'RESULTS_FILE': 'results.txt',
    'SCAN_TIME_RANGE': '7days'  # 1day, 7days, 30days
}

def load_config():
    """Config dosyasını yükle"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                # Eksik alanları default değerlerle doldur
                for key in DEFAULT_CONFIG:
                    if key not in config:
                        config[key] = DEFAULT_CONFIG[key]
                return config
        except Exception as e:
            print(f"Config yükleme hatası: {e}")
            return DEFAULT_CONFIG.copy()
    else:
        # Config dosyası yoksa oluştur
        save_config(DEFAULT_CONFIG.copy())
        return DEFAULT_CONFIG.copy()

def save_config(config):
    """Config dosyasını kaydet"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Config kaydetme hatası: {e}")
        return False

def get_config():
    """Config'i Python modülü formatında döndür (eski kod uyumluluğu için)"""
    config_dict = load_config()
    
    # Bir class oluştur ve config değerlerini attribute olarak ekle
    class Config:
        pass
    
    config_obj = Config()
    for key, value in config_dict.items():
        setattr(config_obj, key, value)
    
    return config_obj

