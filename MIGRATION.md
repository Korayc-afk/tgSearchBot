# 🚀 Multi-Tenant Migration Guide

## Yapılan Değişiklikler

### 1. Database Yapısı
- **PostgreSQL** desteği eklendi (SQLite fallback)
- Yeni tablolar:
  - `users`: Kullanıcı yönetimi
  - `tenants`: Grup/tenant yönetimi
  - `tenant_configs`: Her tenant için ayrı config
  - `results`: Sonuçlar (istatistiklerle birlikte)
  - `message_statistics`: Günlük istatistikler
  - `user_tenants`: Kullanıcı-tenant ilişkisi

### 2. Yeni Dosyalar
- `database.py`: Database modelleri ve bağlantı
- `auth.py`: Flask-Login entegrasyonu
- `tenant_manager.py`: Tenant CRUD işlemleri
- `tg_monitor_tenant.py`: Tenant bazlı monitoring botu
- `web_panel_new.py`: Yeni multi-tenant web paneli

### 3. Özellikler
- ✅ Çoklu grup desteği (her grup izole)
- ✅ Süper admin paneli (tüm grupları görme/yönetme)
- ✅ Normal admin paneli (sadece kendi grubu)
- ✅ İstatistik toplama (görüntülenme, paylaşım, emoji reaksiyonları)
- ✅ Günlük istatistikler
- ✅ Database tabanlı authentication

### 4. Eksikler (Yapılacaklar)
- ⏳ Template'ler (super_admin.html, admin.html)
- ⏳ Chart.js grafikleri
- ⏳ Modern UI/UX tasarımı
- ⏳ Kullanıcı yönetimi UI
- ⏳ Tenant yönetimi UI

## Kurulum

### 1. Database Kurulumu

**PostgreSQL (Production):**
```bash
# Environment variables
export DB_USER=postgres
export DB_PASSWORD=your_password
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=tgmonitor
```

**SQLite (Development):**
- Otomatik olarak `tgmonitor.db` oluşturulur

### 2. Paket Kurulumu
```bash
pip install -r requirements.txt
```

### 3. Database Başlatma
```bash
python database.py
```

Bu komut:
- Database tablolarını oluşturur
- İlk süper admin kullanıcısını oluşturur (superadmin / admin123)

### 4. Web Paneli Başlatma
```bash
python web_panel_new.py
```

## Kullanım

### Süper Admin
1. Giriş: `superadmin` / `admin123`
2. Dashboard'da tüm grupları görür
3. Yeni grup ekleyebilir
4. Kullanıcı ekleyebilir/çıkarabilir
5. Tüm grupların sonuçlarını görebilir

### Normal Admin
1. Süper admin tarafından oluşturulan kullanıcı ile giriş
2. Sadece kendi grubunu görür
3. Kendi Telegram hesabını bağlar
4. Kendi ayarlarını yapar
5. Kendi sonuçlarını görür

## API Endpoints

### Süper Admin
- `GET /api/super-admin/dashboard` - Dashboard verileri
- `GET /api/super-admin/tenants` - Tüm tenant'ları listele
- `POST /api/super-admin/tenants` - Yeni tenant oluştur
- `PUT /api/super-admin/tenants/<id>` - Tenant güncelle
- `DELETE /api/super-admin/tenants/<id>` - Tenant sil
- `GET /api/super-admin/users` - Tüm kullanıcıları listele
- `POST /api/super-admin/users` - Yeni kullanıcı oluştur
- `GET /api/super-admin/tenants/<id>/results` - Tenant sonuçları

### Normal Admin
- `GET /api/admin/<tenant_id>/config` - Config al
- `POST /api/admin/<tenant_id>/config` - Config kaydet
- `GET /api/admin/<tenant_id>/results` - Sonuçları al
- `GET /api/admin/<tenant_id>/statistics` - İstatistikleri al
- `POST /api/admin/<tenant_id>/scan` - Tarama başlat
- `GET /api/admin/<tenant_id>/scan/status` - Tarama durumu
- `POST /api/admin/<tenant_id>/telegram/login` - Telegram giriş
- `GET /api/admin/<tenant_id>/telegram/groups` - Grupları listele

## Dosya Yapısı

```
tenants/
  ├── tenant-1/
  │   ├── config.json
  │   ├── session.session
  │   └── results.txt
  ├── tenant-2/
  │   └── ...
```

Her tenant için ayrı klasör ve dosyalar.

## Notlar

- İlk süper admin şifresini değiştirmeyi unutmayın!
- Production'da `ENCRYPTION_KEY` environment variable'ını ayarlayın
- PostgreSQL kullanıyorsanız connection pool ayarlarını yapın
- Her tenant için ayrı Telegram hesabı gereklidir

