import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת חכם", layout="wide")
st.markdown('<style>html, body { direction: rtl; text-align: right; }</style>', unsafe_allow_html=True)

# קישור לגליון
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

st.title("🎂 ניהול ימי הולדת חכם")

try:
    df = pd.read_csv(SHEET_URL)
    df.columns = [col.strip() for col in df.columns]
    df['Birthday'] = pd.to_datetime(df['Birthday'], dayfirst=True)
    
    today = date.today()
    full_data = []
    celebrants_today = []

    for _, row in df.iterrows():
        bday_dt = row['Birthday']
        bday = bday_dt.date()
        
        # חישוב גיל
        age = today.year - bday.year
        
        # בדיקה אם היום יום הולדת
        is_today = (bday.day == today.day and bday.month == today.month)
        if is_today:
            celebrants_today.append({"שם": row['Full_Name'], "גיל": age})

        # חישוב ימים שנותרו (רק לחוגגי החודש נציג את זה בטבלה)
        this_year_bday = bday.replace(year=today.year)
        if this_year_bday < today:
            this_year_bday = this_year_bday.replace(year=today.year + 1)
        days_left = (this_year_bday - today).days
        
        # תאריך עברי (מספרים ואותיות)
        h_date = dates.HebrewDate.from_pydate(bday)
        hebrew_numbers = f"{h_date.day}.{h_date.month}.{h_date.year}"
        hebrew_letters = h_date.hebrew_date_string() # מחזיר בפורמט "י"ח בשבט"

        full_data.append({
            "שם": row['Full_Name'],
            "תאריך לועזי": bday.strftime('%d/%m/%Y'),
            "תאריך עברי (מספרים)": hebrew_numbers,
            "תאריך עברי (אותיות)": hebrew_letters,
            "מזל": get_zodiac(bday.day, bday.month),
            "ימים שנותרו": days_left,
            "חודש": bday.month,
            "גיל": age
        })

    report_df = pd.DataFrame(full_data)

    # הצגת חוגגי היום עם בלונים
    if celebrants_today:
        st.balloons()
        for person in celebrants_today:
            st.success(f"🎉 מזל טוב ל**{person['שם']}** שחוגג/ת היום יום הולדת {person['גיל']}! 🎈")

    # טבלת חוגגי החודש - כולל "ימים שנותרו"
    st.subheader(f"📅 חוגגים החודש ({today.strftime('%m')})")
    current_month = report_df[report_df['חודש'] == today.month].sort_values("ימים שנותרו")
    if not current_month.empty:
        st.table(current_month[["שם", "תאריך לועזי", "ימים שנותרו", "גיל"]])
    else:
        st.info("אין ימי הולדת החודש 🎈")

    # טבלה כללית - ללא "ימים שנותרו" (לפי בקשתך)
    st.subheader("📋 רשימה כללית")
    st.dataframe(report_df[["שם", "תאריך לועזי", "תאריך עברי (מספרים)", "תאריך עברי (אותיות)", "מזל", "גיל"]], 
                 use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"שגיאה: {e}")
