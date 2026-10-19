import streamlit as st


class Visualizer:
    def __init__(self, fig, summary=None):
        self.fig = fig
        self.title = "Data Visualizer"
        self.description = "A simple data visualization tool using Streamlit."
        self.summary = summary

    def display(self):
        st.title(self.title)
        st.write(self.description)
        if self.summary:
            st.caption(self.summary)
        st.plotly_chart(self.fig, width='stretch')
