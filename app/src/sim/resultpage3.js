import React, { useState, useRef, useEffect } from "react";

import Grid from '@material-ui/core/Grid';

import * as Plotly from 'plotly.js';
import Plot from 'react-plotly.js';
import { csvJSON, csv2JSONarr, csv2arr, strip_text } from "../utils/files";
import { hist, padZeros } from "../utils/functions";

import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import TextField from "@material-ui/core/TextField";

import Typography from '@material-ui/core/Typography';
import Slider from '@material-ui/core/Slider';

import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import { ConsoleLog } from "react-console-log";

import randomColor from "randomcolor";

import Tree from 'react-d3-tree';
import DataFrame from 'dataframe-js';
import axios from 'axios'
import { api } from '../utils/constants';
import DirSelect from "../components/DirSelect";
function ResultsPage3() {
    const [initialLoad, setInitialLoad] = useState(true);

    const [locs, setLocs] = useState([]);
    const [people, setPeople] = useState([]);
    const [movement, setMovement] = useState([]);
    const [groupOptions, setGroupOptions] = useState([]);

    const [selectedLogDir, setSelectedLogDir] = useState('');
    const [selectedDay, setSelectedDay] = useState('');


    const [cpuTimeData, setCpuTimeData] = useState([]);
    const [cpuTimeLayout, setCpuTimeLayout] = useState([]);

    const handleSelectDir = function (_selectedLogDir) {
        setSelectedLogDir(_selectedLogDir)
        drawCPUTimeWithInfections(_selectedLogDir)
    }

    const handleDayChange = function (_day) {
        setSelectedDay(_day);
    }

    const handleAnalyzePeopleClick = (_selectedPeople) => {
        axios.post(api + "/flask/setpeopleclasses", { dir: selectedLogDir, classes: _selectedPeople.join(',') })
            .then(function (response) {

            })
    }
    const getLocsArr = (arr) => { setLocs(arr) }
    const getPeopleArr = (arr) => { setPeople(arr) }
    const getMovementArr = (arr) => { setMovement(arr) }
    const getGroupOptionsArr = (arr) => { setGroupOptions(arr) }
    useEffect(() => {
        drawCPUMEMPerformance()
    }, [initialLoad])

    function drawCPUMEMPerformance() {
        //loading density info
        axios.post(api + "/flask/performance", {})
            .then(function (response) {
                const data = response.data.data;

                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data);
                    console.log("Performance", _df)
                    var traces = [];
                    traces.push({
                        x: _df.select("Population").toArray().map(e => e[0]),
                        y: _df.select('Avg. CPU Time').toArray().map(e => e[0]),
                        error_y: {
                            type: 'data',
                            array: _df.select('Std. CPU Time').toArray().map(e => e[0]),
                            visible: true
                        },
                        xaxis: 'x',
                        yaxis: 'y',
                        name: 'Avg. CPU Time',
                        mode: "markers",
                        type: "scatter",
                    })
                    traces.push({
                        x: _df.select("Population").toArray().map(e => e[0]),
                        y: _df.select('Avg. Memory').toArray().map(e => e[0]),
                        xaxis: 'x2',
                        yaxis: 'y2',
                        error_y: {
                            type: 'data',
                            array: _df.select('Std. Memory').toArray().map(e => e[0]),
                            visible: true
                        },
                        name: 'Avg. Memory',
                        mode: "markers",
                        type: "scatter",
                    })

                    setCpuTimeData(traces)
                    let layout = {
                        title: 'Performance',
                        width: 1000,
                        height: 500,
                        xaxis: {
                            type: 'log',
                            title: 'Population size',
                            autorange: true
                        },
                        yaxis: {
                            type: 'log',
                            title: 'Avg. CPU Time',
                            autorange: true
                        },
                        xaxis2: {
                            type: 'log',
                            title: 'Population size',
                            autorange: true
                        },
                        yaxis2: {
                            type: 'log',
                            title: 'Avg. Memory',
                            autorange: true
                        },

                        showlegend: false,
                        grid: {
                            subplots: [['xy', 'x2y2'],],
                            rows: 1,
                            columns: 2,
                        }
                    }
                    setCpuTimeLayout(layout)
                })

            });
    }

    function drawCPUTimeWithInfections(_selectedLogDir) {
        axios.post(api + '/flask/n_days', { dir: _selectedLogDir }).then(response => {
            let _days = response.data.message.split('|').length
            var _data = []
            // var trace1 = {
            //     x: [],//infection_df.select('time').toArray().map((e) => e[0]),
            //     y: [],//,
            //     name: 'Infected people',
            //     type: 'line'
            // };

            // var trace2 = {
            //     x: [],//resource_df.select('time').toArray().map((e) => e[0]),
            //     y: [],//resource_df.select('cpu_time').toArray().map((e) => e[0]),
            //     name: 'CPU Time',
            //     yaxis: 'y2',
            //     type: 'scatter'
            // };

            for (let _day = 0; _day < _days; _day++) {
                axios.post(api + "/flask/csvfile", { dir: _selectedLogDir, d: _day, type: '_cov_info', columns: "INFECTED|time" })
                    .then(function (response) {
                        const data = response.data.data;
                        csv2JSONarr(data, (pr) => { }).then((json_data) => {
                            var infection_df = new DataFrame(json_data)
                            axios.post(api + "/flask/csvfile", { dir: _selectedLogDir, d: _day, type: '_resource_info', columns: "" })
                                .then(function (response) {
                                    const data = response.data.data;
                                    csv2JSONarr(data, (pr) => { }).then((json_data) => {
                                        var resource_df = new DataFrame(json_data)
                                        let time = infection_df.select('time').toArray().map((e) => e[0]/1440)
                                        let infections = infection_df.select('INFECTED').toArray().map((e) => e[0])
                                        let cputime = resource_df.select('cpu_time').toArray().map((e) => parseFloat(e[0]))

                                        for (var i = 1; i < time.length; i++) {
                                            _data.push({ t: parseFloat(time[i]), infs: infections[i], cpu: cputime[i] - cputime[i - 1] })
                                        }
                                        _data.push({ t: parseFloat(time[0]), infs: infections[0], cpu: cputime[1] - cputime[0] })

                                        _data.sort(function (a, b) {
                                            return ((a.t < b.t) ? -1 : ((a.t == b.t) ? 0 : 1));
                                        });

                                        if (_day == _days - 1) {
                                            var layout = {
                                                title: 'Variation of CPU time with number of infections',
                                                yaxis: { title: 'Number of infected people' },
                                                yaxis2: {
                                                    title: 'CPU Time (s)',
                                                    type: 'log',
                                                    titlefont: { color: 'rgb(148, 103, 189)' },
                                                    tickfont: { color: 'rgb(148, 103, 189)' },
                                                    overlaying: 'y',
                                                    side: 'right'
                                                },
                                                xaxis:{
                                                    title: "Simulation Days"
                                                }

                                            };
                                            console.log(_data)
                                            var trace1 = {
                                                x: _data.map((e) => e.t),
                                                y: _data.map((e) => e.infs),
                                                name: 'Infected people',
                                                type: 'scatter'
                                            };
                                            var trace2 = {
                                                x: _data.map((e) => e.t),
                                                y: _data.map((e) => e.cpu),
                                                name: 'CPU Time',
                                                yaxis: 'y2',
                                                mode: 'markers',
                                                type: 'scatter'
                                            };
                                            Plotly.newPlot('cpuTimeWithInfections', [trace1, trace2], layout);
                                        }

                                    })

                                })
                        })

                    })
            }
        })
    }
    return (
        <div>
            <div className="results-page">
                <h1>Sim Performance analysis</h1>
            </div>

            <div>
                <h4>Select log location</h4>
                <DirSelect
                    onSelect={handleSelectDir}
                    onAnalyzePeople={handleAnalyzePeopleClick}
                    onDayChange={handleDayChange}
                    getLocsArr={getLocsArr}
                    getPeopleArr={getPeopleArr}
                    getMovementArr={getMovementArr}
                    getGroupOptionsArr={getGroupOptionsArr}
                />
            </div>

            {/* =================================================================================================== map */}

            <div id="cpumem">
                <h4>CPU Time</h4>
                {/* <Button onClick={drawPerformance}>Plot Performance Graphs</Button> */}
                <Plot
                    data={cpuTimeData}
                    layout={cpuTimeLayout}
                />
            </div>
            <div>
                <h4>CPU Time with infections</h4>
                <div id="cpuTimeWithInfections" />
            </div>
        </div>
    )
}


export default ResultsPage3;