import os

import streamlit as st

from functools import wraps
import streamlit.components.v1 as components
def intro():

    st.write("# Welcome to EngageLane AI! 👋")
    st.markdown("""
    
    ## Thanks Trimble, for giving opportunity to explore AI
    
    This is a streamlit application using azure openai, Initially we are integrating some of the most used graphql api.
    By using langchain agents we have achieved integration api, formatted the response and where the end user can easily get the information.


    As this is exclusively for hackathon-2023, we still need to go long way by integrating chat module to the all the apis available. 

    """)

st.set_page_config(
        page_title="EngageLane AI",
        page_icon= '',
        layout='centered',
        menu_items={
        'About': "This is an *extremely* cool app! to try it"
    }
)
hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 


def unauthorized():
    st.write("# Unauthorized")
    st.stop()

if __name__ == "__main__":
    intro()


