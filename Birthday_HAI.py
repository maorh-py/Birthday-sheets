import streamlit as st
import pandas as pd
from datetime import date
from pyluach import dates

# הגדרות דף
st.set_page_config(page_title="לוח ימי הולדת משפחתי", layout="centered")

try:
    from st_gsheets_connection import GSheetsConnection
except ImportError:
    from streamlit_gsheets import GSheetsConnection

# פונקציית מזלות 
def get_zodiac(d, m):
    zodiacs = [(21,3,19,4,"טלה ♈"),(20,4,20,5,"שור ♉"),(21,5,20,6,"תאומים ♊"),
               (21,6,22,7,"סרטן ♋"),(23,7,22,8,"אריה ♌"),(23,8,22,9,"בתולה ♍"),
               (23,9,22,10,"מאזניים ♎"),(23,10,21,11,"עקרב ♏"),(22,11,21,12,"קשת ♐"),
               (22,12,19,1,"גדי ♑"),(20,1,18,2,"דלי ♒"),(19,2,20,3,"דגים ♓")]
    for sd,sm,ed,em,n in zodiacs:
        if (m==sm and d>=sd) or (m==em and d<=ed): return n
    return "דגים ♓"

# עיבוד תאריכים
def process_person(name, bday_date, is_temporary=False):
    today = date.today()
    h_date = dates.HebrewDate.from_pydate(bday_date)
    next_bday = bday_date.replace(year=today.year)
    if next_bday < today:
        next_bday = next_bday.replace(year=today.year + 1)
    
    return {
        "שם": name,
        "תאריך לועזי": bday_date.strftime('%d/%m/%Y'),
        "תאריך עברי": h_date.hebrew_date_string(),
        "מזל": get_zodiac(bday_date.day, bday_date.month),
        "גיל": (lambda y, m: f"{y}" if y > 0 else f"{m}M")(
            today.year - bday_date.year - ((today.month, today.day) < (bday_date.month, bday_date.day)),
            (today.year - bday_date.year) * 12 + today.month - bday_date.month),# אם הגיל קטן משנה יוצג בחודשים
        "עוד כמה ימים": (next_bday - today).days, 
        "חודש": bday_date.month,
        "יום": bday_date.day,
        "זמני": is_temporary
    }

if "temp_people" not in st.session_state:
    st.session_state.temp_people = []

all_data = []

# טעינת נתונים מגוגל שיטס
try:
    # שליפת המזהים מה-Secrets מאתר streamlit
    sheet_id = st.secrets["gsheets"]["sheet_id"]
    gid = st.secrets["gsheets"]["gid"]
    
    # בניית הקישור בצורה דינמית
    csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid={gid}"
    
    # קריאת הנתונים
    df = pd.read_csv(csv_url)

    if not df.empty:
        # ניקוי רווחים משמות העמודות
        df.columns = df.columns.str.strip()
        
        for _, row in df.iterrows():
            name = row.get('Full_Name')
            b_day = row.get('Birthday')
            
            if pd.notnull(name) and pd.notnull(b_day):
                try:
                    b_date = pd.to_datetime(b_day, dayfirst=True).date()
                    # קריאה לפונקציית העיבוד 
                    all_data.append(process_person(str(name), b_date))
                except:
                    continue
except Exception:
    st.error("שגיאה בטעינת הנתונים מהגיליון.")
#-------------------------------------------------------------------------------------------------------
# הוספת אנשים זמניים מה-session_state אם יש
if 'temp_people' in st.session_state:
    all_data.extend(st.session_state.temp_people)
today = date.today()

# --- מי חוגג היום ---
hbd_today = [p for p in all_data if p["חודש"] == today.month and p["יום"] == today.day]
if hbd_today:
    st.balloons()
    for p in hbd_today:
        html_content = f"""
            <div style="text-align: center; border: 3px solid #FF4B4B; border-radius: 20px; padding: 20px; background-color: #FFF5F5; margin-bottom: 20px; direction: rtl;">
                <div style="font-size: 40px; margin-bottom: 10px;">🎈 מזל טוב 🎈</div>
                <div style="font-size: 60px; font-weight: bold; color: #FF4B4B; margin-bottom: 10px;">{p['שם']}</div>
                <div style="font-size: 30px; color: #31333F;">חוגג/ת היום {p['גיל']} 🎂</div>
            </div>
        """
        st.markdown(html_content, unsafe_allow_html=True)

# פונקציית צביעה
def color_rows(df, original_list):
    colors = pd.DataFrame('', index=df.index, columns=df.columns)
    for i in range(len(df)):
        if i < len(original_list) and original_list[i]['זמני']:
            colors.iloc[i] = 'background-color: #ffffd1'
    return colors

# --- טבלת החודש ---
st.header(f" חגיגות החודש")
this_month_list = sorted([p for p in all_data if p["חודש"] == today.month and p["יום"] >= today.day], key=lambda x: x["יום"])

if this_month_list:
    df_month = pd.DataFrame(this_month_list)[["עוד כמה ימים","תאריך לועזי", "גיל","שם"]]
    st.dataframe(df_month, hide_index=True, use_container_width=True)

# --- רשימת כל החוגגים ---
st.header("📊 רשימת כל החוגגים")
if all_data:
    all_sorted = sorted(all_data, key=lambda x: (x["חודש"], x["יום"]))
    
    columns_order = ["מזל", "תאריך לועזי", "תאריך עברי","גיל","שם"]
    df_all = pd.DataFrame(all_sorted)[columns_order]
    styled_df = df_all.style.apply(lambda x: color_rows(df_all, all_sorted), axis=None).format(str, subset=["גיל"])
    st.dataframe(
        df_all.style.apply(lambda x: color_rows(df_all, all_sorted), axis=None),
        column_config={
            "שם": st.column_config.TextColumn("שם חוגג", width="medium"),
            "מזל": st.column_config.TextColumn("מזל", width="small"),
            "גיל": st.column_config.NumberColumn("גיל", width="small"),
        },
        hide_index=True,
        use_container_width=True,
        height=600 
    )

# ---   הוספה   ---
form_link = st.secrets["gsheets"].get("form_url", "#")

# יצירת הכפתור הדינמי
st.link_button("➕ הוסף בן משפחה חדש", form_link)
# ---   רענון ---
if st.button("🔄 רענון נתונים"):
        st.cache_data.clear()
        st.rerun()
 








































