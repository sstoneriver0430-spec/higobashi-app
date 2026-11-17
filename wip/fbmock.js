(function(){
  const data = window.__SEED__ || {};            // {collection:{docId:obj}}
  const subs = [];
  const colDocs = (c) => data[c] || (data[c] = {});
  const snapDoc = (c, id) => ({ id, metadata: { fromCache: false }, exists: id in colDocs(c), data: () => JSON.parse(JSON.stringify(colDocs(c)[id])) });
  const snapCol = (c) => { const ids = Object.keys(colDocs(c)); return { empty: !ids.length, docs: ids.map(i => snapDoc(c, i)), metadata: { fromCache: false }, forEach(f){ this.docs.forEach(f); } }; };
  const fire = () => subs.forEach(s => setTimeout(s, 0));
  const merge = (a, b) => { Object.keys(b).forEach(k => { if (b[k] && typeof b[k] === "object" && !Array.isArray(b[k]) && a[k] && typeof a[k] === "object") merge(a[k], b[k]); else a[k] = b[k]; }); return a; };
  const chk = (v, path) => { if (v === undefined) throw new Error("Firestore: undefined at " + path); if (Array.isArray(v)) v.forEach((x, i) => { if (Array.isArray(x)) throw new Error("Firestore: nested array at " + path); chk(x, path + "[" + i + "]"); }); else if (v && typeof v === "object") Object.keys(v).forEach(k => chk(v[k], path + "." + k)); };
  const docRef = (c, id) => ({ id,
    get: () => Promise.resolve(snapDoc(c, id)),
    set: (v, o) => { try { chk(v, c + "/" + id); } catch (e) { console.error("WRITE REJECTED", e.message); return Promise.reject(e); } window.__WRITES__.push(c + "/" + id); colDocs(c)[id] = o && o.merge && colDocs(c)[id] ? merge(colDocs(c)[id], JSON.parse(JSON.stringify(v))) : JSON.parse(JSON.stringify(v)); fire(); return Promise.resolve(); },
    delete: () => { delete colDocs(c)[id]; fire(); return Promise.resolve(); },
    onSnapshot: (f) => { const s = () => f(snapDoc(c, id)); subs.push(s); if (window.__CACHE_FIRST__) setTimeout(() => f({ id, exists: false, metadata: { fromCache: true }, data: () => undefined }), 5); setTimeout(s, 300); return () => {}; } });
  const col = (c) => ({ doc: (id) => docRef(c, id), onSnapshot: (f) => { const s = () => f(snapCol(c)); subs.push(s); setTimeout(s, 30); return () => {}; }, get: () => Promise.resolve(snapCol(c)) });
  window.__WRITES__ = [];
  window.firebase = { initializeApp(){}, firestore: () => ({ enablePersistence: () => Promise.resolve(), collection: col }),
    auth: () => ({ onAuthStateChanged: (f) => setTimeout(() => f({ uid: "x" }), 20), signInAnonymously: () => Promise.resolve() }) };
})();
