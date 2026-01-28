import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת חכם", layout="wide")

# חיבור לגליון
conn = st.connection("gsheets", type=GSheetsConnection)

# קריאת נתונים - ttl=0 מבטיח רענון
df_raw = conn.read(worksheet="Data", ttl=0).dropna(how="all")

# פונקציית מזלות
def get_zodiac(d, m):
    zodiacs = [(21,3,19,4,"טלה"),(20,4,20,5,"שור"),(21,5,20,6,"תאומים"),(21,6,22,7,"סרטן"),
               (23,7,22,8,"אריה"),(23,8,22,9,"בתולה"),(23,9,22,10,"מאזניים"),(23,10,21,11,"עקרב"),
               (22,11,21,12,"קשת"),(22,12,19,1,"גדי"),(20,1,18,2,"דלי"),(19,2,20,3,"דגים")]
    for sd,sm,ed,em,n in zodiacs:
        if (m==sm and d>=sd) or (m==em and d<=ed): return n
    return "דגים"

# עיבוד נתונים לתצוגה
today = date.today()
processed = []
if not df_raw.empty:
    for _, row in df_raw.iterrows():
        try:
            b_dt = pd.to_datetime(row['Birthday'], dayfirst=True).date()
            h_date = dates.HebrewDate.from_pydate(b_dt)
            age = today.year - b_dt.year
            processed.append({
                "שם": row['Full_Name'], "תאריך": b_dt.strftime('%d/%m/%Y'),
                "עברי": h_date.hebrew_date_string(), "מזל": get_zodiac(b_dt.day, b_dt.month), "גיל": age
            })
        except: continue

# תצוגה
st.title("🎂 ניהול ימי הולדת")
if processed:
    st.dataframe(pd.DataFrame(processed), use_container_width=True, hide_index=True)
else:
    st.info("הרשימה ריקה כרגע.")

st.write("---")

# טופס הוספה עם תיקון השנים
with st.expander("➕ הוספת חוגג חדש"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם מלא:")
        # כאן התיקון הקריטי לבחירת השנים:
        bday = st.date_input(
            "תאריך לידה:", 
            value=date(1990, 1, 1),    # תאריך התחלתי
            min_value=date(1920, 1, 1), # מאפשר לבחור מ-1920
            max_value=today             # עד היום
        )
        
        if st.form_submit_button("שמור וסנכרן"):
            if name:
                new_row = pd.DataFrame([{"Full_Name": name, "Birthday": bday.strftime("%d/%m/%Y")}])
                updated_df = pd.concat([df_raw, new_row], ignore_index=True)
                
               try:
                    conn.update(worksheet="Data", data=updated_df)
                    st.cache_data.clear()
                    st.success("נשמר בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error("גוגל עדיין חוסם את הכתיבה.")
