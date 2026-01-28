import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת", layout="wide")

# חיבור (משתמש בקישור מה-Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# קריאת נתונים - ttl=0 מבטיח רענון בכל טעינה
df_raw = conn.read(ttl=0).dropna(how="all")

st.title("🎂 ניהול ימי הולדת")

# הצגת הטבלה הקיימת
if not df_raw.empty:
    st.dataframe(df_raw, use_container_width=True, hide_index=True)
else:
    st.info("הרשימה ריקה כרגע.")

st.write("---")

# טופס הוספה
with st.expander("➕ הוספה חדשה"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם מלא:")
        # כאן התיקון של השנים שעבד לך
        bday = st.date_input(
            "תאריך לידה:", 
            value=date(1990, 1, 1),
            min_value=date(1920, 1, 1),
            max_value=date.today()
        )
        
        if st.form_submit_button("שמור"):
            if name:
                # יצירת שורה חדשה
                new_row = pd.DataFrame([{"Full_Name": name, "Birthday": bday.strftime("%d/%m/%Y")}])
                updated_df = pd.concat([df_raw, new_row], ignore_index=True)
                
                # ניסיון עדכון מפורש
                try:
                    # שימי לב: הוספנו כאן worksheet="Sheet1"
                    conn.update(data=updated_df, worksheet="Sheet1")
                    st.cache_data.clear()
                    st.success(f"החוגג {name} נוסף בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error("שגיאת הרשאה: גוגל עדיין חוסם את הכתיבה.")
                    st.info("פתרון סופי: ב-Secrets ב-Streamlit, וודא שהקישור מסתיים ב-edit ולא ב-export.")
