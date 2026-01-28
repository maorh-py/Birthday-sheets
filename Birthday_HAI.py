import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת חכם", layout="wide")

# עיצוב CSS למרכז ויישור לימין
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    .birthday-center {
        text-align: center; font-size: 50px; font-weight: bold; color: #FF4B4B;
        padding: 30px; border: 10px double #FF4B4B; border-radius: 30px;
        margin: 40px auto; width: 80%; background-color: #FFF5F5;
    }
    </style>
    """, unsafe_allow_html=True)

# חיבור לגליון
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

# קריאת נתונים
df_raw = conn.read(ttl=0).dropna(how="all")

today = date.today()
processed = []
celebrants_today = []

for _, row in df_raw.iterrows():
    try:
        b_dt = pd.to_datetime(row['Birthday'], dayfirst=True)
        b_date = b_dt.date()
        age = today.year - b_date.year
        
        if b_date.day == today.day and b_date.month == today.month:
            celebrants_today.append(f"{row['Full_Name']} (חוגג/ת {age})")
            
        h_date = dates.HebrewDate.from_pydate(b_date)
        this_year = b_date.replace(year=today.year)
        if this_year < today: this_year = this_year.replace(year=today.year + 1)
        
        processed.append({
            "שם": row['Full_Name'],
            "תאריך לועזי": b_date.strftime('%d/%m/%Y'),
            "יום": b_date.day,
            "חודש": b_date.month,
            "תאריך עברי": h_date.hebrew_date_string(),
            "מזל": get_zodiac(b_date.day, b_date.month),
            "ימים שנותרו": (this_year - today).days,
            "גיל": age
        })
    except: continue

report_df = pd.DataFrame(processed)

# --- תצוגה ---
st.title("🎂 ניהול ימי הולדת חכם")

if celebrants_today:
    st.balloons()
    st.markdown(f'<div class="birthday-center">🎉 מזל טוב! 🎉<br>{"<br>".join(celebrants_today)}</div>', unsafe_allow_html=True)

st.subheader(f"📅 נותרו לחגוג החודש")
if not report_df.empty:
    current = report_df[(report_df['חודש'] == today.month) & (report_df['יום'] >= today.day)].sort_values("יום")
    st.dataframe(current[["שם", "תאריך לועזי", "תאריך עברי", "ימים שנותרו", "גיל"]], use_container_width=True, hide_index=True)

st.subheader("📋 רשימה מלאה")
if not report_df.empty:
    st.dataframe(report_df[["שם", "תאריך לועזי", "תאריך עברי", "מזל", "גיל"]], use_container_width=True, hide_index=True)

st.write("---")
# הוספת חוגג - בתחתית
with st.expander("➕ הוספת חוגג חדש (נשמר בגליון)"):
    with st.form("add_form", clear_on_submit=True):
        new_name = st.text_input("שם מלא:")
        new_bday = st.date_input("תאריך לידה:", value=date(1990, 1, 1))
        if st.form_submit_button("שמור באקסל"):
            if new_name:
                # יצירת שורה חדשה
                new_entry = pd.DataFrame([{"Full_Name": new_name, "Birthday": new_bday.strftime("%d/%m/%Y")}])
                # עדכון הדאטה-פריים הקיים
                updated_df = pd.concat([df_raw, new_entry], ignore_index=True)
                # כתיבה מחדש לגליון
                conn.update(data=updated_df)
                st.cache_data.clear() # ניקוי זיכרון כדי לראות את השינוי מיד
                st.success(f"החוגג {new_name} נשמר!")
                st.rerun()
