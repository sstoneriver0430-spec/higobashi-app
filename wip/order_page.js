// ───────── 発注表（ペルゴ：ファクトリー課・物流課） ─────────
// 流れ：今の在庫を入れる → 届く日の朝の在庫見込みを計算 → 発注数 → 紙の「物流発注表」の届く日の列に書く → ASPITに入力 → 「発注した」で記録
const OR_MASTER_KEY = "higo_order_master_v1";
const OR_LOG_KEY = "higo_order_log_v1";
// rate＝売上10万円（税抜）あたりの使用量（2026/10/1〜11/12 の納品書と売上から）。point/pq＝「在庫が point 以下なら pq 頼む」品目
const OR_HIST = {"2026-11-18": {"qty": {"grill": 8, "ekisu": 6, "tare": 1, "seabura": 5, "men": 9, "gyoza": 7, "kome": 6, "akanegi": 1, "takana": 4}, "by": "納品書", "t": 0}, "2026-10-26": {"qty": {"gyoza": 5, "kome": 5, "takana": 2, "grill": 4, "ekisu": 6, "seabura": 5, "men": 8}, "by": "納品書", "t": 0}, "2026-10-28": {"qty": {"gyoza": 8, "kome": 5, "akanegi": 1, "takana": 4, "grill": 9, "ekisu": 5, "tare": 2, "seabura": 2, "men": 9}, "by": "納品書", "t": 0}, "2026-10-30": {"qty": {"grill": 6, "ekisu": 4, "seabura": 4, "men": 6, "gyoza": 5, "kome": 3, "takana": 2}, "by": "納品書", "t": 0}, "2026-10-31": {"qty": {"grill": 5, "ekisu": 2, "tare": 1, "seabura": 2, "men": 3, "gyoza": 4, "akanegi": 1, "takana": 2}, "by": "納品書", "t": 0}, "2026-11-01": {"qty": {"grill": 3, "ekisu": 4, "tare": 1, "men": 5, "gyoza": 2, "kome": 6, "takana": 2}, "by": "納品書", "t": 0}, "2026-11-02": {"qty": {"grill": 6, "ekisu": 5, "tare": 1, "seabura": 6, "men": 7, "gyoza": 6, "kome": 5, "takana": 3}, "by": "納品書", "t": 0}, "2026-11-03": {"qty": {"grill": 1, "ekisu": 2, "men": 2}, "by": "納品書", "t": 0}, "2026-11-04": {"qty": {"gyoza": 5, "kome": 4, "takana": 4, "grill": 6, "ekisu": 5, "tare": 2, "seabura": 3, "men": 10}, "by": "納品書", "t": 0}, "2026-11-06": {"qty": {"grill": 4, "ekisu": 3, "tare": 1, "men": 5, "gyoza": 4, "kome": 3, "takana": 2}, "by": "納品書", "t": 0}, "2026-11-07": {"qty": {"gyoza": 4, "takana": 2, "grill": 5, "ekisu": 3, "tare": 1, "seabura": 2, "men": 4}, "by": "納品書", "t": 0}, "2026-11-08": {"qty": {"grill": 5, "ekisu": 4, "seabura": 3, "men": 5, "gyoza": 4, "kome": 3, "takana": 2}, "by": "納品書", "t": 0}, "2026-11-09": {"qty": {"grill": 5, "ekisu": 6, "tare": 1, "seabura": 5, "men": 7, "gyoza": 4, "kome": 5, "akanegi": 1, "takana": 5}, "by": "納品書", "t": 0}, "2026-11-11": {"qty": {"gyoza": 4, "kome": 3, "takana": 4, "grill": 5, "ekisu": 5, "tare": 1, "seabura": 4, "men": 10}, "by": "納品書", "t": 0}, "2026-11-13": {"qty": {"grill": 5, "ekisu": 4, "men": 5, "gyoza": 4, "kome": 3, "takana": 2}, "by": "納品書", "t": 0}, "2026-11-14": {"qty": {"grill": 5, "ekisu": 3, "tare": 1, "seabura": 3, "men": 5, "gyoza": 4, "kome": 6, "goma": 1, "akanegi": 1, "takana": 2}, "by": "納品書", "t": 0}, "2026-11-15": {"qty": {"grill": 3, "ekisu": 4, "tare": 1, "men": 5, "gyoza": 1, "kome": 2, "takana": 2}, "by": "納品書", "t": 0}, "2026-11-16": {"qty": {"grill": 5, "ekisu": 6, "tare": 2, "seabura": 6, "men": 9, "gyoza": 6, "kome": 7, "takana": 3}, "by": "納品書", "t": 0}};
const orLogSeed = () => JSON.parse(JSON.stringify(OR_HIST));
const orMasterSeed = () => ({
  aspit: "https://www.f-aspit.com/aspit2/logon/index",
  items: [
    { id: "grill",  grp: "ファクトリー", name: "グリル",     unit: "P",  rate: 1.104 },
    { id: "ekisu",  grp: "ファクトリー", name: "エキス",     unit: "箱", rate: 0.928 },
    { id: "men",    grp: "ファクトリー", name: "28番麺",     unit: "箱", rate: 1.35 },
    { id: "tare",   grp: "ファクトリー", name: "ラーたれ",   unit: "本", rate: 0.211 },
    { id: "seabura",grp: "ファクトリー", name: "背脂",       unit: "kg", rate: 0.597 },
    { id: "gyoza",  grp: "物流",         name: "餃子の皮",   unit: "P",  rate: 0.942 },
    { id: "kome",   grp: "物流",         name: "米",         unit: "袋", rate: 0.703 },
    { id: "goma",   grp: "物流",         name: "ゴマ油",     unit: "本", point: 1, pq: 1 },
    { id: "akanegi",grp: "物流",         name: "赤葱",       unit: "袋", point: 1, pq: 1 },
    { id: "takana", grp: "物流",         name: "高菜",       unit: "P",  rate: 0.59 },
    { id: "kimuchi",grp: "物流",         name: "キムチタレ", unit: "本", point: 1, pq: 1 }
  ]
});
// 発注日（getDay）→ 届く日・何日分。紙の発注表は「届く日」の列に書く
const OR_SLOTS = [
  { od: 2, del: 5, days: 1, label: "金曜分" },
  { od: 4, del: 6, days: 1, label: "土曜分" },
  { od: 5, del: 0, days: 1, label: "日曜分" },
  { od: 6, del: 1, days: 2, label: "月・火曜分" },
  { od: 0, del: 3, days: 2, label: "水・木曜分" }
];
// 売上の記録が足りないときの曜日ごとの売上（税抜。10/16〜11/12の平均）
const OR_FALLBACK = { 0: 343541, 1: 333582, 2: 323761, 3: 312904, 4: 318814, 5: 326939, 6: 329060 };
const orYmd = (d) => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`;
const orAdd = (d, n) => { const x = new Date(d); x.setDate(x.getDate() + n); return x; };
const orMD = (d) => `${d.getMonth() + 1}/${d.getDate()}（${WD[d.getDay()]}）`;
const orR = (n) => Math.round(n * 10) / 10;

// 金種の「当日売上」（税込）を月ごとに読む
const _orKin = {}, _orKinSub = {};
function orKinMonth(y, m0) {
  const mk = `${y}-${pad(m0 + 1)}`;
  if (db) {
    if (!_orKinSub[mk]) { _orKinSub[mk] = 1; db.collection("kinshu").doc(mk).onSnapshot(d => { _orKin[mk] = d.exists ? (d.data().days || {}) : {}; emitAll(); }, e => console.error(e)); }
    return { data: _orKin[mk] || {}, real: true };
  }
  try { const m = localStorage.getItem("higo_kinshu2_" + mk); if (m) return { data: JSON.parse(m), real: true }; } catch (e) {}
  return { data: {}, real: false };
}
// 直近14日（今日を除く）の曜日ごとの平均・最大（税抜）
function orSalesBasis(today) {
  const vals = {}; let n = 0, real = false;
  for (let i = 1; i <= 14; i++) {
    const d = orAdd(today, -i), m = orKinMonth(d.getFullYear(), d.getMonth()); real = real || m.real;
    const e = m.data[String(d.getDate())], v = e ? Number(String(e.uday || "").replace(/[^\d]/g, "")) : 0;
    if (v > 0) { (vals[d.getDay()] = vals[d.getDay()] || []).push(v / 1.1); n++; }
  }
  const avg = {}, max = {};
  for (let w = 0; w < 7; w++) {
    const a = vals[w];
    if (a && a.length) { avg[w] = a.reduce((s, x) => s + x, 0) / a.length; max[w] = Math.max(...a); }
    else { avg[w] = OR_FALLBACK[w]; max[w] = OR_FALLBACK[w] * 1.08; }
  }
  return { avg, max, n, from: orAdd(today, -14), to: orAdd(today, -1), sample: n < 7 };
}
// 今日（または次）の発注日と、その発注の届く日
function orSlotFor(today, idx) {
  const list = [];
  for (let i = 0; i < 7; i++) { const d = orAdd(today, i), s = OR_SLOTS.find(x => x.od === d.getDay()); if (s) list.push({ ...s, orderDate: d }); }
  const cur = list[idx || 0];
  let del = orAdd(cur.orderDate, 1); while (del.getDay() !== cur.del) del = orAdd(del, 1);
  return { ...cur, delDate: del, list };
}
// 1日分の見込み売上（1日分の枠は一番売れた日、2日分の枠は平均）
const orDaySales = (basis, d, oneDay) => oneDay ? basis.max[d.getDay()] : basis.avg[d.getDay()];

function orCalc(master, log, slot, basis, stock, timing) {
  const out = {};
  const cover = [...Array(slot.days)].map((_, i) => orAdd(slot.delDate, i));
  // 届く日までに使う日：発注日の残り（timing）＋その間の日
  const before = []; for (let d = orAdd(slot.orderDate, 1); d < slot.delDate; d = orAdd(d, 1)) before.push(d);
  // 間に届く分（記録があれば記録の数、なければ目安）
  const mid = []; for (let d = orAdd(slot.orderDate, 1); d < slot.delDate; d = orAdd(d, 1)) { const s = OR_SLOTS.find(x => x.del === d.getDay()); if (s) mid.push({ d, s }); }
  master.items.forEach(it => {
    const st = stock[it.id], has = st !== "" && st != null && !isNaN(Number(st));
    if (it.point != null) {
      out[it.id] = { point: true, has, qty: has ? (Number(st) <= it.point ? it.pq : 0) : null };
      return;
    }
    const use = (d, oneDay) => it.rate * orDaySales(basis, d, oneDay) / 1e5;
    const need = cover.reduce((s, d) => s + use(d, slot.days === 1), 0);
    const usedBefore = use(slot.orderDate, false) * timing + before.reduce((s, d) => s + use(d, false), 0);
    let pending = 0, pendNote = [];
    mid.forEach(({ d, s }) => {
      const rec = log[orYmd(d)];
      if (rec && rec.qty && rec.qty[it.id] != null) { pending += Number(rec.qty[it.id]) || 0; pendNote.push(`${d.getMonth() + 1}/${d.getDate()}着 ${rec.qty[it.id]}`); }
      else { const est = [...Array(s.days)].reduce((a, _, i) => a + use(orAdd(d, i), s.days === 1), 0); pending += Math.round(est); pendNote.push(`${d.getMonth() + 1}/${d.getDate()}着 目安${Math.round(est)}`); }
    });
    const proj = has ? Number(st) + pending - usedBefore : null;
    const qty = has ? Math.max(0, Math.round(need - Math.max(0, proj))) : Math.round(need);
    out[it.id] = { has, need, usedBefore, pending, pendNote, proj, qty };
  });
  return out;
}

function OrderApp({ go }) {
  const [master, saveMaster] = useStored(OR_MASTER_KEY, orMasterSeed);
  const [log, saveLog] = useStored(OR_LOG_KEY, orLogSeed);
  const [me] = useMe();
  const today = (() => { const d = new Date(); d.setHours(0, 0, 0, 0); return d; })();
  const [slotIdx, setSlotIdx] = useState(0);
  const slot = orSlotFor(today, slotIdx);
  const delKey = orYmd(slot.delDate);
  const rec = log[delKey];
  const [stock, setStock] = useState(() => (rec && rec.stock) || {});
  const [over, setOver] = useState({});
  const [timing, setTiming] = useState(1);
  const [setOpen, setSetOpen] = useState(false);
  const [msg, setMsg] = useState("");
  useEffect(() => { const r = log[delKey]; setStock((r && r.stock) || {}); setOver({}); }, [delKey]);
  useEffect(() => { if (!msg) return; const t = setTimeout(() => setMsg(""), 2200); return () => clearTimeout(t); }, [msg]);
  const basis = orSalesBasis(today);
  const calc = orCalc(master, log, slot, basis, stock, timing);
  const qtyOf = (id) => over[id] != null ? over[id] : calc[id].qty;
  const isToday = orYmd(slot.orderDate) === orYmd(today);
  const anyStock = master.items.some(it => calc[it.id].has);
  const record = () => {
    const qty = {}; master.items.forEach(it => { const q = qtyOf(it.id); if (q != null) qty[it.id] = q; });
    const st = {}; Object.keys(stock).forEach(k => { if (stock[k] !== "" && stock[k] != null) st[k] = Number(stock[k]); });
    saveLog({ ...log, [delKey]: { order: orYmd(slot.orderDate), qty, stock: st, by: me || "", t: Date.now() } });
    setMsg("発注を記録しました");
  };
  const numIn = { width: 64, minHeight: 44, borderRadius: 10, border: `1.5px solid ${C.line}`, padding: "8px 10px", fontSize: 17, fontWeight: 600, textAlign: "right", fontVariantNumeric: "tabular-nums", color: C.ink, background: C.card, outline: "none" };
  const stepBtn = { width: 34, height: 34, borderRadius: 999, border: "none", background: C.lineSoft, color: C.ink, fontSize: 18, fontWeight: 600, cursor: "pointer", display: "grid", placeItems: "center", lineHeight: 1 };
  const row = (it, i, arr) => {
    const c = calc[it.id], q = qtyOf(it.id), changed = over[it.id] != null;
    const sub = it.point != null ? `在庫${it.point}以下なら${it.pq}${it.unit}`
      : c.has ? `届く日の朝の見込み ${orR(Math.max(0, c.proj))}／必要 ${orR(c.need)}`
      : `必要 ${orR(c.need)}（在庫を入れると差し引きます）`;
    return h("div", { key: it.id, style: { display: "flex", alignItems: "center", gap: 10, padding: "12px 14px", borderTop: i ? `1px solid ${C.lineSoft}` : "none" } },
      h("div", { style: { flex: 1, minWidth: 0 } },
        h("div", { style: { fontSize: 15.5, fontWeight: 700 } }, it.name, h("span", { style: { fontSize: 12, color: C.sub, fontWeight: 500, marginLeft: 6 } }, it.unit)),
        h("div", { style: { fontSize: 12, color: C.sub, marginTop: 3, lineHeight: 1.45 } }, sub)),
      h("label", { style: { display: "flex", flexDirection: "column", alignItems: "center", gap: 2 } },
        h("span", { style: { fontSize: 10.5, color: C.subLight, fontWeight: 600 } }, "今の在庫"),
        h("input", { type: "text", inputMode: "decimal", value: stock[it.id] == null ? "" : String(stock[it.id]), placeholder: "—", "aria-label": `${it.name}の今の在庫`,
          onChange: e => { const v = e.target.value.replace(/[^\d.]/g, ""); setStock(s => ({ ...s, [it.id]: v })); setOver(o => { const n = { ...o }; delete n[it.id]; return n; }); }, style: numIn })),
      h("div", { style: { display: "flex", flexDirection: "column", alignItems: "center", gap: 2, width: 104 } },
        h("span", { style: { fontSize: 10.5, color: C.subLight, fontWeight: 600 } }, changed ? "発注（手で変更）" : "発注"),
        q == null ? h("div", { style: { fontSize: 13, color: C.subLight, height: 40, display: "grid", placeItems: "center" } }, "在庫を入力")
        : h("div", { style: { display: "flex", alignItems: "center", gap: 6 } },
          h("button", { type: "button", "aria-label": "1つ減らす", style: stepBtn, onClick: () => setOver(o => ({ ...o, [it.id]: Math.max(0, q - 1) })) }, "−"),
          h("span", { style: { minWidth: 26, textAlign: "center", fontSize: 24, fontWeight: 700, fontVariantNumeric: "tabular-nums", color: q === 0 ? C.subLight : C.ink } }, q === 0 ? "／" : q),
          h("button", { type: "button", "aria-label": "1つ増やす", style: stepBtn, onClick: () => setOver(o => ({ ...o, [it.id]: q + 1 })) }, "+"))));
  };
  const groups = ["ファクトリー", "物流"];
  const hist = Object.keys(log);
  return h("div", { className: "fk-page" },
    h(Header, null, h(BackHome, { go }),
      h("div", { style: { display: "flex", alignItems: "flex-end", justifyContent: "space-between", gap: 8 } },
        h(AppTitle, { title: "発注表" }),
        h("button", { type: "button", className: "fk-tap", onClick: () => setSetOpen(true), style: { flexShrink: 0, minHeight: 36, background: C.card, color: C.ink, border: `1px solid ${C.line}`, borderRadius: 999, padding: "6px 14px", fontSize: 13, fontWeight: 600, cursor: "pointer", marginBottom: 4 } }, "設定"))),
    h("div", { style: { maxWidth: 640, margin: "0 auto", padding: "14px 14px calc(110px + env(safe-area-inset-bottom))" } },
      // 発注日の切り替え
      h("div", { style: { display: "flex", gap: 7, overflowX: "auto", paddingBottom: 4, marginBottom: 10 } },
        slot.list.map((s, i) => { const on = i === slotIdx, d = s.orderDate;
          return h("button", { key: i, type: "button", className: "fk-tap", onClick: () => setSlotIdx(i), style: { flexShrink: 0, border: "none", borderRadius: 999, padding: "8px 13px", fontSize: 12.5, fontWeight: 600, cursor: "pointer", background: on ? C.ink : C.card, color: on ? "#fff" : C.sub, boxShadow: on ? "none" : `inset 0 0 0 1px ${C.line}` } },
            (orYmd(d) === orYmd(today) ? "今日 " : "") + `${d.getMonth() + 1}/${d.getDate()}（${WD[d.getDay()]}）`); })),
      // いまの発注
      h("div", { style: { ...cardStyle, padding: "16px 16px 14px" } },
        h("div", { style: { fontSize: 12.5, color: C.sub, fontWeight: 600 } }, `${isToday ? "今日" : orMD(slot.orderDate)}の発注 → ${slot.label}`),
        h("div", { style: { fontSize: 22, fontWeight: 700, marginTop: 4, letterSpacing: "-.01em" } }, `${orMD(slot.delDate)}に届く分`),
        h("div", { style: { fontSize: 13, color: C.ink, marginTop: 8, lineHeight: 1.6 } }, "紙の物流発注表の ", h("b", null, `${slot.delDate.getDate()}日（${WD[slot.delDate.getDay()]}）の列`), " に書いて、ASPITに入力してください"),
        rec && h("div", { style: { marginTop: 10, display: "inline-flex", alignItems: "center", gap: 6, fontSize: 12.5, fontWeight: 600, color: C.done, background: C.doneSoft, borderRadius: 999, padding: "5px 11px" } }, h(Icon, { name: "check", size: 15, sw: 2.6 }), `記録済み${rec.by ? `（${rec.by}）` : ""}`)),
      // 在庫を数えたタイミング
      h("div", { style: { margin: "16px 4px 8px", fontSize: 13, fontWeight: 700 } }, "在庫を数えたのは"),
      h("div", { style: { display: "flex", gap: 6, background: C.lineSoft, borderRadius: 10, padding: 3 } },
        [[1, "営業前"], [0.5, "営業中"], [0, "閉店後"]].map(([v, l]) => { const on = v === timing;
          return h("button", { key: l, type: "button", onClick: () => setTiming(v), style: { flex: 1, border: "none", borderRadius: 8, padding: "8px 0", fontSize: 13, fontWeight: 600, cursor: "pointer", background: on ? C.card : "transparent", color: on ? C.ink : C.sub, boxShadow: on ? "0 1px 3px rgba(0,0,0,.12)" : "none" } }, l); })),
      h("div", { style: { fontSize: 12, color: C.sub, margin: "6px 4px 0", lineHeight: 1.6 } }, "今日このあと使う分と、届く日までに使う分・間に届く分を差し引いて計算します"),
      // 品目
      groups.map(g => { const arr = master.items.filter(it => it.grp === g);
        return h(React.Fragment, { key: g },
          h("div", { style: { margin: "18px 4px 8px", fontSize: 13, fontWeight: 700, color: C.sub } }, g),
          h("div", { style: { ...cardStyle, overflow: "hidden" } }, arr.map(row))); }),
      !anyStock && h("div", { style: { fontSize: 12, color: C.sub, margin: "10px 4px 0", lineHeight: 1.6 } }, "在庫が空欄の品目は、売上からの目安だけを出しています"),
      // ボタン
      h("div", { style: { display: "flex", gap: 10, marginTop: 18 } },
        h("a", { href: master.aspit, target: "_blank", rel: "noopener noreferrer", className: "fk-tap", style: { flex: 1, minHeight: 52, borderRadius: 12, border: `1.5px solid ${C.line}`, background: C.card, color: C.ink, fontSize: 15, fontWeight: 600, display: "flex", alignItems: "center", justifyContent: "center", textDecoration: "none" } }, "ASPITを開く"),
        h("button", { type: "button", className: "fk-tap", onClick: record, style: { flex: 1.3, minHeight: 52, borderRadius: 12, border: "none", background: C.ink, color: "#fff", fontSize: 15, fontWeight: 600, cursor: "pointer" } }, rec ? "記録を上書き" : "発注した（記録）")),
      h("div", { style: { fontSize: 12, color: C.sub, margin: "8px 4px 0", lineHeight: 1.6 } }, "記録した数は、次の発注で「間に届く分」として使います"),
      // 見込み売上
      h("div", { style: { margin: "22px 4px 8px", fontSize: 13, fontWeight: 700, color: C.sub } }, "計算に使った売上（税抜）"),
      h("div", { style: { ...cardStyle, padding: "4px 16px 10px" } },
        [...Array(slot.days)].map((_, i) => { const d = orAdd(slot.delDate, i);
          return h(DRow, { key: i, label: `${orMD(d)}の見込み`, value: "¥" + Math.round(orDaySales(basis, d, slot.days === 1)).toLocaleString("ja-JP") + (slot.days === 1 ? "（直近2週の一番売れた日）" : "（直近2週の平均）") }); }),
        h("div", { style: { fontSize: 12, color: basis.sample ? C.drop : C.subLight, paddingTop: 8, lineHeight: 1.6 } },
          basis.sample ? `金種の当日売上が${basis.n}日分しかないため、10〜11月の平均で計算しています` : `金種の当日売上 ${orMD(basis.from)}〜${orMD(basis.to)}（${basis.n}日分）から`)),
      // 発注の記録（紙の物流発注表と同じ形：列＝届く日）
      hist.length > 0 && h(React.Fragment, null,
        h("div", { style: { margin: "22px 4px 8px", fontSize: 13, fontWeight: 700, color: C.sub } }, "発注表（届く日ごと）"),
        h(OrderGrid, { master, log, hi: delKey, draft: (() => { const q = {}; master.items.forEach(it => { const v = qtyOf(it.id); if (v != null) q[it.id] = v; }); return q; })() }))),
    h(Sheet, { open: setOpen, onClose: () => setSetOpen(false), title: "発注の設定" }, setOpen && h(OrderSettings, { master, saveMaster })),
    h(Toast, { text: msg }));
}

function OrderGrid({ master, log, hi, draft }) {
  const ref = useRef(null);
  const keys = Array.from(new Set([...Object.keys(log), hi])).sort().slice(-14);
  useEffect(() => { const el = ref.current; if (el) el.scrollLeft = el.scrollWidth; }, [keys.length]);
  const cell = { padding: "8px 0", textAlign: "center", fontSize: 14, fontVariantNumeric: "tabular-nums", minWidth: 44, borderLeft: `1px solid ${C.lineSoft}` };
  const nameCell = { position: "sticky", left: 0, background: C.card, zIndex: 1, padding: "8px 12px", fontSize: 13, fontWeight: 600, whiteSpace: "nowrap", textAlign: "left" };
  return h("div", { style: { ...cardStyle, overflow: "hidden" } },
    h("div", { ref, style: { overflowX: "auto", WebkitOverflowScrolling: "touch" } },
      h("table", { style: { borderCollapse: "collapse", width: "100%" } },
        h("thead", null, h("tr", { style: { borderBottom: `1px solid ${C.line}` } },
          h("th", { style: { ...nameCell, fontSize: 11.5, color: C.sub } }, "届く日"),
          keys.map(k => { const d = new Date(k + "T00:00:00"), on = k === hi, we = d.getDay() === 0 || d.getDay() === 6;
            return h("th", { key: k, style: { ...cell, fontSize: 12, fontWeight: 700, background: on ? C.lineSoft : "transparent", color: on ? C.ink : C.sub } },
              h("div", null, `${d.getMonth() + 1}/${d.getDate()}`), h("div", { style: { fontSize: 11, fontWeight: 500, color: we ? C.drop : C.subLight } }, WD[d.getDay()])); }))),
        h("tbody", null, master.items.map((it, i) => h("tr", { key: it.id, style: { borderTop: i ? `1px solid ${C.lineSoft}` : "none" } },
          h("td", { style: nameCell }, it.name),
          keys.map(k => { const on = k === hi, r = log[k], v = on && !r ? draft[it.id] : r && r.qty ? r.qty[it.id] : null;
            return h("td", { key: k, style: { ...cell, background: on ? C.lineSoft : "transparent", fontWeight: on ? 700 : 500, color: v ? (on && !r ? C.sub : C.ink) : C.subLight } }, v ? v : "／"); })))))),
    h("div", { style: { fontSize: 11.5, color: C.subLight, padding: "8px 12px", borderTop: `1px solid ${C.lineSoft}` } }, "灰色の列が今回の発注。記録前はうすい字で表示しています"));
}

function OrderSettings({ master, saveMaster }) {
  const upd = (id, patch) => saveMaster({ ...master, items: master.items.map(it => it.id === id ? { ...it, ...patch } : it) });
  const inp = { width: 70, minHeight: 40, borderRadius: 10, border: `1.5px solid ${C.line}`, padding: "6px 8px", fontSize: 15, textAlign: "right", color: C.ink, background: C.card, outline: "none" };
  return h("div", null,
    h("div", { style: { fontSize: 12.5, color: C.sub, lineHeight: 1.7, marginBottom: 12 } }, "使用量は「売上10万円（税抜）あたり、いくつ使うか」です。10/1〜11/12のペルゴの納品書と売上から出しました。"),
    h("div", { style: { ...cardStyle, overflow: "hidden" } },
      master.items.map((it, i) => h("div", { key: it.id, style: { display: "flex", alignItems: "center", gap: 8, padding: "10px 14px", borderTop: i ? `1px solid ${C.lineSoft}` : "none" } },
        h("div", { style: { flex: 1, fontSize: 14.5, fontWeight: 600 } }, it.name, h("span", { style: { fontSize: 12, color: C.sub, marginLeft: 4 } }, it.unit)),
        it.point != null
          ? h(React.Fragment, null, h("span", { style: { fontSize: 12, color: C.sub } }, "在庫"),
              h("input", { inputMode: "numeric", value: it.point, onChange: e => upd(it.id, { point: Number(e.target.value.replace(/[^\d]/g, "")) || 0 }), style: { ...inp, width: 48 } }),
              h("span", { style: { fontSize: 12, color: C.sub } }, "以下で"),
              h("input", { inputMode: "numeric", value: it.pq, onChange: e => upd(it.id, { pq: Number(e.target.value.replace(/[^\d]/g, "")) || 0 }), style: { ...inp, width: 48 } }))
          : h(React.Fragment, null, h("span", { style: { fontSize: 12, color: C.sub } }, "10万円あたり"),
              h("input", { inputMode: "decimal", defaultValue: it.rate, onBlur: e => { const v = Number(e.target.value); if (v > 0) upd(it.id, { rate: v }); }, style: inp }))))),
    h("label", { style: { display: "block", marginTop: 18 } },
      h("div", { style: { fontSize: 12.5, fontWeight: 700, color: C.sub, marginBottom: 6 } }, "ASPITのリンク"),
      h("input", { type: "url", defaultValue: master.aspit, onBlur: e => saveMaster({ ...master, aspit: e.target.value.trim() }), style: { ...inp, width: "100%", textAlign: "left", fontSize: 14 } })));
}

function HomeOrder({ go }) {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const s = OR_SLOTS.find(x => x.od === today.getDay());
  const log = readStored(OR_LOG_KEY, orLogSeed);
  if (!s) return null;
  const sl = orSlotFor(today, 0), done = !!log[orYmd(sl.delDate)];
  const p = PAGES.find(x => x.k === "order");
  return h("div", { style: { marginTop: 12 } }, h(HomeTile, { icon: p.icon, tint: p.tint, soft: p.soft, title: `今日は発注日（${sl.label}）`, badge: done ? "記録済み" : "まだ", warn: !done, onClick: () => go("order") }));
}
