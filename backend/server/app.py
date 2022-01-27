from flask import Flask, send_from_directory
from flask_restful import Api, Resource, reqparse, abort

from flask_cors import CORS  # comment this on deployment
import os
import pathlib
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter

app = Flask(__name__, static_url_path='', static_folder='frontend/build')
CORS(app)  # comment this on deployment
api = Api(app)

log_base_dir = pathlib.Path("../../app/src/data/")
selected_people_classes = []


def getMap(name, dir):
    if 'person_class' in name:
        return Loader.getPeopleList(dir)
    if 'location_class' in name:
        return Loader.getLocationList(dir)
    if 'movement_class' in name:
        return Loader.getMovementList(dir)


class Loader:

    @staticmethod
    def getFile(rdir, day, f_type):
        if rdir == '':
            abort(500)
        day = int(day)
        f_name = f"{day:05d}" + f_type + ".csv"
        return pd.read_csv(log_base_dir.joinpath(rdir).joinpath(f_name), low_memory=False)

    @staticmethod
    def getLocationList(rdir):
        f_name = "locs.txt"
        fh = open(log_base_dir.joinpath(rdir).joinpath(f_name), 'r')
        return fh.read().split('\n')

    @staticmethod
    def getPeopleList(rdir):
        f_name = "people.txt"
        print(log_base_dir.joinpath(rdir).joinpath(f_name))
        fh = open(log_base_dir.joinpath(rdir).joinpath(f_name), 'r')
        return fh.read().split('\n')

    @staticmethod
    def getMovementList(rdir):
        f_name = "movement.txt"
        fh = open(log_base_dir.joinpath(rdir).joinpath(f_name), 'r')
        return fh.read().split('\n')

    @staticmethod
    def getResourceLog(rdir):
        f_name = "resource_info.csv"
        return pd.read_csv(log_base_dir.joinpath(rdir).joinpath(f_name))


class LogListHandler(Resource):
    def get(self):
        fols = [os.path.split(x[0])[-1] for x in os.walk(log_base_dir)]
        return {
            'resultStatus': 'SUCCESS',
            'message': ",".join(map(str, fols[1:]))
        }


class PostTextFileHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('filename', type=str)

        args = parser.parse_args()

        request_dir = args['dir']
        request_fname = args['filename']
        if request_dir:
            filedir = log_base_dir.joinpath(request_dir).joinpath(request_fname)
        else:
            filedir = '-1'
        try:
            status = "Success"
            message = open(filedir, 'r').read()
        except Exception as e:
            status = "Error"
            message = str(e)
            print(e)

        final_ret = {"status": status, "data": message}

        return final_ret


class PostCSVasJSONHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('d', type=str)
        parser.add_argument('type', type=str)
        parser.add_argument('columns', type=str, default='')

        args = parser.parse_args()
        print(args)
        request_dir = args['dir']
        request_day = args['d']
        request_type = args['type']
        request_cols = args['columns']

        try:
            status = "Success"
            if request_type == "resource_log":
                df = Loader.getResourceLog(request_dir)
            else:
                df = Loader.getFile(request_dir, int(request_day), request_type)
            if len(request_cols) > 0:
                df = df[request_cols.split('|')]
            if 'person_class' in df.columns:
                if selected_people_classes:
                    df = df.loc[df.person_class.apply(lambda x: x in selected_people_classes)]
            # print(df)
            message = df.to_csv(index=False)
        except Exception as e:
            status = "Error"
            message = str(e)
            print(e)
            abort(500)

        final_ret = {"status": status, "data": message}

        return final_ret


class NDaysHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)

        args = parser.parse_args()

        request_dir = args['dir']
        files = [os.path.split(x)[-1] for x in os.listdir(log_base_dir.joinpath(request_dir))]

        days = 0
        for f in files:
            if 'person_info' in f.__str__():
                days += 1
        return {
            'resultStatus': 'SUCCESS',
            'message': str(days)
        }


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
        print(RenderTree(parent_node))
        exporter = JsonExporter(indent=2, sort_keys=False)
        json_tree = exporter.export(parent_node)
        return {
            'resultStatus': 'SUCCESS',
            'data': df.to_csv(),
            'json': json_tree
        }


class LocationTreeHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('day', type=str)
        args = parser.parse_args()
        print(args)
        request_dir = args['dir']
        request_selectedDay = args['day']

        df_loc = Loader.getFile(request_dir, request_selectedDay, '_location_info')
        df_time: pd.DataFrame = Loader.getFile(request_dir, request_selectedDay, '')[['current_location_id', 'time']]

        ids = list(map(str, df_loc['id'].values))
        parents = list(map(str, df_loc['parent_id'].values))
        loc_class = df_loc['class'].values
        counts = [[] for _ in range(len(ids))]
        # adding people count at each time
        df_time_grouped = df_time.groupby('time')
        for grp_key in df_time_grouped.groups.keys():
            print(grp_key)
            df_time_t = df_time_grouped.get_group(grp_key)
            count = df_time_t.groupby('current_location_id').count()
            for i in range(len(ids)):
                try:
                    counts[i].append(str(count.loc[int(ids[i])]['time']))
                except:
                    counts[i].append('0')

        df_loc = pd.DataFrame({'id': ids, 'parent': parents, 'class': loc_class, 'counts': counts})
        df_loc = df_loc.set_index('id')

        print("Location Tree\n", df_loc)

        nodes_dict = {}
        root = df_loc.loc[df_loc['parent'] == '-1']
        print(root)
        parent_node = Node(str(root.index[0]), attributes={'class': str(root['class'][0]), 'n': root['counts'][0]})
        for idx, i in enumerate(ids):
            if i not in nodes_dict.keys():
                nodes_dict[i] = Node(i, attributes={'parent': str(parents[idx]),
                                                    'class': str(loc_class[idx]), 'n': counts[idx]})
        for idx, p in enumerate(parents):
            if p not in nodes_dict.keys():
                nodes_dict[p] = Node(p, attributes={'parent': str(parents[idx]),
                                                    'class': str(loc_class[idx]), 'n': counts[idx]})
        for i, p in zip(ids, parents):
            if p == '-1':
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
            'data': df_loc.to_csv(),
            'json': json_tree,
            'timeLen': len(df_time_grouped.groups.keys())
        }


class PossibleGroupsHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']
        return {'status': 'SUCCESS',
                'data': ['person',
                         'person_class',
                         'age',
                         'gender',

                         ]
                }


class SetPeopleClassesHandler(Resource):
    def post(self):
        global selected_people_classes
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('classes', type=str)
        args = parser.parse_args()

        request_dir = args['dir']
        request_group = args['classes'].split(',')
        print(args)

        m = Loader.getPeopleList(request_dir)
        selected_people_classes = list(map(str, request_group))
        selected_people_classes = [m.index(v) for v in selected_people_classes]
        return {'status': 'SUCCESS'}


class PeoplePathHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('day', type=str)
        parser.add_argument('people', type=str)
        args = parser.parse_args()
        print(args)
        request_dir = args['dir']
        request_selectedDay = args['day']
        try:
            request_people = list(map(int, args['people'].split(',')))
            df = Loader.getFile(request_dir, int(request_selectedDay), '')

            df = df[["person", "time", "x", "y"]]
            df = df.loc[df.person.apply(lambda x: x in request_people)]
        except Exception as e:
            return
        print("Person Paths", df)
        return {'status': 'SUCCESS', 'data': df.to_csv()}


class LocationPeopleCountHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('day', type=str)
        parser.add_argument('time', type=str)
        args = parser.parse_args()
        print(args)
        request_dir = args['dir']
        request_selectedDay = args['day']
        request_time = args['time']

        try:
            df = Loader.getFile(request_dir, int(request_selectedDay), '')
            df = df[["person", "time", "current_location_id"]]
        except Exception as e:
            return
        locs = df['current_location_id'].unique()
        d = {}
        for l in locs:
            d[l] = np.zeros(1)
        df['time'] = df['time'] % 1440
        df = df.loc[df['time'] == int(request_time)]
        for loc in df['current_location_id']:
            d[loc][0] += 1
        df = pd.DataFrame(d)
        df.index.name = 'id'
        # df= df.reset_index()
        print("Person count", df)
        return {'status': 'SUCCESS', 'data': df.to_csv()}


class LocationPeopleCountSurfaceHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('day', type=str)
        parser.add_argument('time', type=str)
        args = parser.parse_args()
        print(args)
        request_dir = args['dir']
        request_selectedDay = args['day']
        request_time = args['time']

        try:
            df = Loader.getFile(request_dir, int(request_selectedDay), '')
            df = df[["person", "time", "current_location_id"]]
            df['time'] = df['time'] % 1440
            df = df.loc[df['time'] == int(request_time)]

        except Exception as e:
            return

        df_loc = Loader.getFile(request_dir, request_selectedDay, '_location_info')

        xmin = int(np.floor(min(df_loc['x'] - df_loc['radius'])))
        xmax = int(np.ceil(max(df_loc['x'] + df_loc['radius'])))

        ymin = int(np.floor(min(df_loc['y'] - df_loc['radius'])))
        ymax = int(np.ceil(max(df_loc['y'] + df_loc['radius'])))

        x = np.arange(xmin, xmax, 1)
        y = np.arange(ymin, ymax, 1)
        d = {}

        for _y in y:
            d[int(_y)] = np.zeros(len(x))
        for _loc in df['current_location_id']:
            loc_x = int(np.round(df_loc.loc[_loc, 'x']))
            loc_y = int(np.round(df_loc.loc[_loc, 'y']))
            d[loc_y][loc_x - xmin] += 1

        df = pd.DataFrame(d)
        # plt.imshow(df.to_numpy())
        # plt.colorbar()
        # plt.show()

        df['x'] = x
        df['y'] = y
        # df = df.set_index('x')
        # df= df.reset_index()
        print("Person count", df)
        return {'status': 'SUCCESS', 'data': df.to_csv(index=False)}


class ActualLocationHistHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('day', type=str)
        parser.add_argument('groupBy', type=str)
        args = parser.parse_args()
        print(args)
        request_dir = args['dir']
        request_selectedDay = args['day']
        request_groupBy = args['groupBy']

        try:
            df = Loader.getFile(request_dir, int(request_selectedDay), '')
            df = df[[request_groupBy, "time"]]
            df_gr = df.groupby(request_groupBy)
            if int(request_selectedDay) == 0:
                df_prev = None
            else:
                df_prev = Loader.getFile(request_dir, int(request_selectedDay) - 1, '')
                df_prev = df_prev[[request_groupBy, "time"]]
                df_prev_gr = df_prev.groupby(request_groupBy)
        except Exception as e:
            abort(500)
            return

        start_t = df['time'].min() % 1440

        m = getMap(request_groupBy, request_dir)

        arr = {'group': [], 'time': []}
        for key in df_gr.groups.keys():
            arr['group'].append(key if m is None else m[key])
            freq = np.zeros(1440)
            for t_rec in df_gr.get_group(key)['time'].values:
                if t_rec % 1440 < start_t:
                    continue
                freq[t_rec % 1440] += 1
            if df_prev is not None:
                if key in df_prev_gr.groups.keys():

                    for t_rec in df_prev_gr.get_group(key)['time'].values:
                        if t_rec % 1440 >= start_t:
                            continue
                        freq[t_rec % 1440] += 1
            arr['time'].append('|'.join([str(int(e)) for e in freq]))

        result = pd.DataFrame(arr)
        print(result)
        return {'status': 'SUCCESS', 'data': result.to_csv()}


class RouteLocationHistHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('day', type=str)
        args = parser.parse_args()
        print(args)
        request_dir = args['dir']
        request_selectedDay = args['day']

        try:
            df = Loader.getFile(request_dir, int(request_selectedDay), '_person_info')
        except Exception as e:
            abort(500)
        df = df[["person", "route"]]
        df["route"] = df["route"].map(lambda x: x.split(" "))
        m = getMap('location_class', request_dir)
        arr = {'group': m, 'time': [np.zeros(1440) for _ in range(len(m))]}

        for p_route in df["route"]:
            for t, loc_class in enumerate(p_route):
                loc_class = int(loc_class)
                for _t in range(t * 5, t * 5 + 5):
                    arr['time'][loc_class][_t] += 1
        for i in range(len(arr['time'])):
            arr['time'][i] = '|'.join([str(int(e)) for e in arr['time'][i]])
        result = pd.DataFrame(arr)
        print(result)
        return {'status': 'SUCCESS', 'data': result.to_csv()}


class LocationShapes(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('day', type=str)
        args = parser.parse_args()
        request_dir = args['dir']
        request_day = args['day']

        df = Loader.getFile(request_dir, request_day, "_location_info")
        df = df[['class', 'x', 'y', 'radius', 'name', 'id']]

        print(df)
        return {'status': 'SUCCESS',
                'data': df.to_csv()}


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

        df_p = Loader.getFile(request_dir, 0, '_person_info')
        df_p = df_p.set_index('person')
        df_l = Loader.getFile(request_dir, 0, '_location_info')

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
            df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '')
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
        df = Loader.getFile(request_dir, 0, '_person_info')
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

        df_p = Loader.getFile(request_dir, 0, '_person_info')
        df_l = Loader.getFile(request_dir, 0, '_location_info')

        con_df = pd.DataFrame({'location': df_l['id'], 'contacts': [[0] for _ in range(len(df_l))]})
        con_df = con_df.set_index('location')
        df_l = df_l.set_index('id')

        for pi in day_info:
            df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '')
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

        df_p = Loader.getFile(request_dir, 0, '_person_info')
        df_l = Loader.getFile(request_dir, 0, '_location_info')

        con_df = pd.DataFrame({'person': df_p['person'], 'contacts': [[0] for _ in range(len(df_p))]})
        con_df = con_df.set_index('person')
        df_p = df_p.set_index('person')

        for pi in day_info:
            df = Loader.getFile(request_dir, int(re.search("[0-9]{5}", pi).group()), '')
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

        df_p = Loader.getFile(request_dir, 0, '_person_info')
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
        count_df = pd.DataFrame(index=group_names, columns=['infected']).fillna('')

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
                    p_id = row['person']
                    s_id = row['infected_source_id']
                    if s_id == -1:
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


