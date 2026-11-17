"""デザインの土台を作り直す：白と黒を基調に、色は「状態」だけに使う。iPhone標準の文字・並び・タブに寄せる。"""
import sys, re
src = open(sys.argv[1], encoding="utf-8").read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, f"anchor count {n} != {count}: {old[:100]!r}"
    src = src.replace(old, new)

def rep_all(old, new, min_count=1):
    global src
    n = src.count(old)
    assert n >= min_count, f"anchor count {n} < {min_count}: {old[:100]!r}"
    src = src.replace(old, new)

# ───────── 1. 文字：iPhone標準の書体 ─────────
rep('''const FONT = "'Manrope','Zen Kaku Gothic New','Hiragino Kaku Gothic ProN','Hiragino Sans','Meiryo',system-ui,sans-serif";''',
    '''const FONT = "-apple-system,BlinkMacSystemFont,'Hiragino Sans','Hiragino Kaku Gothic ProN','Noto Sans JP','Yu Gothic UI','Meiryo',system-ui,sans-serif";''')
src = re.sub(r'<link rel="preconnect" href="https://fonts\.googleapis\.com">\n<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\n<link rel="stylesheet" href="https://fonts\.googleapis\.com/css2[^"]*">\n', '', src, count=1)
assert 'fonts.googleapis.com' not in src

# ───────── 2. 色：白・黒・グレー。緑＝済み、赤＝要対応 ─────────
a = src.index('const C = {'); b = src.index('};', a) + 2
src = src[:a] + '''const C = {
  ink: "#111113", inkSoft: "#2C2C2E", head: "#111113", headLine: "#E3E3E8", headAccent: "#6C6C72",
  cyan: "#111113", cyanDeep: "#111113", cyanSoft: "#EDEDF1", onAccent: "#FFFFFF",
  paper: "#F2F2F7", card: "#FFFFFF", line: "#E3E3E8", lineSoft: "#EFEFF3",
  done: "#1F8A4C", doneSoft: "#E4F4EA", drop: "#D92D20", sub: "#5F5F66", subLight: "#77777E"
};''' + src[b:]
a = src.index('const THEMES = ['); b = src.index('];', a) + 2
src = src[:a] + '''const THEMES = [
  { k: "std", l: "標準", c: { head: "#111113", headLine: "#E3E3E8", headAccent: "#6C6C72", ink: "#111113", inkSoft: "#2C2C2E", cyan: "#111113", cyanDeep: "#111113", cyanSoft: "#EDEDF1", onAccent: "#FFFFFF", paper: "#F2F2F7" } }
];''' + src[b:]
rep('''const readTheme = () => { try { return localStorage.getItem(THEME_KEY) || "kin"; } catch (e) { return "kin"; } };''',
    '''const readTheme = () => "std";''')
rep('''if (m) m.setAttribute("content", C.head);''', '''if (m) m.setAttribute("content", C.paper);''')
rep('''<meta name="theme-color" content="#1A1816">''', '''<meta name="theme-color" content="#F2F2F7">''')
rep(''', h("div", { style: { height: 1, background: C.line, margin: "18px 0 16px" } }), h(ThemePicker, null))));''', ''')));''')
# 暖色のグレーを中立のグレーに
for old, new in [("#F4F2EE", "#F2F2F7"), ("#FAF9F6", "#F7F7F9"), ("#E6E2DA", "#E3E3E8"), ("#F0EDE7", "#EFEFF3"), ("#1A1816", "#111113"),
                 ("#2A2622", "#2C2C2E"), ("#6A6258", "#5F5F66"), ("#F8F0DF", "#EDEDF1"), ("#8A6418", "#111113"),
                 ("rgba(26,24,22,", "rgba(0,0,0,"), ("rgba(28,26,23,", "rgba(0,0,0,")]:
    src = src.replace(old, new)
# ページごとの色つきアイコンをやめる（色は状態だけ）
rep('''const NAV = ["home", "shift", "clean", "kinshu", "board"];''',
    '''PAGES.forEach(p => { p.tint = "#111113"; p.soft = "#EDEDF1"; });
const NAV = ["home", "shift", "clean", "kinshu", "board"];''')
for lit in ['color: "#2563A8"', 'color: "#44548A"', 'color: "#2F7A6E"']:
    src = src.replace(lit, 'color: C.ink')

# ───────── 3. 文字の太さ・角丸をそろえる ─────────
src = re.sub(r'fontWeight: 700\b', 'fontWeight: 500', src)
src = re.sub(r'fontWeight: 800\b', 'fontWeight: 600', src)
src = re.sub(r'fontWeight: 900\b', 'fontWeight: 700', src)
def _rad(m):
    v = int(m.group(1))
    if v >= 90: return m.group(0)
    if v >= 13: return 'borderRadius: 12'
    if v >= 11: return 'borderRadius: 10'
    return m.group(0)
