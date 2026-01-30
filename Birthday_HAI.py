import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="לוח ימי הולדת משפחתי", layout="centered")

# ניסיון ייבוא לספריית גוגל שיטס
try:
    from st_gsheets_connection import GSheetsConnection
except ImportError:
    from streamlit_gsheets import GSheetsConnection

# פונקציית מזלות
def get_zodiac(d, m):
    zodiacs = [(21,3,19,4,"טלה ♈"),(20,4,20,5,"שור ♉"),(21,5,20,6,"תאומים ♊"),
               (21,6,22,7,"סרטן ♋"),(23,7,22,8,"אריה ♌"),(23,8,22,9,"בתולה ♍"),
               (23,9,22,10,"מאזניים ♎"),(23,10,21,11,"עקרב ♏"),(22,11,21,12,"קשת ♐"),
               (22,12,19,1,"גדי ♑"),(20,1,18,2,"דלי ♒"),(19,2,20,3,"דגים ♓")]
    for sd,sm,ed,em,n in zodiacs:
        if (m==sm and d>=sd) or (m==em and d<=ed): return n
    return "דגים ♓"

# פונקציה לעיבוד נתונים
def process_person(name, bday_date, is_temporary=False):
    today = date.today()
    h_date = dates.HebrewDate.from_pydate(bday_date)
    
    # חישוב יום הולדת הבא והפרש ימים
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

# אתחול רשימת זמניים
if "temp_people" not in st.session_state:
    st.session_state.temp_people = []

# קריאת נתונים קבועים
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
except:
    pass

# שילוב זמניים
all_people.extend(st.session_state.temp_people)

# --- בדיקה אם יש יום הולדת היום ---
today = date.today()
hbd_today = [p for p in all_people if p["חודש"] == today.month and p["יום"] == today.day]

if hbd_today:
    for p in hbd_today:
        st.balloons()
        st.markdown(f"""
            <div style="background-color: #ff4b4b; padding: 20px; border-radius: 10px; text-align: center; color: white; margin-bottom: 20px;">
                <h1 style="margin: 0;">🎉 מזל טוב {p['שם']}! 🎉</h1>
                <h2 style="margin: 0;">חוגג/ת היום {p['גיל']} שנים! 🎂</h2>
            </div>
        """, unsafe_allow_name=True)

# כותרת וכפתור רענון
col_t, col_r = st.columns([0.9, 0.1])
with col_t:
    st.title("📅 חגיגות החודש הקרובות")
with col_r:
    if st.button("🔄"):
        st.cache_data.clear()
        st.rerun()

# סינון לטבלה: רק החודש ורק מי שטרם עבר
this_month = [p for p in all_people if p["חודש"] == today.month and p["יום"] >= today.day]
this_month = sorted(this_month, key=lambda x: x["יום"])

if this_month:
    df = pd.DataFrame(this_month)
    def style_temp(row):
        return ['background-color: #ffffcc' if row.זמני else '' for _ in row]
    
    display_cols = ["שם", "תאריך לידה", "גיל", "מזל", "תאריך עברי", "ימים ליומולדת"]
    st.table(df[display_cols + ["זמני"]].style.apply(style_temp, axis=1))
else:
    st.info("אין חגיגות נוספות המתוכננות לחודש זה.")

st.markdown("---")

# הוספה זמנית
st.subheader("⏱️ הוספה זמנית")
with st.form("temp_form", clear_on_submit=True):
    c1, c2 = st.columns(2)
    with c1: t_name = st.text_input("שם:")
    with c2: t_date = st.date_input("תאריך לידה:", value=date(2000,1,1))
    if st.form_submit_button("הוסף זמנית לטבלה"):
        if t_name:
            new_p = process_person(t_name, t_date, is_temporary=True)
            st.session_state.temp_people.append(new_p)
            st.rerun()

st.markdown("---")

# הוספה קבועה
st.subheader("📌 הוספה קבועה")
if url:
    st.link_button("🔗 פתח אקסל להוספה קבועה", url)
else:
    st.warning("קישור לאקסל חסר ב-Secrets")
