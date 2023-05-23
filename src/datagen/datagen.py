from math import e
import os
import random
import json
from flask import Flask, jsonify, render_template
from cfenv import AppEnv

from faker import Faker
import psycopg2
import uuid
from time import sleep
from threading import Thread
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor



app = Flask(__name__)
env = AppEnv()
FlaskInstrumentor().instrument_app(app)

Psycopg2Instrumentor().instrument()
postgres = 'postgresql-db'
postgres_service = env.get_service(label=postgres)

# Predefined goals
predefined_goals = ["build better hygiene habits", "exercise regularly", 
                    "eat healthier", "reduce screen time", "improve sleeping schedule"]

# Counter for number of generated goals
goal_counter = 0

port = int(os.environ.get('PORT', 3000))

def get_postgres_service():
    # Extract VCAP_SERVICES
    vcap_services_str = os.environ.get('VCAP_SERVICES')
    if vcap_services_str is None:
        raise Exception('VCAP_SERVICES environment variable not found.')
    vcap_services = json.loads(vcap_services_str)


    # Extract PostgreSQL service details
    return vcap_services['postgresql-db'][0]['credentials']

def connect_to_db():
    postgres_service = get_postgres_service()

    # Connect to the PostgreSQL database
    conn = psycopg2.connect(
        host=postgres_service['hostname'],
        port=postgres_service['port'],
        user=postgres_service['username'],
        password=postgres_service['password'],
        dbname=postgres_service['dbname'],

    )
    return conn

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/env')
def env_variables():
    return jsonify(dict(os.environ))

@app.route('/services')
def services():
    return jsonify(env.get_services())

@app.route('/status')
def status():
    records = []

    conn = connect_to_db()

    with conn.cursor() as cur:
        # Fetch the last 10 inserted records
        cur.execute("SELECT * FROM public.goals ORDER BY id DESC LIMIT 10;")
        records = cur.fetchall()

    records = [{'id': record[0], 'goal': record[1]} for record in records]

    return render_template('status.html', records=records)

@app.route('/goal/<id>', methods=['GET'])
def get_goal(id):
    conn = connect_to_db()

    with conn.cursor() as cur:
        cur.execute("SELECT * FROM public.goals WHERE id = %s;", (id, ))
        record = cur.fetchone()

    if record is None:
        return jsonify({'error': 'No goal found with the given id.'}), 404
    else:
        return jsonify({'id': record[0], 'goal': record[1]})


def data_generator():
    global goal_counter

    conn = connect_to_db()

    with conn.cursor() as cur:
        fake = Faker()

        # Check if the 'public.goals' table exists and if not, create it.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.goals (
                id uuid PRIMARY KEY,
                goal text NOT NULL,
                goal_user_id uuid NOT NULL
            );
        """)
        cur.execute("""
            ALTER TABLE public.goals 
            ADD COLUMN IF NOT EXISTS goal_user_id uuid;
        """)

        num_iterations = 0  

        # generate 5 random unique user ids
        user_ids = [str(uuid.uuid4()) for _ in range(50)]

        while num_iterations < 10000:
            # Randomly select a user id from generated user ids
            goal_user_id = random.choice(user_ids)

            # Randomly select between predefined goals and fake generated ones
            if random.random() < 0.5:
                goal_text = random.choice(predefined_goals)
            else:
                num_words = random.randint(3, 20)
                goal_text = ' '.join(fake.words(nb=num_words))

            goal_id = str(uuid.uuid4())
            try:
                cur.execute(
                    "INSERT INTO public.goals (id, goal, goal_user_id) VALUES (%s, %s, %s);",
                    (goal_id, goal_text, goal_user_id)
                )

                conn.commit()

                goal_counter += 1

                print(f"Inserted goal {goal_id} for user {goal_user_id} with text: {goal_text}")

            except Exception as e:
                print(f"Error: {e}")
                conn.rollback()

            sleep(1)
            num_iterations += 1
        print("finished generating data!")

if __name__ == "__main__":
    # Start the data generator in a separate thread
    thread = Thread(target=data_generator)
    thread.start()

    # Run the flask app
    port = int(os.getenv("PORT", 5001))  # set a default port if none is provided by environment
    app.run(host='0.0.0.0', port=env.port)
