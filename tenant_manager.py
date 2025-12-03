"""
Tenant (Grup) Yönetimi Modülü
CRUD işlemleri ve dosya yönetimi
"""

import os
import json
import shutil
import re
from datetime import datetime
from database import SessionLocal, Tenant, TenantConfig, UserTenant, User

def slugify(text):
    """Basit slugify fonksiyonu"""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text.strip('-')

TENANTS_DIR = 'tenants'

def ensure_tenants_dir():
    """Tenants klasörünü oluştur"""
    if not os.path.exists(TENANTS_DIR):
        os.makedirs(TENANTS_DIR)

def get_tenant_dir(tenant_slug):
    """Tenant klasör yolunu al"""
    return os.path.join(TENANTS_DIR, tenant_slug)

def create_tenant(name, created_by_user_id=None):
    """Yeni tenant oluştur"""
    db = SessionLocal()
    try:
        # Slug oluştur
        slug = slugify(name)
        
        # Benzersiz slug kontrolü
        counter = 1
        original_slug = slug
        while db.query(Tenant).filter_by(slug=slug).first():
            slug = f"{original_slug}-{counter}"
            counter += 1
        
        # Tenant oluştur
        tenant = Tenant(
            name=name,
            slug=slug,
            created_by=created_by_user_id,
            is_active=True
        )
        db.add(tenant)
        db.flush()  # ID'yi almak için
        
        # Tenant config oluştur
        tenant_dir = get_tenant_dir(slug)
        ensure_tenants_dir()
        os.makedirs(tenant_dir, exist_ok=True)
        
        config = TenantConfig(
            tenant_id=tenant.id,
            results_file_path=os.path.join(tenant_dir, 'results.txt'),
            session_file_path=os.path.join(tenant_dir, 'session.session'),
            group_ids=[],
            search_keywords=[],
            search_links=[],
            scan_time_range='7days'
        )
        db.add(config)
        
        # Eğer created_by varsa, o kullanıcıyı tenant'a ekle
        if created_by_user_id:
            user_tenant = UserTenant(
                user_id=created_by_user_id,
                tenant_id=tenant.id,
                role='owner'
            )
            db.add(user_tenant)
        
        db.commit()
        
        # Boş dosyaları oluştur
        with open(config.results_file_path, 'w', encoding='utf-8') as f:
            f.write('')
        
        # Session dışında kullanım için expunge
        db.expunge(tenant)
        return tenant
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_tenant(tenant_id):
    """Tenant'ı ID ile al"""
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter_by(id=tenant_id).first()
        if tenant:
            # Lazy loading için gerekli alanları yükle
            _ = tenant.name
            _ = tenant.slug
            _ = tenant.is_active
            # Session dışında kullanım için expunge
            db.expunge(tenant)
        return tenant
    finally:
        db.close()

def get_tenant_by_slug(slug):
    """Tenant'ı slug ile al"""
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter_by(slug=slug).first()
        if tenant:
            # Lazy loading için gerekli alanları yükle
            _ = tenant.name
            _ = tenant.slug
            _ = tenant.is_active
            # Session dışında kullanım için expunge
            db.expunge(tenant)
        return tenant
    finally:
        db.close()

def get_user_tenants(user_id):
    """Kullanıcının erişebildiği tenant'ları al"""
    db = SessionLocal()
    try:
        # Süper admin ise tüm tenant'ları döndür
        user = db.query(User).filter_by(id=user_id).first()
        if user and user.role == 'super_admin':
            tenants = db.query(Tenant).filter_by(is_active=True).all()
        else:
            # Normal kullanıcı ise sadece erişebildiği tenant'ları döndür
            user_tenants = db.query(UserTenant).filter_by(user_id=user_id).all()
            tenant_ids = [ut.tenant_id for ut in user_tenants]
            tenants = db.query(Tenant).filter(
                Tenant.id.in_(tenant_ids),
                Tenant.is_active == True
            ).all()
        
        # Session dışında kullanım için expunge
        for tenant in tenants:
            # Lazy loading için gerekli alanları yükle
            _ = tenant.id
            _ = tenant.name
            _ = tenant.slug
            _ = tenant.is_active
            db.expunge(tenant)
        
        return tenants
    finally:
        db.close()

