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

# פונקציה לעיבוד שורה (חישוב גיל, עברי ומזל)
def process_birthday(name, bday_date):
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

# חיבור וקריאת נתונים
conn = st.connection("gsheets", type=GSheetsConnection)
url = st.secrets["connections"]["gsheets"]["spreadsheet"]

st.title("🎂 לוח ימי הולדת משפחתי")

try:
    df_raw = conn.read(ttl=0).dropna(how="all")
    processed_data = []
    for _, row in df_raw.iterrows():
        try:
            dt = pd.to_datetime(row['Birthday'], dayfirst=True).date()
            processed_data.append(process_birthday(row['Full_Name'], dt))
        except: continue
    
    if processed_data:
        st.subheader("📋 רשימת החוגגים")
        st.dataframe(pd.DataFrame(processed_data), use_container_width=True, hide_index=True)
    else:
        st.info("הרשימה באקסל ריקה.")
except:
    st.error("לא הצלחתי להתחבר לאקסל. וודא שהקישור ב-Secrets תקין.")

st.write("---")

# אזור הוספה (זמני + קבוע)
col1, col2 = st.columns(2)

with col1:
    st.subheader("🔍 בדיקה מהירה (לא נשמר)")
    with st.form("temp_add"):
        t_name = st.text_input("שם החוגג:")
        t_bday = st.date_input("תאריך לידה:", value=date(1990,1,1), min_value=date(1920,1,1))
        if st.form_submit_button("חשב מזל וגיל"):
            res = process_birthday(t_name, t_bday)
            st.success(f"תוצאה: {res['שם']} בן/בת {res['גיל']}, מזל {res['מזל']}, תאריך עברי: {res['תאריך עברי']}")
            st.warning("⚠️ שים לב: המידע הזה לא נשמר באקסל.")

with col2:
    st.subheader("📌 הוספה קבועה")
    st.write("כדי להוסיף חוגג לרשימה הקבועה, יש להוסיף אותו ישירות לקובץ האקסל:")
    st.link_button("🔗 פתח אקסל להוספת חוגג", url)
    st.info("לאחר ההוספה באקסל, רענן את הדף הזה כדי לראות את השינויים.")
