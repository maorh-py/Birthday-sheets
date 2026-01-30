import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates
from streamlit_gsheets import GSheetsConnection

# הגדרות דף
st.set_page_config(page_title="לוח ימי הולדת", layout="wide")

# פונקציית מזלות
def get_zodiac(d, m):
    zodiacs = [(21,3,19,4,"טלה ♈"),(20,4,20,5,"שור ♉"),(21,5,20,6,"תאומים ♊"),
               (21,6,22,7,"סרטן ♋"),(23,7,22,8,"אריה ♌"),(23,8,22,9,"בתולה ♍"),
               (23,9,22,10,"מאזניים ♎"),(23,10,21,11,"עקרב ♏"),(22,11,21,12,"קשת ♐"),
               (22,12,19,1,"גדי ♑"),(20,1,18,2,"דלי ♒"),(19,2,20,3,"דגים ♓")]
    for sd,sm,ed,em,n in zodiacs:
        if (m==sm and d>=sd) or (m==em and d<=ed): return n
    return "דגים ♓"

# פונקציית עיבוד נתונים
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

# כותרת האפליקציה
st.title("🎂 לוח ימי הולדת משפחתי")

# חיבור (קריאה בלבד)
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
        
        st.subheader("📋 רשימת החוגגים הקבועה")
        st.dataframe(pd.DataFrame(processed_list), use_container_width=True, hide_index=True)
    else:
        st.info("הרשימה באקסל ריקה.")
except Exception as e:
    st.error(f"שגיאת חיבור: {e}")
    st.info("וודא שהגדרת את ה-spreadsheet ב-Secrets ושמות העמודות באקסל הם Full_Name ו-Birthday.")

st.write("---")

# אזור הבדיקה והקישור
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 בדיקה מהירה (סימולטור)")
    with st.form("temp_check"):
        t_name = st.text_input("שם לבדיקה:")
        t_bday = st.date_input("תאריך לידה:", value=date(1990,1,1), min_value=date(1920,1,1))
        if st.form_submit_button("חשב נתונים"):
            if t_name:
                res = process_person(t_name, t_bday)
                st.success(f"תוצאות עבור {res['שם']}: {res['גיל']} שנים, מזל {res['מזל']}, עברי: {res['תאריך עברי']}")
                st.warning("שים לב: המידע לא נשמר בקובץ.")

with col2:
    st.subheader("📌 הוספה קבועה")
    st.write("להוספה קבועה, לחץ על הכפתור והוסף שורה חדשה באקסל:")
    if 'url' in locals():
        st.link_button("🔗 פתח אקסל לעריכה", url)
    st.info("לאחר ההוספה באקסל, רענן את האפליקציה.")
