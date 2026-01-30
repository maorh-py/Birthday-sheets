import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# מנגנון ייבוא גמיש למניעת שגיאות שרת
try:
    from streamlit_gsheets import GSheetsConnection
except ImportError:
    try:
        from st_gsheets_connection import GSheetsConnection
    except ImportError:
        st.error("שגיאה: חסרה ספריית החיבור. וודא ש-st-gsheets-connection מופיע ב-requirements.txt")

# הגדרות דף
st.set_page_config(page_title="לוח ימי הולדת משפחתי", layout="centered")

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
def process_person(name, bday_date):
    today = date.today()
    h_date = dates.HebrewDate.from_pydate(bday_date)
    age = today.year - bday_date.year - ((today.month, today.day) < (bday_date.month, bday_date.day))
    return {
        "שם": name,
        "תאריך לידה": bday_date.strftime('%d/%m/%Y'),
        "תאריך עברי": h_date.hebrew_date_string(),
        "מזל": get_zodiac(bday_date.day, bday_date.month),
        "גיל": age
    }

st.title("🎂 לוח ימי הולדת משפחתי")

# --- חלק 1: תצוגת הרשימה הקבועה ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    df_raw = conn.read(ttl=0).dropna(how="all")
    
    if not df_raw.empty:
        processed_list = []
        for _, row in df_raw.iterrows():
            try:
                b_date = pd.to_datetime(row['Birthday'], dayfirst=True).date()
                processed_list.append(process_person(row['Full_Name'], b_date))
            except: continue
        
        if processed_list:
            st.subheader("📋 רשימת החוגגים")
            st.dataframe(pd.DataFrame(processed_list), use_container_width=True, hide_index=True)
except Exception:
    st.info("מתחבר לנתונים...")

st.markdown("---")

# --- חלק 2: הוספה זמנית (עבר לכאן) ---
st.subheader("⏱️ הוספה זמנית")
st.info("כאן אפשר לבדוק מזל וגיל בלי לשמור את הנתונים.")
with st.form("temp_add", clear_on_submit=True):
    t_name = st.text_input("שם החוגג:")
    t_bday = st.date_input("תאריך לידה:", value=date(2000, 1, 1), min_value=date(1920, 1, 1))
    submit = st.form_submit_button("בדוק נתונים")
    
    if submit:
        if t_name:
            res = process_person(t_name, t_bday)
            st.success(f"**תוצאה זמנית עבור {res['שם']}:**")
            st.write(f"גיל: {res['גיל']} | מזל: {res['מזל']} | תאריך עברי: {res['תאריך עברי']}")
            st.balloons()
            st.warning("שים לב: המידע הזה לא נשמר באקסל.")
        else:
            st.error("נא להזין שם.")

st.markdown("---")

# --- חלק 3: הוספה קבועה (עבר לסוף) ---
st.subheader("📌 הוספה קבועה")
st.write("להוספת חוגג שיופיע כאן תמיד, יש להוסיף אותו ישירות לקובץ האקסל:")
if 'url' in locals():
    st.link_button("🔗 פתח אקסל להוספה קבועה", url)
st.caption("לאחר השמירה באקסל, רענן את האפליקציה כדי לראות את השינוי.")