def update_tenant(tenant_id, name=None, is_active=None):
    """Tenant'ı güncelle"""
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter_by(id=tenant_id).first()
        if not tenant:
            return None
        
        if name is not None:
            # Slug'ı da güncelle
            new_slug = slugify(name)
            # Eski klasörü yeniden adlandır
            old_dir = get_tenant_dir(tenant.slug)
            new_dir = get_tenant_dir(new_slug)
            if os.path.exists(old_dir) and old_dir != new_dir:
                os.rename(old_dir, new_dir)
                # Config'teki dosya yollarını güncelle
                if tenant.config:
                    tenant.config.results_file_path = os.path.join(new_dir, 'results.txt')
                    tenant.config.session_file_path = os.path.join(new_dir, 'session.session')
            tenant.slug = new_slug
            tenant.name = name
        
        if is_active is not None:
            tenant.is_active = is_active
        
        db.commit()
        return tenant
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def delete_tenant(tenant_id):
    """Tenant'ı sil"""
    db = SessionLocal()
    try:
        tenant = db.query(Tenant).filter_by(id=tenant_id).first()
        if not tenant:
            return False
        
        # Klasörü sil
        tenant_dir = get_tenant_dir(tenant.slug)
        if os.path.exists(tenant_dir):
            shutil.rmtree(tenant_dir)
        
        # Database'den sil (cascade ile ilişkili kayıtlar da silinir)
        db.delete(tenant)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_tenant_config(tenant_id):
    """Tenant config'ini al"""
    db = SessionLocal()
    try:
        config = db.query(TenantConfig).filter_by(tenant_id=tenant_id).first()
        return config
    finally:
        db.close()

def update_tenant_config(tenant_id, **kwargs):
    """Tenant config'ini güncelle"""
    db = SessionLocal()
    try:
        config = db.query(TenantConfig).filter_by(tenant_id=tenant_id).first()
        if not config:
            return None
        
        # Güncellenebilir alanlar
        updatable_fields = [
            'api_id', 'phone_number', 'group_ids', 'search_keywords',
            'search_links', 'scan_time_range'
        ]
        
        for field in updatable_fields:
            if field in kwargs:
                setattr(config, field, kwargs[field])
        
        # API hash özel işlem
        if 'api_hash' in kwargs:
            config.set_api_hash(kwargs['api_hash'])
        
        db.commit()
        return config
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def add_user_to_tenant(user_id, tenant_id, role='owner'):
    """Kullanıcıyı tenant'a ekle"""
    db = SessionLocal()
    try:
        # Zaten var mı kontrol et
        existing = db.query(UserTenant).filter_by(
            user_id=user_id,
            tenant_id=tenant_id
        ).first()
        
        if existing:
            existing.role = role
        else:
            user_tenant = UserTenant(
                user_id=user_id,
                tenant_id=tenant_id,
                role=role
            )
            db.add(user_tenant)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def remove_user_from_tenant(user_id, tenant_id):
    """Kullanıcıyı tenant'tan çıkar"""
    db = SessionLocal()
    try:
        user_tenant = db.query(UserTenant).filter_by(
            user_id=user_id,
            tenant_id=tenant_id
        ).first()
        
        if user_tenant:
            db.delete(user_tenant)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def get_tenant_users(tenant_id):
    """Tenant'a erişimi olan kullanıcıları al"""
    db = SessionLocal()
    try:
        user_tenants = db.query(UserTenant).filter_by(tenant_id=tenant_id).all()
        user_ids = [ut.user_id for ut in user_tenants]
        return db.query(User).filter(User.id.in_(user_ids)).all()
    finally:
        db.close()

