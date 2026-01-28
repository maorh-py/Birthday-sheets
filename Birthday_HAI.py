import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
from pyluach import dates

st.set_page_config(page_title="ניהול ימי הולדת", layout="wide")

# חיבור
conn = st.connection("gsheets", type=GSheetsConnection)

# קריאה מלשונית Data
try:
    df_raw = conn.read(worksheet="Data", ttl=0).dropna(how="all")
except:
    df_raw = pd.DataFrame(columns=["Full_Name", "Birthday"])

st.title("🎂 ניהול ימי הולדת")

# הצגת נתונים קיימים
if not df_raw.empty:
    st.dataframe(df_raw, use_container_width=True, hide_index=True)
else:
    st.info("הרשימה ריקה כרגע. הוסיפו חוגג למטה.")

st.write("---")

# טופס הוספה
with st.expander("➕ הוספת חוגג חדש"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם מלא:")
        # כאן התיקון של השנים שכבר עבד לך
        bday = st.date_input(
            "תאריך לידה:", 
            value=date(1990, 1, 1),
            min_value=date(1920, 1, 1),
            max_value=date.today()
        )
        
        if st.form_submit_button("שמור וסנכרן"):
            if name:
                new_row = pd.DataFrame([{"Full_Name": name, "Birthday": bday.strftime("%d/%m/%Y")}])
                updated_df = pd.concat([df_raw, new_row], ignore_index=True)
                
                try:
                    # כתיבה מפורשת ללשונית Data
                    conn.update(worksheet="Data", data=updated_df)
                    st.cache_data.clear()
                    st.success(f"החוגג {name} נוסף בהצלחה!")
                    st.rerun()
                except Exception as e:
                    st.error("גוגל עדיין חוסם את הכתיבה.")
                    st.info("וודא שנתת הרשאת Editor למייל של streamlit (הסמל ה-S האדום בתמונה שלך).")
