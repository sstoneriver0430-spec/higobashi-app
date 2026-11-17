import sys, pathlib, json, datetime
from playwright.sync_api import sync_playwright
S = pathlib.Path('/tmp/claude-0/-home-claude/efc70fbe-5a08-5f14-bbf0-922ffc11eb85/scratchpad')
src = pathlib.Path(sys.argv[1]).read_text(encoding='utf-8'); mode = sys.argv[2]
out = S/('prod_'+mode); out.mkdir(exist_ok=True)
seed = {}
if mode == 'real':
    names = ["石川","安田","ミン","ポー","リン","細田","姜"]
    seed['single'] = {'higo_staff_v1': {'v': {'names': names}}}
    t = int(datetime.datetime(2026,11,14,10,0).timestamp()*1000)
    seed['higo_board_v1'] = {'b1': {'id':'b1','cat':'連絡','title':'年末の営業時間','body':'12/30は18時まで','author':'石川','createdAt':t,'reads':[{'name':'安田','t':t}]}}
    seed['higo_clean_done_v1'] = {'2026-11-13': {'v': {'im': {'by':'ポー','t':t,'photos':['photo:p1']}, 'dh': {'by':'リン','t':t}}}, '2026-11-10': {'v': {'dm': {'by':'安田','t':t,'photo':'photo:p1'}}}}
    seed['higo_clean_free_v1'] = {'2026-11-12': {'v': [{'id':'f1','place':'イスの脚','by':'ミン','t':t,'photos':[]}]}}
    seed['single']['higo_shift_v2'] = {'v': {'days': {d: [{'name':'石川','tags':['社員'],'segs':[{'s':570,'e':900,'label':'麺場','type':'work'}]},{'name':'リン','tags':['28h'],'segs':[{'s':1080,'e':1380,'label':'トップ','type':'work'}]}] for d in ['2026-11-15','2026-11-16','2026-11-17']}, 'mkAt': {'2026-11-16': t}}}
    seed['photos'] = {'p1': {'d': 'data:image/gif;base64,R0lGODlhAQABAAAAACw='}}
html = src.replace('<script src="https://www.gstatic.com/firebasejs/10.12.2/firebase-app-compat.js"></script>', '<script>window.__CACHE_FIRST__=true;window.__SEED__='+json.dumps(seed, ensure_ascii=False)+';</script><script>'+(S/'fbmock.js').read_text()+'</script>')
(S/'prod_test.html').write_text(html, encoding='utf-8')
errs=[]
def route(r):
    u=r.request.url
    if 'react-dom' in u: r.fulfill(path=str(S/'npm/node_modules/react-dom/umd/react-dom.production.min.js'), content_type='text/javascript')
    elif 'react.production' in u: r.fulfill(path=str(S/'npm/node_modules/react/umd/react.production.min.js'), content_type='text/javascript')
    elif u.startswith('file:'): r.continue_()
    else: r.abort()
with sync_playwright() as p:
    b=p.chromium.launch(); cx=b.new_context(viewport={'width':390,'height':844}, locale='ja-JP', timezone_id='Asia/Tokyo'); pg=cx.new_page()
    pg.on('console', lambda m: errs.append(m.text[:300]) if m.type=='error' and 'net::' not in m.text else None)
    pg.on('pageerror', lambda e: errs.append('PAGEERROR '+str(e)[:400]))
    pg.route('**/*', route)
    if len(sys.argv)>3: pg.add_init_script("try{localStorage.setItem('higo_me_v1','石川')}catch(e){}")
    for hsh in ['home','clean','kinshu','board','shift','report','lost','staff','recipe']:
        pg.goto((S/'prod_test.html').as_uri()+'#'+hsh); pg.reload(); pg.wait_for_timeout(900)
        txt = pg.evaluate('document.getElementById("root").innerText.length')
        pg.screenshot(path=str(out/(hsh+'.png')))
        print(hsh, 'textlen', txt, 'writes', pg.evaluate('window.__WRITES__.filter(w=>w.includes("shift")).join(",")'), '| 16日あり' if '麺場' in pg.evaluate('document.getElementById("root").innerText') else '')
    b.close()
print('ERR', errs[:12])
