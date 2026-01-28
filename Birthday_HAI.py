import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת חכם", layout="wide")

# עיצוב CSS למרכז, יישור לימין והודעת יום הולדת
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .birthday-center {
        text-align: center;
        font-size: 50px;
        font-weight: bold;
        color: #FF4B4B;
        padding: 30px;
        border: 10px double #FF4B4B;
        border-radius: 30px;
        margin: 40px auto;
        width: 80%;
        background-color: #FFF5F5;
    }
    div[data-testid="stExpander"] {
        background-color: #f0f2f6;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1dIJIgpiND9yj4mWPZNxDwZaQyxDqAATH6Lp_TLFXmwI/export?format=csv"

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

def process_data(df):
    today = date.today()
    full_data = []
    celebrants_today = []
    
    for _, row in df.iterrows():
        try:
            bday_dt = pd.to_datetime(row['Birthday'], dayfirst=True)
            bday = bday_dt.date()
            age = today.year - bday.year
            
            if bday.day == today.day and bday.month == today.month:
                celebrants_today.append(f"{row['Full_Name']} (חוגג/ת {age})")

            h_date = dates.HebrewDate.from_pydate(bday)
            
            this_year_bday = bday.replace(year=today.year)
            if this_year_bday < today:
                this_year_bday = this_year_bday.replace(year=today.year + 1)
            days_left = (this_year_bday - today).days

            full_data.append({
                "שם": row['Full_Name'],
                "תאריך לועזי": bday.strftime('%d/%m/%Y'),
                "יום": bday.day,
                "חודש": bday.month,
                "תאריך עברי": h_date.hebrew_date_string(),
                "מזל": get_zodiac(bday.day, bday.month),
                "ימים שנותרו": days_left,
                "גיל": age
            })
        except: continue
    return pd.DataFrame(full_data), celebrants_today

# טעינת נתונים
if 'df_main' not in st.session_state:
    try:
        st.session_state.df_main = pd.read_csv(SHEET_URL)
    except:
        st.session_state.df_main = pd.DataFrame(columns=['Full_Name', 'Birthday'])

# עיבוד
report_df, celebrants = process_data(st.session_state.df_main)
today = date.today()

# --- תצוגה ---
st.title("🎂 מערכת ימי הולדת משפחתית")

# 1. חוגגי היום (במרכז)
if celebrants:
    st.balloons()
    names_text = "<br>".join(celebrants)
    st.markdown(f'<div class="birthday-center">🎉 מזל טוב! 🎉<br>{names_text}</div>', unsafe_allow_html=True)

# 2. טבלת החודש (רק מי שטרם חגג)
st.subheader(f"📅 נותרו לחגוג החודש (חודש {today.month})")
current_month_future = report_df[
    (report_df['חודש'] == today.month) & 
    (report_df['יום'] >= today.day)
].sort_values("יום")

if not current_month_future.empty:
    st.table(current_month_future[["שם", "תאריך לועזי", "תאריך עברי", "ימים שנותרו", "גיל"]])
else:
    st.info("אין יותר ימי הולדת החודש. נתראה בחודש הבא! 🎈")

# 3. רשימה כללית
st.subheader("📋 רשימת החוגגים המלאה")
st.dataframe(report_df[["שם", "תאריך לועזי", "תאריך עברי", "מזל", "גיל"]], 
             use_container_width=True, hide_index=True)

st.write("---") # קו מפריד

# 4. הוספת חוגג (בתחתית הדף)
with st.expander("➕ הוספת חוגג חדש לרשימה"):
    c1, c2, c3 = st.columns([2, 2, 1])
    with c1: new_name = st.text_input("שם מלא:")
    with c2: new_date = st.date_input("תאריך לידה:", min_value=date(1940, 1, 1), value=date(1990, 1, 1))
    with c3:
        if st.button("הוסף"):
            new_row = pd.DataFrame({'Full_Name': [new_name], 'Birthday': [new_date.strftime('%d/%m/%Y')]})
            st.session_state.df_main = pd.concat([st.session_state.df_main, new_row], ignore_index=True)
            st.success("החוגג נוסף!")
            st.rerun()