src = re.sub(r'borderRadius: (\d+)\b', _rad, src)
rep('''const cardStyle = { background: C.card, border: "1px solid rgba(0,0,0,.07)", borderRadius: 12, boxShadow: "0 1px 2px rgba(0,0,0,.04), 0 8px 24px rgba(0,0,0,.04)" };''',
    '''const cardStyle = { background: C.card, border: "none", borderRadius: 14 };''')
src = src.replace('boxShadow: "0 1px 2px rgba(0,0,0,.04)", ', '')

# ───────── 4. 見出し：明るい地に大きなタイトル ─────────
rep('''  return h("div", { className: "fk-appbar", style: { position: tall ? "relative" : "sticky", top: 0, zIndex: 30, background: C.head, color: "#fff", borderBottom: `1px solid ${C.headLine}` } },
    h("div", { style: { maxWidth: 640, margin: "0 auto", padding: tall ? "2px 16px 22px" : "0 16px 14px" } }, children));''',
'''  return h("div", { className: "fk-appbar", style: { position: tall ? "relative" : "sticky", top: 0, zIndex: 30, background: tall ? "transparent" : "rgba(242,242,247,.92)", backdropFilter: tall ? "none" : "saturate(180%) blur(16px)", WebkitBackdropFilter: tall ? "none" : "saturate(180%) blur(16px)", color: C.ink, borderBottom: tall ? "none" : `1px solid ${C.line}` } },
    h("div", { style: { maxWidth: 640, margin: "0 auto", padding: tall ? "4px 18px 10px" : "0 18px 12px" } }, children));''')
a = src.index('function Seal({ size = 30 }) {'); b = src.index('const K_FLOAT_DEFAULT', a)
src = src[:a] + '''function Seal({ size = 30 }) {
  return h("div", { style: { width: size, height: size, borderRadius: 8, background: C.ink, color: "#fff", display: "grid", placeItems: "center", fontSize: size * 0.34, fontWeight: 700, lineHeight: 1.08, letterSpacing: 0, flexShrink: 0, textAlign: "center" } },
    h("span", null, "神", h("br"), "虎"));
}
function AppTitle({ title, solo }) {
  if (solo) return h("div", { style: { display: "flex", alignItems: "center", gap: 9 } }, h(Seal, { size: 28 }), h("div", { style: { fontSize: 16, fontWeight: 600, letterSpacing: ".01em", whiteSpace: "nowrap" } }, title));
  return h("div", null,
    h("div", { style: { fontSize: 12, color: C.subLight, fontWeight: 600, letterSpacing: ".04em" } }, "神虎 肥後橋店"),
    h("div", { style: { fontSize: 24, fontWeight: 700, marginTop: 1, letterSpacing: "-.01em", whiteSpace: "nowrap", lineHeight: 1.3 } }, title));
}
''' + src[b:]
# 見出しの中のボタン（白抜き → 白いボタン）
rep_all('"1px solid rgba(255,255,255,.22)"', '`1px solid ${C.line}`', 4)
rep_all('"rgba(255,255,255,.22)"', 'C.line', 1)
rep_all('background: "rgba(255,255,255,.14)", color: "#fff"', 'background: C.card, color: C.ink', 4)
rep('''background: showSettings ? C.cyan : "rgba(255,255,255,.14)", color: showSettings ? C.onAccent : "#fff"''',
    '''background: showSettings ? C.cyan : C.card, color: showSettings ? C.onAccent : C.ink''')
rep_all('color: "rgba(255,255,255,.7)"', 'color: C.sub', 1)
rep_all('color: "rgba(255,255,255,.75)"', 'color: C.sub', 1)
# 見出しの下の切り替え（フォルダ型のタブ → iPhoneの切り替えスイッチ型）
rep_all('''background: on ? C.paper : "transparent", color: on ? C.ink : "rgba(255,255,255,.72)", borderRadius: "11px 11px 0 0", padding: "9px 2px 10px"''',
        '''background: on ? C.card : "transparent", color: on ? C.ink : C.sub, borderRadius: 8, padding: "7px 2px", boxShadow: on ? "0 1px 3px rgba(0,0,0,.12)" : "none"''', 3)
