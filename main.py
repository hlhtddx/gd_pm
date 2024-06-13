import asyncio
import os

import dash
import uvicorn
from dash import html, dcc
from fastapi.middleware.wsgi import WSGIMiddleware

from backend.app import app
from session.common import Tenant
from session.login import Login
from utils.config import SqliteConfig


async def login_feishu():
    config = SqliteConfig()
    tenant = Tenant(name='rt', app_id=os.getenv('APP_ID'), app_secret=os.getenv('APP_SECRET'))
    login = Login(config, tenant)
    await login.login()
    # auth = Authentication(login)


async def start_server():
    config = uvicorn.Config(app, port=5001, host='0.0.0.0', log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


# 创建 Dash 应用
dash_app = dash.Dash(__name__, requests_pathname_prefix='/dash/')
dash_app.layout = html.Div([
    html.H1("Dash Plotly 仪表板"),
    dcc.Graph(id='example-graph')
])
# 将 Dash 应用挂载到 FastAPI
app.mount("/dash", WSGIMiddleware(dash_app.server))


async def main():
    task1 = asyncio.create_task(start_server())
    await asyncio.sleep(1)
    task2 = asyncio.create_task(login_feishu())
    await asyncio.gather(task1, task2)


if __name__ == "__main__":
    asyncio.run(start_server())
