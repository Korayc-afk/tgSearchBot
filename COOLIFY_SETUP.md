# 🚀 Coolify Deployment Guide

## PostgreSQL Kurulumu

### 1. Coolify'da PostgreSQL Servisi Oluştur

1. Coolify dashboard'a giriş yapın
2. **Services** sekmesine gidin
3. **PostgreSQL** servisini seçin
4. Yeni bir PostgreSQL instance oluşturun:
   - **Name**: `tgmonitor-db` (veya istediğiniz isim)
   - **Version**: `15` veya `16` (önerilen)
   - **Database Name**: `tgmonitor`
   - **Username**: `postgres` (veya özel)
   - **Password**: Güçlü bir şifre oluşturun (kaydedin!)

### 2. PostgreSQL Bağlantı Bilgilerini Al

PostgreSQL servisi oluşturulduktan sonra, Coolify size şu bilgileri verecek:
- **Host**: `tgmonitor-db.internal` (internal network için) veya public IP
- **Port**: `5432`
- **Database**: `tgmonitor`
- **Username**: `postgres`
- **Password**: Oluşturduğunuz şifre

### 3. Web Uygulamasını Deploy Et

1. **Applications** sekmesine gidin
2. **New Application** butonuna tıklayın
3. GitHub repository'nizi bağlayın
4. **Build Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python web_panel_new.py`
   - **Port**: `5000` (veya PORT environment variable)

### 4. Environment Variables Ayarla

Web uygulamanızın **Environment Variables** sekmesine gidin ve şunları ekleyin:

```bash
# Database
DB_USER=postgres
DB_PASSWORD=<postgres_password>  # PostgreSQL'den aldığınız şifre
DB_HOST=tgmonitor-db.internal    # PostgreSQL servis adı
DB_PORT=5432
DB_NAME=tgmonitor

# Veya tek bir DATABASE_URL kullanabilirsiniz:
DATABASE_URL=postgresql://postgres:<password>@tgmonitor-db.internal:5432/tgmonitor

# Flask Secret Key (güvenlik için önemli!)
SECRET_KEY=<rastgele_güçlü_şifre>  # Örnek: openssl rand -hex 32

# Encryption Key (API hash şifreleme için)
ENCRYPTION_KEY=<rastgele_32_byte_key>  # Örnek: python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

# Port (opsiyonel, varsayılan 5000)
PORT=5000
```

### 5. İlk Başlatma

1. Uygulamayı deploy edin
2. İlk başlatmada database tabloları otomatik oluşturulacak
3. İlk süper admin kullanıcısı oluşturulacak:
   - **Username**: `superadmin`
   - **Password**: `admin123`
   - ⚠️ **İlk girişten sonra şifreyi değiştirin!**

### 6. Database Migration (İlk Kurulum)

Eğer database tabloları oluşturulmadıysa, manuel olarak çalıştırabilirsiniz:

```bash
# Coolify'da web uygulamanızın terminal'ine girin
python database.py
```

### 7. Health Check

Uygulamanın çalıştığını kontrol edin:
- Web paneli: `http://your-app-url`
- Login sayfası görünmeli
- Süper admin ile giriş yapabilmelisiniz

## 🔒 Güvenlik Notları

1. **SECRET_KEY**: Production'da mutlaka güçlü bir secret key kullanın
2. **ENCRYPTION_KEY**: API hash'leri şifrelemek için kullanılır, güvenli tutun
3. **Database Password**: Güçlü bir şifre kullanın
4. **HTTPS**: Production'da mutlaka HTTPS kullanın (Coolify otomatik sağlar)

## 🐛 Sorun Giderme

### Database Bağlantı Hatası

Eğer "connection refused" hatası alıyorsanız:
- PostgreSQL servisinin çalıştığından emin olun
- `DB_HOST` değerinin doğru olduğundan emin olun (internal network için `.internal` kullanın)
- Firewall ayarlarını kontrol edin

### Tablolar Oluşturulmadı

```bash
# Terminal'de çalıştırın
python database.py
```

### İlk Süper Admin Oluşturulmadı

```bash
# Terminal'de çalıştırın
python database.py
```

Veya manuel olarak:
```python
from database import create_super_admin
create_super_admin('superadmin', 'admin123')
```

## 📝 Notlar

- PostgreSQL internal network'te `.internal` domain'i kullanır
- Public IP kullanmak isterseniz, PostgreSQL servisinin public erişimini açmanız gerekir
- Her tenant için ayrı Telegram hesabı gereklidir
- `tenants/` klasörü persistent storage olarak mount edilebilir (önerilir)

## 🔄 Güncelleme

Yeni bir commit push ettiğinizde, Coolify otomatik olarak:
1. Yeni kodu çeker
2. Build eder
3. Deploy eder
4. Uygulamayı yeniden başlatır

Database migration'lar otomatik çalışmaz, manuel yapmanız gerekebilir.

