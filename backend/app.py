import json
import logging
import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import (
    RedirectResponse,
)
from pydantic import BaseModel

from feishu.auth import Authentication
from utils.cipher import AESCipher

load_dotenv()
app = FastAPI()
cipher = AESCipher(os.getenv('ENCRYPT_KEY'))


async def start_server():
    config = uvicorn.Config(app, port=5001, host='0.0.0.0', log_level="info")
    server = uvicorn.Server(config)
    await server.serve()


@app.get("/")
async def root():
    return {"message": "Hello World"}


class Events(BaseModel):
    challenge: str | None
    token: str | None
    type: str


@app.get("/feishu/login_success")
async def login_success(code: str, state: str):
    logging.info('code, %s', code)
    logging.info('state, %s', state)
    Authentication.on_login_success(state, code)
    return RedirectResponse('/')


@app.post("/feishu/events")
async def events(request: Request):
    txt = await request.json()
    item = json.loads(cipher.decrypt_string(txt['encrypt']))
    event = Events(**item)
    logging.info('event, %r', event)
    if event.type == 'url_verification':
        return {
            "challenge": event.challenge
        }
    return {}
