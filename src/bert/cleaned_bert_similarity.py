import os
import json
import psycopg2
import psycopg2.extras
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer('distilbert-base-nli-mean-tokens')

alpha = 0.9

#Function that will take a list of goals and goal ids and output the similar goals
def my_calc_similarity(list_of_goals, list_of_ids):
    sentence_embeddings = model.encode(list_of_goals)
    #I want to turn this into a matrix of cosine similarity scores
    sim_scores = cosine_similarity(sentence_embeddings)
    #Set up a list to hold the potential matches goal ids
    match_goal_ids = [[] for x in range(len(list_of_goals))]
    for j in range(len(list_of_goals)):
        #ignore the diagnol entry
        cur_sim_scores = sim_scores[j]
        cur_sim_scores[j] = 0
        #index where greater than alpha
        cur_potential_idx = [i for i,v in enumerate(cur_sim_scores) if v > alpha]
        for k in range(len(cur_potential_idx)):
            #Need to append the goal ID to the list
            match_goal_ids[j].append(list_of_ids[cur_potential_idx[k]])
            if j > cur_potential_idx[k]:
                continue
            #Print the current goals as potential matches
            print("Potential Match: Goals ", j," and ", cur_potential_idx[k])
            print("Potential Match: Goal ", j, ": ", list_of_goals[j],". and Goal ", cur_potential_idx[k],": ", list_of_goals[cur_potential_idx[k]])
    return(match_goal_ids)


conn = connect_to_db()
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
cur.execute("SELECT * FROM public.goals;")
rows = cur.fetchall()

cur_goals_list = [row['goal'] for row in rows]
cur_goal_ids = [row['id'] for row in rows]

match_ids = my_calc_similarity(cur_goals_list,cur_goal_ids)
