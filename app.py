import streamlit as st, sqlite3, hashlib, secrets, hmac, json, html
from pathlib import Path
from datetime import date,datetime,time
import streamlit.components.v1 as components

DB=Path(__file__).with_name("dose_reminde.sqlite3")
st.set_page_config(page_title="Dose Reminde",page_icon="💚",layout="wide")
def con():
 c=sqlite3.connect(DB,timeout=15);c.row_factory=sqlite3.Row;return c
with con() as c:
 c.executescript("""
 CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,email TEXT UNIQUE,salt TEXT,pwhash TEXT,language TEXT,role TEXT);
 CREATE TABLE IF NOT EXISTS meds(id INTEGER PRIMARY KEY,uid INTEGER REFERENCES users(id) ON DELETE CASCADE,name TEXT,label TEXT,notes TEXT,tm TEXT,days TEXT,start TEXT,end TEXT,active INTEGER DEFAULT 1);
 CREATE TABLE IF NOT EXISTS logs(id INTEGER PRIMARY KEY,uid INTEGER,mid INTEGER,day TEXT,tm TEXT,status TEXT,updated TEXT,UNIQUE(mid,day,tm));
 """)
def pw_hash(p,salt=None):
 salt=salt or secrets.token_hex(16)
 return salt,hashlib.pbkdf2_hmac("sha256",p.encode(),bytes.fromhex(salt),310000).hex()
def get_user(e):
 with con() as c:return c.execute("SELECT * FROM users WHERE email=?",(e.strip().lower(),)).fetchone()
def auth(u):
 st.session_state.uid=u["id"];st.session_state.name=u["name"];st.session_state.language=u["language"]
def medlist(active=False):
 with con() as c:return c.execute("SELECT * FROM meds WHERE uid=?"+(" AND active=1" if active else "")+" ORDER BY tm",(st.session_state.uid,)).fetchall()
def status(mid,d,tm):
 with con() as c:r=c.execute("SELECT status FROM logs WHERE uid=? AND mid=? AND day=? AND tm=?",(st.session_state.uid,mid,d,tm)).fetchone()
 return r["status"] if r else "Unconfirmed"
def setstat(mid,d,tm,s):
 with con() as c:c.execute("""INSERT INTO logs(uid,mid,day,tm,status,updated) VALUES(?,?,?,?,?,?)
 ON CONFLICT(mid,day,tm) DO UPDATE SET status=excluded.status,updated=excluded.updated""",(st.session_state.uid,mid,d,tm,s,datetime.now().isoformat()))
