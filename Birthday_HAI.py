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
# מזלות
def get_zodiac_info(d, m):
   
    icon_base = "https://img.icons8.com/external-flat-icons-inmotus-design/40/external-"
    zodiacs = [
        (21,3,19,4, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Aries-zodiac-flat-round-vectorslab.png", "טלה"),
        (20,4,20,5, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Taurus-zodiac-flat-round-vectorslab.png", "שור"),
        (21,5,20,6, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Gemini-zodiac-flat-round-vectorslab.png", "תאומים"),
        (21,6,22,7, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Cancer-zodiac-flat-round-vectorslab.png", "סרטן"),
        (23,7,22,8, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Leo-zodiac-flat-round-vectorslab.png", "אריה"),
        (23,8,22,9, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Virgo-zodiac-flat-round-vectorslab.png", "בתולה"),
        (23,9,22,10, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Libra-zodiac-flat-round-vectorslab.png", "מאזניים"),
        (23,10,21,11, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Scorpio-zodiac-flat-round-vectorslab.png", "עקרב"),
        (22,11,21,12, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Sagittarius-zodiac-flat-round-vectorslab.png", "קשת"),
        (22,12,19,1, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Capricorn-zodiac-flat-round-vectorslab.png", "גדי"),
        (20,1,18,2, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Aquarius-zodiac-flat-round-vectorslab.png", "דלי"),
        (19,2,20,3, "https://img.icons8.com/external-flat-round-vectorslab/100/external-Pisces-zodiac-flat-round-vectorslab.png", "דגים")
        [
    for sd, sm, ed, em, img, name in zodiacs:
        if (m == sm and d >= sd) or (m == em and d <= ed):
            return img, name
    return zodiacs[-1][4], zodiacs[-1][5]
# עיבוד תאריכים
def process_person(name, bday_date, is_temporary=False):
    today = date.today()
    h_date = dates.HebrewDate.from_pydate(bday_date)
    next_bday = bday_date.replace(year=today.year)
    if next_bday < today:
        next_bday = next_bday.replace(year=today.year + 1)
    
    z_img, z_name = get_zodiac_info(bday_date.day, bday_date.month)
    
    return {
        "שם": name,
        "תאריך לועזי": bday_date.strftime('%d/%m/%Y'),
        "תאריך עברי": h_date.hebrew_date_string(),
        "סמל מזל": z_img,
        "מזל": z_name,
        "גיל": today.year - bday_date.year - ((today.month, today.day) < (bday_date.month, bday_date.day)),
        "עוד כמה ימים ליום הולדת": (next_bday - today).days,
        "חודש": bday_date.month,
        "יום": bday_date.day,
        "זמני": is_temporary
    }

if "temp_people" not in st.session_state:
    st.session_state.temp_people = []

all_data = []
spreadsheet_url = ""

# טעינת נתונים
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    spreadsheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
    df_raw = conn.read(ttl=0).dropna(how="all")
    for _, row in df_raw.iterrows():
        try:
            b_date = pd.to_datetime(row['Birthday'], dayfirst=True).date()
            all_data.append(process_person(row['Full_Name'], b_date))
        except: continue
except: pass

all_data.extend(st.session_state.temp_people)
today = date.today()

# --- מי חוגג היום ---
hbd_today = [p for p in all_data if p["חודש"] == today.month and p["יום"] == today.day]
if hbd_today:
    st.balloons()
    for p in hbd_today:
        st.markdown(f'<div style="background-color: #ffffff; padding: 20px; border-radius: 15px; text-align: center; border: 2px solid #f0f2f6; margin-bottom: 20px;"><h3>🎈 מזל טוב {p["שם"]}! חוגג/ת היום {p["גיל"]} 🎈</h3></div>', unsafe_allow_html=True)

# פונקציית צביעה
def color_rows(df, original_list):
    colors = pd.DataFrame('', index=df.index, columns=df.columns)
    for i in range(len(df)):
        if i < len(original_list) and original_list[i]['זמני']:
            colors.iloc[i] = 'background-color: #ffffd1'
    return colors

# ---  טבלת החודש ---
st.header(f"📅 חגיגות קרובות")
this_month_list = sorted([p for p in all_data if p["חודש"] == today.month and p["יום"] >= today.day], key=lambda x: x["יום"])

if this_month_list:
    df_month = pd.DataFrame(this_month_list)[["שם", "תאריך לועזי", "גיל", "עוד כמה ימים ליום הולדת"]]
    st.dataframe(
        df_month.style.apply(lambda x: color_rows(df_month, this_month_list), axis=None),
        hide_index=True, use_container_width=True
    )

# ---  רשימת כל החוגגים ---
st.header("📊 רשימת כל החוגגים")
if all_data:
    all_sorted = sorted(all_data, key=lambda x: (x["חודש"], x["יום"]))
    df_all = pd.DataFrame(all_sorted)[["סמל מזל", "מזל", "שם", "תאריך לועזי", "תאריך עברי", "גיל"]]
    
    st.dataframe(
        df_all.style.apply(lambda x: color_rows(df_all, all_sorted), axis=None),
        column_config={
            "סמל מזל": st.column_config.ImageColumn(" ", width="small"),
            "גיל": st.column_config.NumberColumn("גיל", format="%d")
        },
        hide_index=True,
        use_container_width=True,
        height=500  # גובה שמציג כ-15 שורות לפני שצריך לגלול
    )

# ---  הוספה זמנית ---
with st.expander("⏱️ הוספה זמנית / רענון"):
    if st.button("🔄 רענון נתונים"):
        st.cache_data.clear()
        st.rerun()
    with st.form("temp_add", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1: t_name = st.text_input("שם:")
        with c2: t_date = st.date_input("תאריך לידה:", value=date(2000, 1, 1))
        if st.form_submit_button("הוסף"):
            if t_name:
                st.session_state.temp_people.append(process_person(t_name, t_date, is_temporary=True))
                st.rerun()




