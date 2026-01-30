import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="לוח ימי הולדת משפחתי", layout="centered")# הגדרת דפדפן ומרכוז התוכן   

# CSS לניקוי הטבלה (העלמת אינדקס)
st.markdown("""
    <style>
    table th:first-child, table td:first-child { display: none !important; }
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
    
    # כאן שיניתי את המפתח למה שחיפשת בשורה 101
    return {
        "שם": name,
        "תאריך לועזי": bday_date.strftime('%d/%m/%Y'),
        "תאריך עברי": h_date.hebrew_date_string(),
        "מזל": get_zodiac(bday_date.day, bday_date.month),
        "גיל": today.year - bday_date.year - ((today.month, today.day) < (bday_date.month, bday_date.day)),
        "עוד כמה ימים ליום הולדת": (next_bday - today).days, 
        "חודש": bday_date.month,
        "יום": bday_date.day,
        "זמני": is_temporary
    }

if "temp_people" not in st.session_state:
    st.session_state.temp_people = []

all_data = []
spreadsheet_url = ""

# טעינת נתונים
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

# --- 1. חגיגות היום (מופיע לפני הכל) ---
hbd_today = [p for p in all_data if p["חודש"] == today.month and p["יום"] == today.day]
if hbd_today:
    st.balloons()
    for p in hbd_today:
        st.markdown(f"""
            <div style="background-color: #ffffff; padding: 25px; border-radius: 20px; text-align: center; 
                        border: 3px solid #f0f2f6; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 30px;">
                <h3 style="color: #ff4b4b; margin: 0; font-size: 24px;">🎈 מזל טוב 🎈</h3>
                <h1 style="color: #1f1f1f; margin: 10px 0; font-size: 45px;">🎁 {p['שם']} 🎁</h1>
                <h2 style="color: #ff4b4b; margin: 0;">חוגג/ת היום {p['גיל']} שנים! 🎂</h2>
            </div>
        """, unsafe_allow_html=True)

# פונקציית צביעה
def color_rows(df, original_list):
    colors = pd.DataFrame('', index=df.index, columns=df.columns)
    for i in range(len(df)):
        if i < len(original_list) and original_list[i]['זמני']:
            colors.iloc[i] = 'background-color: #ffffd1'
    return colors

# --- 2. טבלת החודש ---
st.header(f"📅 חגיגות קרובות לחודש זה")
this_month_list = sorted([p for p in all_data if p["חודש"] == today.month and p["יום"] >= today.day], key=lambda x: x["יום"])

if this_month_list:
    df_month = pd.DataFrame(this_month_list)[["שם", "תאריך לועזי", "גיל", "עוד כמה ימים ליום הולדת"]]
    st.table(df_month.style.apply(lambda x: color_rows(df_month, this_month_list), axis=None))
else:
    st.info("אין חגיגות נוספות החודש.")

st.markdown("---")

# --- 3. רשימת כל החוגגים ---
st.header("📊 רשימת כל החוגגים")
if all_data:
    all_sorted = sorted(all_data, key=lambda x: (x["חודש"], x["יום"]))
    df_all = pd.DataFrame(all_sorted)[["שם", "תאריך לועזי", "תאריך עברי", "מזל", "גיל"]]
    st.table(df_all.style.apply(lambda x: color_rows(df_all, all_sorted), axis=None))

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

