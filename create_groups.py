"""
Grup oluşturma scripti
Belirtilen grupları oluşturur
"""

import os
import sys
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()

from database import SessionLocal, Tenant, User
from tenant_manager import create_tenant

def create_groups():
    """Belirtilen grupları oluştur"""
    groups = [
        "padişah",
        "gala",
        "hit",
        "pipo",
        "office"
    ]
    
    db = SessionLocal()
    try:
        # Süper admin kullanıcısını bul
        super_admin = db.query(User).filter_by(role='super_admin').first()
        if not super_admin:
            print("❌ Süper admin kullanıcısı bulunamadı!")
            return
        
        print(f"✅ Süper admin bulundu: {super_admin.username} (ID: {super_admin.id})")
        
        # "vuradak qeqwe" grubunu sil
        vuradak_tenant = db.query(Tenant).filter_by(name="vuradak qeqwe").first()
        if vuradak_tenant:
            print(f"🗑️  'vuradak qeqwe' grubu bulundu, siliniyor...")
            db.delete(vuradak_tenant)
            db.commit()
            print(f"✅ 'vuradak qeqwe' grubu silindi!")
        else:
            print(f"ℹ️  'vuradak qeqwe' grubu bulunamadı (zaten silinmiş olabilir)")
        
        # Yeni grupları oluştur
        created_count = 0
        for group_name in groups:
            # Grup zaten var mı kontrol et
            existing = db.query(Tenant).filter_by(name=group_name).first()
            if existing:
                print(f"⚠️  '{group_name}' grubu zaten mevcut (ID: {existing.id})")
            else:
                tenant = create_tenant(group_name, super_admin.id)
                if tenant:
                    print(f"✅ '{group_name}' grubu oluşturuldu (ID: {tenant.id}, Slug: {tenant.slug})")
                    created_count += 1
                else:
                    print(f"❌ '{group_name}' grubu oluşturulamadı!")
        
        print(f"\n🎉 İşlem tamamlandı! {created_count} yeni grup oluşturuldu.")
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == '__main__':
    print("🔧 Gruplar oluşturuluyor...")
    create_groups()

