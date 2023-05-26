# math import e
import random
import string
from cfenv import AppEnv
from faker import Faker
from .db import connect_to_db
import uuid
from time import sleep
from threading import Thread, Event
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.flask import FlaskInstrumentor

env = AppEnv()
Psycopg2Instrumentor().instrument()

# Predefined goals
predefined_goals = []
is_generating_data = False

# Counter for number of generated goals
goal_counter = 0

# Stop event for the thread
stop_event = Event()

def data_generator():
    global goal_counter
    global stop_event
    global predefined_goals

    conn = connect_to_db()

    if conn is None:
        print("Could not connect to the database. Data generation terminated.")
        return

    with conn.cursor() as cur:
        fake = Faker()

        # Enable uuid-ossp extension if not done yet
        cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";")
        conn.commit()

        # Check if the 'public.goals' table exists and if not, create it.
        cur.execute("""
            CREATE TABLE IF NOT EXISTS public.goals (
                id uuid PRIMARY KEY,
                goal text NOT NULL,
                goal_user_id uuid NOT NULL
            );
        """)

        num_iterations = 0

        # generate random unique user ids
        user_ids = [str(uuid.uuid4()) for _ in range(5)]

        while not stop_event.is_set() and num_iterations < 10000:
            # Randomly select a user id from generated user ids
            goal_user_id = random.choice(user_ids)

            # Generate a goal
            num_words = random.randint(3, 20)
            goal_text = ' '.join(fake.words(nb=num_words))

            # Add random punctuation to the end of the goal text
            punctuation = random.choice(string.punctuation)
            goal_text += punctuation

            # Add the first 10 generated goals to predefined goals
            if len(predefined_goals) < 10:
                predefined_goals.append(goal_text)
            elif random.random() < 0.5:
                goal_text = random.choice(predefined_goals)

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
        print("Finished generating data!")
        
# Start the data generator in a new thread
data_gen_thread = Thread(target=data_generator)
