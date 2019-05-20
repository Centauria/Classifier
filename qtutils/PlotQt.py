import pandas as pd
import os
import random
import string
import plotly.offline as pl
import plotly.graph_objs as go
from tempfile import TemporaryDirectory


class PlotQt:
    def __init__(self):
        self.html_directory = TemporaryDirectory('tmp')

    def scatter(self, x: pd.Series, y: pd.Series, c: pd.Series = None, traces=None, marker=None, file_name=None):
        traces = traces or []
        file_name = file_name or ''.join(random.sample(string.ascii_uppercase, 8)) + '.html'
        path_html = os.sep.join([self.html_directory.name, file_name])
        if c is not None:
            classes = set(c)
            for cl in classes:
                x_s = x[c == cl]
                y_s = y[c == cl]
                traces.append(go.Scatter(
                        x=x_s,
                        y=y_s,
                        mode='markers',
                        marker=marker,
                        name=cl
                ))
        else:
            traces.append(go.Scatter(
                    x=x,
                    y=y,
                    mode='markers'
            ))
        layout = dict(
                xaxis=dict(title=x.name),
                yaxis=dict(title=y.name)
        )
        fig = go.Figure(data=traces, layout=layout)
        pl.plot(fig, filename=path_html, auto_open=False)
        return path_html, traces

    def line(self, a, b, c, traces=None, file_name='temp.html'):
        """
        plot a line determined by equation a*x+b*y+c=0
        :param a:
        :param b:
        :param c:
        :param traces:
        :param file_name:
        :return:
        """
        traces = traces or []
        path_html = os.sep.join([self.html_directory.name, file_name])
