import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="לוח ימי הולדת משפחתי", layout="centered")

# CSS להעלמת עמודת האינדקס - הדרך היחידה שבאמת עובדת ב-st.table
st.markdown("""
    <style>
    thead tr th:first-child, tbody tr td:first-child {
        display: none !important;
    }
    [data-testid="stTable"] { width: 100%; }
    </style>
    """, unsafe_allow_html=True)

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
    
    return {
        "שם": name,
        "תאריך לועזי": bday_date.strftime('%d/%m/%Y'),
        "תאריך עברי": h_date.hebrew_date_string(),
        "מזל": get_zodiac(bday_date.day, bday_date.month),
        "גיל": today.year - bday_date.year - ((today.month, today.day) < (bday_date.month, bday_date.day)),
        "ימים ליום הולדת": (next_bday - today).days,
        "חודש": bday_date.month,
        "יום": bday_date.day,
        "זמני": is_temporary
    }

if "temp_people" not in st.session_state:
    st.session_state.temp_people = []

all_data = []
spreadsheet_url = ""

# טעינת נתונים בסיסיים
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    df_raw = conn.read(ttl=0).dropna(how="all")
    for _, row in df_raw.iterrows():
        try:
            b_date = pd.to_datetime(row['Birthday'], dayfirst=True).date()
            all_data.append(process_person(row['Full_Name'], b_date))
        except: continue
except: pass

all_data.extend(st.session_state.temp_people)
today = date.today()

# פונקציית צביעה למערך החדש
def apply_yellow(row):
    return ['background-color: #ffffd1' if row.זמני else '' for _ in row]

# --- 1. חגיגות היום ---
# (נשאר אותו דבר)
hbd_today = [p for p in all_data if p["חודש"] == today.month and p["יום"] == today.day]
if hbd_today:
    st.balloons()
    for p in hbd_today:
        st.markdown(f'<div style="background-color: #ffffff; padding: 25px; border-radius: 20px; text-align: center; border: 3px solid #f0f2f6; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px;"><h3>🎈 מזל טוב 🎈</h3><h1>🎁 {p["שם"]} 🎁</h1><h2>חוגג/ת היום {p["גיל"]} שנים! 🎂</h2></div>', unsafe_allow_html=True)

# --- 2. בניית מערך חדש לטבלת החודש ---
st.header(f"📅 חגיגות קרובות לחודש זה")
this_month_list = [p for p in all_data if p["חודש"] == today.month and p["יום"] >= today.day]
if this_month_list:
    df_m_raw = pd.DataFrame(sorted(this_month_list, key=lambda x: x["יום"]))
    
    # בניית המערך החדש עם העמודות שביקשת בלבד + עמודת עזר לצבע
    df_month_final = df_m_raw[["שם", "תאריך לועזי", "גיל", "ימים ליום הולדת", "זמני"]]
    
    # הצגה ללא אינדקס וללא עמודת זמני
    st.table(df_month_final.style.apply(apply_yellow, axis=1)
             .hide(axis="columns", subset=["זמני"]))
else:
    st.info("אין חגיגות נוספות החודש.")

st.markdown("---")

# --- 3. בניית מערך חדש לטבלה הכללית ---
st.header("📊 רשימת כל החוגגים")
if all_data:
    df_all_raw = pd.DataFrame(sorted(all_data, key=lambda x: (x["חודש"], x["יום"])))
    
    # בניית המערך החדש עם העמודות שביקשת בלבד + עמודת עזר לצבע
    df_all_final = df_all_raw[["שם", "תאריך לועזי", "תאריך עברי", "מזל", "גיל", "זמני"]]
    
    # הצגה ללא אינדקס וללא עמודת זמני
    st.table(df_all_final.style.apply(apply_yellow, axis=1)
             .hide(axis="columns", subset=["זמני"]))

st.markdown("---")

# --- 4. הוספה זמנית ורענון ---
col_head, col_refresh = st.columns([0.8, 0.2])
with col_head: st.subheader("⏱️ הוספה זמנית")
with col_refresh:
    if st.button("🔄 רענון"):
        st.cache_data.clear()
        st.rerun()

with st.form("temp_add", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1: t_name = st.text_input("שם:")
    with c2: t_date = st.date_input("תאריך לידה:", value=date(2000, 1, 1), min_value=date(1920, 1, 1), max_value=today)
    if st.form_submit_button("הוסף זמנית"):
        if t_name:
            st.session_state.temp_people.append(process_person(t_name, t_date, is_temporary=True))
            st.rerun()

st.markdown("---")

# --- 5. הוספה קבועה ---
st.subheader("📌 הוספה קבועה")
if spreadsheet_url: st.link_button("🔗 פתח אקסל לעריכה קבועה", spreadsheet_url)