def tr(en,hi):return hi if st.session_state.get("language","English")=="हिंदी" else en
st.markdown("<style>.block-container{max-width:1100px;padding-top:1.4rem}.stButton button{min-height:46px;border-radius:12px;font-size:16px}</style>",unsafe_allow_html=True)
if "uid" not in st.session_state:st.session_state.uid=None
if "language" not in st.session_state:st.session_state.language="English"
if not st.session_state.uid:
 a,b=st.columns(2,gap="large")
 with a:
  st.title("💚 Dose Reminde")
  st.subheader(tr("Gentle reminders. Clear tracking.","आसान रिमाइंडर। साफ़ रिकॉर्ड।"))
  st.write(tr("A dose schedule helper for older adults and trusted caregivers.","बुज़ुर्गों और भरोसेमंद केयरगिवर के लिए डोज़ शेड्यूल सहायता।"))
  st.info(tr("Reminder tool only. Always follow the prescription.","यह केवल रिमाइंडर टूल है। प्रिस्क्रिप्शन का पालन करें।"))
 with b:
  st.header(tr("Welcome","स्वागत है"))
  st.session_state.language=st.selectbox("Language / भाषा",["English","हिंदी"])
  mode=st.radio(tr("Account","अकाउंट"),["Sign In","Sign Up"],horizontal=True)
  if mode=="Sign Up":
   with st.form("register"):
    name=st.text_input(tr("Full name","पूरा नाम"))
    email=st.text_input("Email")
    role=st.selectbox(tr("Role","भूमिका"),["Elderly User","Caregiver"])
    p=st.text_input(tr("Password (10+ characters)","पासवर्ड (10+ अक्षर)"),type="password")
    p2=st.text_input(tr("Confirm password","पासवर्ड दोबारा"),type="password")
    ok=st.checkbox(tr("I understand this is a demo, not medical advice.","मैं समझता/समझती हूँ कि यह डेमो है, मेडिकल सलाह नहीं।"))
    submit=st.form_submit_button(tr("Create account","खाता बनाएँ"),use_container_width=True)
   if submit:
    if not name.strip() or "@" not in email:st.error(tr("Enter name and valid email.","नाम और सही ईमेल भरें।"))
    elif len(p)<10:st.error(tr("Password must be at least 10 characters.","पासवर्ड कम से कम 10 अक्षर का हो।"))
    elif p!=p2:st.error(tr("Passwords do not match.","पासवर्ड मेल नहीं खाते।"))
    elif not ok:st.error(tr("Please accept the notice.","कृपया सूचना स्वीकार करें।"))
    elif get_user(email):st.error(tr("Email already registered.","ईमेल पहले से रजिस्टर्ड है।"))
    else:
     salt,digest=pw_hash(p)
     try:
      with con() as c:c.execute("INSERT INTO users(name,email,salt,pwhash,language,role) VALUES(?,?,?,?,?,?)",(name.strip(),email.strip().lower(),salt,digest,st.session_state.language,role))
      auth(get_user(email));st.rerun()
     except sqlite3.IntegrityError:st.error(tr("Email already registered.","ईमेल पहले से रजिस्टर्ड है।"))
  else:
   with st.form("login"):
    email=st.text_input("Email");p=st.text_input(tr("Password","पासवर्ड"),type="password")
    submit=st.form_submit_button(tr("Sign In","लॉगिन"),use_container_width=True)
   if submit:
    u=get_user(email)
    if not u:st.error(tr("Account not found. Please sign up.","अकाउंट नहीं मिला। पहले साइन अप करें।"))
    else:
     _,digest=pw_hash(p,u["salt"])
     if hmac.compare_digest(digest,u["pwhash"]):auth(u);st.rerun()
     else:st.error(tr("Incorrect credentials.","जानकारी गलत है।"))
 st.stop()
with con() as c:u=c.execute("SELECT * FROM users WHERE id=?",(st.session_state.uid,)).fetchone()
if not u:st.session_state.uid=None;st.rerun()
with st.sidebar:
 st.markdown("## 💚 Dose Reminde");st.write(tr("Hello","नमस्ते")+", "+u["name"])
 language=st.selectbox("Language / भाषा",["English","हिंदी"],index=0 if u["language"]=="English" else 1)
 if language!=u["language"]:
  with con() as c:c.execute("UPDATE users SET language=? WHERE id=?",(language,u["id"]))
  st.session_state.language=language;st.rerun()
 page=st.radio(tr("Menu","मेन्यू"),["Today","Add Schedule","History","Manage"])
 if st.button(tr("Log out","लॉगआउट")):st.session_state.uid=None;st.rerun()
