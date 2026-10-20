import streamlit as st

_CSS = """<style>
[data-testid="stMainBlockContainer"] {
    padding-left: 1rem;
    padding-right: 1rem;
}
</style>"""


class Visualizer:
    def __init__(self, fig, summary=None, charts=None, left_fig=None):
        self.fig = fig
        self.title = "Data Visualizer"
        self.description = "A simple data visualization tool using Streamlit."
        self.summary = summary
        self.charts = charts or []
        self.left_fig = left_fig

    def display(self):
        st.html(_CSS)
        st.title(self.title)
        st.write(self.description)
        if self.summary:
            st.caption(self.summary)
        if self.left_fig is None:
            st.plotly_chart(self.fig, width='stretch')
        else:
            left, right = st.columns(2)
            left.plotly_chart(self.left_fig, width='stretch')
            right.plotly_chart(self.fig, width='stretch')
        for chart in self.charts:
            st.plotly_chart(chart, width='stretch')
