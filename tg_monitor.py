"""
Telegram Grup Monitoring Botu
Belirli gruplarda kullanıcı adı, link ve bahsedilme durumunu izler
"""

import asyncio
import re
import sys
import io
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityMention, MessageEntityUrl
from config_manager import get_config

# Windows terminal encoding sorununu düzelt
if sys.platform == 'win32':
    try:
        # Python 3.7+ için
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        else:
            # Eski Python versiyonları için
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass  # Encoding zorlanamazsa devam et

class TelegramMonitor:
    def __init__(self):
        config = get_config()
        self.client = TelegramClient('session', config.API_ID, config.API_HASH)
        self.config = config
        self.results = []
        # Config'den kelimeleri ve linkleri yükle (boş olabilir)
        search_keywords = getattr(config, 'SEARCH_KEYWORDS', []) or []
        search_links = getattr(config, 'SEARCH_LINKS', []) or []
        self.keywords_lower = [kw.lower().strip() for kw in search_keywords if kw and kw.strip()]
        self.links_lower = [link.lower().strip() for link in search_links if link and link.strip()]
        
        # Debug: Hangi kelimeler aranıyor göster
        if self.keywords_lower:
            print(f"[ARAMA] Aranacak kelimeler: {', '.join(self.keywords_lower)}")
        else:
            print("[UYARI] Aranacak kelime tanimlanmamis! Lutfen web panelinden kelime ekleyin.")
        
        if self.links_lower:
            print(f"[ARAMA] Aranacak linkler: {', '.join(self.links_lower)}")
        else:
            print("[INFO] Aranacak link tanimlanmamis.")
        
    async def start(self):
        """Botu başlat"""
        import os
        
        # Session dosyası var mı kontrol et
        session_file = 'session.session'
        if os.path.exists(session_file):
            # Session varsa direkt bağlan
            await self.client.connect()
            if not await self.client.is_user_authorized():
                print("[HATA] Session dosyasi gecersiz! Lutfen web panelinden tekrar giris yapin.")
                return
            print("[OK] Mevcut session ile Telegram'a baglandi!")
        else:
            # Session yoksa telefon numarası ile başlat
            if not self.config.PHONE_NUMBER:
                print("[HATA] Telefon numarasi bulunamadi! Lutfen web panelinden ayarlari yapin.")
                return
            await self.client.start(phone=self.config.PHONE_NUMBER)
            print("[OK] Telegram'a basariyla baglandi!")
        
        # Grup listesini göster
        await self.list_groups()
        
        # Geçmiş mesajları tara
        scan_range = getattr(self.config, 'SCAN_TIME_RANGE', '7days')
        print(f"\n[TARAMA] Gecmis mesajlar taranıyor ({scan_range})...")
        await self.scan_history_messages()
        
        # Tarama modunda sadece geçmiş mesajları tara, yeni mesajları izleme
        # Event handler'ı kaydetme - sadece tarama yapıyoruz
        
        print("\n[OK] Tarama tamamlandi! Bot kapatiliyor...")
        
        # Tarama modunda botu kapat (sadece geçmiş mesajları taradık)
        await self.client.disconnect()
    
    async def list_groups(self):
        """Katıldığınız grupları listele"""
        print("\n[GRUPLAR] Katildiginiz gruplar (Acik ve Kapali):")
        print("-" * 50)
        print("[INFO] Not: Bot, sizin hesabinizla calistigi icin erisebildiginiz TUM gruplari gorebilir")
        print("-" * 50)
        
        groups = []
        async for dialog in self.client.iter_dialogs():
            if dialog.is_group:
                groups.append({
                    'id': dialog.id,
                    'name': dialog.name,
                    'unread': dialog.unread_count
                })
                print(f"ID: {dialog.id} | İsim: {dialog.name}")
        
        print("-" * 50)
        print(f"\nToplam {len(groups)} grup bulundu.")
        
        if not self.config.GROUP_IDS:
            print("\n[UYARI] GROUP_IDS bos! Hicbir grup izlenmeyecek.")
            print("Izlemek istediginiz grup ID'lerini web panelinden secip ekleyin.")
            print("Gruplar sekmesinden 'Gruplari Yukle' butonuna tiklayip gruplari secebilirsiniz.")
        else:
            print(f"\n[OK] {len(self.config.GROUP_IDS)} grup izleniyor:")
            for group_info in self.config.GROUP_IDS:
                try:
                    # Grup bilgisini parse et (obje veya sadece ID olabilir)
                    if isinstance(group_info, dict):
                        group_id = group_info.get('id')
                    else:
                        group_id = group_info
                    
                    if group_id:
                        group_name = await self.get_group_name(group_id)
                        print(f"   - {group_name} (ID: {group_id})")
                    else:
                        print(f"   - Geçersiz grup bilgisi: {group_info}")
                except Exception as e:
                    print(f"   - ID: {group_info} (Hata: {e})")
    
    def get_scan_date(self):
        """Zaman aralığına göre başlangıç tarihini döndür"""
        scan_range = getattr(self.config, 'SCAN_TIME_RANGE', '7days')
        now = datetime.now(timezone.utc)
        
        if scan_range == '1day':
            return now - timedelta(days=1)
        elif scan_range == '7days':
            return now - timedelta(days=7)
        elif scan_range == '30days':
            return now - timedelta(days=30)
        else:
            # Varsayılan olarak 7 gün
            return now - timedelta(days=7)
    
    async def analyze_message(self, message, chat_id):
        """Mesajı analiz et ve sonuçları kaydet"""
        try:
            message_text = message.message or ""
            
            # Eğer mesaj boşsa ve medya varsa, caption'ı kontrol et
            if not message_text and hasattr(message, 'media') and message.media:
                if hasattr(message, 'raw_text'):
                    message_text = message.raw_text or ""
                elif hasattr(message, 'message'):
                    message_text = message.message or ""
            
            message_text_lower = message_text.lower()
            
            # Mesajı analiz et
            found_keywords = []
            found_links = []
            
            # Anahtar kelimeleri ara (case-insensitive)
            for keyword in self.keywords_lower:
                if keyword and keyword in message_text_lower:
                    found_keywords.append(keyword)
            
            # Linkleri ara
            for link in self.links_lower:
                if link and link in message_text_lower:
                    found_links.append(link)
            
            # Mesajdaki tüm linkleri çıkar
            if message.entities:
                for entity in message.entities:
                    if isinstance(entity, MessageEntityUrl):
                        url = message_text[entity.offset:entity.offset + entity.length]
                        for search_link in self.links_lower:
                            if search_link and search_link in url.lower():
                                found_links.append(url)
            
            # Eğer bir şey bulunduysa kaydet
            if found_keywords or found_links:
                message_date = message.date if hasattr(message, 'date') else datetime.now()
                result = {
                    'timestamp': message_date.strftime('%Y-%m-%d %H:%M:%S'),
                    'group_id': chat_id,
                    'group_name': await self.get_group_name(chat_id),
                    'message_id': message.id,
                    'sender_id': message.sender_id if hasattr(message, 'sender_id') else None,
                    'message_text': message_text,  # Tam mesaj
                    'found_keywords': found_keywords,
                    'found_links': found_links,
                    'message_link': f"https://t.me/c/{str(chat_id).replace('-100', '')}/{message.id}"
                }
                
                self.results.append(result)
                await self.save_result(result)
                await self.print_result(result)
                return True  # Eşleşme bulundu
            return False  # Eşleşme bulunamadı
        except Exception as e:
            print(f"[HATA] Mesaj analiz hatasi: {e}")
            return False
    
    async def scan_history_messages(self):
        """Geçmiş mesajları tara"""
        try:
            groups_to_scan = self.config.GROUP_IDS if self.config.GROUP_IDS else []
            
            # Eğer grup seçilmemişse hiçbir şey yapma
            if not groups_to_scan:
                print("⚠️  Grup seçilmedi! Geçmiş mesaj taraması yapılmayacak.")
                print("ℹ️  Gruplar sekmesinden izlemek istediğiniz grupları seçin.")
                return
            
            print(f"📜 {len(groups_to_scan)} seçili grupta geçmiş mesajlar taranıyor...")
            print("ℹ️  Not: Sadece seçtiğiniz gruplar taranacak")
            
            for group_info in groups_to_scan:
                try:
                    # Grup bilgisini parse et (obje veya sadece ID olabilir)
                    if isinstance(group_info, dict):
                        group_id = group_info.get('id')
                        start_date_str = group_info.get('startDate')
                        end_date_str = group_info.get('endDate')
                    else:
                        # Eski format: sadece ID
                        group_id = group_info
                        start_date_str = None
                        end_date_str = None
                    
                    if not group_id:
                        continue
                    
                    # Tarih aralığını parse et
                    scan_start_date = None
                    scan_end_date = None
                    
                    if start_date_str:
                        try:
                            scan_start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
                            # Timezone-aware yap (UTC)
                            scan_start_date = scan_start_date.replace(tzinfo=timezone.utc)
                        except:
                            pass
                    
                    if end_date_str:
                        try:
                            scan_end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                            # Bitiş tarihini günün sonuna ayarla ve timezone-aware yap (UTC)
                            scan_end_date = scan_end_date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                        except:
                            pass
                    
                    # Eğer tarih aralığı yoksa, zaman aralığına göre hesapla
                    if not scan_start_date:
                        scan_start_date = self.get_scan_date()
                        # Timezone-aware yap
                        if scan_start_date.tzinfo is None:
                            scan_start_date = scan_start_date.replace(tzinfo=timezone.utc)
                    
                    if not scan_end_date:
                        scan_end_date = datetime.now(timezone.utc)
                    
                    # Tarih kontrolü - gelecekteki tarihler için uyarı
                    now = datetime.now(timezone.utc)
                    if scan_start_date > now:
                        print(f"  [UYARI] {group_id} icin baslangic tarihi gelecekte ({scan_start_date.strftime('%Y-%m-%d')})! Bu tarih henuz gelmedi.")
                        print(f"  [INFO] Su anki tarih: {now.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"  [ATLANDI] Bu grup atlaniyor...")
                        continue
                    
                    if scan_end_date > now:
                        print(f"  [UYARI] {group_id} icin bitis tarihi gelecekte ({scan_end_date.strftime('%Y-%m-%d')})! Bitis tarihi su anki tarihe ayarlaniyor.")
                        scan_end_date = now
                    
                    group_name = await self.get_group_name(group_id)
                    date_range = f"{scan_start_date.strftime('%Y-%m-%d')} - {scan_end_date.strftime('%Y-%m-%d')}"
                    print(f"  [TARAMA] {group_name} taranıyor... (Tarih: {date_range})")
                    print(f"  [ARAMA] Aranacak kelimeler: {', '.join(self.keywords_lower) if self.keywords_lower else 'YOK'}")
                    
                    # Geçmiş mesajları çek
                    # iter_messages varsayılan olarak en yeni mesajlardan başlar ve geçmişe doğru gider
                    message_count = 0
                    match_count = 0
                    
                    print(f"  [MESAJLAR] Mesajlar cekiliyor: {scan_start_date.strftime('%Y-%m-%d')} ile {scan_end_date.strftime('%Y-%m-%d')} arasi...")
                    
                    # iter_messages ile mesajları çek
                    # offset_date: Bu tarihten itibaren mesajları getir (geçmişe doğru)
                    # min_date ve max_date kullanarak tarih aralığını sınırla
                    try:
                        async for message in self.client.iter_messages(
                            group_id, 
                            offset_date=scan_end_date,
                            reverse=False  # En yeni mesajlardan başla
                        ):
                            # Eğer başlangıç tarihinden eski bir mesaj gelirse dur
                            if scan_start_date and message.date < scan_start_date:
                                print(f"    [DUR] Baslangic tarihine ulasildi, tarama durduruluyor.")
                                break
                            
                            # Eğer bitiş tarihinden yeni bir mesaj gelirse atla
                            if scan_end_date and message.date > scan_end_date:
                                continue
                            
                            message_count += 1
                            
                            # İlk 5 mesajı debug için göster
                            if message_count <= 5:
                                msg_preview = (message.message or "")[:50]
                                print(f"    [DEBUG] Mesaj #{message_count}: {message.date.strftime('%Y-%m-%d %H:%M')} - {msg_preview}...")
                            
                            # Mesajı analiz et ve eşleşme sayısını kontrol et
                            match_found = await self.analyze_message(message, group_id)
                            if match_found:
                                match_count += 1
                                print(f"    [BULUNDU] Eslesme bulundu! Mesaj #{message_count}")
                            
                            # Her 50 mesajda bir ilerleme göster
                            if message_count % 50 == 0:
                                print(f"    [ILERLEME] {message_count} mesaj taranıyor... ({match_count} eslesme bulundu)")
                        
                        print(f"    [TAMAMLANDI] {group_name}: {message_count} mesaj tarandı, {match_count} eslesme bulundu")
                        
                        if message_count == 0:
                            print(f"    [UYARI] Bu tarih araliginda hic mesaj bulunamadi!")
                            print(f"    [OZET] Grup ID: {group_id}, Tarih: {date_range}")
                    except Exception as iter_error:
                        print(f"    [HATA] Mesaj cekme hatasi: {iter_error}")
                        import traceback
                        traceback.print_exc()
                        
                except Exception as e:
                    print(f"  [HATA] {group_info} grubunda hata: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            print(f"[TAMAMLANDI] Gecmis mesaj taramasi tamamlandi! {len(self.results)} sonuc bulundu.\n")
        except Exception as e:
            print(f"[HATA] Gecmis mesaj tarama hatasi: {e}")
            import traceback
            traceback.print_exc()
    
    async def message_handler(self, event):
        """Yeni mesaj geldiğinde çalışır"""
        try:
            # Sadece izlenen gruplarda kontrol et
            chat_id = event.chat_id
            
            # GROUP_IDS boşsa hiçbir şey izleme
            if not self.config.GROUP_IDS:
                return
            
            # Seçilen gruplardan biri değilse izleme
            # GROUP_IDS artık obje array'i olabilir, ID'leri çıkar
            group_ids = []
            for group_info in self.config.GROUP_IDS:
                if isinstance(group_info, dict):
                    group_ids.append(group_info.get('id'))
                else:
                    group_ids.append(group_info)
            
            if chat_id not in group_ids:
                return
            
            message = event.message
            await self.analyze_message(message, chat_id)
        
        except Exception as e:
            print(f"[HATA] Hata: {e}")
    
    async def get_group_name(self, chat_id):
        """Grup adını al"""
        try:
            entity = await self.client.get_entity(chat_id)
            return entity.title if hasattr(entity, 'title') else str(chat_id)
        except:
            return str(chat_id)
    
    async def save_result(self, result):
        """Sonucu dosyaya kaydet"""
        try:
            with open(self.config.RESULTS_FILE, 'a', encoding='utf-8') as f:
                f.write("\n" + "="*60 + "\n")
                f.write(f"Tarih: {result['timestamp']}\n")
                f.write(f"Grup: {result['group_name']} (ID: {result['group_id']})\n")
                f.write(f"Mesaj ID: {result['message_id']}\n")
                f.write(f"Gönderen ID: {result['sender_id']}\n")
                if result['found_keywords']:
                    f.write(f"Bulunan Kelimeler: {', '.join(result['found_keywords'])}\n")
                if result['found_links']:
                    f.write(f"Bulunan Linkler: {', '.join(result['found_links'])}\n")
                f.write(f"Mesaj: {result['message_text']}\n")
                f.write(f"Link: {result['message_link']}\n")
        except Exception as e:
            print(f"[HATA] Dosyaya kaydetme hatasi: {e}")
    
    async def print_result(self, result):
        """Sonucu konsola yazdır"""
        print("\n" + "=" * 60)
        print(f"[BULUNDU] Tarih: {result['timestamp']}")
        print(f"[GRUP] {result['group_name']}")
        print(f"[MESAJ_ID] {result['message_id']}")
        if result['found_keywords']:
            print(f"[KELIMELER] Bulunan Kelimeler: {', '.join(result['found_keywords'])}")
        if result['found_links']:
            print(f"[LINKLER] Bulunan Linkler: {', '.join(result['found_links'])}")
        print(f"[MESAJ] {result['message_text'][:100]}...")
        print(f"[LINK] {result['message_link']}")
        print("=" * 60 + "\n")

async def main():
    monitor = TelegramMonitor()
    await monitor.start()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot durduruldu.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

