import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת חכם", layout="wide")

# עיצוב
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .birthday-center {
        text-align: center; font-size: 50px; font-weight: bold; color: #FF4B4B;
        padding: 30px; border: 10px double #FF4B4B; border-radius: 30px;
        margin: 20px auto; width: 80%; background-color: #FFF5F5;
    }
    </style>
    """, unsafe_allow_html=True)

# חיבור
conn = st.connection("gsheets", type=GSheetsConnection)

def get_zodiac(d, m):
    if (m == 3 and d >= 21) or (m == 4 and d <= 19): return "טלה ♈"
    if (m == 4 and d >= 20) or (m == 5 and d <= 20): return "שור ♉"
    if (m == 5 and d >= 21) or (m == 6 and d <= 20): return "תאומים ♊"
    if (m == 6 and d >= 21) or (m == 7 and d <= 22): return "סרטן ♋"
    if (m == 7 and d >= 23) or (m == 8 and d <= 22): return "אריה ♌"
    if (m == 8 and d >= 23) or (m == 9 and d <= 22): return "בתולה ♍"
    if (m == 9 and d >= 23) or (m == 10 and d <= 22): return "מאזניים ♎"
    if (m == 10 and d >= 23) or (m == 11 and d <= 21): return "עקרב ♏"
    if (m == 11 and d >= 22) or (m == 12 and d <= 21): return "קשת ♐"
    if (m == 12 and d >= 22) or (m == 1 and d <= 19): return "גדי ♑"
    if (m == 1 and d >= 20) or (m == 2 and d <= 18): return "דלי ♒"
    return "דגים ♓"

# קריאה
df_raw = conn.read(ttl=0).dropna(how="all")

today = date.today()
processed = []
celebrants_today = []

if not df_raw.empty:
    for _, row in df_raw.iterrows():
        try:
            b_dt = pd.to_datetime(row['Birthday'], dayfirst=True)
            b_date = b_dt.date()
            age = today.year - b_date.year
            if b_date.day == today.day and b_date.month == today.month:
                celebrants_today.append(f"{row['Full_Name']} (גיל {age})")
            
            h_date = dates.HebrewDate.from_pydate(b_date)
            this_year = b_date.replace(year=today.year)
            if this_year < today: this_year = this_year.replace(year=today.year + 1)
            
            processed.append({
                "שם": row['Full_Name'],
                "תאריך לועזי": b_date.strftime('%d/%m/%Y'),
                "תאריך עברי": h_date.hebrew_date_string(),
                "מזל": get_zodiac(b_date.day, b_date.month),
                "ימים שנותרו": (this_year - today).days,
                "גיל": age,
                "חודש": b_date.month,
                "יום": b_date.day
            })
        except: continue

report_df = pd.DataFrame(processed)

# תצוגה
st.title("🎂 ניהול ימי הולדת משפחתי")

if celebrants_today:
    st.balloons()
    st.markdown(f'<div class="birthday-center">🎉 מזל טוב! 🎉<br>{"<br>".join(celebrants_today)}</div>', unsafe_allow_html=True)

if not report_df.empty:
    st.subheader("📅 נותרו לחגוג החודש")
    current = report_df[(report_df['חודש'] == today.month) & (report_df['יום'] >= today.day)].sort_values("יום")
    st.dataframe(current[["שם", "תאריך לועזי", "תאריך עברי", "ימים שנותרו", "גיל"]], use_container_width=True, hide_index=True)

    st.subheader("📋 רשימה מלאה")
    st.dataframe(report_df[["שם", "תאריך לועזי", "תאריך עברי", "מזל", "גיל"]], use_container_width=True, hide_index=True)

st.write("---")
# הוספה - כאן התיקון של השנים
with st.expander("➕ הוספת חוגג וסנכרון לאקסל"):
    with st.form("add_form", clear_on_submit=True):
        name = st.text_input("שם מלא:")
      
        new_bday = st.date_input(
            "תאריך לידה:", 
            value=date(1990, 1, 1), 
            min_value=date(1920, 1, 1), 
            max_value=date.today()
        )
        if st.form_submit_button("שמור ועדכן גליון"):
            if name:
                new_row = pd.DataFrame([{"Full_Name": name, "Birthday": new_bday.strftime("%d/%m/%Y")}])
                updated_df = pd.concat([df_raw, new_row], ignore_index=True)
                conn.update(data=updated_df)
                st.cache_data.clear()
                st.success(f"החוגג {name} נוסף בהצלחה!")
                st.rerun()
