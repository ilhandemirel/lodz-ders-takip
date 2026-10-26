#!/usr/bin/env python3
"""Değişiklik ya da hata olursa e-posta (dosyalar ekli) ve WhatsApp (yazı) gönderir.

Kullanım: python3 takip/notify.py changed|failed
Gerekli GitHub Secrets: GMAIL_USER, GMAIL_APP_PASSWORD, MAIL_TO
İsteğe bağlı: CALLMEBOT_PHONE (+48..., +90...), CALLMEBOT_APIKEY
"""
import os, re, sys, smtplib, ssl, urllib.parse, urllib.request
from email.message import EmailMessage

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'out')
status = sys.argv[1]
report = open(os.path.join(OUT, 'rapor.txt'), encoding='utf-8').read().strip()
repo = os.environ.get('GITHUB_REPOSITORY', '')
owner, _, name = repo.partition('/')
site = f'https://{owner.lower()}.github.io/{name}/' if repo else ''

if status == 'changed':
    subject = "⚠️ Łódź ders programın değişti"
    body = (report + "\n\n"
            "Ekte yeni takvim dosyası (.ics) ve Excel var.\n"
            + (f"Takvim sayfası: {site}\n"
               f"Takvim aboneliği kurduysan iPhone takvimin kendiliğinden güncellenir: {site}lodz.ics\n" if site else ''))
elif status == 'test':
    subject = "Łódź ders takibi: test bildirimi"
    body = "Kurulum çalışıyor, Celcat okundu.\n\n" + report + (f"\n\nTakvim sayfası: {site}" if site else '')
else:
    subject = "Łódź ders takibi: bugün kontrol edilemedi"
    body = report + "\n\nYarın tekrar denenecek. Birkaç gün üst üste gelirse Claude'a haber ver."

# --- e-posta ---
user, pw, to = os.environ.get('GMAIL_USER'), os.environ.get('GMAIL_APP_PASSWORD'), os.environ.get('MAIL_TO')
if user and pw and to:
    msg = EmailMessage()
    msg['Subject'] = subject; msg['From'] = user; msg['To'] = to
    msg.set_content(body)
    if status in ('changed', 'test'):
        for fn, mt in (('lodz-ders-programi.ics', ('text', 'calendar')),
                       ('lodz-ders-programi.xlsx', ('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet'))):
            p = os.path.join(OUT, fn)
            if os.path.exists(p):
                msg.add_attachment(open(p, 'rb').read(), maintype=mt[0], subtype=mt[1], filename=fn)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=ssl.create_default_context()) as s:
        s.login(user, pw.replace(' ', ''))
        s.send_message(msg)
    print('e-posta gönderildi')
else:
    print('e-posta ayarları eksik, atlandı')

# --- WhatsApp (CallMeBot, sadece yazı) ---
phone, key = os.environ.get('CALLMEBOT_PHONE'), os.environ.get('CALLMEBOT_APIKEY')
if phone and key:
    text = f"*{subject}*\n\n{report}"
    if len(text) > 1500:
        text = text[:1450] + "\n… (devamı e-postada)"
    if status == 'changed' and site:
        text += f"\n\nSayfa: {site}"
    url = 'https://api.callmebot.com/whatsapp.php?' + urllib.parse.urlencode({'phone': phone, 'text': text, 'apikey': key})
    print('WhatsApp numarası:', phone[:4] + '…' + phone[-2:], '| apikey uzunluğu:', len(key))
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            body_txt = r.read().decode('utf-8', 'replace')
        clean = re.sub(r'<[^>]+>', ' ', body_txt); clean = re.sub(r'\s+', ' ', clean).strip()
        print('WhatsApp cevabı (CallMeBot):', clean[:400])
        if 'queued' not in clean.lower() and 'sent' not in clean.lower():
            print('::warning::WhatsApp mesajı gönderilemedi: ' + clean[:200])
    except Exception as e:
        print('::warning::WhatsApp gönderilemedi: ' + str(e))
else:
    print('::warning::WhatsApp ayarları yok (CALLMEBOT_PHONE / CALLMEBOT_APIKEY secret eksik), atlandı')
