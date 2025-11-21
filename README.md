# 📱 Telegram Monitoring Bot

Telegram gruplarında belirli kelimeleri, linkleri ve bahsedilmeleri izleyen ve web paneli üzerinden yönetilebilen bir bot.

## ✨ Özellikler

- 🔍 **Kelime Arama**: Belirli kelimeleri Telegram gruplarında ara
- 🔗 **Link Takibi**: Belirli linklerin kullanımını takip et
- 📅 **Tarih Aralığı**: Geçmiş mesajları belirli tarih aralıklarında tara
- 🎯 **Grup Seçimi**: Sadece seçtiğiniz grupları izle
- 📊 **Web Paneli**: Kullanıcı dostu web arayüzü
- 📥 **Excel Export**: Sonuçları Excel dosyası olarak indir
- 🔍 **Grup Filtresi**: Sonuçları grup bazında filtrele
- 🐛 **Debug Paneli**: Gerçek zamanlı tarama durumu ve loglar

## 🚀 Hızlı Başlangıç

### Gereksinimler
- Python 3.7+
- Telegram hesabı
- Telegram API ID ve API Hash

### Kurulum

1. **Paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

2. **Botu başlatın:**
```bash
python web_panel.py
```

3. **Web paneline erişin:**
```
http://localhost:5000
```

4. **İlk kullanım:**
   - Ayarlar sekmesinde API bilgilerinizi girin
   - Telegram'a giriş yapın
   - Grupları ekleyin ve tarama yapın

Detaylı kurulum talimatları için [KURULUM.md](KURULUM.md) dosyasına bakın.

## 📖 Kullanım

### API Bilgilerini Alma

1. https://my.telegram.org/apps adresine gidin
2. Telegram hesabınızla giriş yapın
3. "API development tools" bölümüne gidin
4. Yeni bir uygulama oluşturun
5. **API ID** ve **API Hash** değerlerini kopyalayın

### Grup Ekleme

- **Link ile**: `https://t.me/bonusbossduyuru` gibi linkleri yapıştırın
- **Arama ile**: Grup adını yazıp arama yapın
- **Toplu ekleme**: Birden fazla linki virgülle ayırarak ekleyin

### Tarama Yapma

1. Her grup için tarih aralığı seçin
2. "Grupları Kaydet" butonuna tıklayın
3. Sonuçlar sekmesinde "Tara" butonuna tıklayın
4. Sonuçları görüntüleyin

## 📁 Dosya Yapısı

```
tgSearchBot/
├── web_panel.py          # Flask web uygulaması
├── tg_monitor.py         # Telegram bot mantığı
├── config_manager.py     # Config yönetimi
├── config.json           # Ayarlar (otomatik oluşur)
├── session.session       # Telegram session (otomatik oluşur)
├── results.txt           # Tarama sonuçları
├── requirements.txt      # Python paketleri
├── templates/
│   └── index.html        # Web panel arayüzü
└── README.md            # Bu dosya
```

## 🔒 Güvenlik

- `config.json` ve `session.session` dosyalarını kimseyle paylaşmayın
- API bilgilerinizi güvenli tutun
- Bu dosyaları `.gitignore`'a ekleyin

## 🌐 Ücretsiz Dağıtım Seçenekleri

### 1. GitHub (Önerilen)
- **Avantajlar**: Ücretsiz, sınırsız, versiyon kontrolü
- **Nasıl**: 
  1. GitHub'da yeni bir repository oluşturun
  2. Dosyaları yükleyin (config.json ve session.session hariç)
  3. README.md ve KURULUM.md dosyalarını ekleyin
  4. Arkadaşlarınız repository'yi klonlayabilir

### 2. Railway.app
- **Avantajlar**: Ücretsiz tier, otomatik deployment
- **Nasıl**: 
  1. https://railway.app adresine gidin
  2. GitHub ile giriş yapın
  3. Yeni proje oluşturun
  4. Repository'nizi bağlayın
  5. Otomatik deploy edilir

### 3. Render.com
- **Avantajlar**: Ücretsiz tier, kolay kurulum
- **Nasıl**: 
  1. https://render.com adresine gidin
  2. Yeni Web Service oluşturun
  3. GitHub repository'nizi bağlayın
  4. Build ve start komutlarını ayarlayın

### 4. Replit
- **Avantajlar**: Tarayıcıda çalışır, kolay paylaşım
- **Nasıl**: 
  1. https://replit.com adresine gidin
  2. Yeni repl oluşturun
  3. Dosyaları yükleyin
  4. "Run" butonuna tıklayın

### 5. Google Colab (Sadece test için)
- **Avantajlar**: Ücretsiz, Jupyter notebook desteği
- **Not**: Web paneli için uygun değil, sadece test için

## 📝 Notlar

- Bot, sadece hesabınızın erişebildiği grupları tarayabilir
- Gelecekteki tarihler için tarama yapılamaz
- İlk kullanımda Telegram'a giriş yapmanız gerekir
- Session dosyası oluştuktan sonra tekrar giriş yapmanıza gerek yok

## 🐛 Sorun Giderme

Detaylı sorun giderme için [KURULUM.md](KURULUM.md) dosyasındaki "Sorun Giderme" bölümüne bakın.

## 📄 Lisans

Bu proje eğitim amaçlıdır. Kendi sorumluluğunuzda kullanın.

## 🤝 Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 İletişim

Sorularınız için GitHub Issues kullanabilirsiniz.
