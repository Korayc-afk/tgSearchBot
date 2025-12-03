"""
Telegram Grup Monitoring Botu - Tenant Bazlı
Belirli gruplarda kullanıcı adı, link ve bahsedilme durumunu izler
İstatistikler toplar: görüntülenme, paylaşım, emoji reaksiyonları
"""

import asyncio
import re
import sys
import io
import os
from datetime import datetime, timedelta, timezone
from telethon import TelegramClient, events
from telethon.tl.types import MessageEntityMention, MessageEntityUrl
from database import SessionLocal, Tenant, TenantConfig, Result, MessageStatistics
from tenant_manager import get_tenant_config

# Windows terminal encoding sorununu düzelt
if sys.platform == 'win32':
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        else:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except:
        pass

class TelegramMonitorTenant:
    def __init__(self, tenant_id):
        self.tenant_id = tenant_id
        self.db = SessionLocal()
        
        # Tenant bilgilerini al
        self.tenant = self.db.query(Tenant).filter_by(id=tenant_id).first()
        if not self.tenant:
            raise ValueError(f"Tenant bulunamadı: {tenant_id}")
        
        # Config'i al
        self.config = self.db.query(TenantConfig).filter_by(tenant_id=tenant_id).first()
        if not self.config:
            raise ValueError(f"Tenant config bulunamadı: {tenant_id}")
        
        # Telegram client oluştur
        api_id = self.config.api_id
        api_hash = self.config.get_api_hash()
        
        if not api_id or not api_hash:
            raise ValueError("API ID veya API Hash bulunamadı!")
        
        session_path = self.config.session_file_path or f'tenants/{self.tenant.slug}/session.session'
        self.client = TelegramClient(session_path.replace('.session', ''), api_id, api_hash)
        
        # Arama ayarları
        self.keywords_lower = [kw.lower().strip() for kw in (self.config.search_keywords or []) if kw and kw.strip()]
        self.links_lower = [link.lower().strip() for link in (self.config.search_links or []) if link and link.strip()]
        
        self.results = []
        
        # Debug
        if self.keywords_lower:
            print(f"[ARAMA] Aranacak kelimeler: {', '.join(self.keywords_lower)}")
        else:
            print("[UYARI] Aranacak kelime tanimlanmamis!")
        
        if self.links_lower:
            print(f"[ARAMA] Aranacak linkler: {', '.join(self.links_lower)}")
    
    async def start(self):
        """Botu başlat"""
        session_file = self.config.session_file_path or f'tenants/{self.tenant.slug}/session.session'
        
        if os.path.exists(session_file):
            await self.client.connect()
            if not await self.client.is_user_authorized():
                print("[HATA] Session dosyasi gecersiz! Lutfen web panelinden tekrar giris yapin.")
                return
            print("[OK] Mevcut session ile Telegram'a baglandi!")
        else:
            phone = self.config.phone_number
            if not phone:
                print("[HATA] Telefon numarasi bulunamadi!")
                return
            await self.client.start(phone=phone)
            print("[OK] Telegram'a basariyla baglandi!")
        
        await self.list_groups()
        
        scan_range = self.config.scan_time_range or '7days'
        print(f"\n[TARAMA] Gecmis mesajlar taranıyor ({scan_range})...")
        await self.scan_history_messages()
        
        print("\n[OK] Tarama tamamlandi! Bot kapatiliyor...")
        await self.client.disconnect()
        self.db.close()
    
    async def list_groups(self):
        """Katıldığınız grupları listele"""
        print("\n[GRUPLAR] Katildiginiz gruplar:")
        print("-" * 50)
        
        groups = []
        async for dialog in self.client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                groups.append({
                    'id': dialog.id,
                    'name': dialog.name,
                    'unread': dialog.unread_count
                })
                print(f"ID: {dialog.id} | İsim: {dialog.name}")
        
        print("-" * 50)
        print(f"\nToplam {len(groups)} grup bulundu.")
        
        group_ids = self.config.group_ids or []
        if not group_ids:
            print("\n[UYARI] GROUP_IDS bos! Hicbir grup izlenmeyecek.")
        else:
            print(f"\n[OK] {len(group_ids)} grup izleniyor:")
            for group_info in group_ids:
                if isinstance(group_info, dict):
                    group_id = group_info.get('id')
                    group_name = group_info.get('name', 'Bilinmeyen')
                else:
                    group_id = group_info
                    group_name = await self.get_group_name(group_id)
                print(f"   - {group_name} (ID: {group_id})")
    
    def get_scan_date(self):
        """Zaman aralığına göre başlangıç tarihini döndür"""
        scan_range = self.config.scan_time_range or '7days'
        now = datetime.now(timezone.utc)
        
        if scan_range == '1day':
            return now - timedelta(days=1)
        elif scan_range == '7days':
            return now - timedelta(days=7)
        elif scan_range == '30days':
            return now - timedelta(days=30)
        else:
            return now - timedelta(days=7)
    
    async def get_message_statistics(self, message):
        """Mesaj istatistiklerini al (görüntülenme, paylaşım, reaksiyonlar)"""
        stats = {
            'views_count': 0,
            'forwards_count': 0,
            'reactions_count': 0,
            'reactions_detail': {},
            'replies_count': 0
        }
        
        try:
            # Mesaj detaylarını al
            if hasattr(message, 'views'):
                stats['views_count'] = message.views or 0
            
            if hasattr(message, 'forwards'):
                stats['forwards_count'] = message.forwards or 0
            
            if hasattr(message, 'replies'):
                if hasattr(message.replies, 'replies'):
                    stats['replies_count'] = message.replies.replies or 0
            
            # Reaksiyonları al
            if hasattr(message, 'reactions'):
                if message.reactions:
                    total_reactions = 0
                    reactions_detail = {}
                    
                    for reaction in message.reactions.results:
                        emoji = reaction.reaction.emoticon if hasattr(reaction.reaction, 'emoticon') else str(reaction.reaction)
                        count = reaction.count or 0
                        total_reactions += count
                        reactions_detail[emoji] = count
                    
                    stats['reactions_count'] = total_reactions
                    stats['reactions_detail'] = reactions_detail
            
            # Eğer mesaj entity'si varsa, detaylı bilgi al
            try:
                full_message = await self.client.get_messages(message.peer_id, ids=message.id)
                if full_message:
                    if hasattr(full_message, 'views'):
                        stats['views_count'] = full_message.views or 0
                    if hasattr(full_message, 'forwards'):
                        stats['forwards_count'] = full_message.forwards or 0
            except:
                pass
                
        except Exception as e:
            print(f"[UYARI] İstatistik alma hatası: {e}")
        
        return stats
    
    async def analyze_message(self, message, chat_id):
        """Mesajı analiz et ve sonuçları kaydet"""
        try:
            message_text = message.message or ""
            
            if not message_text and hasattr(message, 'media') and message.media:
                if hasattr(message, 'raw_text'):
                    message_text = message.raw_text or ""
                elif hasattr(message, 'message'):
                    message_text = message.message or ""
            
            message_text_lower = message_text.lower()
            
            found_keywords = []
            found_links = []
            
            # Anahtar kelimeleri ara
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
                message_date = message.date if hasattr(message, 'date') else datetime.now(timezone.utc)
                
                # İstatistikleri al
                stats = await self.get_message_statistics(message)
                
                # Database'e kaydet
                result = Result(
                    tenant_id=self.tenant_id,
                    timestamp=message_date,
                    group_id=chat_id,
                    group_name=await self.get_group_name(chat_id),
                    message_id=message.id,
                    sender_id=message.sender_id if hasattr(message, 'sender_id') else None,
                    message_text=message_text,
                    found_keywords=found_keywords,
                    found_links=found_links,
                    message_link=f"https://t.me/c/{str(chat_id).replace('-100', '')}/{message.id}",
                    views_count=stats['views_count'],
                    forwards_count=stats['forwards_count'],
                    reactions_count=stats['reactions_count'],
                    reactions_detail=stats['reactions_detail'],
                    replies_count=stats['replies_count']
                )
                
                self.db.add(result)
                self.db.commit()
                
                # Dosyaya da kaydet (eski format uyumluluğu için)
                await self.save_result_to_file(result, stats)
                await self.print_result(result, stats)
                
                # Günlük istatistikleri güncelle
                await self.update_daily_statistics(message_date.date(), found_keywords, found_links, stats)
                
                return True
            return False
        except Exception as e:
            print(f"[HATA] Mesaj analiz hatasi: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def update_daily_statistics(self, date, found_keywords, found_links, stats):
        """Günlük istatistikleri güncelle"""
        try:
            # Tarihi datetime'a çevir
            date_start = datetime.combine(date, datetime.min.time()).replace(tzinfo=timezone.utc)
            
            # Mevcut istatistiği al veya oluştur
            daily_stat = self.db.query(MessageStatistics).filter_by(
                tenant_id=self.tenant_id,
                date=date_start
            ).first()
            
            if not daily_stat:
                daily_stat = MessageStatistics(
                    tenant_id=self.tenant_id,
                    date=date_start,
                    total_messages=0,
                    total_matches=1,
                    total_views=stats['views_count'],
                    total_forwards=stats['forwards_count'],
                    total_reactions=stats['reactions_count'],
                    keyword_stats={},
                    link_stats={}
                )
                self.db.add(daily_stat)
            else:
                daily_stat.total_matches += 1
                daily_stat.total_views += stats['views_count']
                daily_stat.total_forwards += stats['forwards_count']
                daily_stat.total_reactions += stats['reactions_count']
            
            # Kelime istatistiklerini güncelle
            keyword_stats = daily_stat.keyword_stats or {}
            for keyword in found_keywords:
                keyword_stats[keyword] = keyword_stats.get(keyword, 0) + 1
            
            # Link istatistiklerini güncelle
            link_stats = daily_stat.link_stats or {}
            for link in found_links:
                link_stats[link] = link_stats.get(link, 0) + 1
            
            daily_stat.keyword_stats = keyword_stats
            daily_stat.link_stats = link_stats
            daily_stat.updated_at = datetime.utcnow()
            
            self.db.commit()
        except Exception as e:
            print(f"[UYARI] İstatistik güncelleme hatası: {e}")
            self.db.rollback()
    
    async def scan_history_messages(self):
        """Geçmiş mesajları tara"""
        try:
            groups_to_scan = self.config.group_ids or []
            
            if not groups_to_scan:
                print("⚠️  Grup seçilmedi!")
                return
            
            print(f"📜 {len(groups_to_scan)} seçili grupta geçmiş mesajlar taranıyor...")
            
            for group_info in groups_to_scan:
                try:
                    if isinstance(group_info, dict):
                        group_id = group_info.get('id')
                        start_date_str = group_info.get('startDate')
                        end_date_str = group_info.get('endDate')
                    else:
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
                            scan_start_date = scan_start_date.replace(tzinfo=timezone.utc)
                        except:
                            pass
                    
                    if end_date_str:
                        try:
                            scan_end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
                            scan_end_date = scan_end_date.replace(hour=23, minute=59, second=59, tzinfo=timezone.utc)
                        except:
                            pass
                    
                    if not scan_start_date:
                        scan_start_date = self.get_scan_date()
                        if scan_start_date.tzinfo is None:
                            scan_start_date = scan_start_date.replace(tzinfo=timezone.utc)
                    
                    if not scan_end_date:
                        scan_end_date = datetime.now(timezone.utc)
                    
                    now = datetime.now(timezone.utc)
                    if scan_start_date > now:
                        print(f"  [UYARI] {group_id} için başlangıç tarihi gelecekte!")
                        continue
                    
                    if scan_end_date > now:
                        scan_end_date = now
                    
                    group_name = await self.get_group_name(group_id)
                    date_range = f"{scan_start_date.strftime('%Y-%m-%d')} - {scan_end_date.strftime('%Y-%m-%d')}"
                    print(f"  [TARAMA] {group_name} taranıyor... (Tarih: {date_range})")
                    
                    message_count = 0
                    match_count = 0
                    
                    async for message in self.client.iter_messages(
                        group_id, 
                        offset_date=scan_end_date,
                        reverse=False
                    ):
                        if scan_start_date and message.date < scan_start_date:
                            break
                        
                        if scan_end_date and message.date > scan_end_date:
                            continue
                        
                        message_count += 1
                        
                        match_found = await self.analyze_message(message, group_id)
                        if match_found:
                            match_count += 1
                        
                        if message_count % 50 == 0:
                            print(f"    [ILERLEME] {message_count} mesaj taranıyor... ({match_count} eşleşme)")
                    
                    print(f"    [TAMAMLANDI] {group_name}: {message_count} mesaj tarandı, {match_count} eşleşme bulundu")
                        
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
    
    async def get_group_name(self, chat_id):
        """Grup adını al"""
        try:
            entity = await self.client.get_entity(chat_id)
            return entity.title if hasattr(entity, 'title') else str(chat_id)
        except:
            return str(chat_id)
    
    async def save_result_to_file(self, result, stats):
        """Sonucu dosyaya kaydet (eski format uyumluluğu)"""
        try:
            results_file = self.config.results_file_path or f'tenants/{self.tenant.slug}/results.txt'
            os.makedirs(os.path.dirname(results_file), exist_ok=True)
            
            with open(results_file, 'a', encoding='utf-8') as f:
                f.write("\n" + "="*60 + "\n")
                f.write(f"Tarih: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Grup: {result.group_name} (ID: {result.group_id})\n")
                f.write(f"Mesaj ID: {result.message_id}\n")
                f.write(f"Gönderen ID: {result.sender_id}\n")
                if result.found_keywords:
                    f.write(f"Bulunan Kelimeler: {', '.join(result.found_keywords)}\n")
                if result.found_links:
                    f.write(f"Bulunan Linkler: {', '.join(result.found_links)}\n")
                f.write(f"Görüntülenme: {stats['views_count']}\n")
                f.write(f"Paylaşım: {stats['forwards_count']}\n")
                f.write(f"Reaksiyonlar: {stats['reactions_count']} {str(stats['reactions_detail'])}\n")
                f.write(f"Yanıtlar: {stats['replies_count']}\n")
                f.write(f"Mesaj: {result.message_text}\n")
                f.write(f"Link: {result.message_link}\n")
        except Exception as e:
            print(f"[HATA] Dosyaya kaydetme hatasi: {e}")
    
    async def print_result(self, result, stats):
        """Sonucu konsola yazdır"""
        print("\n" + "=" * 60)
        print(f"[BULUNDU] Tarih: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"[GRUP] {result.group_name}")
        print(f"[MESAJ_ID] {result.message_id}")
        if result.found_keywords:
            print(f"[KELIMELER] {', '.join(result.found_keywords)}")
        if result.found_links:
            print(f"[LINKLER] {', '.join(result.found_links)}")
        print(f"[İSTATİSTİKLER] 👁️ {stats['views_count']} | 🔄 {stats['forwards_count']} | ❤️ {stats['reactions_count']} | 💬 {stats['replies_count']}")
        if stats['reactions_detail']:
            print(f"[EMOJİLER] {stats['reactions_detail']}")
        print(f"[MESAJ] {result.message_text[:100]}...")
        print(f"[LINK] {result.message_link}")
        print("=" * 60 + "\n")

async def main(tenant_id):
    """Ana fonksiyon"""
    try:
        monitor = TelegramMonitorTenant(tenant_id)
        await monitor.start()
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print("Kullanım: python tg_monitor_tenant.py <tenant_id>")
        sys.exit(1)
    
    tenant_id = int(sys.argv[1])
    try:
        asyncio.run(main(tenant_id))
    except KeyboardInterrupt:
        print("\n\n⏹️  Bot durduruldu.")
    except Exception as e:
        print(f"\n❌ Hata: {e}")

