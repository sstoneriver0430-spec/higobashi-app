import sys
src = open(sys.argv[1], encoding="utf-8").read()

def rep(old, new, count=1):
    global src
    n = src.count(old)
    assert n == count, f"anchor count {n} != {count}: {old[:90]!r}"
    src = src.replace(old, new)

# ───────── 1. 下のタブを5つに（勤怠・破損はホームから開く） ─────────
rep('const NAV = ["home", "shift", "clean", "kinshu", "report", "board"];',
    'const NAV = ["home", "shift", "clean", "kinshu", "board"];')
rep('function ReportApp({ initialTab }) {', 'function ReportApp({ initialTab, go }) {')
rep('''    h(Header, null,
      h(AppTitle, { title: "勤怠・破損" }),''', '''    h(Header, null,
      go && h(BackHome, { go }),
      h(AppTitle, { title: "勤怠・破損" }),''')
rep('h(ReportApp, { key: "r" })', 'h(ReportApp, { key: "r", go })')

# ───────── 2. カードをやわらかく ─────────
rep('const cardStyle = { background: C.card, border: `1px solid ${C.line}`, borderRadius: 18 };',
    'const cardStyle = { background: C.card, border: "1px solid rgba(26,24,22,.07)", borderRadius: 20, boxShadow: "0 1px 2px rgba(26,24,22,.04), 0 8px 24px rgba(26,24,22,.04)" };')

# ───────── 3. 金種の入力欄を大きく ─────────
rep('''style: { width: 130, borderRadius: 11, border: `1.5px solid ${C.line}`, padding: "9px 11px", fontSize: 16, color: C.ink, outline: "none", textAlign: align === "left" ? "left" : "right", fontVariantNumeric: "tabular-nums" }''',
    '''style: { width: 148, minHeight: 48, borderRadius: 13, border: `1.5px solid ${C.line}`, padding: "10px 12px", fontSize: 18, fontWeight: 700, color: C.ink, outline: "none", textAlign: align === "left" ? "left" : "right", fontVariantNumeric: "tabular-nums", background: C.card }''')
rep('''React.createElement("label", { style: { display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, padding: "10px 0" } }, /* @__PURE__ */ React.createElement("span", { style: { fontSize: 13.5, color: C.sub, flexShrink: 0 } }, label)''',
    '''React.createElement("label", { style: { display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, padding: "9px 0" } }, /* @__PURE__ */ React.createElement("span", { style: { fontSize: 14.5, fontWeight: 700, color: C.inkSoft, minWidth: 0 } }, label)''')

# ───────── 4. 掃除：完了のしるしに動きをつける ─────────
rep('''      h("span", { style: { width: 30, height: 30, borderRadius: 99, flexShrink: 0, display: "grid", placeItems: "center", background: rec ? C.done : "transparent", border: rec ? "none" : `2px solid ${C.line}`, color: "#fff" } }, rec && h(Icon, { name: "check", size: 18, sw: 2.8 })),
      h("div", { style: { flex: 1, minWidth: 0 } },
        h("div", { style: { fontSize: 12, fontWeight: 800, color: sl.tint } }, sl.place),''',
'''      h("span", { key: rec ? "d" : "n", className: rec ? "fk-pop" : undefined, style: { width: 30, height: 30, borderRadius: 99, flexShrink: 0, display: "grid", placeItems: "center", background: rec ? C.done : "transparent", border: rec ? "none" : `2px solid ${C.line}`, color: "#fff" } }, rec && h(Icon, { name: "check", size: 18, sw: 2.8 })),
      h("div", { style: { flex: 1, minWidth: 0 } },
        h("div", { style: { fontSize: 12, fontWeight: 800, color: sl.tint } }, sl.place),''')
rep('''      @keyframes fkIn{from{opacity:.4;transform:translateY(6px);}to{opacity:1;transform:none;}}''',
'''      @keyframes fkIn{from{opacity:.4;transform:translateY(6px);}to{opacity:1;transform:none;}}
      .fk-pop{animation:fkPop .38s cubic-bezier(.2,1.4,.4,1) both;}
      @keyframes fkPop{0%{transform:scale(.4);opacity:.3;}70%{transform:scale(1.14);opacity:1;}100%{transform:scale(1);}}
      .fk-bar{transition:width .5s cubic-bezier(.2,.8,.2,1);}''')

