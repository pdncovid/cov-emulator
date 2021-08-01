import logo from './logo.svg';
import './App.css';
import { BrowserRouter, Router, Route, Switch } from "react-router-dom";
import TopBar from "./topnav/topbar";
import HomePage from "./home/homepage"
import ProbDensePage from "./probpage/probpage"

import { createBrowserHistory as createHistory } from "history";
const history = createHistory();
function App() {
  return (

    <div className="App">

      <BrowserRouter>
        <Switch>
          <Route path="/home" history={history}>
            <TopBar />
            <HomePage />
          </Route>
          <Route path="/prob" history={history}>
            <TopBar />
            <ProbDensePage />
          </Route>
          {/* <Route path="/whale" history={history}>
            <Whale />
          </Route> */}
        </Switch>
      </BrowserRouter>

      {/* <Router >
      
        <Route path="/" exact component={HomePage} />
      </Router> */}
    </div>


  );
}

export default App;
