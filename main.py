"""
@Time    : 2023/11/12 17:45
@Author  : asanthan
@File    : main.py
@Description: The app is hosts the backend service support for Streamlit Application
"""



from fastapi import FastAPI 
from pydantic import BaseModel
from metagpt.roles.cpg_product_researcher import RESEARCH_PATH, Researcher
from metagpt.config import CONFIG

import uvicorn

class Task(BaseModel):
    name: str
    topic: str
    userid: str
    task_id: str


app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/agent/run")
async def read_item(task:Task):
    CONFIG.setTaskConfig(task.userid,task.task_id)
    role = Researcher(language="en-us")
    await role.run(task.topic)
    print(f"save report to {RESEARCH_PATH / f'{task.topic}.md'}.")

    return {"response": f"save report to {RESEARCH_PATH / f'{task.topic}.md'}."}


uvicorn.run(app, host="0.0.0.0", port=8010)