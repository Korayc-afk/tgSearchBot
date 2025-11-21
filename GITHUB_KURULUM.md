# 🚀 GitHub'a Yükleme ve Render'da Çalıştırma Rehberi

## 📦 Adım 1: GitHub'a Yükleme

### 1.1 GitHub Repository Oluşturma

1. https://github.com adresine gidin ve giriş yapın
2. Sağ üstteki **"+"** butonuna tıklayın → **"New repository"**
3. Repository bilgilerini doldurun:
   - **Repository name**: `tgSearchBot` (veya istediğiniz isim)
   - **Description**: "Telegram Monitoring Bot - Grup mesajlarını izleme botu"
   - **Public** veya **Private** seçin
   - **Initialize this repository with a README** seçeneğini işaretlemeyin
4. **"Create repository"** butonuna tıklayın

### 1.2 Dosyaları GitHub'a Yükleme

#### Yöntem 1: GitHub Desktop (Kolay)

1. https://desktop.github.com adresinden GitHub Desktop'ı indirin ve kurun
2. GitHub Desktop'ı açın ve GitHub hesabınızla giriş yapın
3. **File** → **Add Local Repository**
4. Proje klasörünüzü seçin (`C:\Users\User\Desktop\tgSearchBot`)
5. Sol tarafta değişiklikleri göreceksiniz
6. **Summary** kısmına "Initial commit" yazın
7. **"Commit to main"** butonuna tıklayın
8. **"Publish repository"** butonuna tıklayın

#### Yöntem 2: Terminal/CMD (Manuel)

Proje klasöründe terminal/CMD açın ve şu komutları çalıştırın:

```bash
# Git'i başlat
git init

# Tüm dosyaları ekle (config.json ve session dosyaları otomatik hariç tutulur)
git add .

# İlk commit
git commit -m "Initial commit: Telegram Monitoring Bot"

# GitHub repository'nizi ekleyin (URL'yi kendi repository'nizle değiştirin)
git remote add origin https://github.com/KULLANICI_ADINIZ/tgSearchBot.git

# Dosyaları yükle
git branch -M main
git push -u origin main
```

### 1.3 Kontrol

GitHub'da repository'nize gidin ve tüm dosyaların yüklendiğini kontrol edin.

**ÖNEMLİ:** `config.json` ve `session.session` dosyaları `.gitignore` sayesinde yüklenmeyecek (güvenlik).

---

## 🌐 Adım 2: Render'da Çalıştırma

### 2.1 Render Hesabı Oluşturma

1. https://render.com adresine gidin
2. **"Get Started for Free"** butonuna tıklayın
3. **"Sign up with GitHub"** seçeneğini seçin
4. GitHub hesabınızla giriş yapın ve yetkilendirin

### 2.2 Yeni Web Service Oluşturma

1. Render dashboard'da **"New +"** butonuna tıklayın
2. **"Web Service"** seçeneğini seçin
3. GitHub repository'nizi seçin (veya **"Connect account"** ile bağlayın)
4. Repository'nizi seçin: `tgSearchBot`

### 2.3 Ayarları Yapılandırma

Aşağıdaki ayarları yapın:

- **Name**: `telegram-monitoring-bot` (veya istediğiniz isim)
- **Region**: En yakın bölgeyi seçin (örn: Frankfurt)
- **Branch**: `main` (veya `master`)
- **Root Directory**: Boş bırakın (otomatik)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```
  python web_panel.py
  ```
- **Plan**: **Free** seçin

### 2.4 Environment Variables (Opsiyonel)

Şu an için environment variable eklemenize gerek yok. Bot kendi config.json dosyasını kullanacak.

### 2.5 Deploy

1. **"Create Web Service"** butonuna tıklayın
2. Render otomatik olarak:
   - Repository'yi klonlar
   - Paketleri yükler
   - Botu başlatır
3. Build işlemi 2-3 dakika sürebilir
4. Build tamamlandığında yeşil "Live" yazısını göreceksiniz

### 2.6 URL'yi Bulma

1. Render dashboard'da servisinize tıklayın
2. Üstte **"https://telegram-monitoring-bot.onrender.com"** gibi bir URL göreceksiniz
3. Bu URL'yi kopyalayın ve tarayıcıda açın

---

## ⚙️ Adım 3: İlk Kullanım

### 3.1 Web Paneline Erişim

1. Render'dan aldığınız URL'yi tarayıcıda açın
2. Web paneli açılacaktır

### 3.2 Ayarları Yapma

1. **Ayarlar** sekmesine gidin
2. API ID ve API Hash bilgilerinizi girin
3. Telefon numaranızı girin
4. "Ayarları Kaydet" butonuna tıklayın
5. "Telegram'a Giriş Yap" butonuna tıklayın ve giriş yapın

### 3.3 Grupları Ekleme ve Tarama

1. Grupları ekleyin
2. Tarih aralıklarını seçin
3. "Tara" butonuna tıklayın

---

## 🔧 Sorun Giderme

### Build Hatası

- **Hata**: "Module not found"
  - **Çözüm**: `requirements.txt` dosyasının doğru olduğundan emin olun

### Bot Çalışmıyor

- **Hata**: "Port already in use"
  - **Çözüm**: Render otomatik port atar, sorun olmamalı. Eğer olursa `web_panel.py`'deki port ayarını kontrol edin

### Session Dosyası Kayboluyor

- **Sorun**: Render'da session dosyası kalıcı değil
  - **Çözüm**: Render'ın ücretsiz planında disk kalıcı değil. Her deploy'da session yeniden oluşturulur. Bu normaldir.

### Web Paneli Açılmıyor

- **Kontrol**: Render dashboard'da servisinizin "Live" durumunda olduğundan emin olun
- **Logs**: Render dashboard'da "Logs" sekmesine bakın ve hata mesajlarını kontrol edin

---

## 💡 İpuçları

1. **Free Plan Limitleri**:
   - 750 saat/ay (yaklaşık 31 gün sürekli çalışma)
   - 15 dakika inaktiflikten sonra uyku moduna geçer
   - İlk istekte 30-60 saniye uyanma süresi olabilir

2. **Kalıcılık**:
   - Ücretsiz planda disk kalıcı değil
   - Her deploy'da `config.json` ve `session.session` yeniden oluşturulur
   - Bu yüzden her deploy'dan sonra ayarları tekrar yapmanız gerekebilir

3. **Güncelleme**:
   - GitHub'a yeni commit attığınızda Render otomatik deploy eder
   - Manuel deploy için Render dashboard'da "Manual Deploy" butonunu kullanın

---

## 📞 Destek

Sorun yaşarsanız:
1. Render dashboard'da "Logs" sekmesini kontrol edin
2. GitHub repository'nizde Issues açın
3. README.md ve KURULUM.md dosyalarına bakın

---

## ✅ Kontrol Listesi

- [ ] GitHub repository oluşturuldu
- [ ] Dosyalar GitHub'a yüklendi
- [ ] Render hesabı oluşturuldu
- [ ] Web service oluşturuldu
- [ ] Build başarılı
- [ ] Web paneli açılıyor
- [ ] Ayarlar yapıldı
- [ ] Telegram girişi yapıldı
- [ ] Bot çalışıyor

Başarılar! 🎉

