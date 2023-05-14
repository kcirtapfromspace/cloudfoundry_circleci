import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


model = SentenceTransformer('bert-base-nli-mean-tokens')
df = pd.read_csv('')

#get the grant number
#cur_grant = df.at[0,'grant_number']
cur_grant = ''
#get the data frame for that grant
cur_who_grant_df = df.loc[df['grant_number'] == cur_grant]
#want all the goals from that grant
cur_goals_list = list(cur_who_grant_df["goal text"])
cur_goal_ids = list(cur_who_grant_df["goal_id"])
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

match_ids = my_calc_similarity(cur_goals_list,cur_goal_ids)
