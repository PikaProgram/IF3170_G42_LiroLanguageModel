import plotly.graph_objects as go


def _line(y, name):
    return go.Scatter(y=y, mode="lines", name=name)


class ObjectiveGraph:
    def __init__(self, maximum, average=None):
        self.maximum = maximum
        self.average = average

    def draw(self) -> go.Figure:
        fig = go.Figure(_line(self.maximum, "max"))
        if self.average is not None:
            fig.add_trace(_line(self.average, "average"))
        fig.update_layout(title="Objective value progression",
                          xaxis_title="Iteration", yaxis_title="Objective value")
        return fig


class AcceptanceProbabilityGraph:
    def __init__(self, probability):
        self.probability = probability

    def draw(self) -> go.Figure:
        fig = go.Figure(_line(self.probability, "e^(dE/T)"))
        fig.update_layout(title="Acceptance probability e^(dE/T)", yaxis_type="log",
                          xaxis_title="Iteration", yaxis_title="e^(dE/T)")
        return fig
