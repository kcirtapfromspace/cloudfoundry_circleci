import os
from flask import Flask, render_template
from db import connect_to_db
from cleaned_bert_similarity import my_calc_similarity
import psycopg2
import psycopg2.extras

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/compute_similarities')
def compute_similarities():
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM public.goals;")
    rows = cur.fetchall()

    cur_goals_list = [row['goal'] for row in rows]
    cur_goal_ids = [row['id'] for row in rows]

    match_ids = my_calc_similarity(cur_goals_list,cur_goal_ids)

    return {"match_ids": match_ids}

if __name__ == '__main__':
    app.run()

def run():
    port = int(os.getenv("PORT"))
    app.run(host='0.0.0.0', port=port)