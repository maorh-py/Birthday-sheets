import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת חכם", layout="wide")
st.markdown('<style>html, body { direction: rtl; text-align: right; }</style>', unsafe_allow_html=True)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1dIJIgpiND9yj4mWPZNxDwZaQyxDqAATH6Lp_TLFXmwI/edit?usp=sharing"

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

def get_hebrew_date(d_obj):
    try:
        h = dates.HebrewDate.from_pydate(d_obj)
        # פורמט בסיסי: יום, חודש (מספר)
        return f"{h.day} ב{h.month_name('he')}"
    except: return "לא חושב"

st.title("🎂 ניהול ימי הולדת חכם")

try:
    df = pd.read_csv(SHEET_URL)
    df.columns = [col.strip() for col in df.columns]
    df['Birthday'] = pd.to_datetime(df['Birthday'])
    
    today = date.today()
    full_data = []

    for _, row in df.iterrows():
        bday = row['Birthday'].date()
        
        # חישוב ימים שנותרו
        this_year_bday = bday.replace(year=today.year)
        if this_year_bday < today:
            this_year_bday = this_year_bday.replace(year=today.year + 1)
        days_left = (this_year_bday - today).days
        
        full_data.append({
            "שם": row['Full_Name'],
            "תאריך לועזי": bday.strftime('%d/%m/%Y'),
            "תאריך עברי": get_hebrew_date(bday),
            "מזל": get_zodiac(bday.day, bday.month),
            "ימים שנותרו": days_left,
            "חודש": bday.month
        })

    report_df = pd.DataFrame(full_data)

    # טבלת חוגגי החודש
    st.subheader(f"📅 חוגגים החודש ({today.strftime('%m')})")
    current_month = report_df[report_df['חודש'] == today.month]
    if not current_month.empty:
        st.table(current_month[["שם", "תאריך לועזי", "ימים שנותרו"]])
    else:
        st.info("אין ימי הולדת החודש 🎈")

    # טבלה כללית
    st.subheader("📋 רשימה כללית")
    st.dataframe(report_df[["שם", "תאריך לועזי", "תאריך עברי", "מזל", "ימים שנותרו"]].sort_values("ימים שנותרו"), use_container_width=True)

except Exception as e:
    st.error(f"שגיאה בעיבוד הנתונים: {e}")


