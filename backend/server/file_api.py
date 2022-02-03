from flask import Flask, send_from_directory
from flask_restful import Api, Resource, reqparse, abort
from .constants import log_base_dir, selected_people_classes

from flask_cors import CORS  # comment this on deployment
import os
import pathlib
import pandas as pd
import numpy as np
import re

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

def getMap(name, dir):
    if 'person_class' in name:
        return Loader.getPeopleList(dir)
    if 'location_class' in name:
        return Loader.getLocationList(dir)
    if 'movement_class' in name:
        return Loader.getMovementList(dir)

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


class LogListHandler(Resource):
    def get(self):
        fols = [os.path.split(x[0])[-1] for x in os.walk(log_base_dir)]
        return {
            'resultStatus': 'SUCCESS',
            'message': ",".join(map(str, fols[1:]))
        }

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