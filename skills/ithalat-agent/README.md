# 🚢 İthalat Agent

**Türkiye→Birleşik Krallık ithalat şirketi için yapay zeka destekli şirket işletim sistemi (OS).**

## 🎯 Ne İşe Yarar?

Bir ithalat şirketini (Türkiye'den ürün alıp UK'ye satan) **tek kişi + AI ajanları** ile yönetmek için kapsamlı bir sistem:

- 🏢 **ERPNext entegrasyonu** — stok, sipariş, tedarikçi yönetimi (bkz. `scripts/erpnext_api.py`, `references/erpnext-setup.md`)
- 📧 **Gmail izleme** — tedarikçi ve müşteri e-postalarını otomatik işler (bkz. `scripts/gmail_monitor.py`)
- 🤖 **Sanal ajanlar** — araştırma ajanı (Bing haber/RSS), mesajlaşma altyapısı, görev zincirleri
- ✅ **Onay kuralları** — kritik işlemler için onay mekanizması (çoğaltma/onay hata ayıklama notları dahil)
- 📊 **Ticaret hazırlığı** — hibe eşleştirme, pazar araştırması, konu çıkarımı

## ⚙️ Nasıl Çalışır?

Skill, Hermes Agent'ın çoklu ajan yetenekleriyle ERPNext ve Gmail'i birbirine bağlar:

1. **Gmail monitörü** (`scripts/gmail_monitor.py`) tedarikçi e-postalarını tarar
2. **ERPNext API** (`scripts/erpnext_api.py`) sipariş/stok kayıtlarını yönetir
3. **Araştırma ajanı** pazar ve tedarikçi araştırması yapar (Bing haber arama, RSS)
4. **Onay kuralı** eşiği aşan işlemleri kullanıcıya iletir
5. **Sanal ajan mesajlaşması** (`references/agent-message-bus.md`) ajanlar arası iletişimi sağlar

## 📥 Kurulum

```bash
cp -r skills/ithalat-agent ~/.hermes/skills/
```

Gereksinimler: ERPNext kurulumu (bkz. `references/erpnext-setup.md`), Gmail erişimi (Himalaya/IMAP), Hermes çoklu ajan yapılandırması.

## 🧩 Özellikler

- ✅ Türkiye→UK ticaret akışına özel
- ✅ ERPNext + Gmail + ajan entegrasyonu
- ✅ Onay kuralları ve hata ayıklama rehberi
- ✅ Araştırma ajanı (Bing haber + RSS)
- ✅ HTML raporlar, hibe eşleştirme, ticaret hazırlığı

## 📄 Dosyalar

- `SKILL.md` — ana talimatlar
- `scripts/erpnext_api.py`, `scripts/gmail_monitor.py` — çalışan betikler
- `references/` — ERPNext kurulumu, onay hata ayıklama, araştırma ajanı, mesajlaşma, hibe eşleştirme ve daha fazlası (16 referans)

## ⚠️ Not

Bu skill, tek kişilik bir ithalat şirketini yönetmek için geliştirilmiş **uçtan uca bir sistem**dir. Kurulumu diğer skill'lere göre daha kapsamlıdır (ERPNext + Gmail + ajan konfigürasyonu).
