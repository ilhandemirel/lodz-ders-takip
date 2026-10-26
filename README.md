# Łódź ders takibi

Her akşam 19:52'de (Łódź saati) GitHub'ın sunucularında çalışır. Bilgisayarının açık olmasına gerek yoktur.

1. Celcat'tan derslerini çeker (sadece senin gruplarını).
2. Bir önceki günle karşılaştırır: saat, salon, grup, yeni ya da iptal edilen ders.
3. Değişiklik varsa:
   - E-postana yeni takvim dosyası (.ics) ve Excel'i yollar.
   - WhatsApp'a kısa bir özet atar.
   - `docs/` klasöründeki takvim, Excel ve sayfayı günceller.
4. Değişiklik yoksa sessiz kalır.

## Kurulum (bir kere, ~10 dakika)

### 1. Repoyu oluştur
- GitHub'da **New repository** → adı `lodz-ders-takip` → **Public**.
  - Takvim aboneliği için public olmalı. İçinde adın ya da öğrenci numaran yok, sadece ders saatleri var.
- Bu klasördeki her şeyi yükle (`.github` klasörü dahil):
  ```
  cd lodz-ders-takip
  git init -b main
  git add .
  git commit -m "Ders takibi"
  git remote add origin https://github.com/KULLANICI_ADIN/lodz-ders-takip.git
  git push -u origin main
  ```
  - Ya da repo sayfasında **Add file → Upload files** ile klasörün içindekileri sürükleyip bırak.

### 2. Şifreleri ekle (Settings → Secrets and variables → Actions → New repository secret)

| Ad | Değer |
|---|---|
| `GMAIL_USER` | Gmail adresin (ör. ilhandemirel23@gmail.com) |
| `GMAIL_APP_PASSWORD` | Google **uygulama şifresi**, normal şifren değil. https://myaccount.google.com/apppasswords → ad: "ders takip" → çıkan 16 haneli şifre. İki adımlı doğrulama açık olmalı. |
| `MAIL_TO` | Bildirimin geleceği adres (aynı Gmail olabilir) |
| `CALLMEBOT_PHONE` | WhatsApp numaran, ülke koduyla: `+90...` ya da `+48...` |
| `CALLMEBOT_APIKEY` | Aşağıdaki WhatsApp adımından gelen anahtar |

**WhatsApp anahtarı (CallMeBot, ücretsiz, sadece yazı):**
1. **+34 694 25 79 52** numarasını rehbere kaydet.
2. WhatsApp'tan bu numaraya şu mesajı gönder: `I allow callmebot to send me messages`
3. Gelen cevaptaki APIKEY'i `CALLMEBOT_APIKEY` olarak ekle.

WhatsApp istemiyorsan son iki şifreyi ekleme, sadece e-posta gelir.

### 3. Sayfayı aç (Settings → Pages)
- Source: **Deploy from a branch** → Branch: `main`, klasör: `/docs` → Save.
- Birkaç dakika sonra sayfan şu adreste açılır: `https://KULLANICI_ADIN.github.io/lodz-ders-takip/`

### 4. Dene
- **Actions** sekmesi → **Ders takibi** → **Run workflow** → "test bildirimi" kutusunu işaretle → Run.
- 1–2 dakika içinde test e-postası ve WhatsApp mesajı gelmeli.
- Kırmızı ✗ çıkarsa logu Claude'a gönder.

### 5. iPhone takvimine abone ol (dosya yükleme derdi biter)
- Ayarlar → Takvim → Hesaplar → Hesap Ekle → Diğer → **Abone Olunan Takvim Ekle**
- Adres: `https://KULLANICI_ADIN.github.io/lodz-ders-takip/lodz.ics`
- Daha önce elle yüklediğin "Łódź Dersler" takvimini sil, yoksa dersler çift görünür.
- iPhone abone olunan takvimi kendisi yeniler. Program değişince takvimin de değişir.

## Grup değiştirirsen
`takip/fetch.py` içindeki `MY` listesini değiştir ya da Claude'a "grubum değişti" de.
Bir dersi tek bir gün programdan çıkarmak için `takip/config.json` → `skip` kullanılır.

## Sorun giderme
- **Push hatası (403):** Settings → Actions → General → Workflow permissions → **Read and write permissions**.
- **"kontrol edilemedi" e-postası:** Celcat o an cevap vermemiş olabilir. Birkaç gün üst üste gelirse Claude'a haber ver.
- **60 gün kuralı:** GitHub, uzun süre hareketsiz kalan repoların zamanlanmış görevlerini durdurur. Bu sistem her gün `state/last_check.txt` dosyasını güncellediği için durmaz.
