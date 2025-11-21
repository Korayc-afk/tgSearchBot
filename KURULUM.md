# 📦 Telegram Monitoring Bot - Kurulum Rehberi

## 🚀 Hızlı Başlangıç

### 1. Gereksinimler
- Python 3.7 veya üzeri
- Telegram hesabı
- Telegram API ID ve API Hash (aşağıda nasıl alınacağı açıklanmıştır)

### 2. Kurulum Adımları

#### Adım 1: Dosyaları İndirin
Tüm dosyaları bir klasöre çıkarın.

#### Adım 2: Python Paketlerini Yükleyin
Terminal/CMD'de proje klasörüne gidin ve şu komutu çalıştırın:

```bash
pip install -r requirements.txt
```

#### Adım 3: Telegram API Bilgilerini Alın

1. https://my.telegram.org/apps adresine gidin
2. Telegram hesabınızla giriş yapın
3. "API development tools" bölümüne gidin
4. Yeni bir uygulama oluşturun:
   - **App title**: İstediğiniz bir isim (örn: "Monitoring Bot")
   - **Short name**: İstediğiniz kısa isim (örn: "monitor")
   - **Platform**: Desktop
   - **Description**: İstediğiniz açıklama
5. **API ID** ve **API Hash** değerlerini kopyalayın

#### Adım 4: Botu Başlatın

Terminal/CMD'de şu komutu çalıştırın:

```bash
python web_panel.py
```

#### Adım 5: Web Paneline Erişin

Tarayıcınızda şu adrese gidin:
```
http://localhost:5000
```

### 3. İlk Kullanım

1. **Ayarlar** sekmesine gidin
2. API ID ve API Hash bilgilerinizi girin
3. Telefon numaranızı girin (örn: +905551234567)
4. "Ayarları Kaydet" butonuna tıklayın
5. "Test Et" butonuna tıklayarak API bilgilerinizi test edin
6. "Telegram'a Giriş Yap" butonuna tıklayın:
   - Telefon numaranızı girin
   - Gelen kodu girin
   - Eğer 2FA (iki faktörlü doğrulama) aktifse şifrenizi girin
7. **Ayarlar** sekmesinde:
   - Aranacak kelimeleri girin (virgülle ayırın, örn: "padişahbet, padisahbet")
   - İzlemek istediğiniz grupları ekleyin
   - Her grup için tarih aralığı seçin
8. **Sonuçlar** sekmesine gidin ve "Tara" butonuna tıklayın

## 📱 Grup/Kanal Ekleme

### Yöntem 1: Link ile Ekleme
1. Telegram'da grup/kanal linkini kopyalayın (örn: `https://t.me/bonusbossduyuru`)
2. Ayarlar sekmesinde "Grup/Kanal Ekle" bölümüne yapıştırın
3. "➕ Ekle" butonuna tıklayın

### Yöntem 2: Grup Adı ile Arama
1. Ayarlar sekmesinde "Grup/Kanal Ekle" bölümüne grup adını yazın
2. "🔍 Ara" butonuna tıklayın
3. Arama sonuçlarından istediğiniz grubu seçin

### Yöntem 3: Birden Fazla Grup Ekleme
- Her satıra bir link yazın VEYA
- Virgülle ayırın (örn: `https://t.me/grup1, https://t.me/grup2`)

## 🔍 Tarama Yapma

1. **Ayarlar** sekmesinde her grup için tarih aralığı seçin
2. "Grupları Kaydet" butonuna tıklayın
3. **Sonuçlar** sekmesine gidin
4. "🔍 Tara" butonuna tıklayın
5. Tarama tamamlanana kadar bekleyin
6. Sonuçları görüntüleyin

## 📊 Sonuçları Filtreleme

1. **Sonuçlar** sekmesinde sağ üstteki "🔍 Grup Filtresi" butonuna tıklayın
2. İstediğiniz grupları seçin (checkbox)
3. Sadece seçili grupların mesajları gösterilecektir

## 📥 Excel İndirme

1. **Sonuçlar** sekmesinde "📊 Excel İndir" butonuna tıklayın
2. Excel dosyası otomatik olarak indirilecektir

## ⚠️ Önemli Notlar

- **Tarihler**: Gelecekteki tarihler için tarama yapılamaz. Geçmiş tarihler seçin.
- **Grup Erişimi**: Bot, sadece hesabınızın erişebildiği grupları tarayabilir.
- **Session Dosyası**: İlk girişten sonra `session.session` dosyası oluşur. Bu dosyayı güvenli tutun.
- **API Bilgileri**: API ID ve API Hash bilgilerinizi kimseyle paylaşmayın.

## 🐛 Sorun Giderme

### Bot çalışmıyor
- Python versiyonunuzu kontrol edin: `python --version` (3.7+ olmalı)
- Tüm paketlerin yüklü olduğundan emin olun: `pip install -r requirements.txt`
- Terminal'de hata mesajlarını kontrol edin

### Sonuç bulunamıyor
- Tarihlerin geçmişte olduğundan emin olun
- Aranacak kelimelerin doğru girildiğinden emin olun
- Grupların seçildiğinden emin olun
- Debug panelini kontrol edin (Sonuçlar sekmesinde)

### Telegram girişi yapılamıyor
- API ID ve API Hash'in doğru olduğundan emin olun
- Telefon numaranızın doğru formatta olduğundan emin olun (+90XXXXXXXXXX)
- İnternet bağlantınızı kontrol edin

## 📞 Destek

Sorun yaşarsanız:
1. Debug panelini kontrol edin
2. Terminal'deki hata mesajlarını okuyun
3. `results.txt` dosyasını kontrol edin

## 🔒 Güvenlik

- `config.json` dosyasını kimseyle paylaşmayın (API bilgileriniz içerir)
- `session.session` dosyasını kimseyle paylaşmayın (Telegram giriş bilgileriniz içerir)
- Bu dosyaları `.gitignore`'a ekleyin (Git kullanıyorsanız)

