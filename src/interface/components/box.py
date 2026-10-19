
import plotly.graph_objects as go
from kelasking import eff_dims, state as State, truck as Truck


class TruckGraph:
    def __init__(self, state: State, truck: Truck):
        self.state = state
        self.truck = truck

    @staticmethod
    def _box_vertices(x, y, z, dx, dy, dz):
        return (
            [
                x, x + dx, x + dx, x,
                x, x + dx, x + dx, x,
            ],
            [
                y, y, y + dy, y + dy,
                y, y, y + dy, y + dy,
            ],
            [
                z, z, z, z,
                z + dz, z + dz, z + dz, z + dz,
            ],
        )

    def draw(self) -> go.Figure:
        fig = go.Figure()

        # Truck dimensions
        w = self.truck.dimentions["w"]
        l = self.truck.dimentions["l"]
        h = self.truck.dimentions["h"]

        corners = [
            (0, 0, 0),
            (w, 0, 0),
            (w, l, 0),
            (0, l, 0),
            (0, 0, h),
            (w, 0, h),
            (w, l, h),
            (0, l, h),
        ]

        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7),
        ]

        xs, ys, zs = [], [], []

        for a, b in edges:
            xs.extend([corners[a][0], corners[b][0], None])
            ys.extend([corners[a][1], corners[b][1], None])
            zs.extend([corners[a][2], corners[b][2], None])

        fig.add_trace(
            go.Scatter3d(
                x=xs,
                y=ys,
                z=zs,
                mode="lines",
                line=dict(color="black", width=5),
                name="Truck",
            )
        )

        i = [0, 0, 4, 4, 0, 0, 1, 1, 2, 2, 3, 3]
        j = [1, 2, 5, 6, 1, 5, 2, 6, 3, 7, 0, 4]
        k = [2, 3, 6, 7, 5, 4, 6, 5, 7, 6, 4, 7]

        for p in self.state.inserted_pack:
            coords = self.state.coords[p.id]
            eff = eff_dims(p.dimentions, p.orientation)

            x, y, z = self._box_vertices(
                coords["x"],
                coords["y"],
                coords["z"],
                eff["x"],
                eff["y"],
                eff["z"],
            )

            fig.add_trace(
                go.Mesh3d(
                    x=x,
                    y=y,
                    z=z,
                    i=i,
                    j=j,
                    k=k,
                    color="royalblue" if p.is_fragile is False else "red",
                    opacity=1.0,
                    flatshading=True,
                    name=f"Package {p.id}",
                    hovertemplate=(
                        f"Package {p.id}<br>"
                        "X: %{x}<br>"
                        "Y: %{y}<br>"
                        "Z: %{z}<extra></extra>"
                    ),
                )
            )
            vertices = list(zip(x, y, z))

            edge_x, edge_y, edge_z = [], [], []

            for a, b in edges:
                edge_x.extend([vertices[a][0], vertices[b][0], None])
                edge_y.extend([vertices[a][1], vertices[b][1], None])
                edge_z.extend([vertices[a][2], vertices[b][2], None])

            fig.add_trace(
                go.Scatter3d(
                    x=edge_x,
                    y=edge_y,
                    z=edge_z,
                    mode="lines",
                    line=dict(
                        color="black",
                        width=4,
                    ),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )
        fig.update_layout(
            title="Trukkun",
            showlegend=True,
            scene=dict(
                xaxis=dict(range=[0, w], title="Width"),
                yaxis=dict(range=[0, l], title="Length"),
                zaxis=dict(range=[0, h], title="Height"),
                aspectmode="data",
            ),
            margin=dict(l=0, r=0, t=40, b=0),
        )

        return fig
