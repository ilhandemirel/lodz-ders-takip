#!/usr/bin/env python3
"""Celcat'tan İlhan'ın derslerini çeker (tarayıcı gerekmez).

Kullanım: python3 takip/fetch.py OUT.json
Başarısız olursa çıkış kodu 2 ve stderr'de sebep.
"""
import json, sys, time, datetime as dt
import requests

BASE = 'https://lodz.celcat.cloud/cal/'
R = 'WBmtIfKE4JASA8wP0'          # Celcat paylaşım linkindeki r= değeri
MODS = {'3434': 'PMM', '3536': 'DS', '3551': 'IoT', '3560': 'IT', '3569': 'WC', '3646': 'ML', '3763': 'CC'}
PREFIX = {'PMM': '3BST', 'DS': '3CS', 'IoT': '5CS', 'IT': '1ETE', 'WC': '5ETE', 'ML': '5MMDA', 'CC': '5IT'}
# Ders + tür -> senin grubun (Lecture'lar herkes için)
MY = {
    'CC|Project': ['5IT - ERASMUS 1', '5IT - ERASMUS 2'],
    'IoT|Laboratory': ['5CS - Erasmus 2'],
    'ML|Project': ['5MMDA - group 1'],
    'WC|Laboratory': ['5ETE - Erasmus 1'],
    'DS|Laboratory': ['3CS - ERASMUS'],
    'DS|Tutorials': ['3CS - group 1', '3CS - group 2'],
    'PMM|Laboratory': ['3BSTen/fr - ERASMUS 1'],
    'IT|Laboratory': ['1ETE - group 2'],
}


def fetch_raw():
    s = requests.Session()
    s.headers.update({
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Referer': f'{BASE}?r={R}',
        'Origin': 'https://lodz.celcat.cloud',
    })
    last = ''
    for attempt in range(3):
        try:
            s.get(BASE, params={'r': R}, timeout=30)
            s.post(BASE + 'session', json={}, timeout=30)
            s.get(BASE + 'resources/ids', params=[('1000', k) for k in MODS], timeout=30)
            r = s.get(BASE + 'events', params=[(k, '1000') for k in MODS], timeout=60)
            if r.status_code == 200 and r.text.lstrip().startswith('{'):
                return r.json()
            last = f'events cevabı: HTTP {r.status_code}, {len(r.text)} bayt'
        except requests.RequestException as e:
            last = f'bağlantı hatası: {e}'
        time.sleep(20 * (attempt + 1))
    raise RuntimeError(last)


def extract(j):
    def N(t, i):
        x = (j.get('names', {}).get(t) or {}).get(str(i))
        return ((x.get('name') or x.get('uniqueName') or '') if x else str(i)).strip()
    out = []
    for e in j['events']:
        k = MODS.get(str(e['modules'][0]['id']))
        if not k:
            continue
        t = N('1105', e['eventCategoryId'])
        gs = [N('1001', s['id']) for s in (e.get('studentSets') or [])]
        if t == 'Lecture':
            mine = ['herkes'] if any(g.startswith(PREFIX[k]) for g in gs) else []
        else:
            want = MY.get(f'{k}|{t}', [])
            mine = [g for g in gs if g in want]
        if not mine:
            continue
        ch = e.get('dateChanged')
        out.append(dict(
            id=str(e['eventId']), k=k, t=t, d=e['dayOfWeek'], s=e['startTime'] // 60000, u=e['duration'],
            w=''.join('1' if x else '0' for x in e['weeks']), g=', '.join(mine), cel='; '.join(gs),
            r=' / '.join(N('1003', f['id']) for f in (e.get('facilities') or [])),
            p=', '.join(N('1002', f['id']) for f in (e.get('staff') or [])),
            n=e.get('eventName') or '', x=bool(e.get('suspended')),
            ch=dt.datetime.utcfromtimestamp(ch / 1000).strftime('%Y-%m-%dT%H:%M') if ch else ''))
    last = max((e.get('dateChanged') or 0) for e in j['events']) if j['events'] else 0
    return dict(fetched=dt.datetime.utcnow().isoformat() + 'Z',
                lastChangeAll=dt.datetime.utcfromtimestamp(last / 1000).strftime('%Y-%m-%dT%H:%M') if last else '',
                events=out)


if __name__ == '__main__':
    try:
        data = extract(fetch_raw())
    except Exception as e:
        print(f'Celcat okunamadı: {e}', file=sys.stderr)
        sys.exit(2)
    if len(data['events']) < 15:
        print(f"Celcat'tan beklenenden az ders geldi ({len(data['events'])}); veri güvenilir değil.", file=sys.stderr)
        sys.exit(2)
    json.dump(data, open(sys.argv[1], 'w', encoding='utf-8'), ensure_ascii=False)
    print(f"{len(data['events'])} ders kaydı alındı")
