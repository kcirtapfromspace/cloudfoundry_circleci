import logging
import psycopg2
import psycopg2.extras
import os
import json

from cfenv import AppEnv
from datagen import data_generator, stop_event
from threading import Thread, Event
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from spacy_similarity import my_calc_similarity
from db import connect_to_db
from typing import List, Optional
import uvicorn

app = FastAPI()
env = AppEnv()
port = int(os.getenv("PORT"))
templates = Jinja2Templates(directory="templates")

logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Global variable to keep track of whether we're generating data
is_generating_data = False
# Store the data generating thread globally
data_gen_thread = None
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.post('/start')
def start_generating_data():
    global is_generating_data, data_gen_thread
    if not is_generating_data:
        is_generating_data = True
        data_gen_thread = Thread(target=data_generator)
        data_gen_thread.start()
    return {"status": "Data generation started"}

@app.post('/stop')
def stop_generating_data():
    global is_generating_data
    if is_generating_data:
        is_generating_data = False
        if data_gen_thread is not None:
            stop_event.set()
            data_gen_thread.join()
    return {"status": "Data generation stopped"}

@app.post('/clear')
def clear_database():
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    try:
        cur.execute("DELETE FROM public.goals;")
        conn.commit()
        print("Database cleared successfully.")
    except Exception as e:
        print(f"Error occurred while clearing the database: {e}")
        conn.rollback()
    return {"status": "Database cleared"}

@app.get('/last_five_entries')
async def last_five_entries():
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM public.goals ORDER BY id DESC LIMIT 5;")
    rows = cur.fetchall()
    return {"lastFiveEntries": [dict(row) for row in rows]}

@app.get('/')
def main(request: Request):
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT DISTINCT goal_user_id FROM public.goals;")
    rows = cur.fetchall()
    user_ids = [row['goal_user_id'] for row in rows]
    return templates.TemplateResponse("index.html", {"request": request, "user_ids": user_ids, "is_generating_data": is_generating_data})

@app.get('/select_user')
async def get_select_user(request: Request):
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT DISTINCT goal_user_id FROM public.goals;")
    rows = cur.fetchall()
    user_ids = [row['goal_user_id'] for row in rows]
    return templates.TemplateResponse('select_user.html', {"request": request, "user_ids": user_ids})

@app.get('/compute_similarities/{user_id}')
def compute_similarities(user_id: str):
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM public.goals WHERE goal_user_id = %s;", (user_id,))
    rows = cur.fetchall()
    cur_goals_list = [row['goal'] for row in rows]
    cur_goal_ids = [row['id'] for row in rows]
    matched_goals = my_calc_similarity(user_id, cur_goals_list, cur_goal_ids)
    return {"matched_goals": matched_goals}


if __name__ == '__main__':
    thread = Thread(target=data_generator)
    thread.start()

    uvicorn.run(app, host='0.0.0.0', port=port)