# R0 curve

# Performance Handlers
class PerformanceHandler(Resource):
    def post(self):
        d = log_base_dir
        folders = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]

        df_final = pd.DataFrame(columns=[])
        for folder in folders:
            try:
                folder = os.path.split(folder)[-1]
                df = Loader.getResourceLog(folder)
                df_p = Loader.getFile(folder, 0, '_person_info')
                df_final = df_final.append(pd.DataFrame([{'Population': len(df_p),
                                                          'Avg. CPU Time': df['cpu_time'].mean(),
                                                          'Std. CPU Time': df['cpu_time'].std(),
                                                          'Avg. Memory': df['mem'].mean(),
                                                          'Std. Memory': df['mem'].std(),
                                                          }]))
            except:
                pass
        df_final = df_final.fillna(0)
        print(df_final)

        return {'status': 'SUCCESS',
                'data': df_final.to_csv(index=False),
                }


# Get colors
# `rgba(${r()}, ${r()}, ${r()}, 0.3)`
class GetColors(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']

        people_classes = Loader.getPeopleList(request_dir)
        location_classes = Loader.getLocationList(request_dir)
        movement_classes = Loader.getMovementList(request_dir)

        cmap = plt.get_cmap('brg')
        people_colors = [list(cmap(i / len(people_classes))) for i in range(len(people_classes))]
        cmap = plt.get_cmap('hsv')
        location_colors = [list(cmap(i / len(location_classes))) for i in range(len(location_classes))]
        cmap = plt.get_cmap('gnuplot2')
        movement_colors = [list(cmap(i / len(movement_classes))) for i in range(len(movement_classes))]

        for i in range(len(people_colors)):
            for j in range(3):
                people_colors[i][j] = int(people_colors[i][j] * 255)
            people_colors[i] = 'rgba(' + '|'.join(map(str, people_colors[i])) + ')'
        for i in range(len(location_colors)):
            for j in range(3):
                location_colors[i][j] = int(location_colors[i][j] * 255)
            location_colors[i] = 'rgba(' + '|'.join(map(str, location_colors[i])) + ')'
        for i in range(len(movement_colors)):
            for j in range(3):
                movement_colors[i][j] = int(movement_colors[i][j] * 255)
            movement_colors[i] = 'rgba(' + '|'.join(map(str, movement_colors[i])) + ')'
        return {
            'status': 'SUCCESS',
            'people_colors': pd.DataFrame(
                {'people_class': people_classes + [str(i) for i in range(len(people_classes))],
                 'color': people_colors + people_colors}).to_csv(index=False),
            'location_colors': pd.DataFrame(
                {'location_class': location_classes + [str(i) for i in range(len(location_classes))],
                 'color': location_colors + location_colors}).to_csv(index=False),
            'movement_colors': pd.DataFrame(
                {'movement_class': movement_classes + [str(i) for i in range(len(movement_classes))],
                 'color': movement_colors + movement_colors}).to_csv(index=False),
        }


@app.route("/", defaults={'path': ''})
def serve(path):
    return send_from_directory(app.static_folder, 'index.html')


api.add_resource(LogListHandler, '/flask/dirs')
api.add_resource(PostTextFileHandler, '/flask/textfile')
api.add_resource(PostCSVasJSONHandler, '/flask/csvfile')
api.add_resource(NDaysHandler, '/flask/n_days')
api.add_resource(InfectionTreeHandler, '/flask/infectiontree')
api.add_resource(LocationTreeHandler, '/flask/locationtree')
api.add_resource(SetPeopleClassesHandler, '/flask/setpeopleclasses')

api.add_resource(GetColors, '/flask/get_colors')

api.add_resource(PossibleGroupsHandler, '/flask/possible_groups')
api.add_resource(ContactHandler, '/flask/contacts')
api.add_resource(PersonContactHandler, '/flask/personcontacts')
api.add_resource(LocationContactHandler, '/flask/locationcontacts')

api.add_resource(InfectionHandler, '/flask/newinfections')

api.add_resource(ActualLocationHistHandler, '/flask/ActualLocationHist')
api.add_resource(RouteLocationHistHandler, '/flask/RouteLocationHist')
api.add_resource(PeoplePathHandler, '/flask/peoplepath')
api.add_resource(LocationPeopleCountHandler, '/flask/LocationPeopleCountHandler')
api.add_resource(LocationPeopleCountSurfaceHandler, '/flask/LocationPeopleCountSurfaceHandler')
api.add_resource(LocationShapes, '/flask/locationData')

api.add_resource(PerformanceHandler, '/flask/performance')
