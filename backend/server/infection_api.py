import json
import matplotlib
matplotlib.use('Agg')
from flask_restful import Resource, reqparse
import matplotlib.pyplot as plt
from .constants import log_base_dir, selected_people_classes
from .file_api import Loader, getMap, getArgs
from anytree import Node
from anytree.exporter import JsonExporter
import os
import pandas as pd
import numpy as np
import re
import seaborn as sns


# CONTACTS HANDLERS
class ContactHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('group_by1', type=str)
        parser.add_argument('group_by2', type=str)
        parser.add_argument('start_day', type=str)
        parser.add_argument('end_day', type=str)
        args = parser.parse_args()
        request_dir = args['dir']
        request_start_day = int(args['start_day'])
        request_end_day = int(args['end_day'])

        contact1_group = args['group_by1']
        contact2_group = args['group_by2']

        # filter requested days
        day_info = Loader.get_day_file_names_sorted(request_dir)
        day_info = [x for x in day_info if
                    request_start_day <= int(re.search("[0-9]{5}", x).group()) <= request_end_day]

        # load person and location info
        df_p = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_person_info')
        df_p = df_p.set_index('person')
        df_l = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_location_info')
        df_l = df_l.set_index('id')

        def loadContactDfOnDay(day):
            _df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day).group()), '')
            _df = _df[['person', 'time', 'current_location_id', 'current_location_class']]
            _dfc = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day).group()), '_contact_info')
            _dfc = _dfc[['n_contacts', 'contacts']]
            _df = pd.concat([_df, _dfc], axis=1)
            return _df

        df = loadContactDfOnDay(day_info[0])

        def getMapFunction(g, _df):
            def f_age(x):
                gap = 5
                age = int((df_p.loc[x, 'age'] // gap) * gap)
                return str(age) + "-" + str(age + gap)

            if g == 'age':
                return f_age
            if g == 'person':
                return lambda x: x
            if g in df_p.columns:
                return lambda x: df_p.loc[x, g]
            if g in _df.columns:
                return lambda x: _df.loc[x, g]  # df err

        def getAllPossibleValues(g):
            if 'loc_class' in g or 'location_class' in g:
                return df_l['class'].unique()
            if 'loc_id' in g or 'location_id' in g:
                return df_l['id'].unique()
            return df_p.index.map(getMapFunction(g, df)).unique()

        contact1_group_names = getAllPossibleValues(contact1_group)
        contact2_group_names = getAllPossibleValues(contact2_group)
        con_df = pd.DataFrame(index=contact1_group_names, columns=contact2_group_names).fillna('')
        count_df = pd.DataFrame(index=contact1_group_names, columns=['count']).fillna(0)

        for pi in day_info:
            df = loadContactDfOnDay(pi)
            df: pd.DataFrame = df.loc[df['n_contacts'] > 0]
            df['contacts'] = df['contacts'].map(lambda x: list(map(int, map(float, str(x).split(' ')))))

            day_con_df = pd.DataFrame(index=contact1_group_names, columns=contact2_group_names).fillna(0)

            # print(df)
            dfg = df.groupby('time')
            for t in dfg.groups:
                _df = dfg.get_group(t)
                _df = _df.set_index('person')
                contact1_group_mapper = getMapFunction(contact1_group, _df)
                contact2_group_mapper = getMapFunction(contact2_group, _df)
                print(f'\r {pi} {t}', end='')
                for pid, row in _df.iterrows():
                    contacts = row['contacts']
                    for i in range(len(contacts)):
                        contacts[i] = contact2_group_mapper(contacts[i])
                    counts = pd.Series(contacts).value_counts()
                    for group_name in counts.index:
                        day_con_df.loc[contact1_group_mapper(pid), group_name] += counts[group_name]
            for group_name1 in contact1_group_names:
                for group_name2 in contact2_group_names:
                    con_df.loc[group_name1, group_name2] += ' ' + str(day_con_df.loc[group_name1, group_name2])

        # df = loadContactDfOnDay(day_info[0])
        # contact1_group_mapper = getMapFunction(contact1_group, df)
        # for pid in df_p.index:
        #     count_df.loc[contact1_group_mapper(pid), 'count'] += 1

        m1 = getMap(contact1_group, request_dir)
        m2 = getMap(contact2_group, request_dir)
        if m1 is None:
            m1 = {i: i for i in con_df.index}
        if m2 is None:
            m2 = {i: i for i in con_df.columns}

        con_df = con_df.rename(columns={i: m2[i] for i in con_df.columns})
        con_df.index = [m1[i] for i in con_df.index]
        count_df.index = [m1[i] for i in count_df.index]

        con_df = con_df.sort_index()
        con_df = con_df.reindex(sorted(con_df.columns), axis=1)
        count_df = count_df.sort_index()
        print(con_df)
        print(count_df)
        return {'status': 'SUCCESS',
                'contacts': con_df.to_csv(index=False),
                'count': count_df.to_csv(index=False),
                'index': list(con_df.index)
                }


class LocationContactHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('start_day', type=str)
        parser.add_argument('end_day', type=str)
        args = parser.parse_args()
        request_dir = args['dir']
        request_start_day = int(args['start_day'])
        request_end_day = int(args['end_day'])

        day_info = Loader.get_day_file_names_sorted(request_dir)
        day_info = [x for x in day_info if
                    request_start_day <= int(re.search("[0-9]{5}", x).group()) <= request_end_day]

        df_p = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_person_info')
        df_l = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_location_info')

        con_df = pd.DataFrame({'location': df_l['id'], 'contacts': [[0] for _ in range(len(df_l))]})
        con_df = con_df.set_index('location')
        df_l = df_l.set_index('id')

        for pi in day_info:
            print("Processing", pi)
            df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '')
            df = df[['person', 'current_location_id', 'current_location_class']]
            dfc = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '_contact_info')[
                ['n_contacts']]
            df = pd.concat([df, dfc], axis=1)

            df = df.loc[df['n_contacts'] > 0]

            for idx, row in df[['person', 'n_contacts', 'current_location_id']].iterrows():
                lid = row['current_location_id']
                con_df.loc[lid, 'contacts'][-1] += row['n_contacts']
            for lid in df_l.index:
                con_df.loc[lid, 'contacts'].append(0)

        con_df['request_group'] = con_df.index.map(lambda x: df_l.loc[x, 'class'])
        # con_df['contacts'] = con_df['contacts'].map(lambda x: [pID2requesetGroupMap(i) for i in x])
        # print(con_df)

        gr = con_df.groupby('request_group')
        # print(gr.groups)

        group_names = list(gr.groups.keys())

        gr_df = pd.DataFrame({'group_names': group_names,
                              'contacts': ['' for _ in range(len(group_names))],
                              'daily_total': ['' for _ in range(len(group_names))]
                              })
        gr_df = gr_df.set_index('group_names')
        # print(gr_df)
        for g in gr.groups.keys():
            for lis in gr.get_group(g)['contacts']:
                gr_df.loc[g, 'contacts'] += ' ' + ' '.join(map(str, lis))
            tot = []
            for lis in gr.get_group(g)['contacts']:
                tot.append(lis)
            gr_df.loc[g, 'daily_total'] = ' '.join(map(str, np.sum(tot, axis=0)))
        m = getMap('location_class', request_dir)
        if m is None:
            m = {i: i for i in gr_df.index}
        gr_df.index = [m[i] for i in gr_df.index]
        gr_df.index.name = 'location_class'
        print(gr_df)

        return {'status': 'SUCCESS',
                'contacts': gr_df.to_csv(index=True),
                }


class PersonContactHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('start_day', type=str)
        parser.add_argument('end_day', type=str)
        args = parser.parse_args()
        request_dir = args['dir']
        request_start_day = int(args['start_day'])
        request_end_day = int(args['end_day'])

        day_info = Loader.get_day_file_names_sorted(request_dir)
        day_info = [x for x in day_info if
                    request_start_day <= int(re.search("[0-9]{5}", x).group()) <= request_end_day]

        df_p = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_person_info')
        df_l = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_location_info')

        con_df = pd.DataFrame({'person': df_p['person'], 'contacts': [[0] for _ in range(len(df_p))]})
        con_df = con_df.set_index('person')
        df_p = df_p.set_index('person')

        for pi in day_info:
            print("Processing", pi)
            df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '')
            df = df[['person', 'current_location_id', 'current_location_class']]
            dfc = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '_contact_info')[
                ['n_contacts']]
            df = pd.concat([df, dfc], axis=1)

            df = df.loc[df['n_contacts'] > 0]

            for idx, row in df[
                ['person', 'n_contacts', ]].iterrows():
                pid = row['person']
                con_df.loc[pid, 'contacts'][-1] += row['n_contacts']
            for pid in df_p.index:
                con_df.loc[pid, 'contacts'].append(0)

        con_df['request_group'] = con_df.index.map(lambda x: df_p.loc[x, 'person_class'])
        # con_df['contacts'] = con_df['contacts'].map(lambda x: [pID2requesetGroupMap(i) for i in x])
        print(con_df)

        gr = con_df.groupby('request_group')
        print(gr.groups)

        group_names = list(gr.groups.keys())

        gr_df = pd.DataFrame({'group_names': group_names,
                              'contacts': ['' for _ in range(len(group_names))],
                              'daily_total': ['' for _ in range(len(group_names))]
                              })
        gr_df = gr_df.set_index('group_names')
        print(gr_df)
        for g in gr.groups.keys():
            for lis in gr.get_group(g)['contacts']:
                gr_df.loc[g, 'contacts'] += ' ' + ' '.join(map(str, lis))
            tot = []
            for lis in gr.get_group(g)['contacts']:
                tot.append(lis)
            gr_df.loc[g, 'daily_total'] = ' '.join(map(str, np.sum(tot, axis=0)))

        m = getMap('person_class', request_dir)
        if m is None:
            m = {i: i for i in gr_df.index}
        gr_df.index = [m[i] for i in gr_df.index]
        gr_df.index.name = 'person_class'
        print(gr_df)

        return {'status': 'SUCCESS',
                'contacts': gr_df.to_csv(index=True),
                }


