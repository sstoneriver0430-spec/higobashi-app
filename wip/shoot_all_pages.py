import sys, pathlib
from playwright.sync_api import sync_playwright
S = pathlib.Path('/tmp/claude-0/-home-claude/efc70fbe-5a08-5f14-bbf0-922ffc11eb85/scratchpad')
html = (S/'test.html').resolve(); out = S/(sys.argv[1] if len(sys.argv)>1 else 'rev'); out.mkdir(exist_ok=True)
errs=[]
def route(r):
    u=r.request.url
    if 'react-dom' in u: r.fulfill(path=str(S/'npm/node_modules/react-dom/umd/react-dom.production.min.js'), content_type='text/javascript')
    elif 'react.production' in u: r.fulfill(path=str(S/'npm/node_modules/react/umd/react.production.min.js'), content_type='text/javascript')
    elif u.startswith('file:'): r.continue_()
    else: r.abort()
with sync_playwright() as p:
    b=p.chromium.launch()
    cx=b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, locale='ja-JP', timezone_id='Asia/Tokyo')
    pg=cx.new_page()
    pg.on('console', lambda m: errs.append(m.text) if m.type=='error' and 'net::' not in m.text else None)
    pg.on('pageerror', lambda e: errs.append('PAGEERROR '+str(e)))
    pg.route('**/*', route)
    pg.add_init_script("try{localStorage.setItem('higo_me_v1','田中')}catch(e){}")
    def go(hash_, name, full=True, wait=500):
        pg.goto(html.as_uri()+'#'+hash_); pg.reload(); pg.wait_for_timeout(wait)
        pg.screenshot(path=str(out/(name+'.png')), full_page=full)
    go('home','home'); go('shift','shift'); go('report','report'); go('lost','lost'); go('staff','staff'); go('kinshu','kinshu'); go('board','board'); go('clean','clean'); go('recipe','recipe')
    # kinshu month
    pg.goto(html.as_uri()+'#kinshu'); pg.reload(); pg.wait_for_timeout(400)
    pg.get_by_role('button', name='月次').click(); pg.wait_for_timeout(300); pg.screenshot(path=str(out/'kinshu_month.png'), full_page=True)
    # report tabs
    pg.goto(html.as_uri()+'#report'); pg.reload(); pg.wait_for_timeout(400)
    tabs = pg.locator('.fk-appbar button').all_inner_texts(); print('report tabs', tabs)
    b.close()
print('ERR', errs)
