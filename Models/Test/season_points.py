import importlib
import test_by_season_cache
import pandas as pd
import json
import os

def generate_points(file: str, output_json: str = None, model_name = None, needs_merge = True, restrict_search = True):

    importlib.reload(test_by_season_cache)

    final_data = pd.read_csv(file, index_col=0)
    final_data.reset_index(inplace=True, drop=True)

    points = []
    points_bb = []
    top_scores = []
    rounds = []

    out_dic = {}

    if output_json == None:
        output_json = 'results_3.json'

    for i in range(1, 20):
        rounds.append(i)

        round_dic = test_by_season_cache.get_best_team(final_data, i, needs_merge = needs_merge, restrict_search = restrict_search)
        #points.append(round_dic['points'])
        #points_bb.append(round_dic['points'] + round_dic['bench_points'])
        #top_scores.append(round_dic['top_score'])

        #print(f"round {i}: {round_dic['best_team']}")

        out_dic[i + 1] = round_dic

        with open(output_json, 'r') as f:

            out_json = json.load(f)

        if model_name == None:
            out_json[file[11:-4]] = out_dic
        else:
            out_json[model_name] = out_dic

        with open(output_json, 'w') as f:
        
            json.dump(out_json, f, indent = 5)

    return out_dic