# ホームの見出し
rep('''        h("div", { style: { fontSize: 12.5, color: C.headAccent || C.cyan, fontWeight: 600, letterSpacing: ".08em" } }, `${mo}月${now.getDate()}日（${WD[now.getDay()]}）`),
        h("div", { style: { fontSize: 21, fontWeight: 700, letterSpacing: ".01em", lineHeight: 1.45, marginTop: 4, textWrap: "balance" } }, greetText(greet, me))),''',
'''        h("div", { style: { fontSize: 13, color: C.subLight, fontWeight: 600 } }, `${mo}月${now.getDate()}日 ${WD[now.getDay()]}曜日`),
        h("div", { style: { fontSize: 27, fontWeight: 700, letterSpacing: "-.01em", lineHeight: 1.32, marginTop: 4, textWrap: "balance" } }, greetText(greet, me))),''')

# ───────── 5. 下のタブ：iPhone標準の形 ─────────
rep('''background: on ? C.cyanSoft : "transparent", color: on ? C.cyanDeep : C.subLight, transition: "background .18s ease" } },
              h(Icon, { name: p ? p.icon : "home", size: 23, sw: on ? 2.1 : 1.7 }),''',
    '''background: "transparent", color: on ? C.ink : "#9A9AA1" } },
              h(Icon, { name: p ? p.icon : "home", size: 25, sw: on ? 2.2 : 1.7 }),''')
rep('''color: on ? C.ink : C.subLight, fontWeight: 600, display: "flex", flexDirection: "column", alignItems: "center", gap: 3 } },''',
    '''color: on ? C.ink : "#8A8A91", fontWeight: 600, display: "flex", flexDirection: "column", alignItems: "center", gap: 1 } },''')
rep('''h("span", { style: { fontSize: 11.5, whiteSpace: "nowrap", fontWeight: on ? 900 : 700 } }, p ? p.nav : "ホーム")''',
    '''h("span", { style: { fontSize: 10.5, whiteSpace: "nowrap", fontWeight: on ? 700 : 500, letterSpacing: ".02em" } }, p ? p.nav : "ホーム")''')
rep('''background: "rgba(255,255,255,.94)", backdropFilter: "blur(12px)", WebkitBackdropFilter: "blur(12px)", borderTop: `1px solid ${C.line}`''',
    '''background: "rgba(249,249,251,.92)", backdropFilter: "saturate(180%) blur(16px)", WebkitBackdropFilter: "saturate(180%) blur(16px)", borderTop: "1px solid rgba(0,0,0,.10)"''')

# ───────── 6. 個別の部品 ─────────
# お知らせ（トースト）のチェックは白
rep('''h(Icon, { name: "check", size: 18, sw: 2.4, color: C.cyan }), text), document.body);''',
    '''h(Icon, { name: "check", size: 18, sw: 2.4, color: "#fff" }), text), document.body);''')
# ホームの未読：赤い帯をやめ、赤い件数だけにする
rep('''  return h("div", { style: { ...cardStyle, marginTop: 10, overflow: "hidden", border: `1.5px solid ${C.drop}` } },
    h("div", { style: { display: "flex", alignItems: "center", gap: 8, padding: "11px 14px", background: C.drop, color: "#fff" } },
      h(Icon, { name: "board", size: 20 }),
      h("span", { style: { fontSize: 15, fontWeight: 700 } }, `${me}さんの未読`),
      h("span", { style: { marginLeft: "auto", fontSize: 15, fontWeight: 700, fontVariantNumeric: "tabular-nums" } }, `${mine.length}件`)),''',
'''  return h("div", { style: { ...cardStyle, marginTop: 10, overflow: "hidden" } },
    h("div", { style: { display: "flex", alignItems: "center", gap: 8, padding: "13px 16px 11px", borderBottom: `1px solid ${C.lineSoft}` } },
      h(Icon, { name: "board", size: 20 }),
      h("span", { style: { fontSize: 15, fontWeight: 700 } }, "まだ読んでいない掲示"),
      h("span", { style: { marginLeft: "auto", minWidth: 24, height: 24, padding: "0 7px", borderRadius: 99, background: C.drop, color: "#fff", display: "grid", placeItems: "center", fontSize: 13, fontWeight: 700, fontVariantNumeric: "tabular-nums" } }, mine.length)),''')
# 金種：ツナグ枠の太い枠線をやめる
rep('''return h(KPanel, { style: { border: `1.5px solid ${C.cyan}` } },''', '''return h(KPanel, null,''')
# 金種のパネル・掲示の枠
rep('''style: { background: C.card, border: `1px solid ${C.line}`, borderRadius: 12, padding: 16, marginBottom: 12, ...style || {} }''',
    '''style: { background: C.card, border: "none", borderRadius: 14, padding: 16, marginBottom: 12, ...style || {} }''')

open(sys.argv[2], "w", encoding="utf-8").write(src)
print("ok", len(src))
