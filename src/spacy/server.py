from sympy import sec
import uvicorn
import os

from utilities.auth_routes import setup_auth_routes
from utilities.auth2 import get_current_active_user
from routes import setup_main_routes
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from fastapi.routing import APIRoute
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware import Middleware
from itsdangerous import URLSafeSerializer

from cfenv import AppEnv

SECRET_KEY = "your-secret-key"
SIGNED_COOKIE_SALT = "your-cookie-salt"
serializer = URLSafeSerializer(SECRET_KEY, salt=SIGNED_COOKIE_SALT)

class BaseRoute(APIRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
        self.dependencies.append(Depends(oauth2_scheme))
        self.dependencies.append(Depends(get_current_active_user))
        
app = FastAPI(default_route_class=BaseRoute, middleware=[
    Middleware(SessionMiddleware, secret_key=SECRET_KEY, https_only=True),
])

env = AppEnv()
port = int(os.getenv("PORT"))

app.mount("/static", StaticFiles(directory="static"), name="static")

# Pass app to setup_routes
setup_main_routes(app)
setup_auth_routes(app)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=port)