# ───────── 5. ホーム：「今日の自分」を先に、店の数字は下に ─────────
rep('''function Home({ go }) {''',
'''// ホーム：今日の掃除の進み具合
function HomeClean({ go }) {
  const ymd = todayYMD();
  const sched = readStored(CL_SCHED_KEY, clSchedSeed), done = readStored(CL_DONE_KEY, clDoneSeed);
  const items = readStored(DC_ITEMS_KEY, seedDaily), dcDone = readStored(DC_DONE_KEY, () => ({}));
  const day = sched[ymd] || null, dd = done[ymd] || {};
  const slots = CL_SLOTS.filter(sl => day && day[sl.k]);
  const cl = { n: slots.filter(sl => dd[sl.k]).length, total: slots.length };
  const dc = dcCount(items, dcDone, ymd);
  if (!cl.total && !dc.total) return null;
  const allDone = (!cl.total || cl.n === cl.total) && (!dc.total || dc.n === dc.total);
  const bar = (label, a, b) => b > 0 && h("div", { style: { flex: 1, minWidth: 0 } },
    h("div", { style: { display: "flex", alignItems: "baseline", justifyContent: "space-between", gap: 6 } },
      h("span", { style: { fontSize: 12.5, fontWeight: 800, color: C.sub, whiteSpace: "nowrap" } }, label),
      h("span", { style: { fontSize: 15, fontWeight: 900, fontVariantNumeric: "tabular-nums", color: a === b ? C.done : C.ink } }, a, h("span", { style: { fontSize: 12, color: C.subLight, fontWeight: 800 } }, ` / ${b}`))),
    h("div", { style: { height: 7, borderRadius: 99, background: C.lineSoft, marginTop: 6, overflow: "hidden" } },
      h("div", { className: "fk-bar", style: { width: `${Math.round(a / b * 100)}%`, height: "100%", borderRadius: 99, background: a === b ? C.done : C.cyan } })));
  return h("button", { type: "button", className: "fk-tap", onClick: () => go("clean"), style: { ...cardStyle, width: "100%", marginTop: 12, padding: "14px 16px 16px", textAlign: "left", cursor: "pointer", color: C.ink } },
    h("div", { style: { display: "flex", alignItems: "center", gap: 8, marginBottom: 12 } },
      h(Icon, { name: "clean", size: 20, color: "#2F7A6E" }),
      h("span", { style: { fontSize: 15, fontWeight: 900 } }, "今日の掃除"),
      allDone && h(Pill, { text: "完了", color: C.done, bg: C.doneSoft }),
      h("span", { style: { marginLeft: "auto", display: "flex", alignItems: "center", gap: 2, fontSize: 12.5, fontWeight: 800, color: C.sub } }, "開く", h(Icon, { name: "chev", size: 15, sw: 2 }))),
    h("div", { style: { display: "flex", gap: 18 } }, bar("日次チェック", dc.n, dc.total), bar("掃除表", cl.n, cl.total)));
}
function HomeTile({ icon, tint, soft, title, badge, warn, onClick }) {
  return h("button", { type: "button", className: "fk-tap", onClick, style: { ...cardStyle, minWidth: 0, padding: "14px 14px 13px", textAlign: "left", cursor: "pointer", color: C.ink, display: "flex", flexDirection: "column", gap: 10 } },
    h("div", { style: { display: "flex", alignItems: "center", justifyContent: "space-between", width: "100%" } },
      h("span", { style: { width: 40, height: 40, borderRadius: 12, background: soft, color: tint, display: "grid", placeItems: "center" } }, h(Icon, { name: icon, size: 22 })),
      badge ? h("span", { style: { fontSize: 12, fontWeight: 800, borderRadius: 999, padding: "4px 10px", whiteSpace: "nowrap", color: warn ? "#fff" : C.cyanDeep, background: warn ? C.drop : C.cyanSoft } }, badge) : null),
    h("span", { style: { fontSize: 15, fontWeight: 800 } }, title));
}
function Home({ go }) {''')