st.title("💚 Dose Reminde")
st.warning(tr("Follow the prescription. This app does not choose, calculate, or change doses.","प्रिस्क्रिप्शन का पालन करें। ऐप खुराक तय, गणना या बदलता नहीं है।"))
today=date.today()
if page=="Today":
 st.header(tr("Today's doses","आज की डोज़"));entries=[]
 for m in medlist(True):
  if today.isoformat()<m["start"] or (m["end"] and today.isoformat()>m["end"]) or today.strftime("%a") not in m["days"].split(","):continue
  entries.append((m,status(m["id"],today.isoformat(),m["tm"])))
 counts={s:sum(v==s for _,v in entries) for s in ["Taken","Skipped","Unconfirmed"]}
 a,b,c=st.columns(3);a.metric(tr("Taken","ली गई"),counts["Taken"]);b.metric(tr("Skipped","छोड़ी"),counts["Skipped"]);c.metric(tr("Unconfirmed","पुष्टि बाकी"),counts["Unconfirmed"])
 rem=[{"name":m["name"],"tm":m["tm"],"id":m["id"],"status":s} for m,s in entries]
 # Best-effort in-page alerts. They are not background alarms.
 components.html(f"""<section style="font:16px Arial;border:1px solid #8888;border-radius:12px;padding:12px">
 <b>🔔 Browser reminders / ब्राउज़र रिमाइंडर</b><p id="info">Permission not requested / अनुमति नहीं मिली</p>
 <button id="allow" style="padding:10px;font-size:16px">Enable notifications / चालू करें</button>
 <p style="font-size:13px">Keep this page open. Alerts are not guaranteed if tab/device sleeps or closes.</p></section>
 <script>
 const ds={json.dumps(rem,ensure_ascii=False)};let seen=new Set(),info=document.getElementById('info');
 function refresh(){{info.textContent='Notification permission: '+(('Notification'in window)?Notification.permission:'unsupported')}}
 refresh();document.getElementById('allow').onclick=async()=>{{if(!('Notification'in window)){{info.textContent='Not supported in this browser';return}};await Notification.requestPermission();refresh();if(Notification.permission==='granted')new Notification('Dose Reminde',{{body:'Browser notifications enabled'}})}};
 setInterval(()=>{{if(!('Notification'in window)||Notification.permission!=='granted')return;
 let n=new Date(),d=n.getFullYear()+'-'+String(n.getMonth()+1).padStart(2,'0')+'-'+String(n.getDate()).padStart(2,'0');
 for(let x of ds){{let k=x.id+d+x.tm,[h,m]=x.tm.split(':').map(Number);if(x.status==='Unconfirmed'&&n.getHours()===h&&n.getMinutes()===m&&!seen.has(k)){{seen.add(k);new Notification('💊 Dose Reminde',{{body:x.name+' — scheduled dose time. Check your prescription and record status.'}})}}}}
 }},15000);
 </script>""",height=175)
 if not entries:st.info(tr("No doses today. Add a schedule to start.","आज कोई डोज़ नहीं। शेड्यूल जोड़ें।"))
 for m,s in entries:
  with st.container(border=True):
   x,y=st.columns([3,2])
   with x:
    st.subheader("💊 "+m["name"]);st.markdown("### "+datetime.strptime(m["tm"],"%H:%M").strftime("%I:%M %p"));st.write("Status: "+s)
    if m["label"]:st.write(m["label"])
    if m["notes"]:st.write(m["notes"])
   with y:
    if s!="Taken" and st.button(tr("✓ Mark Taken","✓ ली गई"),key=f"t{m['id']}",use_container_width=True):setstat(m["id"],today.isoformat(),m["tm"],"Taken");st.rerun()
    if s=="Unconfirmed" and st.button(tr("Skipped","छोड़ी गई"),key=f"s{m['id']}",use_container_width=True):setstat(m["id"],today.isoformat(),m["tm"],"Skipped");st.rerun()
    if s!="Unconfirmed" and st.button(tr("Reset status","रीसेट"),key=f"r{m['id']}",use_container_width=True):setstat(m["id"],today.isoformat(),m["tm"],"Unconfirmed");st.rerun()
 st.caption(tr("Browser reminders are best-effort only: Today page must stay open, and browser/device settings must allow notifications.","ब्राउज़र रिमाइंडर की गारंटी नहीं: Today पेज खुला और नोटिफिकेशन अनुमति चालू होनी चाहिए।"))
