#!/usr/bin/env python3
"""GitHub Actions'ta her gün çalışır: Celcat'ı çeker, programı üretir, değişiklik varsa dosyaları günceller.

Çıktı: GITHUB_OUTPUT'a status=changed|nochange|failed yazar.
"""
import json, os, shutil, subprocess, sys, datetime as dt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = os.path.join(ROOT, 'takip')
OUT = os.path.join(ROOT, 'out')
os.makedirs(OUT, exist_ok=True)


def set_output(**kw):
    p = os.environ.get('GITHUB_OUTPUT')
    if p:
        with open(p, 'a') as f:
            for k, v in kw.items():
                f.write(f'{k}={v}\n')
    print(kw)


def wrap(html):
    if html.lstrip().lower().startswith('<!doctype'):
        return html
    return ('<!doctype html><html lang="tr"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">'
            '<style>body{margin:0}</style></head><body>' + html + '</body></html>')


events = os.path.join(OUT, 'events.json')
if os.environ.get('TAKIP_EVENTS_FILE'):   # sadece test için
    shutil.copy(os.environ['TAKIP_EVENTS_FILE'], events)
    r = subprocess.CompletedProcess([], 0, 'test verisi', '')
else:
    r = subprocess.run([sys.executable, os.path.join(T, 'fetch.py'), events], capture_output=True, text=True)
print(r.stdout, r.stderr)
with open(os.path.join(ROOT, 'state', 'last_check.txt'), 'w') as f:
    f.write(dt.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC') + (' OK' if r.returncode == 0 else ' HATA') + '\n')
if r.returncode != 0:
    open(os.path.join(OUT, 'rapor.txt'), 'w', encoding='utf-8').write(
        "Bugün Celcat'a bağlanılamadı, program kontrol edilemedi.\nSebep: " + (r.stderr.strip() or 'bilinmiyor') + '\n')
    set_output(status='failed')
    sys.exit(0)

r = subprocess.run([sys.executable, os.path.join(T, 'takip.py'), '--events', events,
                    '--config', os.path.join(T, 'config.json'), '--template', os.path.join(T, 'template.html'),
                    '--prev', os.path.join(ROOT, 'state', 'snapshot.json'), '--out', OUT], capture_output=True, text=True)
print(r.stdout, r.stderr)
if r.returncode != 0:
    open(os.path.join(OUT, 'rapor.txt'), 'w', encoding='utf-8').write('Program üretilirken hata oluştu:\n' + r.stderr[-1500:] + '\n')
    set_output(status='failed')
    sys.exit(0)

res = json.load(open(os.path.join(OUT, 'sonuc.json')))
if res['changed'] or res['first_run']:
    shutil.copy(os.path.join(OUT, 'snapshot.json'), os.path.join(ROOT, 'state', 'snapshot.json'))
    shutil.copy(os.path.join(OUT, 'lodz-ders-programi.ics'), os.path.join(ROOT, 'docs', 'lodz.ics'))
    shutil.copy(os.path.join(OUT, 'lodz-ders-programi.xlsx'), os.path.join(ROOT, 'docs', 'lodz-ders-programi.xlsx'))
    page = open(os.path.join(OUT, 'page.html'), encoding='utf-8').read()
    open(os.path.join(ROOT, 'docs', 'index.html'), 'w', encoding='utf-8').write(wrap(page))
    set_output(status='changed' if res['changed'] else 'nochange')
else:
    set_output(status='nochange')
