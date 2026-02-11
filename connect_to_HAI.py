import streamlit as st

with open("Birthday_HAI.py", encoding="utf-8") as f:
    code = f.read()
    exec(code)