elif page=="Add Schedule":
 st.header(tr("Add schedule","शेड्यूल जोड़ें"));st.info(tr("Enter only a schedule checked against the current prescription.","केवल प्रिस्क्रिप्शन से जाँचा हुआ शेड्यूल भरें।"))
 dayopts=[("Mon","Monday","सोमवार"),("Tue","Tuesday","मंगलवार"),("Wed","Wednesday","बुधवार"),("Thu","Thursday","गुरुवार"),("Fri","Friday","शुक्रवार"),("Sat","Saturday","शनिवार"),("Sun","Sunday","रविवार")]
 with st.form("doseform",clear_on_submit=True):
  name=st.text_input(tr("Medicine name *","दवा का नाम *"));label=st.text_input(tr("Prescription label (optional)","प्रिस्क्रिप्शन लेबल"));notes=st.text_area(tr("Instructions (optional)","निर्देश"))
  tm=st.time_input(tr("Reminder time","रिमाइंडर समय"),time(9)).strftime("%H:%M")
  days=st.multiselect(tr("Repeat days","दोहराने के दिन"),[tr(en,hi) for _,en,hi in dayopts],default=[tr("Monday","सोमवार")])
  start=st.date_input(tr("Start date","शुरू तारीख"),today);noend=st.checkbox(tr("No end date","अंतिम तारीख नहीं"),True);end=None if noend else st.date_input(tr("End date","अंतिम तारीख"),today)
  verified=st.checkbox(tr("Verified with current prescription","प्रिस्क्रिप्शन से जाँच लिया"))
  go=st.form_submit_button(tr("Save schedule","सेव करें"),use_container_width=True)
 if go:
  codes=[code for code,en,hi in dayopts if tr(en,hi) in days]
  if not name.strip():st.error(tr("Enter a medicine name.","दवा का नाम भरें।"))
  elif not codes:st.error(tr("Choose at least one day.","कम से कम एक दिन चुनें।"))
  elif end and end<start:st.error(tr("End date must follow start date.","अंतिम तारीख सही रखें।"))
  elif not verified:st.error(tr("Verify schedule before saving.","पहले शेड्यूल जाँचें।"))
  else:
   with con() as c:c.execute("INSERT INTO meds(uid,name,label,notes,tm,days,start,end) VALUES(?,?,?,?,?,?,?,?)",(st.session_state.uid,name.strip(),label.strip(),notes.strip(),tm,",".join(codes),start.isoformat(),end.isoformat() if end else ""))
   st.success(tr("Schedule saved.","शेड्यूल सेव हो गया।"));st.rerun()
elif page=="History":
 st.header(tr("History","इतिहास"));d=st.date_input(tr("Date","तारीख"),today)
 for m in medlist():
  if d.isoformat()<m["start"] or (m["end"] and d.isoformat()>m["end"]) or d.strftime("%a") not in m["days"].split(","):continue
  st.write(f"**{m['name']}** · {m['tm']} · {status(m['id'],d.isoformat(),m['tm'])}")
elif page=="Manage":
 st.header(tr("Manage schedules","शेड्यूल प्रबंधन"))
 for m in medlist():
  with st.container(border=True):
   st.subheader(m["name"]);st.write(f"{m['tm']} · {m['days']} · "+("Active" if m["active"] else "Paused"))
   a,b=st.columns(2)
   if a.button("Pause" if m["active"] else "Resume",key=f"p{m['id']}"):
    with con() as c:c.execute("UPDATE meds SET active=? WHERE id=? AND uid=?",(0 if m["active"] else 1,m["id"],st.session_state.uid))
    st.rerun()
   with b.popover("Remove"):
    st.warning("This also deletes dose history.")
    if st.button("Confirm remove",key=f"d{m['id']}"):
     with con() as c:c.execute("DELETE FROM logs WHERE mid=? AND uid=?",(m["id"],st.session_state.uid));c.execute("DELETE FROM meds WHERE id=? AND uid=?",(m["id"],st.session_state.uid))
     st.rerun()
st.divider()
st.caption(tr("Demo only. Status is self-reported, not proof of taking medicine. Browser notifications may fail. No password recovery, email verification, MFA, caregiver sharing, cloud encryption or production security review. Do not use real patient data or publish this version as-is. For late/uncertain doses, ask a pharmacist/clinician; never double a dose based on this app.","केवल डेमो। स्टेटस स्वयं दर्ज किया जाता है, दवा लेने का प्रमाण नहीं। नोटिफिकेशन छूट सकते हैं। पासवर्ड रिकवरी, ईमेल सत्यापन, MFA, केयरगिवर शेयरिंग, क्लाउड सुरक्षा या प्रोडक्शन समीक्षा नहीं है। असली मरीज डेटा न डालें। देर/संदेह पर डॉक्टर/फार्मासिस्ट से पूछें; ऐप के आधार पर दोहरी खुराक न लें।"))
