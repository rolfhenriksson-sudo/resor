#!/usr/bin/env python3
"""Bygger resesajten (GitHub Pages) med veckoarkiv.
  python3 build_site.py --add [YYYY-MM-DD]   # spara veckans resultat (från build_mail.load()) i /workspace/history och bygg + pusha
  python3 build_site.py                      # bara bygg om + pusha
  --no-push                                  # bygg lokalt utan git push
"""
import sys,os,json,glob,html,datetime,subprocess
sys.path.insert(0,'/workspace')
HIST='/workspace/history'; SITE=os.path.dirname(os.path.abspath(__file__))
COUNTRIES=['Spanien','Grekland','Cypern','Malta']
M=['jan','feb','mar','apr','maj','jun','jul','aug','sep','okt','nov','dec']
def fd(s): x=datetime.date.fromisoformat(s); return f"{x.day} {M[x.month-1]} {x.year}"
def kr(n): return f"{int(n):,}".replace(',',' ')+' kr'
def E(s): return html.escape(str(s or ''))

def snapshot(day):
    os.chdir("/workspace"); import build_mail as bm
    rows=bm.load(); top=bm.uniq(rows,5)
    pc=[x[0] for x in (bm.uniq([r for r in rows if r['country']==c],1) for c in COUNTRIES) if x]
    d=dict(week=day,generated=datetime.datetime.now().isoformat(timespec='minutes'),
           sites=[s for s in ['Apollo','Ving','TUI'] if any(r['site']==s for r in rows)],top=top,per_country=pc)
    json.dump(d,open(f'{HIST}/week_{day}.json','w'),ensure_ascii=False,indent=1)

def weeks():
    W={}
    for f in glob.glob(f'{HIST}/week_*.json'):
        d=json.load(open(f)); W[d['week']]=d
    for f in glob.glob(f'{HIST}/final_*.json'):   # äldre format (bara topp 5)
        day=f.split('_')[-1][:-5]
        if day not in W: W[day]=dict(week=day,top=json.load(open(f))['top'],per_country=[])
    return [W[k] for k in sorted(W,reverse=True)]

def link(r): return (r.get('link') or '').replace('|','%7C')
def table(L):
    if not L: return '<p class="muted">Inga data sparade.</p>'
    h='<div class="tw"><table><tr><th>#</th><th>Avresa</th><th>Hotell / destination</th><th>Längd</th><th>Pris (3 vuxna)</th><th></th></tr>'
    for i,r in enumerate(L,1):
        extra=' · '.join(x for x in [r['site'],r.get('kind'),r.get('meal')] if x)
        h+=(f'<tr><td class="n">{i}</td><td>{fd(r["date"])}<br><small>hem {fd(r["ret"])}</small></td>'
            f'<td><b>{E(r["hotel"])}</b><br>{E(r["loc"])}, {E(r["country"])}<br><small>{E(extra)}</small></td>'
            f'<td>{r["days"]} dagar<br><small>{r["nights"]} nätter</small></td>'
            f'<td><b>{kr(r["total"])}</b><br><small>{kr(r["pp"])}/pers</small></td>'
            f'<td><a class="btn" href="{E(link(r))}" target="_blank" rel="noopener">Boka här</a></td></tr>')
    return h+'</table></div>'

