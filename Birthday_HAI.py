import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.set_page_config(page_title="ניהול ימי הולדת", layout="wide")
st.title("🎂 ניהול ימי הולדת")

# חיבור לגליון - משתמש רק בקישור מה-Secrets
conn = st.connection("gsheets", type=GSheetsConnection)

# קריאת נתונים
try:
    df = conn.read(ttl=0).dropna(how="all")
except Exception:
    df = pd.DataFrame(columns=["Full_Name", "Birthday"])

# הצגת הטבלה
st.dataframe(df, use_container_width=True, hide_index=True)

st.write("---")

# טופס הוספה
with st.form("add_birthday"):
    name = st.text_input("שם מלא:")
    # כאן התיקון של השנים
    bday = st.date_input("תאריך לידה:", 
                        value=date(1990, 1, 1), 
                        min_value=date(1920, 1, 1), 
                        max_value=date.today())
    
    submit = st.form_submit_button("שמור")
    
    if submit and name:
        new_data = pd.DataFrame([{"Full_Name": name, "Birthday": bday.strftime("%d/%m/%Y")}])
        updated_df = pd.concat([df, new_data], ignore_index=True)
        
        try:
            # ניסיון עדכון
            conn.update(data=updated_df)
            st.success(f"החוגג {name} נוסף! רענן את הדף.")
            st.balloons()
        except Exception as e:
            st.error("גוגל חוסם כתיבה אוטומטית ללא קובץ JSON.")
            st.info("מכיוון שהארגון שלך חוסם יצירת מפתח, פשוט הוסף את השם ידנית באקסל והוא יופיע כאן מיד.")