rep('''  const soon = PAGES.filter(p => !p.ready);
  return h("div", { className: "fk-page" },''',
'''  const [statsOpen, setStatsOpenRaw] = useState(() => { try { return localStorage.getItem("higo_home_stats_v1") === "1"; } catch (e) { return false; } });
  const setStatsOpen = (v) => { setStatsOpenRaw(v); try { localStorage.setItem("higo_home_stats_v1", v ? "1" : "0"); } catch (e) {} };
  const repOpen = readStored(A_KEY, seedAtt).filter(r => r.status === "open").length;
  return h("div", { className: "fk-page" },''')

# 見出し：名簿のボタンを外し、あいさつを大きく
rep('''        h("div", { style: { display: "flex", alignItems: "center", gap: 10, minWidth: 0 } },
          h(AppTitle, { title: "肥後橋店", solo: true }),
          h("button", { type: "button", className: "fk-tap", onClick: () => go("staff"), style: { display: "flex", alignItems: "center", gap: 4, background: "rgba(255,255,255,.10)", color: "rgba(255,255,255,.85)", border: "1px solid rgba(255,255,255,.18)", borderRadius: 999, padding: "4px 10px 4px 8px", fontSize: 12, fontWeight: 800, cursor: "pointer", whiteSpace: "nowrap" } },
            h(Icon, { name: "staff", size: 14, sw: 2 }), `名簿 ${staff.length}人`)),
        h("div", { style: { fontSize: 12, color: "rgba(255,255,255,.62)", fontWeight: 700, whiteSpace: "nowrap", flexShrink: 0 } }, `${mo}/${now.getDate()}（${WD[now.getDay()]}）`)),
      h("div", { style: { marginTop: 18, display: "flex", alignItems: "center", justifyContent: "space-between", gap: 10 } },
        h("div", { style: { fontSize: 17, fontWeight: 900, letterSpacing: ".02em", lineHeight: 1.45, minWidth: 0, textWrap: "pretty" } }, greetText(greet, me)),
        h("button", { type: "button", className: "fk-tap", onClick: () => setMeOpen(true), style: { flexShrink: 0, background: "rgba(255,255,255,.14)", color: "#fff", border: "1px solid rgba(255,255,255,.22)", borderRadius: 999, padding: "6px 12px", fontSize: 12.5, fontWeight: 800, cursor: "pointer", display: "flex", alignItems: "center", gap: 5, whiteSpace: "nowrap" } }, h(Icon, { name: me ? "gear" : "staff", size: 14, sw: 2 }), me ? me : "名前を選ぶ")),''',
'''        h(AppTitle, { title: "肥後橋店", solo: true }),
        h("button", { type: "button", className: "fk-tap", onClick: () => setMeOpen(true), style: { flexShrink: 0, minHeight: 36, background: "rgba(255,255,255,.14)", color: "#fff", border: "1px solid rgba(255,255,255,.22)", borderRadius: 999, padding: "6px 13px", fontSize: 13, fontWeight: 800, cursor: "pointer", display: "flex", alignItems: "center", gap: 6, whiteSpace: "nowrap" } }, h(Icon, { name: me ? "gear" : "staff", size: 15, sw: 2 }), me ? me : "名前を選ぶ")),
      h("div", { style: { marginTop: 20 } },
        h("div", { style: { fontSize: 12.5, color: C.headAccent || C.cyan, fontWeight: 800, letterSpacing: ".08em" } }, `${mo}月${now.getDate()}日（${WD[now.getDay()]}）`),
        h("div", { style: { fontSize: 21, fontWeight: 900, letterSpacing: ".01em", lineHeight: 1.45, marginTop: 4, textWrap: "balance" } }, greetText(greet, me))),''')

# 本体：未読 → 今日のシフト → 今日の掃除 → 報告・忘れ物 → 店の数字 → 名簿
rep('''      fbAuthError && h("div", { style: { position: "relative", zIndex: 32, marginTop: -12, marginBottom: 20, background: "#FBEAE6",''',
    '''      fbAuthError && h("div", { style: { position: "relative", zIndex: 32, marginTop: 12, background: "#FBEAE6",''')
