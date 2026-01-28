import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת חכם", layout="wide")

# עיצוב CSS לטקסט במרכז ויישור לימין
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .stButton>button { width: 100%; }
    .birthday-center {
        text-align: center;
        font-size: 60px;
        font-weight: bold;
        color: #FF4B4B;
        padding: 20px;
        border: 5px solid #FF4B4B;
        border-radius: 20px;
        margin-bottom: 30px;
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
                celebrants_today.append(f"{row['Full_Name']} ({age})")

            h_date = dates.HebrewDate.from_pydate(bday)
            
            this_year_bday = bday.replace(year=today.year)
            if this_year_bday < today:
                this_year_bday = this_year_bday.replace(year=today.year + 1)
            days_left = (this_year_bday - today).days

            full_data.append({
                "שם": row['Full_Name'],
                "תאריך לועזי": bday.strftime('%d/%m/%Y'),
                "תאריך עברי (מספרים)": f"{h_date.day}.{h_date.month}.{h_date.year}",
                "תאריך עברי (אותיות)": h_date.hebrew_date_string(),
                "מזל": get_zodiac(bday.day, bday.month),
                "ימים שנותרו": days_left,
                "חודש": bday.month,
                "גיל": age
            })
        except: continue
    return pd.DataFrame(full_data), celebrants_today

st.title("🎂 מערכת ימי הולדת משפחתית")

# טעינת נתונים
if 'df_main' not in st.session_state:
    try:
        st.session_state.df_main = pd.read_csv(SHEET_URL)
    except:
        st.session_state.df_main = pd.DataFrame(columns=['Full_Name', 'Birthday'])

# --- חלק 1: הוספת חוגג חדש ---
with st.expander("➕ הוספת חוגג חדש לרשימה"):
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        new_name = st.text_input("שם מלא:")
    with col2:
        new_date = st.date_input("תאריך לידה לועזי:", min_value=date(1920, 1, 1))
    with col3:
        if st.button("הוסף"):
            new_row = pd.DataFrame({'Full_Name': [new_name], 'Birthday': [new_date.strftime('%d/%m/%Y')]})
            st.session_state.df_main = pd.concat([st.session_state.df_main, new_row], ignore_index=True)
            st.success("החוגג נוסף בהצלחה!")
            st.rerun()

# עיבוד הנתונים
report_df, celebrants = process_data(st.session_state.df_main)

# --- חלק 2: הצגת חוגגי היום במרכז ---
if celebrants:
    st.balloons()
    names_text = " & ".join(celebrants)
    st.markdown(f'<div class="birthday-center">🎉 היום יום הולדת ל: <br> {names_text}! 🎈</div>', unsafe_allow_html=True)

# --- חלק 3: טבלאות ---
today = date.today()
st.subheader(f"📅 חוגגים החודש ({today.month})")
current_month = report_df[report_df['חודש'] == today.month].sort_values("ימים שנותרו")
if not current_month.empty:
    st.table(current_month[["שם", "תאריך לועזי", "ימים שנותרו", "גיל"]])

st.subheader("📋 כל החוגגים")
st.dataframe(report_df[["שם", "תאריך לועזי", "תאריך עברי (מספרים)", "תאריך עברי (אותיות)", "מזל", "גיל"]], 
             use_container_width=True, hide_index=True)
