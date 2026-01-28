import streamlit as st
import pandas as pd
from datetime import date
import requests
from streamlit_gsheets import GSheetsConnection

st.title("🎂 ניהול ימי הולדת (עוקף חסימות)")

# קריאה (תמיד עובדת)
conn = st.connection("gsheets", type=GSheetsConnection)
df = conn.read(ttl=0).dropna(how="all")
st.dataframe(df, use_container_width=True, hide_index=True)

st.write("---")

with st.form("add_form", clear_on_submit=True):
    name = st.text_input("שם מלא:")
    bday = st.date_input("תאריך לידה:", value=date(1990,1,1), min_value=date(1920,1,1))
    
    if st.form_submit_button("שמור"):
        if name and "script_url" in st.secrets:
            # שליחה ישירה ל-Apps Script
            payload = {"name": name, "birthday": bday.strftime("%d/%m/%Y")}
            response = requests.post(st.secrets["script_url"], json=payload)
            
            if response.status_code == 200:
                st.success(f"החוגג {name} נוסף בהצלחה!")
                st.balloons()
                st.rerun()
            else:
                st.error("תקלה בשליחה לשרת.")
        else:
            st.warning("אנא מלא שם וודא שהגדרת script_url ב-Secrets.")
