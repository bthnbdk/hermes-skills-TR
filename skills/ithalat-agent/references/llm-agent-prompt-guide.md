# LLM-Powered Agent Prompt Guide

Hybrid sistemde LLM-powered agent'lar `no_agent=False` cron job'larıdır. Her tick'te Hermes Agent bu prompt'u alır ve araçlarıyla (terminal, web_search, file) çalıştırır.

## Prompt Yapısı

Her prompt şunları içermeli:

1. **Rol tanımı** — Agent kim, ne yapar
2. **Adım adım talimat** — Önce ne, sonra ne
3. **ERPNext API örnekleri** — Doğrudan terminal'de çalıştırılabilir Python one-liner'ları
4. **Kurallar** — Mükerrer kayıt engelleme, sessiz kalma, vb.
5. **Çıktı formatı** — Ne zaman konuş, ne zaman sus

## Şablon

```markdown
## AGENT ADI — Görevin

KISA GÖREV TANIMI.

### Yapılacaklar:

1. **Adım 1: Kontrol**
```python
python3 -c "
import sys, os, json
sys.path.insert(0, os.path.expanduser('~/.hermes/scripts'))
from ithalat_erpnext_api import ERPNext
erp = ERPNext()
# ...
print(json.dumps(result))
"
```

2. **Adım 2: İşlem**
Açıkla + Python örneği ver.

### Kurallar:
- Mükerrer kayıt YAPMA — önce get_list ile kontrol et
- Hiçbir şey bulamazsan/bulunmazsa sessiz kal
- Token sınırına dikkat et — her tick'te max N işlem
- Başarılı işlemleri kısa özetle bildir
```

## Önemli İlkeler

| İlke | Açıklama |
|------|----------|
| **Self-contained** | Prompt her şeyi içermeli. LLM session'ı geçmişi bilmez. |
| **Skill yükle** | Cron job'a `skills=["ithalat-agent"]` ekle ki DocType'ları, API'yi, kuralları bilsin. |
| **Python one-liner** | ERPNext işlemleri için terminal'de direkt çalıştırılabilir Python kodu ver. |
| **Error handling** | try/except kullan, hata olursa sessizce geç. |
| **Token budget** | LLM agent'lar token harcar. Sık çalışanları (her 5dk) mekanik yap, seyrek çalışanları LLM yap. |
| **Silent default** | Sadece işlem yapınca konuş, boş tick'lerde sessiz ol. |

## Mevcut LLM Agent'lar

| Agent | Cron | Token/tick | Toolsets |
|-------|------|-----------|----------|
| Supplier Discovery | every 60m | ~5-10K | terminal, file, web |
| LLM Research | every 30m | ~5-15K | terminal, file, web |
| LLM Orchestrator | 0 */6 * * * | ~3-8K | terminal, file, web |

DeepSeek Flash ile maliyet: ~$0.15/M input, ~$0.60/M output. Günde ~50 çağrı ≈ $0.01-0.05/gün.
