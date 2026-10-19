import streamlit as st

from interface.components.box import TruckGraph

class Visualizer:
    def __init__(self, state, truck):
        self.state = state
        self.fig = TruckGraph(state, truck).draw()
        self.title = "Data Visualizer"
        self.description = "A simple data visualization tool using Streamlit."

    def display(self):
        st.title(self.title)
        st.write(self.description)
        st.plotly_chart(self.fig, use_container_width=True) 