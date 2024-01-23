import pandas as pd
from itertools import combinations
import signal
import time
import requests, json


player_ids = pd.read_csv('/Users/bence/Documents/Personal Projects/FPL/Fantasy-Premier-League/data/2023-24/player_idlist.csv')

def get_top_by_round(round, df, sort_by):


    df = df.loc[df['round'] == round]

    df = df.sort_values(by = sort_by, ascending=False)

    df = pd.merge(df, player_ids, how = 'left', left_on = 'element', right_on='id')

    new_df = df[['element', 'element_type', 'first_name', 'second_name', 'value', 'target', 'predictions', 'minutes', 'team_global']]

    return new_df


def get_best_team(final_data, round):

    out = get_top_by_round(round, final_data, 'predictions')

    to_keep = out

    gks = to_keep[to_keep['element_type'] == 1].head(6)
    defs = to_keep[to_keep['element_type'] == 2].head(10)
    mids = to_keep[to_keep['element_type'] == 3].head(10)
    fwds = to_keep[to_keep['element_type'] == 4].head(7)

    def get_params(gk_set, defy_set, mid_set, fwd_set, value):
        points = sum([gks.loc[[x]][value].item() for x in gk_set]  + [defs.loc[[x]][value].item() for x in defy_set] + [mids.loc[[x]][value].item() for x in mid_set] + [fwds.loc[[x]][value].item() for x in fwd_set])
        cost = sum([gks.loc[[x]]['value'].item() for x in gk_set]  + [defs.loc[[x]]['value'].item() for x in defy_set] + [mids.loc[[x]]['value'].item() for x in mid_set] + [fwds.loc[[x]]['value'].item() for x in fwd_set])

        #print(cost, points)

        return cost, points
    
    def get_params_1(defy_set, mid_set, gk_set):
        cost = sum([defs.loc[[x]]['value'].item() for x in defy_set] + [mids.loc[[x]]['value'].item() for x in mid_set] + [gks.loc[[x]]['value'].item() for x in gk_set])

        #print(cost, points)

        return cost


    import time
    start = time.time()

    best_team = {}

    for j in ['gks', 'defs', 'mids', 'fwds']:
        best_team[j] = []
    best_team['points'] = 0
    best_team['actual_points'] = 0
    best_team['cost'] = 0

    wasted = 0

    teams = {}
    for i in range(36):
        teams[str(i)] = 0


    import signal
    import time


    def handle_timeout(signum, frame):
        raise TimeoutError


    seconds = 20*60

    signal.signal(signal.SIGALRM, handle_timeout)
    signal.alarm(seconds)  # 5 seconds

    x = []
    y = []

    try:
        

        #global wasted
        #global best_team
        #global start
        #global x
        #global y

        gk_points = 0
        gk_cost = 0

        def_points = 0
        def_cost = 0

        mid_points = 0
        mid_cost = 0



        for gk_set in combinations(gks.index, 2):

            temp_gk_points =  sum([gks.loc[[x]]['predictions'].item() for x in gk_set])
            temp_gk_cost = sum([gks.loc[[x]]['value'].item() for x in gk_set])

            if not((gk_cost < temp_gk_cost) and (temp_gk_points < gk_points)):

                gk_points = temp_gk_points
                gk_cost = temp_gk_cost

                for gk in gk_set:
                    teams[str(gks.loc[[gk]]['team_global'].item())] += 1

                for defy_set in combinations(defs.index, 5):

                    temp_def_points =  sum([defs.loc[[x]]['predictions'].item() for x in defy_set])
                    temp_def_cost = sum([defs.loc[[x]]['value'].item() for x in defy_set])

                    for df in defy_set:
                        teams[str(defs.loc[[df]]['team_global'].item())] += 1

                    if (not((def_cost < temp_def_cost) and (temp_def_points < def_points))) and (max(list(teams.values())) < 4):


                        def_points = temp_def_points
                        def_cost = temp_def_cost

                        for mid_set in combinations(mids.index, 5):
                            #if get_params_1(defy_set, mid_set, gk_set) < 1000 - min_fwd:

                            temp_mid_points =  sum([mids.loc[[x]]['predictions'].item() for x in mid_set])
                            temp_mid_cost = sum([mids.loc[[x]]['value'].item() for x in mid_set])

                            for mid in mid_set:
                                teams[str(mids.loc[[mid]]['team_global'].item())] += 1

                            if (not((mid_cost < temp_mid_cost) and (temp_mid_points < mid_points))) and (max(list(teams.values())) < 4):

                                mid_points = temp_mid_points
                                mid_cost = temp_mid_cost

                                for fwd_set in combinations(fwds.index, 3):


                                    cost, points = get_params(gk_set, defy_set, mid_set, fwd_set, 'predictions')
                                    _, actual_points = get_params(gk_set, defy_set, mid_set, fwd_set, 'target')

                                    for fwd in fwd_set:
                                        teams[str(fwds.loc[[fwd]]['team_global'].item())] += 1

                                    if (cost < 1000) and ((max(list(teams.values())) < 4)):
                                        if points > best_team['points']:
                                            best_team['gks'] = gk_set
                                            best_team['defs'] = defy_set
                                            best_team['mids'] = mid_set
                                            best_team['fwds'] = fwd_set
                                            best_team['points'] = points
                                            best_team['actual_points'] = actual_points
                                            best_team['cost'] = cost
                                            #print(best_team)

                                    else:
                                        wasted += 1
                                    
                                    for fwd in fwd_set:
                                        teams[str(fwds.loc[[fwd]]['team_global'].item())] -= 1

                            for mid in mid_set:
                                teams[str(mids.loc[[mid]]['team_global'].item())] -= 1

                    x.append(defy_set)
                    y.append(time.time() - start)

                    for df in defy_set:
                        teams[str(defs.loc[[df]]['team_global'].item())] -= 1

                for gk in gk_set:
                    teams[str(gks.loc[[gk]]['team_global'].item())] -= 1
                
                

        
    except TimeoutError:
        print(f"Timed out after {seconds}")
    finally:
        signal.alarm(0)

    print(f'calculating best team for round {round}')
    temp_best = best_team
    starting_11 = {}
    starting_11['gk'] = temp_best['gks'][0]
    starting_11['defs'] = temp_best['defs'][:3]
    starting_11['mids'] = temp_best['mids'][:2]
    starting_11['fwds'] = temp_best['fwds'][0]

    remainder = pd.concat([defs.loc[list(temp_best['defs'][3:])], mids.loc[list(temp_best['mids'][2:])], fwds.loc[list(temp_best['fwds'][1:])]])

    max_points = 0


    for setty in combinations(remainder.index, 4):
        points = sum(remainder.loc[list(setty)]['predictions'])
        if points > max_points:
            players = setty

    
    starters = []
    for i in list(starting_11.values()):

        if type(i) == int:
            starters.append(i)
        else:
            starters = starters + (list(i))

    starters = starters + list(players)
    subs = [temp_best['gks'][1]]

    for i in remainder.index:
        if i not in starters:
            subs.append(i)



    id_pred = zip(starters, [to_keep.loc[x]['predictions'] for x in starters])
    id_pred = sorted(id_pred, key = lambda x: x[1])

    captain_pred_id = [0][0]
    vice_pred_id = id_pred[1][0]


    position_counter = {'1': 0, '2': 0, '3': 0}
    min_position = {'1': 3, '2': 2, '3': 1}


    for i in starters:
        position = final_data.loc[i]['element_type']
        position_counter[str(position)] += 1


    for i in range(len(starters)): 
        row = final_data.loc[starters[i]]

        if row['minutes'] == 0:     
            element_type = row['element_type']

            if (element_type == 0) and (final_data.loc[subs[0]]['minutes'] != 0):
                starters[0] = subs[0]

            elif element_type != 0:
                for j in subs[1:]:

                    sub_element_type = final_data.loc[j]['element_type']

                    if final_data.loc[j]['minutes'] != 0:
                        
                        position_counter[str(element_type)] -= 1
                        position_counter[str(sub_element_type)] += 1

                        switch = True

                        for x, y in zip(position_counter.values(), min_position.values()):
                            if x < y:
                                switch = False

                        if switch == True:
                            starters[i] = j
                            break

                        else:
                            position_counter[str(element_type)] += 1
                            position_counter[str(sub_element_type)] -= 1
                                                                        

    points = 0

    for i in starters:

        row = to_keep.loc[i]
        points += row['target']

    captain_row = to_keep.loc[captain_pred_id]
    vice_row = to_keep.loc[vice_pred_id]

    if captain_row['minutes'] == 0:
        points += vice_row['target']
    else:
        points += captain_row['target']
    
    
    base_url = 'https://fantasy.premierleague.com/api/' 
    r = requests.get(base_url+'bootstrap-static/').json() 
    r = r['events'][round]['highest_score']

    starters_names = {}
    subs_names = {}

    for i in starters:
        name = to_keep.loc[i]['first_name'] + ' ' + to_keep.loc[i]['second_name']
        starters_names[name] = {'index': i, 'points': to_keep.loc[i]['target'], 'mins': to_keep.loc[i]['minutes'] }

    bench_score = 0

    for i in subs:
        name = to_keep.loc[i]['first_name'] + ' ' +  to_keep.loc[i]['second_name']
        sub_points = to_keep.loc[i]['target']
        subs_names[name] = {'index': i, 'points': sub_points}
        bench_score += sub_points

    output_dic = {}
    output_dic['round'] = round
    output_dic['starters'] = starters_names
    output_dic['subs'] = subs_names
    output_dic['best_team'] = best_team
    output_dic['points'] = points
    output_dic['top_score'] = r
    output_dic['bench_points'] = bench_score
    output_dic['captain'] = {'name': captain_row['second_name'], 'points': captain_row['target'], 'minutes': captain_row['minutes']}
    output_dic['vice_captain'] = {'name': vice_row['second_name'], 'points': vice_row['target'], 'minutes': vice_row['minutes']}
    return output_dic

    
            
                


    

