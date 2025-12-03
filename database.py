"""
PostgreSQL Database Models and Connection
SQLAlchemy ORM kullanarak database yönetimi
"""

from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from cryptography.fernet import Fernet
import base64

Base = declarative_base()

# Encryption key için (production'da environment variable'dan alınmalı)
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY', Fernet.generate_key().decode())
cipher_suite = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)

def encrypt_data(data):
    """Hassas verileri şifrele"""
    if not data:
        return None
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data):
    """Şifreli veriyi çöz"""
    if not encrypted_data:
        return None
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except:
        return None

# Database Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='admin')  # 'admin' veya 'super_admin'
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    tenants = relationship('UserTenant', back_populates='user', cascade='all, delete-orphan')

class Tenant(Base):
    __tablename__ = 'tenants'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey('users.id'), nullable=True)
    
    # Relationships
    config = relationship('TenantConfig', back_populates='tenant', uselist=False, cascade='all, delete-orphan')
    user_tenants = relationship('UserTenant', back_populates='tenant', cascade='all, delete-orphan')
    results = relationship('Result', back_populates='tenant', cascade='all, delete-orphan')
    statistics = relationship('MessageStatistics', back_populates='tenant', cascade='all, delete-orphan')

class UserTenant(Base):
    __tablename__ = 'user_tenants'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    role = Column(String(20), default='owner')  # 'owner' veya 'viewer'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship('User', back_populates='tenants')
    tenant = relationship('Tenant', back_populates='user_tenants')

class TenantConfig(Base):
    __tablename__ = 'tenant_configs'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), unique=True, nullable=False)
    
    # Telegram API bilgileri (şifreli saklanacak)
    api_id = Column(String(50), nullable=True)
    api_hash_encrypted = Column(Text, nullable=True)  # Şifreli
    phone_number = Column(String(20), nullable=True)
    
    # Arama ayarları (JSON)
    group_ids = Column(JSON, default=list)  # [{id, name, startDate, endDate}, ...]
    search_keywords = Column(JSON, default=list)
    search_links = Column(JSON, default=list)
    
    # Dosya yolları
    results_file_path = Column(String(500), nullable=True)
    session_file_path = Column(String(500), nullable=True)
    
    # Tarama ayarları
    scan_time_range = Column(String(20), default='7days')
    
    # Relationships
    tenant = relationship('Tenant', back_populates='config')
    
    def get_api_hash(self):
        """Şifreli API hash'i çöz"""
        return decrypt_data(self.api_hash_encrypted)
    
    def set_api_hash(self, api_hash):
        """API hash'i şifrele ve kaydet"""
        self.api_hash_encrypted = encrypt_data(api_hash)

class Result(Base):
    __tablename__ = 'results'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    
    # Mesaj bilgileri
    timestamp = Column(DateTime, nullable=False)
    group_id = Column(BigInteger, nullable=False)
    group_name = Column(String(200), nullable=True)
    message_id = Column(BigInteger, nullable=False)
    sender_id = Column(BigInteger, nullable=True)
    
    # İçerik
    message_text = Column(Text, nullable=True)
    found_keywords = Column(JSON, default=list)
    found_links = Column(JSON, default=list)
    message_link = Column(String(500), nullable=True)
    
    # İstatistikler
    views_count = Column(Integer, default=0)  # Görüntülenme sayısı
    forwards_count = Column(Integer, default=0)  # Paylaşım sayısı
    reactions_count = Column(Integer, default=0)  # Toplam reaksiyon sayısı
    reactions_detail = Column(JSON, default=dict)  # Emoji bazında reaksiyonlar: {"👍": 5, "❤️": 3}
    replies_count = Column(Integer, default=0)  # Yanıt sayısı
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', back_populates='results')

class MessageStatistics(Base):
    __tablename__ = 'message_statistics'
    
    id = Column(Integer, primary_key=True)
    tenant_id = Column(Integer, ForeignKey('tenants.id'), nullable=False)
    
    # Tarih bazlı istatistikler
    date = Column(DateTime, nullable=False)
    
    # Günlük toplamlar
    total_messages = Column(Integer, default=0)
    total_matches = Column(Integer, default=0)
    total_views = Column(Integer, default=0)
    total_forwards = Column(Integer, default=0)
    total_reactions = Column(Integer, default=0)
    
    # Kelime bazında istatistikler (JSON)
    keyword_stats = Column(JSON, default=dict)  # {"kelime1": 5, "kelime2": 3}
    link_stats = Column(JSON, default=dict)  # {"link1": 2, "link2": 1}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship('Tenant', back_populates='statistics')

# Database connection
def get_database_url():
    """Database URL'ini environment variable'dan al"""
    # PostgreSQL için
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', 'postgres')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'tgmonitor')
    
    return f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# SQLite fallback (development için)
def get_database_url_sqlite():
    """SQLite database URL (development için)"""
    return 'sqlite:///tgmonitor.db'

# Database engine oluştur
def create_engine_instance():
    """Database engine oluştur"""
    # PostgreSQL varsa onu kullan, yoksa SQLite
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        # PostgreSQL environment variables kontrol et
        if os.environ.get('DB_HOST'):
            db_url = get_database_url()
        else:
            # Development için SQLite
            db_url = get_database_url_sqlite()
    
    return create_engine(db_url, echo=False)

engine = create_engine_instance()
SessionLocal = sessionmaker(bind=engine)

def init_db():
    """Database tablolarını oluştur"""
    Base.metadata.create_all(engine)
    print("✅ Database tabloları oluşturuldu!")

def get_db():
    """Database session al"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_super_admin(username='superadmin', password='admin123'):
    """İlk süper admin kullanıcısını oluştur"""
    from hashlib import sha256
    
    db = SessionLocal()
    try:
        # Zaten var mı kontrol et
        existing = db.query(User).filter_by(username=username).first()
        if existing:
            print(f"⚠️  Kullanıcı '{username}' zaten mevcut!")
            return
        
        # Yeni süper admin oluştur
        password_hash = sha256(password.encode()).hexdigest()
        super_admin = User(
            username=username,
            password_hash=password_hash,
            role='super_admin'
        )
        db.add(super_admin)
        db.commit()
        print(f"✅ Süper admin oluşturuldu: {username} / {password}")
    except Exception as e:
        db.rollback()
        print(f"❌ Süper admin oluşturma hatası: {e}")
    finally:
        db.close()

if __name__ == '__main__':
    # Database'i başlat
    print("🔧 Database başlatılıyor...")
    init_db()
    create_super_admin()
    print("✅ Database hazır!")

