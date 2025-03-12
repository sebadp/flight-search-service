from mangum import Mangum
from fastapi import FastAPI

from routers.journeys import router as journeys_router

app = FastAPI()
app.include_router(journeys_router)

lambda_handler = Mangum(app, api_gateway_base_path="/dev")