# INFECTIONS HANDLERS
class InfectionHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('group_by', type=str)
        args = parser.parse_args()
        request_dir = args['dir']
        request_group = args['group_by']

        day_info = Loader.get_day_file_names_sorted(request_dir)

        df_p = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_person_info')
        df_p = df_p.set_index('person')
        to_check_people = [True for _ in range(len(df_p.index))]

        def pID2requesetGroupMap(ID):
            # map from ID of the person to requested group
            if request_group == 'age':
                gap = 5
                age = int((df_p.loc[ID, request_group] // gap) * gap)
                return f"{age:02d} - {age + gap:02d}"
            if request_group == 'person':
                return ID
            return df_p.loc[ID, request_group]

        group_names = df_p.index.map(pID2requesetGroupMap).unique()
        inf_df = pd.DataFrame(index=group_names, columns=group_names).fillna('')
        count_df = pd.DataFrame(index=group_names, columns=['infected', 'total_count', 'total_infected']).fillna('')
        count_df['total_count'] = [0] * len(group_names)

        for p_id in df_p.index:
            _r = pID2requesetGroupMap(p_id)
            count_df.loc[_r, 'total_count'] += 1

        for pi in day_info:
            print(f'Processing day {pi}')
            df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '_person_info')
            # df = df.loc[df['infected_time'] > 0]
            df = df.loc[to_check_people]
            day_con_df = pd.DataFrame(index=group_names, columns=group_names).fillna(0)
            day_count_df = pd.DataFrame(index=group_names, columns=['infected']).fillna(0)
            for idx, row in df[['person', 'state', 'disease_state', 'infected_source_id',
                                'infected_loc_class', 'infected_loc_id']].iterrows():
                if row['state'] > 1:  # infected person
                    p_id = int(row['person'])
                    s_id = int(row['infected_source_id'])
                    if s_id < 0:
                        s_id = p_id
                    _r = pID2requesetGroupMap(p_id)
                    _s = pID2requesetGroupMap(s_id)
                    day_con_df.loc[_s, _r] += 1
                    day_count_df.loc[_s, 'infected'] += 1
                    to_check_people[p_id] = False
            for group_name1 in group_names:
                count_df.loc[group_name1, 'infected'] += ' ' + str(day_count_df.loc[group_name1, 'infected'])
                for group_name2 in group_names:
                    inf_df.loc[group_name1, group_name2] += ' ' + str(day_con_df.loc[group_name1, group_name2])
        for group_name1 in group_names:
            count_df.loc[group_name1, 'total_infected'] = sum(map(int, count_df.loc[group_name1, 'infected'].split()))
        m = getMap(request_group, request_dir)
        if m is None:
            m = {i: i for i in inf_df.index}

        inf_df = inf_df.rename(columns={i: m[i] for i in inf_df.index})
        inf_df.index = [m[i] for i in inf_df.index]
        inf_df = inf_df.sort_index()
        inf_df = inf_df.reindex(sorted(inf_df.columns), axis=1)
        print(inf_df)

        count_df.index = [m[i] for i in count_df.index]
        count_df = count_df.sort_index()
        count_df = count_df.reindex(sorted(count_df.columns), axis=1)
        return {'status': 'SUCCESS',
                'infections': inf_df.to_csv(index=False),
                'count': count_df.to_csv(index=False)
                }


class PeopleStateTimelineHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('parameters', type=str)
        parser.add_argument('end_only', type=bool, default=True)
        parser.add_argument('window', type=int, default=3)
        parser.add_argument('group_curves', type=bool, default=False)
        parser.add_argument('plot_checkp', type=bool, default=False)
        args = parser.parse_args()
        request_dirs = args['dir'].split('#')
        request_params = args['parameters'].split('#')
        if "" in request_params:
            request_params.remove("")
        request_end = args['end_only']
        request_window = args['window']
        request_group_curves = args['group_curves']
        request_plot_checkp = args['plot_checkp']

        final_df = None
        for req_dir in request_dirs:
            day_info = Loader.get_day_file_names_sorted(req_dir)

            df_arr = []
            for day in day_info:
                df_day = Loader.getFile(req_dir, int(re.search("[0-9]{5}", day).group()), '_cov_info')
                if request_end:
                    df_day = df_day.iloc[-1:]
                df_arr.append(df_day)
            df = pd.concat(df_arr)

            tot_cases = df["TOTAL INFECTED CASES"].values
            ratio = tot_cases[request_window:] / tot_cases[:-request_window]
            growth_rate = np.log(np.append(np.zeros(request_window), ratio)) / request_window
            df["D.T."] = np.log(2) / growth_rate
            df["ratio"] = np.append(1 / np.zeros(request_window), ratio)
            df["Re1"] = np.append(1 / np.zeros(request_window), ratio - 1)
            if len(tot_cases) > 10:
                df["Re2"] = np.append(1 / np.zeros(2), (tot_cases[2:] / tot_cases[:-2]) - 1)

            df["NEW IDENTIFIED INFECTED"] = df["IDENTIFIED INFECTED"].diff()
            df["time"] /= 1440
            df["Type"] = req_dir

            if final_df is None:
                final_df = df
            else:
                final_df = pd.concat([final_df, df])

        # final_df = final_df.set_index('time')
        cols = list(final_df.columns)
        cols.remove("time")
        cols.remove("Type")
        if len(request_params) == 0:
            request_params = cols
        newdf = pd.DataFrame(columns=["Time", "Parameter", "Value", "Simulation"])
        for col in request_params:
            newdf = pd.concat([newdf, pd.DataFrame({
                "Time": final_df["time"].values,
                "Parameter": [col] * len(final_df),
                "Value": final_df[col].values,
                "Simulation": final_df["Type"].values})])
        newdf.reset_index(inplace=True)
        if request_group_curves:
            newdf["Simulation"] = newdf["Simulation"].apply(lambda x: x[:-19])
        xlim = newdf["Time"].max()
        # xlim=40
        newdf = newdf.loc[newdf["Time"] <= xlim]
        print(newdf)

        # plot using sns
        request_subplots = True
        plt.cla()
        plt.figure()
        dash_list = sns._core.unique_dashes(newdf["Simulation"].unique().size)
        style = {key: value for key, value in zip(newdf["Simulation"].unique(), dash_list)}
        lines = {}
        text_y_r = 2
        text_y = newdf["Value"][newdf["Value"] != np.inf].max() / text_y_r
        for i, req_dir in enumerate(request_dirs):
            dir_args = getArgs(req_dir)
            if request_group_curves:
                req_dir = req_dir[:-19]
            addedContainmentEvents = json.loads(dir_args["addedContainmentEvents"])
            addedGatheringEvents = json.loads(dir_args["addedGatheringEvents"])
            addedVaccinationEvents = json.loads(dir_args["addedVaccinationEvents"])
            print(addedContainmentEvents, addedGatheringEvents, addedVaccinationEvents)

            for ce in addedContainmentEvents.values():
                x = int(ce['startday'])
                if x in lines.keys():
                    if req_dir in lines[x].keys():
                        lines[x][req_dir].append(ce['containment_strategy'])
                    else:
                        lines[x][req_dir] = [ce['containment_strategy']]
                else:
                    lines[x] = {req_dir: [ce['containment_strategy']]}

            gatherings = []
            for ce in addedGatheringEvents.values():
                gatherings.append(int(ce['day']))
            for x in pd.unique(gatherings):
                if x in lines.keys():
                    if req_dir in lines[x].keys():
                        lines[x][req_dir].append(str(gatherings.count(x)) + " gatherings")
                    else:
                        lines[x][req_dir] = [str(gatherings.count(x)) + " gatherings"]
                else:
                    lines[x] = {req_dir: [str(gatherings.count(x)) + " gatherings"]}

            for ce in addedVaccinationEvents.values():
                x = int(ce['day'])
                if x in lines.keys():
                    if req_dir in lines[x].keys():
                        lines[x][req_dir].append(
                            "Vaccine for age " + str(ce["min_age"]) + " to " + str(ce["max_age"]))
                    else:
                        lines[x][req_dir] = ["Vaccine for age " + str(ce["min_age"]) + " to " + str(ce["max_age"])]
                else:
                    lines[x] = {req_dir: ["Vaccine for age " + str(ce["min_age"]) + " to " + str(ce["max_age"])]}

        def plot_checkpoints(ax):
            if not request_plot_checkp:
                return
            for day in lines.keys():
                x = day  # + i/len(request_dirs)
                if x == 0:
                    continue
                text = []
                for req_dir in lines[x].keys():
                    ax.axvline(x=x, color='black', linestyle=(0, style[req_dir]))
                    text += lines[x][req_dir]
                text = ",".join(pd.unique(text))
                ax.text(x - 2, text_y, text,
                        bbox={'facecolor': 'white', 'alpha': 0, 'edgecolor': 'none', 'pad': 1},
                        ha='center', va='center', rotation=90)

        prefix = "Number of "
        # prefix = "Reproduction number "
        if len(request_params) == 1:
            sns.lineplot(data=newdf, x="Time", y="Value", dashes=style, hue="Simulation")
            plt.ylabel(prefix + request_params[0].lower())
        elif len(newdf["Simulation"].unique()) == 1:
            sns.lineplot(data=newdf, x="Time", y="Value", dashes=style, hue="Parameter")
            plt.ylabel("Number of people")
        elif request_subplots:
            hr = [1] * len(request_params)
            # hr[0]=2
            fig, axs = plt.subplots(len(request_params), 1,
                                    figsize=(6.4, 4.8 * len(request_params) / (sum(hr) / len(request_params))),
                                    gridspec_kw={'height_ratios': hr},
                                    constrained_layout=True)
            for i, param in enumerate(request_params):
                subdf = newdf.loc[newdf["Parameter"] == param]
                text_y = subdf["Value"][subdf["Value"] != np.inf].max() / text_y_r
                sns.lineplot(data=subdf, x="Time", y="Value", hue="Simulation", ax=axs[i])
                axs[i].set_ylabel(prefix + (param.split("_")[0] if '_' in param else param).lower())
                axs[i].set_xlabel("")
                axs[i].set_xlim(0, xlim)
                plot_checkpoints(axs[i])
        else:
            sns.lineplot(data=newdf, x="Time", y="Value", style="Simulation", dashes=style, hue="Parameter")
            plt.ylabel("Number of people")
        plt.xlim(0, xlim)
        plot_checkpoints(plt.gca())
        plt.xlabel("Time (days)")

        plt.tight_layout()
        # plt.legend().set_draggable(True)
        plt.savefig(log_base_dir.joinpath(f"timeline.png"))
        plt.savefig(log_base_dir.joinpath(f"timeline.svg"))

        plt.figure()
        p_hist = pd.read_csv(log_base_dir.joinpath(request_dirs[0]).joinpath(f"p_hist.csv"))
        print(p_hist)
        new_p_hist_df = pd.DataFrame(columns=["Type", "Prob"])
        for col in p_hist.columns:
            new_p_hist_df = pd.concat([new_p_hist_df,
                                       pd.DataFrame({"Type": [col] * len(p_hist), "Prob": p_hist[col].values})])
        new_p_hist_df.reset_index(inplace=True)
        sns.histplot(new_p_hist_df, x="Prob", hue="Type", bins=100, multiple="stack")
        plt.savefig(log_base_dir.joinpath(f"p_hist.png"))
        pd.DataFrame.to_csv(newdf, log_base_dir.joinpath("timeline.csv"), index=False)
        return {'status': 'SUCCESS',
                'data': final_df.to_csv(index=False),
                }


class InfectionStateTimelineHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']

        day_info = Loader.get_day_file_names_sorted(request_dir)

        df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_person_info')
        df_out = pd.DataFrame(index=df['person'], columns=range(len(day_info)))
        for pi in day_info:
            day = int(re.search("[0-9]{5}", pi).group())
            df = Loader.getFile(request_dir, day, '_person_info')
            # df = df.loc[df['state']>1]
            df.loc[df['state'] > 2, 'state'] += 6
            df.loc[df['state'] == 2, 'state'] += df.loc[df['state'] == 2, 'disease_state']
            df_out.loc[df['person'], day] = df['state']

        # plt.figure(figsize=(10,5))
        # plt.imshow(df_out.fillna(0).values, interpolation='nearest', aspect='auto')
        # plt.colorbar()
        # plt.show()
        print(df_out)
        return {"status": "success", "data": df_out.to_csv(index=False)}


class InfectionTreeHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']

        day_info = Loader.get_day_file_names_sorted(request_dir)
        ids = []
        classes = []
        parents = []
        parents_class = []
        infected_loc = []
        infected_loc_class = []
        infect_time = []
        for pi in day_info:
            df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '_person_info')

            # if selected_people_classes:
            #     df = df.loc[df.person_class.apply(lambda x: x in selected_people_classes)]
            if len(ids) == 0:
                ids = df.index
                classes = df['person_class'].values
                parents = df['infected_source_id'].values
                infect_time = df['infected_time'].values
                parents_class = df['infected_source_class'].values
                infected_loc = df['infected_loc_id'].values
                infected_loc_class = df['infected_loc_class'].values
            else:
                classes = np.maximum(classes, df['person_class'].values)
                parents = np.maximum(parents, df['infected_source_id'].values)
                infect_time = np.maximum(infect_time, df['infected_time'].values)
                parents_class = np.maximum(parents_class, df['infected_source_class'].values)
                infected_loc = np.maximum(infected_loc, df['infected_loc_id'].values)
                infected_loc_class = np.maximum(infected_loc_class, df['infected_loc_class'].values)

        df = pd.DataFrame({'id': ids, 'class': classes, 'parent': parents, 'time': infect_time,
                           'parents_class': parents_class, 'infected_loc': infected_loc,
                           'infected_loc_class': infected_loc_class})
        df = df.set_index('id')
        df = df.loc[df['parent'] != -1]
        df.loc[df.index == df['parent'], 'parent'] = ''
        print("Infection Tree\n", df)

        nodes_dict = {}

        parent_node = Node("ROOT")
        for idx, i in enumerate(ids):
            if i not in nodes_dict.keys():
                nodes_dict[i] = Node(i, attributes={'class_number': str(classes[idx]),
                                                    'infect_time': str(infect_time[idx]),
                                                    'infected_loc': str(infected_loc[idx]),
                                                    'infected_loc_class': str(infected_loc_class[idx])})
        for idx, p in enumerate(parents):
            if p not in nodes_dict.keys():
                nodes_dict[p] = Node(p, attributes={'class_number': str(classes[idx]),
                                                    'infect_time': str(infect_time[idx]),
                                                    'infected_loc': str(infected_loc[idx]),
                                                    'infected_loc_class': str(infected_loc_class[idx])})
        for i, p in zip(ids, parents):
            if i == p:
                nodes_dict[i].parent = parent_node
            else:
                nodes_dict[i].parent = nodes_dict[p]
        while parent_node.parent is not None:
            parent_node = parent_node.parent
        # print(RenderTree(parent_node))
        exporter = JsonExporter(indent=2, sort_keys=False)
        json_tree = exporter.export(parent_node)

        df_p = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_person_info')
        occ_class_count = df_p['person_class'].value_counts()

        inf_loc_class_count = df['infected_loc_class'].value_counts()
        inf_occ_class_count = df['parents_class'].value_counts() / occ_class_count
        inf_occ_class_count = inf_occ_class_count.dropna().rename("parents_class")
        print(inf_occ_class_count, inf_loc_class_count)
        self.values_ = {
            'resultStatus': 'SUCCESS',
            'data': df.to_csv(),  # keep index
            'json': json_tree,
            'inf_loc_count': inf_loc_class_count.to_csv(),
            'inf_occ_count': inf_occ_class_count.to_csv(),

        }
        return self.values_


# VARIANT HANDLERS
class VariantHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']

        day_info = Loader.get_day_file_names_sorted(request_dir)
        df_arr = []
        for day in day_info:
            df_p = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day).group()), '_person_info')
            df_p = df_p.loc[df_p["disease_variant"] != ""]
            count = df_p.groupby("disease_variant").agg(len)
            dic = {}
            for v, c in zip(count.index, count.values):
                dic[v] = c[0]
            df_arr.append(dic)
        df = pd.DataFrame(df_arr)

        df_norm = df.div(df.sum(axis=1), axis=0)
        print(df)
        # px.histogram()
        return {'status': 'SUCCESS',
                'df': df.to_csv(index=False),
                'df_norm': df_norm.to_csv(index=False),
                }


class ReprodutionNumberHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']
