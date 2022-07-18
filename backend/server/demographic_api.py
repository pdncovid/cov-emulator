from flask_restful import Api, Resource, reqparse, abort
import os
import pathlib
from anytree import Node, RenderTree
from anytree.exporter import JsonExporter
import pandas as pd
import numpy as np
from .constants import log_base_dir, selected_people_classes
from .file_api import Loader, getMap


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
            print(e)
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
