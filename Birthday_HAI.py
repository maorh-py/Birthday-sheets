import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date

st.title("🎂 ניהול ימי הולדת")

# חיבור
conn = st.connection("gsheets", type=GSheetsConnection)

# קריאה
df = conn.read(ttl=0).dropna(how="all")
st.dataframe(df, use_container_width=True, hide_index=True)

st.write("---")

with st.form("add_form"):
    name = st.text_input("שם מלא:")
    # תיקון השנים כאן
    bday = st.date_input("תאריך לידה:", value=date(1990,1,1), min_value=date(1920,1,1))
    
    if st.form_submit_button("שמור"):
        if name:
            new_row = pd.DataFrame([{"Full_Name": name, "Birthday": bday.strftime("%d/%m/%Y")}])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # ניסיון עדכון
            try:
                conn.update(data=updated_df)
                st.success("נשמר בהצלחה!")
                st.rerun()
            except Exception as e:
                st.error("גוגל עדיין חוסם. וודא שהגדרת Anyone with the link כ-Editor בשיטס.")
