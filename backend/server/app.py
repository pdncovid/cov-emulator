import matplotlib.pyplot as plt

from .file_api import *
from .demographic_api import *
from .constants import *
from .infection_api import *

print("CWD", os.getcwd())
sys.path.append('../../')

from backend.python.sim_args import get_args_web_ui

app = Flask(__name__, static_url_path='', static_folder='frontend/build')
CORS(app)  # comment this on deployment
api = Api(app)


class RunSim(Resource):
    def post(self):
        _parser = get_args_web_ui('')
        _args = _parser.parse_args([])

        parser = reqparse.RequestParser()
        for arg in vars(_args).keys():
            parser.add_argument(arg, type=str)

        args = parser.parse_args()
        args_str = ''
        for arg in args.keys():
            if arg == "locationTreeData":
                s = "\"" + args[arg].replace("'", "\\\"") + "\""
                s = args[arg].replace("'", "\"")
                with open("temp.tree", 'w') as f:
                    f.write(s)
                args[arg] = "temp.tree"
            if arg == "personPercentData" or arg == "addedContainmentEvents" or arg == "addedGatheringEvents" or \
                    arg == "addedVaccinationEvents" or arg == "addedVariantEvents":
                args[arg] = "\"" + args[arg].replace("'", "\\\"") + "\""
            # if arg == "personPercentData":
            #     js = json.loads(args[arg].replace("'","\""))
            #     js_str = ''
            #     for i in js.keys():
            #         js_str += js[i]['p_class']+"#"+str(js[i]['percentage'])+"|"
            #     js_str = js_str[:-1]
            #     args[arg] = js_str
            args_str += ' --' + arg + ' ' + str(args[arg])
        os.system("python runner.py " + args_str)


class NDaysHandler(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('dir', type=str)
        args = parser.parse_args()
        request_dir = args['dir']

        files = [os.path.split(x)[-1] for x in os.listdir(log_base_dir.joinpath(request_dir))]

        days = []
        for f in files:
            if 'person_info' in str(f):
                days += [str(int(re.search("[0-9]{5}", str(f)).group()))]
        return {
            'resultStatus': 'SUCCESS',
            'message': '|'.join(days)
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
                         'current_location_class'
                         ]
                }


# Performance Handlers
class PerformanceHandler(Resource):
    def post(self):
        d = log_base_dir.joinpath("PERFORMANCE_CHECK")
        folders = [os.path.join(d, o) for o in os.listdir(d) if os.path.isdir(os.path.join(d, o))]
        print(folders)
        df_final = pd.DataFrame(columns=[])
        df_all = pd.DataFrame(columns=["Population", "CPU Time", "Memory"])
        for folder in folders:
            folder = os.path.split(folder)[-1]
            folder = pathlib.Path("PERFORMANCE_CHECK").joinpath(folder)
            print(folder)
            df = Loader.getResourceLog(folder)
            df = df.iloc[1:]
            df_p = Loader.getFile(folder, 0, '_person_info')
            df_all = df_all.append(pd.DataFrame({"Population": [len(df_p)] * len(df),
                                                 "CPU Time": df['cpu_time'].values,
                                                 "Memory": df['mem'].values / 1024 / 1024}))
            df_final = df_final.append(pd.DataFrame([{'Population': len(df_p),
                                                      'Avg. CPU Time': df['cpu_time'].mean(),
                                                      'Std. CPU Time': df['cpu_time'].std(),
                                                      'Avg. Memory': df['mem'].mean(),
                                                      'Std. Memory': df['mem'].std(),
                                                      }]))

        df_final = df_final.fillna(0)
        print(df_all)

        f, axs = plt.subplots(1, 2, figsize=(6.4 * 2, 4.8))
        axs[0].set(yscale="log")
        axs[1].set(yscale="log")
        sns.pointplot('Population', 'CPU Time', data=df_all, dodge=True, join=False, ax=axs[0])
        axs[0].set_ylabel("Average CPU Time per day (secs)")
        sns.pointplot('Population', 'Memory', data=df_all, dodge=True, join=False, ax=axs[1])
        axs[1].set_ylabel("Average Memory per day (MB)")
        plt.tight_layout()
        plt.savefig(log_base_dir.joinpath(f"performance.png"))
        plt.savefig(log_base_dir.joinpath(f"performance.svg"))
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


api.add_resource(RunSim, '/flask/run')

api.add_resource(LogListHandler, '/flask/dirs')
api.add_resource(PostTextFileHandler, '/flask/textfile')
api.add_resource(PostCSVasJSONHandler, '/flask/csvfile')
api.add_resource(SaveCSVJSONHandler, '/flask/savecsvfile')

api.add_resource(NDaysHandler, '/flask/n_days')
api.add_resource(InfectionTreeHandler, '/flask/infectiontree')
api.add_resource(InfectionStateTimelineHandler, '/flask/infectionstatetimeline')
api.add_resource(PeopleStateTimelineHandler, '/flask/peoplestatetimeline')

api.add_resource(LocationTreeHandler, '/flask/locationtree')
api.add_resource(SetPeopleClassesHandler, '/flask/setpeopleclasses')

api.add_resource(GetColors, '/flask/get_colors')

api.add_resource(MatrixListHandler, '/flask/matrix_names')

api.add_resource(LogArgsHandler, '/flask/load_args')

api.add_resource(PossibleGroupsHandler, '/flask/possible_groups')
api.add_resource(ContactHandler, '/flask/contacts')
api.add_resource(PersonContactHandler, '/flask/personcontacts')
api.add_resource(LocationContactHandler, '/flask/locationcontacts')

api.add_resource(InfectionHandler, '/flask/newinfections')
api.add_resource(VariantHandler, '/flask/variants')

api.add_resource(ActualLocationHistHandler, '/flask/ActualLocationHist')
api.add_resource(RouteLocationHistHandler, '/flask/RouteLocationHist')
api.add_resource(PeoplePathHandler, '/flask/peoplepath')
api.add_resource(LocationPeopleCountHandler, '/flask/LocationPeopleCountHandler')
api.add_resource(LocationPeopleCountSurfaceHandler, '/flask/LocationPeopleCountSurfaceHandler')
api.add_resource(LocationShapes, '/flask/locationData')

api.add_resource(PerformanceHandler, '/flask/performance')
