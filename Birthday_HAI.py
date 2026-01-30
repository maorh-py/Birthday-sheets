import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="לוח ימי הולדת משפחתי", layout="centered")

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
        "תאריך לועזי": bday_date.strftime('%d/%m/%Y'),
        "תאריך עברי": h_date.hebrew_date_string(),
        "מזל": get_zodiac(bday_date.day, bday_date.month),
        "גיל": age,
        "ימים ליום הולדת": days_left,
        "חודש": bday_date.month,
        "יום": bday_date.day,
        "זמני": is_temporary
    }

if "temp_people" not in st.session_state:
    st.session_state.temp_people = []

all_people = []
spreadsheet_url = ""

# טעינת נתונים
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    df_raw = conn.read(ttl=0).dropna(how="all")
    for _, row in df_raw.iterrows():
        try:
            b_date = pd.to_datetime(row['Birthday'], dayfirst=True).date()
            all_people.append(process_person(row['Full_Name'], b_date))
        except: continue
except: pass

all_people.extend(st.session_state.temp_people)
today = date.today()

# --- CSS להעלמת עמודת האינדקס בטבלאות ---
st.markdown("""
    <style>
    thead tr th:first-child { display:none !important; }
    tbody tr td:first-child { display:none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 1. חגיגות היום ---
hbd_today = [p for p in all_people if p["חודש"] == today.month and p["יום"] == today.day]
if hbd_today:
    st.balloons()
    for p in hbd_today:
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 20px; text-align: center; 
                        border: 3px solid #f0f2f6; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px;">
                <h3 style="color: #ff4b4b; margin: 0; font-size: 24px;">🎈 מזל טוב 🎈</h3>
                <h1 style="color: #1f1f1f; margin: 10px 0; font-size: 45px;">
                    🎁 {p['שם']} 🎁
                </h1>
                <h2 style="color: #ff4b4b; margin: 0;">חוגג/ת היום {p['גיל']} שנים! 🎂</h2>
            </div>
        """, unsafe_allow_html=True)

# פונקציית צביעה
def color_yellow(row):
    return ['background-color: #ffffd1' if row.זמני else '' for _ in row]

# --- 2. טבלת החודש ---
st.header(f"📅 חגיגות קרובות לחודש זה")
this_month = [p for p in all_people if p["חודש"] == today.month and p["יום"] >= today.day]
if this_month:
    df_m = pd.DataFrame(sorted(this_month, key=lambda x: x["יום"]))
    
    # הצגת העמודות המבוקשות בלבד
    cols_m = ["שם", "תאריך לועזי", "גיל", "ימים ליום הולדת"]
    # אנחנו צובעים לפני שמורידים את עמודת ה'זמני' כדי שהמערכת תדע את מי לצבוע
    styled_m = df_m.style.apply(color_yellow, axis=1)
    
    # כאן הסוד: אנחנו מציגים רק את העמודות שרצינו מה-Styler
    st.write(styled_m.hide(axis="index").hide(subset=["זמני", "תאריך עברי", "מזל", "חודש", "יום"], axis="columns"))
else:
    st.info("אין חגיגות נוספות החודש.")

st.markdown("---")

# --- 3. רשימת כל החוגגים ---
st.header("📊 רשימת כל החוגגים")
if all_people:
    df_all = pd.DataFrame(sorted(all_people, key=lambda x: (x["חודש"], x["יום"])))
    
    # הצגת העמודות המבוקשות בלבד
    styled_all = df_all.style.apply(color_yellow, axis=1)
    
    st.write(styled_all.hide(axis="index").hide(subset=["זמני", "ימים ליום הולדת", "חודש", "יום"], axis="columns"))

st.markdown("---")

# --- 4. הוספה זמנית ורענון ---
col_head, col_refresh = st.columns([0.8, 0.2])
with col_head:
    st.subheader("⏱️ הוספה זמנית")
with col_refresh:
    if st.button("🔄 רענון"):
        st.cache_data.clear()
        st.rerun()

with st.form("temp_add", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1: t_name = st.text_input("שם:")
    with c2: t_date = st.date_input("תאריך לידה:", 
                                   value=date(2000, 1, 1),
                                   min_value=date(1920, 1, 1),
                                   max_value=today)
    if st.form_submit_button("הוסף זמנית"):
        if t_name:
            st.session_state.temp_people.append(process_person(t_name, t_date, is_temporary=True))
            st.rerun()

st.markdown("---")

# --- 5. הוספה קבועה ---
st.subheader("📌 הוספה קבועה")
if spreadsheet_url:
    st.link_button("🔗 פתח אקסל לעריכה קבועה", spreadsheet_url)
