import streamlit as st
import urllib.request, json

st.set_page_config(page_title="Elimu Stats — Takwimu za Elimu Kenya", page_icon="📚", layout="wide")
st.markdown("""<style>
.stApp{background:#0a0c14;color:#e8edf5}
.e-card{background:#0d1117;border:1px solid #21262d;border-radius:10px;padding:14px 18px;margin:8px 0}
.stat-box{background:#0d1829;border:1px solid #1e3a6e;border-radius:8px;padding:12px;text-align:center;margin:4px}
.stButton>button{background:#1f6feb;color:#fff;border:none;border-radius:8px;padding:10px 20px;font-weight:700}
</style>""", unsafe_allow_html=True)

API_KEY = st.secrets.get("GOOGLE_API_KEY") or st.secrets.get("GEMINI_API_KEY","")

# DEMO NEMIS-style data (DEMO — synthetic, source label mandatory)
DEMO_STATS = {
    "Nairobi":  {"schools":1847,"teachers":28934,"students":612000,"ptr":21.1,"gcr":94.2,"dropout":3.1,"top_school":"Alliance High School"},
    "Kiambu":   {"schools":1124,"teachers":19234,"students":387000,"ptr":20.1,"gcr":96.1,"dropout":2.4,"top_school":"Naivasha High School"},
    "Kisumu":   {"schools":892, "teachers":14892,"students":298000,"ptr":20.0,"gcr":88.4,"dropout":5.2,"top_school":"Kisumu Boys High School"},
    "Nakuru":   {"schools":1203,"teachers":18234,"students":378000,"ptr":20.7,"gcr":91.3,"dropout":3.8,"top_school":"Nakuru High School"},
    "Mombasa":  {"schools":634, "teachers":10234,"students":198000,"ptr":19.3,"gcr":87.9,"dropout":5.9,"top_school":"Coast Academy"},
    "Turkana":  {"schools":387, "teachers":4234, "students":89000, "ptr":21.0,"gcr":62.1,"dropout":18.4,"top_school":"Lodwar High School"},
    "Mandera":  {"schools":312, "teachers":3891, "students":78000, "ptr":20.0,"gcr":58.3,"dropout":22.1,"top_school":"Mandera Secondary"},
}

def ask(q):
    if not API_KEY: return "❌ API key not configured."
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"
    body = {"contents":[{"role":"user","parts":[{"text":q}]}],
            "systemInstruction":{"parts":[{"text":"Wewe ni mchambuzi wa elimu Kenya. Eleza takwimu na toa mapendekezo ya kuboresha elimu. Jibu kwa Kiingereza na Kiswahili."}]},
            "generationConfig":{"temperature":0.2,"maxOutputTokens":600}}
    try:
        req = urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req,timeout=30) as r:
            return json.loads(r.read())["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e: return f"❌ {e}"

st.markdown("# 📚 Elimu Stats Kenya")
st.markdown("**Takwimu za Elimu — Kenya County Education Dashboard**")
st.info("⚠️ **DEMO DATA** — Takwimu za mfano (synthetic). Kwa data halisi: nemis.go.ke | education.go.ke")

tab1,tab2 = st.tabs(["📊 Dashboard ya Kaunti","🤖 Uchambuzi wa AI"])

with tab1:
    c1,c2 = st.columns([1,2])
    with c1:
        county = st.selectbox("Chagua Kaunti:", list(DEMO_STATS.keys()))
        compare = st.selectbox("Linganisha na:", ["Hakuna"]+[k for k in DEMO_STATS if k != county])
    with c2:
        d = DEMO_STATS[county]
        cols = st.columns(4)
        metrics = [("🏫 Shule",f"{d['schools']:,}"),("👨‍🏫 Walimu",f"{d['teachers']:,}"),("🎓 Wanafunzi",f"{d['students']:,}"),("📊 PTR",f"{d['ptr']:.1f}:1")]
        for col,(label,val) in zip(cols,metrics):
            with col: st.markdown(f'<div class="stat-box"><div style="color:#8b949e;font-size:0.75rem">{label}</div><div style="font-size:1.4rem;font-weight:700">{val}</div></div>', unsafe_allow_html=True)
        st.markdown(f"""<div class="e-card">
📈 GCR (Gross Completion Rate): <b style="color:{'#56d364' if d['gcr']>85 else '#e3b341' if d['gcr']>70 else '#f85149'}">{d['gcr']:.1f}%</b><br>
🚪 Dropout Rate: <b style="color:{'#f85149' if d['dropout']>10 else '#e3b341' if d['dropout']>5 else '#56d364'}">{d['dropout']:.1f}%</b><br>
🏆 Top School: {d['top_school']}
</div>""", unsafe_allow_html=True)

        if compare != "Hakuna":
            d2 = DEMO_STATS[compare]
            st.markdown(f"#### {county} vs {compare}")
            diffs = [("Wanafunzi",d['students'],d2['students'],""),("PTR",d['ptr'],d2['ptr']," (chini = bora)"),("GCR%",d['gcr'],d2['gcr'],"% (juu = bora)"),("Dropout%",d['dropout'],d2['dropout'],"% (chini = bora)")]
            for label,v1,v2,suffix in diffs:
                better = (v1 < v2) if "Dropout" in label or "PTR" in label else (v1 > v2)
                winner = county if better else compare
                st.markdown(f'<div class="e-card">{label}: {county}={v1}{suffix} | {compare}={v2}{suffix} → <b style="color:#56d364">{winner} ni bora</b></div>', unsafe_allow_html=True)

with tab2:
    data_summary = {c: {"gcr":d["gcr"],"dropout":d["dropout"],"ptr":d["ptr"]} for c,d in DEMO_STATS.items()}
    analysis_q = st.selectbox("Swali la uchambuzi:", [
        "Kaunti zipi zina tatizo kubwa la kuacha shule (dropout)?",
        "Jinsi ya kuboresha uandikishaji wa wasichana kaskazini Kenya?",
        "Kaunti zipi zinahitaji walimu zaidi haraka?",
        "Linganisha elimu kati ya mijini na vijijini Kenya",
        "Mapendekezo ya kuboresha GCR chini ya 70%",
    ])
    if st.button("🤖 Changanua", key="ai_btn"):
        with st.spinner("..."):
            result = ask(f"Data ya elimu Kenya: {json.dumps(data_summary)}\n\nUchanganue: {analysis_q}")
        st.markdown(f'<div class="e-card">{result.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

st.markdown("---")
st.caption("📚 Elimu Stats v1.0 | Data: DEMO synthetic | NEMIS: nemis.go.ke | CC BY-NC-ND 4.0")
