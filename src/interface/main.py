import streamlit as st


class Visualizer:
    def __init__(self, fig, summary=None, charts=None):
        self.fig = fig
        self.title = "Data Visualizer"
        self.description = "A simple data visualization tool using Streamlit."
        self.summary = summary
        self.charts = charts or []

    def display(self):
        st.title(self.title)
        st.write(self.description)
        if self.summary:
            st.caption(self.summary)
        st.plotly_chart(self.fig, width='stretch')
        for chart in self.charts:
            st.plotly_chart(chart, width='stretch')
