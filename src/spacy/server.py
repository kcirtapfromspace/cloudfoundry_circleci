import logging
import psycopg2
import psycopg2.extras
import os
import json

from cfenv import AppEnv
from datagen import data_generator, stop_event
from threading import Thread, Event
from flask import Flask, request, redirect, render_template
from flask_wtf import FlaskForm
from spacy_similarity import my_calc_similarity
from db import connect_to_db
from wtforms import SelectField, SubmitField

app = Flask(__name__)
env = AppEnv()
app.config['SECRET_KEY'] = 'your-secret-key'
port = int(os.getenv("PORT"))
# Global variable to keep track of whether we're generating data
is_generating_data = False
# Store the data generating thread globally
data_gen_thread = None

logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')
class UserForm(FlaskForm):
    user_id = SelectField('User', choices=[])
    submit = SubmitField('Find Matches')


@app.route('/start', methods=['POST'])
def start_generating_data():
    global is_generating_data, data_gen_thread
    if not is_generating_data:
        is_generating_data = True
        data_gen_thread = Thread(target=data_generator)
        data_gen_thread.start()
    return redirect(request.referrer)

@app.route('/stop', methods=['POST'])
def stop_generating_data():
    global is_generating_data
    if is_generating_data:
        is_generating_data = False
        if data_gen_thread is not None:
            stop_event.set()
            data_gen_thread.join()
    return redirect(request.referrer)

@app.route('/clear', methods=['POST'])
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
    return redirect(request.referrer)

@app.route('/', methods=['GET', 'POST'])
def main():
    form = UserForm()
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT DISTINCT goal_user_id FROM public.goals;")
    rows = cur.fetchall()
    form.user_id.choices = [(row['goal_user_id'], row['goal_user_id']) for row in rows]
    if form.validate_on_submit():
        user_id = form.user_id.data
        cur.execute("SELECT * FROM public.goals WHERE goal_user_id = %s;", (user_id,))
        rows = cur.fetchall()

        cur_goals_list = [row['goal'] for row in rows]
        cur_goal_ids = [row['id'] for row in rows]

        matched_goals = my_calc_similarity(user_id, cur_goals_list, cur_goal_ids)
        return render_template('index.html', form=form, matched_goals=matched_goals, is_generating_data=is_generating_data)
    return render_template('index.html', form=form, matched_goals=None, is_generating_data=is_generating_data)


@app.route('/select_user', methods=['GET', 'POST'])
def select_user():
    form = UserForm()
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT DISTINCT goal_user_id FROM public.goals;")
    rows = cur.fetchall()
    form.user_id.choices = [(row['goal_user_id'], row['goal_user_id']) for row in rows]
    if form.validate_on_submit():
        return redirect(url_for('compute_similarities', user_id=form.user_id.data))
    return render_template('select_user.html', form=form)

@app.route('/compute_similarities/<user_id>', methods=['GET'])
def compute_similarities(user_id):
    conn = connect_to_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM public.goals WHERE goal_user_id = %s;", (user_id,))
    rows = cur.fetchall()

    cur_goals_list = [row['goal'] for row in rows]
    cur_goal_ids = [row['id'] for row in rows]

    matched_goals = my_calc_similarity(user_id, cur_goals_list, cur_goal_ids)
    return render_template('display_matches.html', matched_goals=matched_goals)

if __name__ == '__main__':
    thread = Thread(target=data_generator)
    thread.start()
    
    app.run(host='0.0.0.0', port=port)