import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates
import gspread
from google.oauth2.service_account import Credentials

# הגדרות דף
st.set_page_config(page_title="ניהול ימי הולדת חכם", layout="wide")

# פונקציית מזלות
def get_zodiac(d, m):
    zodiacs = [
        (21, 3, 19, 4, "טלה ♈"), (20, 4, 20, 5, "שור ♉"), (21, 5, 20, 6, "תאומים ♊"),
        (21, 6, 22, 7, "סרטן ♋"), (23, 7, 22, 8, "אריה ♌"), (23, 8, 22, 9, "בתולה ♍"),
        (23, 9, 22, 10, "מאזניים ♎"), (23, 10, 21, 11, "עקרב ♏"), (22, 11, 21, 12, "קשת ♐"),
        (22, 12, 19, 1, "גדי ♑"), (20, 1, 18, 2, "דלי ♒"), (19, 2, 20, 3, "דגים ♓")
    ]
    for sd, sm, ed, em, name in zodiacs:
        if (m == sm and d >= sd) or (m == em and d <= ed): return name
    return "דגים ♓"

# התחברות לגוגל שיטס (שיטה ישירה)
@st.cache_resource
def get_gsheet_client():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    # אנחנו משתמשים בקישור שהגדרת ב-Secrets
    url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    # כאן אנחנו מתחברים - במידה ויש שגיאת הרשאה, נשתמש בחיבור הקיים
    gc = gspread.oauth_from_dict(st.secrets["gcp_service_account"]) if "gcp_service_account" in st.secrets else None
    return gc, url

# הערה: אם אין לך קובץ JSON של Service Account, נמשיך עם הקיים אך בתיקון פקודת הכתיבה
from streamlit_gsheets import GSheetsConnection
conn = st.connection("gsheets", type=GSheetsConnection)

# קריאת נתונים
df_raw = conn.read(ttl=0).dropna(how="all")

# עיבוד נתונים (אותו לוגיקה מקודם)
today = date.today()
processed = []
celebrants_today = []

for _, row in df_raw.iterrows():
    try:
        b_dt = pd.to_datetime(row['Birthday'], dayfirst=True)
        b_date = b_dt.date()
        h_date = dates.HebrewDate.from_pydate(b_date)
        age = today.year - b_date.year
        if b_date.day == today.day and b_date.month == today.month:
            celebrants_today.append(f"{row['Full_Name']} (גיל {age})")
        
        this_year = b_date.replace(year=today.year)
        if this_year < today: this_year = this_year.replace(year=today.year + 1)
        
        processed.append({
            "שם": row['Full_Name'], "תאריך לועזי": b_date.strftime('%d/%m/%Y'),
            "תאריך עברי": h_date.hebrew_date_string(), "מזל": get_zodiac(b_date.day, b_date.month),
            "ימים שנותרו": (this_year - today).days, "גיל": age, "חודש": b_date.month, "יום": b_date.day
        })
    except: continue

report_df = pd.DataFrame(processed)

# תצוגה
st.title("🎂 ניהול ימי הולדת")
if celebrants_today:
    st.balloons()
    st.success(f"מזל טוב ל: {', '.join(celebrants_today)}!")

if not report_df.empty:
    st.subheader("📅 חוגגים בקרוב")
    st.dataframe(report_df.sort_values("ימים שנותרו"), use_container_width=True, hide_index=True)

# הוספת חוגג - המעקף
with st.expander("➕ הוספה חדשה"):
    with st.form("add_form"):
        name = st.text_input("שם:")
        bday = st.date_input("תאריך:")
        if st.form_submit_button("שמור"):
            new_row = pd.DataFrame([{"Full_Name": name, "Birthday": bday.strftime("%d/%m/%Y")}])
            updated_df = pd.concat([df_raw, new_row], ignore_index=True)
            
            # ניסיון כתיבה עם פרמטרים מחמירים
            try:
                conn.update(data=updated_df)
                st.success("נשמר!")
                st.rerun()
            except Exception as e:
                st.error(f"גוגל עדיין חוסם את הכתיבה. וודא שהגדרת Editor במייל של streamlit.")
                st.code(str(e))