a = src.index('      // 売上\n      h("button", { type: "button", className: "fk-tap", onClick: () => go("kinshu"), style: { ...cardStyle, width: "100%", textAlign: "left", marginTop: -12,')
b = src.index('    h(Sheet, { open: !!person, onClose: () => setPerson(null), title: "個人のシフト" }', a)
assert b > a
src = src[:a] + '''      h("div", { style: { height: 4 } }),
      h(HomeUnread, { go, me, onPickMe: () => setMeOpen(true) }),
      h(HomeShift, { people: shDay, me, go, onName: setPerson }),
      h(HomeClean, { go }),
      h("div", { style: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginTop: 12 } },
        (() => { const p = PAGES.find(x => x.k === "report"); return h(HomeTile, { icon: p.icon, tint: p.tint, soft: p.soft, title: "遅刻・破損の報告", badge: repOpen ? `確認待ち ${repOpen}` : "", onClick: () => go("report") }); })(),
        (() => { const p = PAGES.find(x => x.k === "lost"); return h(HomeTile, { icon: p.icon, tint: p.tint, soft: p.soft, title: "忘れ物", badge: lostNear ? `期限間近 ${lostNear}` : lost.length ? `保管中 ${lost.length}` : "", warn: lostNear > 0, onClick: () => go("lost") }); })()),
      // 店の数字（開いたままかどうかは端末ごとに覚える）
      h("div", { style: { ...cardStyle, marginTop: 12, overflow: "hidden" } },
        h("button", { type: "button", onClick: () => setStatsOpen(!statsOpen), "aria-expanded": statsOpen, style: { width: "100%", minHeight: 50, display: "flex", alignItems: "center", gap: 8, padding: "0 16px", background: "transparent", border: "none", cursor: "pointer", color: C.ink, textAlign: "left" } },
          h(Icon, { name: "kinshu", size: 20, color: C.cyanDeep }),
          h("span", { style: { fontSize: 15, fontWeight: 900 } }, `${mo}月の店の数字`),
          h("span", { style: { marginLeft: "auto", fontSize: 12.5, fontWeight: 800, color: C.sub } }, statsOpen ? "閉じる" : "見る"),
          h("span", { style: { display: "inline-block", transform: statsOpen ? "rotate(-90deg)" : "rotate(90deg)", color: C.subLight, transition: "transform .2s ease" } }, h(Icon, { name: "chev", size: 15, sw: 2.2 }))),
        statsOpen && h("button", { type: "button", className: "fk-tap", onClick: () => go("kinshu"), style: { width: "100%", textAlign: "left", cursor: "pointer", color: C.ink, background: "transparent", border: "none", borderTop: `1px solid ${C.lineSoft}`, display: "grid", gridTemplateColumns: "1fr 1fr", gap: "14px 12px", padding: "16px clamp(12px, 4vw, 18px)" } },
          h(HomeStat, { label: "売上（累計）", value: yenF(total), big: true }),
          h("div", { style: { borderLeft: `1px solid ${C.lineSoft}`, paddingLeft: 12, minWidth: 0 } }, h(HomeStat, { label: "硬貨端数（累計）", value: yenF(hasu), big: true })),
          h("div", { style: { borderTop: `1px solid ${C.lineSoft}`, paddingTop: 12, minWidth: 0 } }, h(HomeStat, { label: "人時生産性", value: prod ? yenF(prod) : "—", sub: prod ? `売上÷シフト時間（${pDays}日分）` : "シフトが入った日がまだありません" })),
          h("div", { style: { borderTop: `1px solid ${C.lineSoft}`, borderLeft: `1px solid ${C.lineSoft}`, paddingTop: 12, paddingLeft: 12, minWidth: 0 } }, h(HomeStat, { label: "着地見込み", value: cnt ? yenF(landing) : "—", color: C.cyanDeep, sub: `日平均×${days}日（${cnt}日分）` })),
          demo && h("div", { style: { gridColumn: "1 / -1", fontSize: 12, color: C.subLight, fontWeight: 700 } }, "サンプルの数値です"))),
      h("button", { type: "button", onClick: () => go("staff"), style: { display: "flex", alignItems: "center", gap: 6, margin: "18px auto 0", minHeight: 40, padding: "0 14px", background: "transparent", border: "none", color: C.sub, fontSize: 13, fontWeight: 800, cursor: "pointer" } },
        h(Icon, { name: "staff", size: 16, sw: 2 }), `名簿（${staff.length}人）`, h(Icon, { name: "chev", size: 14, sw: 2, color: C.subLight }))),
''' + src[b:]

