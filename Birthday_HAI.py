import streamlit as st
import pandas as pd
from datetime import date
import requests

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת", layout="wide")
st.title("🎂 ניהול ימי הולדת")

# 1. קריאת הנתונים (נשאר אותו דבר)
# וודא שהקישור ב-Secrets נשאר כמו שהיה
from streamlit_gsheets import GSheetsConnection
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).dropna(how="all")

# תצוגת הטבלה
if not df.empty:
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("הרשימה ריקה.")

st.write("---")

# 2. הוספת חוגג חדש - בשיטה שעוקפת את החסימה
with st.expander("➕ הוספת חוגג"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם מלא:")
        bday = st.date_input("תאריך לידה:", value=date(1990,1,1), min_value=date(1920,1,1))
        
        if st.form_submit_button("שמור"):
            if name:
                # הוספת השורה לטבלה המקומית
                new_row = pd.DataFrame([{"Full_Name": name, "Birthday": bday.strftime("%d/%m/%Y")}])
                updated_df = pd.concat([df, new_row], ignore_index=True)
                
                # כאן אנחנו משתמשים בטריק: שליחה מפורשת
                try:
                    conn.update(data=updated_df)
                    st.success(f"החוגג {name} נוסף! רענן את הדף כדי לראות.")
                    st.balloons()
                except Exception as e:
                    st.error("גוגל עדיין דורש מפתח JSON לכתיבה ישירה.")
                    st.info("מכיוון שאין לך אפשרות ליצור מפתח, הפתרון הוא להוסיף את השמות ידנית לאקסל, והם יופיעו כאן מיד.")
