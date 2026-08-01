# GitHub Yedekleme

Bu skill ve ilişkili script'ler GitHub'da yedeklenmektedir:

**Repo:** https://github.com/bthnbdk/hermes-skills

## Repo Yapısı

```
hermes-skills/
├── README.md
├── reinstall.sh              # Tek komutla yeniden kurulum
├── scripts/
│   └── hepsiemlak_fetch.py   # Canlı script
├── schemas/
│   └── hepsiemlak_schema.sql # DB şeması (referans)
└── skills/
    └── devops/
        └── hepsiemlak-ev-takip/  # Bu skill
```

## Güncelleme İş Akışı

Skill'de bir değişiklik yapıldığında (script güncellemesi, yeni kriter, vs.):

```bash
cd ~/hermes-skills

# Güncel skill'i kopyala
cp -r ~/.hermes/skills/devops/hepsiemlak-ev-takip/* skills/devops/hepsiemlak-ev-takip/
cp ~/.hermes/scripts/hepsiemlak_fetch.py scripts/

# Commit & push
git add -A
git commit -m "Açıklayıcı mesaj"
git push
```

## Kimlik Doğrulama

Fine-grained PAT kullanılır (token: `github_pat_...`). Token'ın repo'ya erişimi olduğundan emin ol:
- https://github.com/settings/tokens → token → Repository access → `hermes-skills`

## Notlar

- DB dosyası (`hepsiemlak.db`) `.gitignore` ile dışarıda bırakılır — sadece şema yedeklenir
- Script path: `~/.hermes/scripts/hepsiemlak_fetch.py` (cron `no_agent` modu)
- Skill path: `~/.hermes/skills/devops/hepsiemlak-ev-takip/`
