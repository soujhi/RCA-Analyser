"""Timeline figure: temperature, defects and downtime on one clock, with operator notes."""
from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from ..analysis import Analysis
from .tokens import COLORS, FONT_STACK


def timeline_figure(df: pd.DataFrame, analysis: Analysis) -> go.Figure:
    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                        row_heights=[0.4, 0.35, 0.25],
                        subplot_titles=("Oven temperature", "Defects per reading", "Downtime (min)"))
    fig.add_trace(go.Scatter(x=df["timestamp"], y=df["temperature"], mode="lines", name="Temperature",
                             line=dict(color=COLORS["orange"], width=2)), row=1, col=1)
    fig.add_trace(go.Bar(x=df["timestamp"], y=df["defect_count"], name="Defects",
                         marker_color=COLORS["pink"]), row=2, col=1)
    stops = df[df["downtime_minutes"] > 0]
    fig.add_trace(go.Bar(x=stops["timestamp"], y=stops["downtime_minutes"], name="Downtime",
                         marker_color=COLORS["indigo"], width=9 * 60 * 1000), row=3, col=1)
    notes = df[df["operator_note"] != ""]
    fig.add_trace(go.Scatter(x=notes["timestamp"], y=[df["temperature"].max()] * len(notes), mode="markers",
                             name="Operator note", text=notes["operator_note"], hoverinfo="text+x",
                             marker=dict(color=COLORS["purple"], size=9, symbol="diamond")), row=1, col=1)
    inc = analysis.incident
    if inc.onset_time is not None:
        for row in (1, 2, 3):
            fig.add_vline(x=inc.onset_time, line_dash="dot", line_color=COLORS["label2"], row=row, col=1)
    fig.update_layout(height=560, margin=dict(l=8, r=8, t=32, b=8), showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family=FONT_STACK, size=13, color=COLORS["label"]))
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor=COLORS["separator"], zeroline=False)
    return fig
