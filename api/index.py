# Vercel entry point: only expose `app` so the runtime uses ASGI and does not
# hit the Handler/issubclass check (which fails when FastAPI/Starlette add Handler to the module).
from api.backend import app
