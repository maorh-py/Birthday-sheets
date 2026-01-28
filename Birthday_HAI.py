import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת", layout="wide")

# חיבור
conn = st.connection("gsheets", type=GSheetsConnection)

# קריאת נתונים
df_raw = conn.read(ttl=0).dropna(how="all")

st.title("🎂 ניהול ימי הולדת")

# תצוגה
if not df_raw.empty:
    st.dataframe(df_raw, use_container_width=True, hide_index=True)

st.write("---")

# טופס הוספה
with st.expander("➕ הוספה חדשה"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם:")
        # התיקון של השנים
        bday = st.date_input("תאריך:", value=date(1990, 1, 1), 
                            min_value=date(1920, 1, 1), max_value=date.today())
        
        if st.form_submit_button("שמור"):
            if name:
                new_row = pd.DataFrame([{"Full_Name": name, "Birthday": bday.strftime("%d/%m/%Y")}])
                updated_df = pd.concat([df_raw, new_row], ignore_index=True)
                
                try:
                    # ניסיון עדכון - הוספנו כאן worksheet="Sheet1" באופן מפורש
                    conn.update(data=updated_df, worksheet="Sheet1")
                    st.cache_data.clear()
                    st.success("נשמר בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error("שגיאת הרשאה: גוגל עדיין לא מאשר כתיבה.")
                    st.info("כדי לפתור זאת: וודא שהגדרת 'עריכה' (Editor) ב-Share של הגליון עבור המייל של streamlit.")
