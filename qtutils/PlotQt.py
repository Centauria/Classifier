import pandas as pd
import os
import plotly.offline as pl
import plotly.graph_objs as go
import plotly.tools as pltools
import numpy as np
from tempfile import TemporaryDirectory


class PlotQt:
    def __init__(self):
        self.html_directory = TemporaryDirectory('tmp')
    
    def scatter(self, x: pd.Series, y: pd.Series, c: pd.Series = None, file_name='temp.html'):
        path_html = os.sep.join([self.html_directory.name, file_name])
        if c is not None:
            classes = set(c)
            traces = []
            for cl in classes:
                x_s = x[c == cl]
                y_s = y[c == cl]
                traces.append(go.Scatter(
                        x=x_s,
                        y=y_s,
                        mode='markers',
                        name=cl
                ))
        else:
            traces = [go.Scatter(
                    x=x,
                    y=y,
                    mode='markers'
            )]
        layout = dict(
                xaxis=dict(title=x.name),
                yaxis=dict(title=y.name)
        )
        pl.plot(traces, filename=path_html, auto_open=False)
        return path_html
