from flask_restful import Resource, reqparse

from .constants import log_base_dir, selected_people_classes
from .file_api import Loader, getMap
from anytree import Node
from anytree.exporter import JsonExporter
import os
import pandas as pd
import numpy as np
import re


class InfectionTreeHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']

        files = [os.path.split(x)[-1] for x in os.listdir(log_base_dir.joinpath(request_dir))]
        person_infos = []
        for f in files:
            if 'person_info' in f:
                person_infos.append(f)
        person_infos.sort()
        ids = []
        classes = []
        parents = []
        parents_class = []
        infected_loc = []
        infected_loc_class = []
        infect_time = []
        for pi in person_infos:
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
        return {
            'resultStatus': 'SUCCESS',
            'data': df.to_csv(),
            'json': json_tree
        }


# CONTACTS HANDLERS
class ContactHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('group_by', type=str)
        args = parser.parse_args()
        request_dir = args['dir']
        request_group = args['group_by']

        files = [os.path.split(x)[-1] for x in os.listdir(log_base_dir.joinpath(request_dir))]
        day_info = []
        for f in files:
            if re.search("[0-9]{5}.csv", f) is not None:
                day_info.append(f)
        day_info.sort()

        df_p = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_person_info')
        df_p = df_p.set_index('person')
        df_l = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_location_info')

        def pID2requesetGroupMap(ID):
            # map from ID of the person to requested group
            if request_group == 'age':
                gap = 5
                age = int((df_p.loc[ID, request_group] // gap) * gap)
                return str(age) + "-" + str(age + gap)
            if request_group == 'person':
                return ID
            return df_p.loc[ID, request_group]

        group_names = df_p.index.map(pID2requesetGroupMap).unique()
        con_df = pd.DataFrame(index=group_names, columns=group_names).fillna('')
        count_df = pd.DataFrame(index=group_names, columns=['count']).fillna(0)

        for pi in day_info:
            print(f'Processing day {pi}')
            df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '_contact_info')
            df = df.loc[df['n_contacts'] > 0]
            df['contacts'] = df['contacts'].map(lambda x: list(map(int, map(float, str(x).split(' ')))))
            day_con_df = pd.DataFrame(index=group_names, columns=group_names).fillna(0)

            for idx, row in df[['person', 'contacts', 'n_contacts']].iterrows():
                pid, contacts = row['person'], pd.Series(row['contacts'])
                contacts = contacts.map(pID2requesetGroupMap)
                counts = contacts.value_counts()
                for group_name in counts.index:
                    day_con_df.loc[pID2requesetGroupMap(pid), group_name] += counts[group_name]
            for group_name1 in group_names:
                for group_name2 in group_names:
                    con_df.loc[group_name1, group_name2] += ' ' + str(day_con_df.loc[group_name1, group_name2])
        df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_person_info')
        for pid in df['person']:
            count_df.loc[pID2requesetGroupMap(pid), 'count'] += 1
        m = getMap(request_group, request_dir)
        if m is None:
            m = {i: i for i in con_df.index}

        con_df = con_df.rename(columns={i: m[i] for i in con_df.index})
        con_df.index = [m[i] for i in con_df.index]
        count_df.index = [m[i] for i in count_df.index]

        con_df = con_df.sort_index()
        con_df = con_df.reindex(sorted(con_df.columns), axis=1)
        count_df = count_df.sort_index()
        print(con_df)
        print(count_df)
        return {'status': 'SUCCESS',
                'contacts': con_df.to_csv(index=False),
                'count': count_df.to_csv(index=False)
                }


class LocationContactHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']

        files = [os.path.split(x)[-1] for x in os.listdir(log_base_dir.joinpath(request_dir))]
        day_info = []
        for f in files:
            if re.search("[0-9]{5}.csv", f) is not None:
                day_info.append(f)
        day_info.sort()

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
                ['n_contacts', 'contacts']]
            df = pd.concat([df, dfc], axis=1)

            df = df.loc[df['n_contacts'] > 0]
            df['contacts'] = df['contacts'].map(lambda x: list(map(int, map(float, str(x).split(' ')))))

            for idx, row in df[
                ['person', 'contacts', 'n_contacts', 'current_location_id', 'current_location_class']].iterrows():
                lid, contacts = row['current_location_id'], list(row['contacts'])
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
        args = parser.parse_args()
        request_dir = args['dir']

        files = [os.path.split(x)[-1] for x in os.listdir(log_base_dir.joinpath(request_dir))]
        day_info = []
        for f in files:
            if re.search("[0-9]{5}.csv", f) is not None:
                day_info.append(f)
        day_info.sort()

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
                ['n_contacts', 'contacts']]
            df = pd.concat([df, dfc], axis=1)

            df = df.loc[df['n_contacts'] > 0]
            df['contacts'] = df['contacts'].map(lambda x: list(map(int, map(float, str(x).split(' ')))))

            for idx, row in df[
                ['person', 'contacts', 'n_contacts', 'current_location_id', 'current_location_class']].iterrows():
                pid, contacts = row['person'], list(row['contacts'])
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

        files = [os.path.split(x)[-1] for x in os.listdir(log_base_dir.joinpath(request_dir))]
        day_info = []
        for f in files:
            if re.search("[0-9]{5}.csv", f) is not None:
                day_info.append(f)
        day_info.sort()

        df_p = Loader.getFile(request_dir, int(re.search("[0-9]{5}", day_info[0]).group()), '_person_info')
        df_p = df_p.set_index('person')
        to_check_people = [True for _ in range(len(df_p.index))]

        def pID2requesetGroupMap(ID):
            # map from ID of the person to requested group
            if request_group == 'age':
                gap = 5
                age = int((df_p.loc[ID, request_group] // gap) * gap)
                return str(age) + "-" + str(age + gap)
            if request_group == 'person':
                return ID
            return df_p.loc[ID, request_group]

        group_names = df_p.index.map(pID2requesetGroupMap).unique()
        inf_df = pd.DataFrame(index=group_names, columns=group_names).fillna('')
        count_df = pd.DataFrame(index=group_names, columns=['infected', 'total_count', 'total_infected']).fillna('')
        count_df['total_count'] = [0]*len(group_names)

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
            count_df.loc[group_name1, 'total_infected'] = sum(map(int,count_df.loc[group_name1, 'infected'].split()))
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