# ホームの最初のカードの上の余白（ホームの中だけ）
_h = src.index('function Home({ go }) {')
_old = 'padding: "0 14px calc(104px + env(safe-area-inset-bottom))" } },\n      fbAuthError &&'
_k = src.index(_old, _h)
src = src[:_k] + _old.replace('"0 14px', '"6px 14px') + src[_k + len(_old):]

# ───────── 6. 下のタブの見た目と、オフラインの表示 ─────────
rep('''  const [meApp] = useMe();
  const navDot = {}, navCnt = {};''',
'''  const [meApp] = useMe();
  const [online, setOnline] = useState(() => typeof navigator === "undefined" || navigator.onLine !== false);
  useEffect(() => { const on = () => setOnline(true), off = () => setOnline(false); window.addEventListener("online", on); window.addEventListener("offline", off); return () => { window.removeEventListener("online", on); window.removeEventListener("offline", off); }; }, []);
  const navDot = {}, navCnt = {};''')
rep('''    navDot.report = readStored(A_KEY, seedAtt).filter(r => r.status === "open").length > 0;''',
    '''    navDot.home = readStored(A_KEY, seedAtt).filter(r => r.status === "open").length > 0;''')
rep('''    h("nav", { style: { position: "fixed", left: 0, right: 0, bottom: 0, zIndex: 45, background: "rgba(255,255,255,.94)",''',
'''    !online && h("div", { role: "status", style: { position: "fixed", left: 0, right: 0, bottom: "calc(62px + env(safe-area-inset-bottom, 0px))", zIndex: 44, display: "flex", justifyContent: "center", pointerEvents: "none", padding: "0 14px" } },
      h("div", { style: { background: C.ink, color: "#fff", borderRadius: 999, padding: "9px 16px", fontSize: 12.5, fontWeight: 800, boxShadow: "0 8px 24px rgba(26,24,22,.25)", textAlign: "center" } }, "オフラインです。入力はつながったときに送られます")),
    h("nav", { style: { position: "fixed", left: 0, right: 0, bottom: 0, zIndex: 45, background: "rgba(255,255,255,.94)",''')
rep('''            h("span", { style: { position: "relative", width: 48, maxWidth: "100%", height: 30, borderRadius: 999, display: "grid", placeItems: "center", background: on ? C.cyanSoft : "transparent", color: on ? C.cyanDeep : C.subLight } },
              h(Icon, { name: p ? p.icon : "home", size: 22, sw: on ? 2 : 1.7 }),''',
'''            h("span", { style: { position: "relative", width: 56, maxWidth: "100%", height: 32, borderRadius: 999, display: "grid", placeItems: "center", background: on ? C.cyanSoft : "transparent", color: on ? C.cyanDeep : C.subLight, transition: "background .18s ease" } },
              h(Icon, { name: p ? p.icon : "home", size: 23, sw: on ? 2.1 : 1.7 }),''')
rep('''      h("div", { style: { maxWidth: 640, margin: "0 auto", display: "flex", padding: "6px 6px 4px" } },
        NAV.map(''', '''      h("div", { style: { maxWidth: 640, margin: "0 auto", display: "flex", padding: "7px 8px 4px" } },
        NAV.map(''')
rep('''            h("span", { style: { fontSize: 11.5, whiteSpace: "nowrap" } }, p ? p.nav : "ホーム")); }))));''',
    '''            h("span", { style: { fontSize: 11.5, whiteSpace: "nowrap", fontWeight: on ? 900 : 700 } }, p ? p.nav : "ホーム")); }))));''')

open(sys.argv[2], "w", encoding="utf-8").write(src)
print("ok", len(src))
