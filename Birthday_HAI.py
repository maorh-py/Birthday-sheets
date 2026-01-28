import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
from pyluach import dates

st.set_page_config(page_title="ניהול ימי הולדת חכם", layout="wide")

# חיבור
conn = st.connection("gsheets", type=GSheetsConnection)

# קריאה
df_raw = conn.read(ttl=0).dropna(how="all")

# תצוגה
st.title("🎂 ניהול ימי הולדת")

if not df_raw.empty:
    st.dataframe(df_raw, use_container_width=True, hide_index=True)
else:
    st.info("הרשימה ריקה.")

# הוספה
st.write("---")
with st.expander("➕ הוספה חדשה"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם:")
        # כאן התיקון לשנים:
        new_bday = st.date_input(
            "תאריך לידה:", 
            value=date(1990, 1, 1),
            min_value=date(1920, 1, 1),
            max_value=date.today()
        )
        if st.form_submit_button("שמור"):
            if name:
                new_row = pd.DataFrame([{"Full_Name": name, "Birthday": new_bday.strftime("%d/%m/%Y")}])
                updated_df = pd.concat([df_raw, new_row], ignore_index=True)
                
                # המעקף לשגיאת ה-Unsupported: אנחנו שולחים את כל הטבלה מחדש
                try:
                    conn.update(data=updated_df)
                    st.cache_data.clear()
                    st.success("נשמר בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error("גוגל חוסם את השמירה. פתרון: וודא ששם הלשונית באקסל הוא Sheet1")