CSS='''*{box-sizing:border-box}body{margin:0;font-family:"Segoe UI",Arial,sans-serif;background:#fbf3e4;color:#23313a}
header{background:linear-gradient(rgba(0,90,110,.35),rgba(0,60,80,.55)),url(%sassets/header.jpg) center/cover;color:#fff;padding:70px 20px 60px;text-align:center}
header h1{margin:0;font-size:2.4em;text-shadow:0 2px 8px rgba(0,0,0,.4)}header p{margin:8px 0 0;font-size:1.05em}
.sun{display:inline-block;background:#ffcf3f;color:#5a3d00;border-radius:20px;padding:4px 14px;margin-top:14px;font-weight:bold}
main{max-width:1000px;margin:-30px auto 40px;padding:0 14px}.card{background:#fff;border-radius:14px;box-shadow:0 4px 16px rgba(0,80,90,.12);padding:20px;margin-bottom:22px;border-top:6px solid #1fb5ad}
h2{color:#0d7f86;margin-top:0}.c2{border-top-color:#ff7f61}.c2 h2{color:#e2593d}.c3{border-top-color:#ffcf3f}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%%}th{background:#e3f6f4;color:#0d6168;text-align:left;padding:9px;font-size:.9em}
td{padding:9px;border-bottom:1px solid #f0e4cc;vertical-align:top}td.n{font-weight:bold;color:#ff7f61;font-size:1.2em}small,.muted{color:#7a7468}
.btn{display:inline-block;background:#ff7f61;color:#fff;font-weight:bold;padding:8px 14px;border-radius:20px;text-decoration:underline;white-space:nowrap}.btn:hover{background:#e2593d}
.arch a{display:inline-block;margin:4px;padding:6px 14px;background:#e3f6f4;border-radius:16px;color:#0d6168;text-decoration:none}.arch a.cur{background:#1fb5ad;color:#fff}
footer{text-align:center;font-size:.8em;color:#7a7468;padding:20px}footer a{color:#0d7f86}'''

def page(w,all_w,pre,is_index):
    arch=''.join(f'<a class="{"cur" if x["week"]==w["week"] else ""}" href="{pre}{"index.html" if i==0 else "veckor/"+x["week"]+".html"}">Vecka {datetime.date.fromisoformat(x["week"]).isocalendar()[1]} · {fd(x["week"])}</a>' for i,x in enumerate(all_w))
    gen=w.get('generated'); gen=f' · hämtat {gen.replace("T"," kl. ")}' if gen else ''
    src=', '.join(w.get('sites') or sorted({r['site'] for r in w['top']}))
    return f'''<!doctype html><html lang="sv"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Sommarresor 2027 – vecka {fd(w["week"])}</title><style>{CSS%pre}</style></head><body>
<header><h1>☀️ Veckans prisvärda resor</h1><p>Grekland · Spanien · Malta · Cypern — avresa 21 juni–31 juli 2027 · 6–9 dagar · 3 vuxna · från Arlanda</p>
<div class="sun">{"Senaste veckan" if is_index else "Arkiv"}: {fd(w["week"])}</div></header><main>
<div class="card"><h2>Topp 5 efter totalpris</h2><p class="muted">Billigaste datumet per hotell · källor: {E(src)}{gen}. Priserna är dynamiska och kan ha ändrats.</p>{table(w["top"])}</div>
<div class="card c2"><h2>Billigast per land</h2>{table(w.get("per_country"))}</div>
<div class="card c3 arch"><h2>Veckoarkiv</h2>{arch}</div></main>
<footer>Data från apollo.se, ving.se och tui.se. Inga bokningar görs här.<br>Bild: <a href="https://commons.wikimedia.org/wiki/File:Elafonisi_beach_on_Crete,_Greece.jpg">Elafonisi beach on Crete, Greece</a> av dronepicr, <a href="https://creativecommons.org/licenses/by/2.0/">CC BY 2.0</a> (nedskalad).</footer></body></html>'''

def build():
    W=weeks(); os.makedirs(f'{SITE}/veckor',exist_ok=True)
    open(f'{SITE}/index.html','w').write(page(W[0],W,'',True))
    for w in W: open(f'{SITE}/veckor/{w["week"]}.html','w').write(page(w,W,'../',False))
    print('Byggt',len(W),'veckor; senaste',W[0]['week'])

def push(msg):
    g=lambda *a: subprocess.run(['git','-C',SITE,*a],check=False,capture_output=True,text=True)
    g('add','-A'); r=g('commit','-m',msg); print(r.stdout.strip() or r.stderr.strip())
    r=g('push','origin','main'); print(r.stderr.strip())

if __name__=='__main__':
    a=sys.argv[1:]
    if '--add' in a:
        i=a.index('--add'); day=a[i+1] if len(a)>i+1 and a[i+1][:2]=='20' else datetime.date.today().isoformat()
        snapshot(day)
    build()
    if '--no-push' not in a: push(f'Uppdatera resor {datetime.date.today()}')
