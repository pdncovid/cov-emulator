import argparse
import json
import sys

from flask import Flask, send_from_directory
from flask_restful import Api, Resource, reqparse, abort
from .constants import log_base_dir, selected_people_classes, data_path

from flask_cors import CORS  # comment this on deployment
import os
import pathlib
import pandas as pd
import numpy as np
import re

print("CWD", os.getcwd())
sys.path.append('../../')

from backend.python.sim_args import get_args_web_ui

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
        path = data_path if rdir == '' else log_base_dir.joinpath(rdir)
        return list(pd.read_csv(path.joinpath("location_classes.csv"))['l_class'].values)

    @staticmethod
    def getPeopleList(rdir):
        path = data_path if rdir == '' else log_base_dir.joinpath(rdir)
        return list(pd.read_csv(path.joinpath("person_classes.csv"))['p_class'].values)

    @staticmethod
    def getMovementList(rdir):
        path = data_path if rdir == '' else log_base_dir.joinpath(rdir)
        return list(pd.read_csv(path.joinpath("movement_classes.csv"))['m_class'].values)

    @staticmethod
    def getResourceLog(rdir):
        f_name = "resource_info.csv"
        return pd.read_csv(log_base_dir.joinpath(rdir).joinpath(f_name))

    @staticmethod
    def get_day_file_names_sorted(rdir):
        files = [os.path.split(x)[-1] for x in os.listdir(log_base_dir.joinpath(rdir))]
        day_info = []
        for f in files:
            if re.search("[0-9]{5}.csv", f) is not None:
                day_info.append(f)
        day_info.sort()
        return day_info


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

class LogArgsHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']

        with open(log_base_dir.joinpath(request_dir).joinpath("args.data")) as fh:
            arg_parser = get_args_web_ui("")
            # import shlex
            # ret_args = arg_parser.parse_args(shlex.split(fh.read()))
            read = fh.read()
            ret_args = arg_parser.parse_args(read.split())
            print("Loaded Args" , ret_args)
            return  vars(ret_args)



class LogListHandler(Resource):
    def get(self):
        fols = [os.path.split(x[0])[-1] for x in os.walk(log_base_dir)]
        return {
            'resultStatus': 'SUCCESS',
            'message': ",".join(map(str, fols[1:]))
        }


class MatrixListHandler(Resource):
    def get(self):
        fols = []
        for (dirpath, dirnames, filenames) in os.walk(data_path):
            fols.extend(filenames)
            break
        fols = filter(lambda x: 'class' not in x, fols)
        print(fols)
        return {
            'status':'Success',
            'data':'|'.join(fols)
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
            elif 'csv' in request_type:
                if request_dir == '':
                    df = pd.read_csv(data_path.joinpath(request_type))
                else:
                    df = pd.read_csv(log_base_dir.joinpath(request_dir).joinpath(request_type), low_memory=False)
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


class SaveCSVJSONHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        parser.add_argument('filename', type=str)
        parser.add_argument('data', type=str)
        args = parser.parse_args()

        request_dir = args['dir']
        request_data = args['data']
        request_type = args['filename']

        try:
            status = "Success"
            arr = json.loads(request_data)
            df = pd.DataFrame(columns=list(arr[0].keys()))
            for row in arr:
                df = df.append(row, ignore_index=True)
            if "[object Object]" in df.columns:
                df = df.drop("[object Object]", axis=1)
            print(df)
            if dir == '':
                df.to_csv(path_or_buf=data_path.joinpath(request_type), index=False)
            else:
                df.to_csv(path_or_buf=data_path.joinpath(request_dir).joinpath(request_type), index=False)
            message = "Saved"
        except Exception as e:
            status = "Error"
            message = str(e)
            abort(500)
        final_ret = {"status": status, "message": message}

        return final_ret
