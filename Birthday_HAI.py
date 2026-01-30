import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף - centered שומר על טבלאות ברוחב קריא ונעים
st.set_page_config(page_title="לוח ימי הולדת משפחתי", layout="centered")

# מנגנון ייבוא גמיש
try:
    from st_gsheets_connection import GSheetsConnection
except ImportError:
    from streamlit_gsheets import GSheetsConnection

def get_zodiac(d, m):
    zodiacs = [(21,3,19,4,"טלה ♈"),(20,4,20,5,"שור ♉"),(21,5,20,6,"תאומים ♊"),
               (21,6,22,7,"סרטן ♋"),(23,7,22,8,"אריה ♌"),(23,8,22,9,"בתולה ♍"),
               (23,9,22,10,"מאזניים ♎"),(23,10,21,11,"עקרב ♏"),(22,11,21,12,"קשת ♐"),
               (22,12,19,1,"גדי ♑"),(20,1,18,2,"דלי ♒"),(19,2,20,3,"דגים ♓")]
    for sd,sm,ed,em,n in zodiacs:
        if (m==sm and d>=sd) or (m==em and d<=ed): return n
    return "דגים ♓"

def process_person(name, bday_date, is_temporary=False):
    today = date.today()
    h_date = dates.HebrewDate.from_pydate(bday_date)
    next_bday = bday_date.replace(year=today.year)
    if next_bday < today:
        next_bday = next_bday.replace(year=today.year + 1)
    days_left = (next_bday - today).days
    age = today.year - bday_date.year - ((today.month, today.day) < (bday_date.month, bday_date.day))
    return {
        "שם": name,
        "תאריך לידה": bday_date.strftime('%d/%m/%Y'),
        "תאריך עברי": h_date.hebrew_date_string(),
        "מזל": get_zodiac(bday_date.day, bday_date.month),
        "גיל": age,
        "ימים ליומולדת": days_left,
        "חודש": bday_date.month,
        "יום": bday_date.day,
        "זמני": is_temporary
    }

if "temp_people" not in st.session_state:
    st.session_state.temp_people = []

all_people = []
url = ""
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    df_raw = conn.read(ttl=0).dropna(how="all")
    for _, row in df_raw.iterrows():
        try:
            b_date = pd.to_datetime(row['Birthday'], dayfirst=True).date()
            all_people.append(process_person(row['Full_Name'], b_date))
        except: continue
except: pass

all_people.extend(st.session_state.temp_people)
today = date.today()

# --- 1. חגיגות היום (עם "מזל טוב" מעל השם) ---
hbd_today = [p for p in all_people if p["חודש"] == today.month and p["יום"] == today.day]
if hbd_today:
    st.balloons()
    for p in hbd_today:
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 20px; text-align: center; 
                        border: 3px solid #f0f2f6; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px;">
                <p style="color: #ff4b4b; font-size: 28px; font-weight: bold; margin-bottom: 5px;">🎈 מזל טוב! 🎈</p>
                <h1 style="color: #1f1f1f; margin: 0; font-size: 45px;">
                    🎁 {p['שם']} 🎁
                </h1>
                <h2 style="color: #ff4b4b; margin: 10px 0 0 0;">חוגג/ת היום {p['גיל']} שנים! 🎂</h2>
            </div>
        """, unsafe_allow_html=True)

def style_temp(row):
    return ['background-color: #ffffd1' if row.זמני else '' for _ in row]

display_cols = ["שם", "תאריך לידה", "גיל", "מזל", "תאריך עברי", "ימים ליומולדת"]

# --- 2. טבלת החודש ---
st.header(f"📅 חגיגות קרובות לחודש זה")
this_month = [p for p in all_people if p["חודש"] == today.month and p["יום"] >= today.day]
this_month = sorted(this_month, key=lambda x: x["יום"])

if this_month:
    df_m = pd.DataFrame(this_month)
    st.table(df_m[display_cols].style.apply(style_temp, axis=1))
else:
    st.info("אין חגיגות נוספות לחודש זה.")

st.markdown("---")

# --- 3. טבלה כללית ---
st.header("📊 רשימת כל החוגגים")
if all_people:
    all_sorted = sorted(all_people, key=lambda x: (x["חודש"], x["יום"]))
    df_all = pd.DataFrame(all_sorted)
    st.table(df_all[display_cols].style.apply(style_temp, axis=1))

st.markdown("---")

# --- 4. הוספה זמנית + כפתור רענון ---
col_h, col_r = st.columns([0.8, 0.2])
with col_h:
    st.subheader("⏱️ הוספה זמנית")
with col_r:
    if st.button("🔄 רענון"):
        st.cache_data.clear()
        st.rerun()

with st.form("temp_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1: t_name = st.text_input("שם:")
    with c2: t_date = st.date_input("תאריך לידה:", value=date(2000,1,1))
    if st.form_submit_button("הוסף זמנית"):
        if t_name:
            st.session_state.temp_people.append(process_person(t_name, t_date, is_temporary=True))
            st.rerun()

st.markdown("---")

# --- 5. הוספה קבועה ---
st.subheader("📌 הוספה קבועה")
if url: st.link_button("🔗 פתח אקסל לעריכה קבועה", url)
