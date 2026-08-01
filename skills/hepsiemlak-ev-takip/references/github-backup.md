# GitHub Yedekleme

Bu skill ve ilişkili script'ler GitHub'da yedeklenmektedir:

**Repo:** https://github.com/bthnbdk/turkce-ai-skillleri (Türkiye koleksiyonu)

## Repo Yapısı

```
turkce-ai-skillleri/
├── README.md
└── skills/
    └── hepsiemlak-ev-takip/  # Bu skill
```

## Güncelleme İş Akışı

Skill'de bir değişiklik yapıldığında (script güncellemesi, yeni kriter, vs.):

```bash
cd <repo_dizini>

# Güncel skill'i kopyala
cp -r <skill_yolu>/* skills/hepsiemlak-ev-takip/

# Commit & push
git add -A
git commit -m "Açıklayıcı mesaj"
git push
```

## Kimlik Doğrulama

Fine-grained PAT kullanılır (token: `github_pat_...`). Token'ın repo'ya erişimi olduğundan emin ol:
- https://github.com/settings/tokens → token → Repository access → `turkce-ai-skillleri`

## Notlar

- DB dosyası (`hepsiemlak.db`) `.gitignore` ile dışarıda bırakılır — sadece şema yedeklenir
- Script path: `<calisma_dizini>/hepsiemlak_fetch.py` (zamanlanmış görev)
- Skill path: `<skill_yolu>/hepsiemlak-ev-takip/`
