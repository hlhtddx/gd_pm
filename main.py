import asyncio
import os

import dash
from dash import html, dcc

from server.app import run_server
from workspace import Workspace, Tenant

tenant = Tenant(name='rt', app_id=os.getenv('APP_ID'), app_secret=os.getenv('APP_SECRET'))
workspace = Workspace(tenant=tenant, path_name='./data', create=False)

dash_app = dash.Dash(__name__, requests_pathname_prefix='/dash/')
dash_app.layout = html.Div([
    html.H1("Dash Plotly 仪表板"),
    dcc.Graph(id='example-graph')
])

if __name__ == "__main__":
    asyncio.run(run_server(dash_app.server))
