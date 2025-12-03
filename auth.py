"""
Authentication ve Authorization modülü
Flask-Login entegrasyonu
"""

from flask_login import UserMixin, LoginManager
from database import SessionLocal, User, UserTenant
from hashlib import sha256

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.login_message = 'Lütfen giriş yapın.'
login_manager.login_message_category = 'info'

class UserAuth(UserMixin):
    """Flask-Login için User sınıfı"""
    def __init__(self, user_id, username, role):
        self.id = user_id
        self.username = username
        self.role = role
        self.is_super_admin = (role == 'super_admin')
    
    def can_access_tenant(self, tenant_id):
        """Kullanıcının bu tenant'a erişimi var mı?"""
        if self.is_super_admin:
            return True
        
        db = SessionLocal()
        try:
            user_tenant = db.query(UserTenant).filter_by(
                user_id=self.id,
                tenant_id=tenant_id
            ).first()
            return user_tenant is not None
        finally:
            db.close()

@login_manager.user_loader
def load_user(user_id):
    """Kullanıcıyı session'dan yükle"""
    db = SessionLocal()
    try:
        user = db.query(User).filter_by(id=int(user_id)).first()
        if user:
            # Son giriş zamanını güncelle
            from datetime import datetime
            user.last_login = datetime.utcnow()
            db.commit()
            
            return UserAuth(user.id, user.username, user.role)
        return None
    finally:
        db.close()

def verify_password(username, password):
    """Kullanıcı adı ve şifre doğrula"""
    db = SessionLocal()
    try:
        password_hash = sha256(password.encode()).hexdigest()
        user = db.query(User).filter_by(
            username=username,
            password_hash=password_hash
        ).first()
        
        if user:
            return UserAuth(user.id, user.username, user.role)
        return None
    finally:
        db.close()

def require_super_admin(f):
    """Süper admin gerektiren decorator"""
    from functools import wraps
    from flask import abort
    from flask_login import current_user
    
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def require_tenant_access(tenant_id_param='tenant_id'):
    """Tenant erişimi gerektiren decorator"""
    from functools import wraps
    from flask import abort, request
    from flask_login import current_user
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Tenant ID'yi al
            tenant_id = kwargs.get(tenant_id_param) or request.args.get('tenant_id') or request.json.get('tenant_id') if request.is_json else None
            
            if not tenant_id:
                abort(400)
            
            # Süper admin ise geç
            if current_user.is_authenticated and current_user.is_super_admin:
                return f(*args, **kwargs)
            
            # Normal kullanıcı ise erişim kontrolü
            if not current_user.is_authenticated or not current_user.can_access_tenant(tenant_id):
                abort(403)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

