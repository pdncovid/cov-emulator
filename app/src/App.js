import logo from './logo.svg';
import './App.css';
import { BrowserRouter, Router, Route, Switch ,Redirect} from "react-router-dom";
import TopBar from "./topnav/topbar";
import HomePage from "./home/homepage"
import ProbDensePage from "./probpage/probpage"
import ResultsPage from "./sim/resultpage"
import ResultsPage2 from "./sim/resultpage2"
import ResultsPage3 from "./sim/resultpage3"
import ResultsDemographicsPage from './sim/resultspage4';
import SocioEconomic from './sim/socioeconomic';
import 'bootstrap/dist/css/bootstrap.min.css';
// node --max_old_space_size=4096 "D:\Program files\nodejs\node_modules\npm" start
import { createBrowserHistory as createHistory } from "history";
const history = createHistory();


function App() {
  return (

    <div className="App">

      <BrowserRouter>
        <Switch>
          <Route
            exact
            path="/"
            render={() => {
              return (
                  <Redirect to="/home" /> 
              )
            }}
          />
          <Route path="/home" history={history}>
            <TopBar />
            <HomePage />
          </Route>
          <Route path="/prob" history={history}>
            <TopBar />
            <ProbDensePage />
          </Route>
          <Route path="/results" history={history}>
            <TopBar />
            <ResultsPage />
          </Route>
          <Route path="/results2" history={history}>
            <TopBar />
            <ResultsPage2 />
          </Route>
          <Route path="/results3" history={history}>
            <TopBar />
            <ResultsPage3 />
          </Route>
          <Route path="/resultsdemo" history={history}>
            <TopBar />
            <ResultsDemographicsPage />
          </Route>
          <Route path="/resultsse" history={history}>
            <TopBar />
            <SocioEconomic />
          </Route>
        </Switch>
      </BrowserRouter>

      {/* <Router >
      
        <Route path="/" exact component={HomePage} />
      </Router> */}
    </div>


  );
}

export default App;
