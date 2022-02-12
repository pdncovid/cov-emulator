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
import getColors from "../sim/resultpage"

function ResultsDemographicsPage() {
    const [initialLoad, setInitialLoad] = useState(true);

    const [locs, setLocs] = useState([]);
    const [people, setPeople] = useState([]);
    const [movement, setMovement] = useState([]);
    const [groupOptions, setGroupOptions] = useState([]);

    const [selectedLogDir, setSelectedLogDir] = useState('');
    const [selectedDay, setSelectedDay] = useState('');

    const [peopleClassColors, setPeopleClassColor] = useState({});
    const [locationClassColor, setLocationClassColor] = useState({});
    const [movementClassColor, setMovementClassColor] = useState({});
    useEffect(() => {
    }, [selectedLogDir])

    useEffect(()=>{
        processPieChart()
        processPopPyramid()
        plotLocationTree()
    }, [selectedDay])

    const handleSelectDir = function (_selectedLogDir) {
        setSelectedLogDir(_selectedLogDir)
        getColors(_selectedLogDir)
    }

    const handleDayChange = function (_day) {
        setSelectedDay(_day);
    }

    const handleAnalyzePeopleClick = (_selectedPeople) => {
        axios.post(api + "/flask/setpeopleclasses", { dir: selectedLogDir, classes: _selectedPeople.join(',') })
            .then(function (response) {
                processPieChart()
                processPopPyramid()
                plotLocationTree()
            })
    }
    const getLocsArr = (arr) => { setLocs(arr) }
    const getPeopleArr = (arr) => { setPeople(arr) }
    const getMovementArr = (arr) => { setMovement(arr) }
    const getGroupOptionsArr = (arr) => { setGroupOptions(arr) }
    
    async function getColors(_selectedLogDir) {
        axios.post(api + "/flask/get_colors", { dir: _selectedLogDir })
            .then(function (response) {
                const people_colors = response.data.people_colors;
                const location_colors = response.data.location_colors;
                const movement_colors = response.data.movement_colors;

                var _people_colors = {}
                var _location_colors = {}
                var _movement_colors = {}
                csv2JSONarr(people_colors, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    _df.select('people_class', 'color').map(row => {
                        var pc = row.get('people_class')
                        var c = row.get('color').replaceAll('|', ',')
                        _people_colors[pc] = c
                        return row
                    })
                    console.log(_people_colors)
                })
                csv2JSONarr(location_colors, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    _df.select('location_class', 'color').map(row => {
                        var pc = row.get('location_class')
                        var c = row.get('color').replaceAll('|', ',')
                        _location_colors[pc] = c
                        return row
                    })
                    console.log(_location_colors)
                })
                csv2JSONarr(movement_colors, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    _df.select('movement_class', 'color').map(row => {
                        var pc = row.get('movement_class')
                        var c = row.get('color').replaceAll('|', ',')
                        _movement_colors[pc] = c
                        return row
                    })
                    console.log(_movement_colors)
                })
                setMovementClassColor(_movement_colors)
                setLocationClassColor(_location_colors)
                setPeopleClassColor(_people_colors)
                setSelectedLogDir(_selectedLogDir)
            })
    }

    // show the population occupation pie chart
    async function processPieChart() {
        console.log("loading data for pie chart of people")


        axios.post(api + "/flask/csvfile", {
            dir: selectedLogDir, d: selectedDay.toString(),
            type: '_person_info', columns: "person|person_class"
        })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data).castAll(Array(2).fill(Number))

                    // setting people pie chart data
                    var grp = sub_df.groupBy("person_class")
                    var pieData = [];
                    var pieLabels = [];
                    var colors = [];
                    // Loading People
                    // axios.post(api + "/flask/textfile", { dir: selectedLogDir, filename: 'people.txt' })
                    //     .then(function (response) {
                    //         var people_str = response.data.data.split("\n").map((e) => strip_text(e));

                            grp.aggregate((g, pc) => {
                                try {
                                    pc = pc['person_class']
                                    pieLabels.push(people[pc])
                                    colors.push(peopleClassColors[pc].replace(/[^,]+(?=\))/, '1.0'))

                                    try {
                                        pieData.push(g.count())
                                    } catch (error) {
                                        pieData.push(0)
                                    }
                                } catch (error) {

                                }
                            });
                            console.log("Pie data", pieData, pieLabels, colors)
                            Plotly.newPlot("distributionpeople", [{
                                type: 'pie',
                                values: pieData,
                                marker: {
                                    colors: colors
                                },
                                labels: pieLabels
                            }],
                                {
                                    title: 'Distribution of people',
                                }
                            )
                        // })

                })
            })
    }

    // show population pyramid
    async function processPopPyramid() {
        axios.post(api + "/flask/csvfile", {
            dir: selectedLogDir, d: selectedDay.toString(),
            type: '_person_info', columns: "person_class|gender|age"
        })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data).castAll(Array(3).fill(Number))

                    let m_bins = hist(sub_df.where(row => row.get('gender') == 1).toArray('age'), 10, 10);
                    let f_bins = hist(sub_df.where(row => row.get('gender') == 0).toArray('age'), 10, 10);

                    let trace1 = {
                        uid: '9f2de8e2-01e2-44cf-9597-d8c9d17a223a',
                        meta: {
                            columnNames: {
                                x: 'Men, x',
                                y: 'Men, y; Women, y'
                            }
                        },
                        name: 'Men',
                        type: 'bar',
                        x: m_bins.map((e) => e.count),
                        y: m_bins.map((e) => e.minNum),
                        marker: { color: 'powderblue' },
                        text: m_bins.map((e) => e.count),
                        hoverinfo: 'text',
                        orientation: 'h'
                    };
                    let trace2 = {
                        uid: '31653fd0-228e-4932-88af-340740cd1dea',
                        meta: {
                            columnNames: {
                                x: 'Women, x',
                                y: 'Men, y; Women, y',
                                text: 'text'
                            }
                        },
                        name: 'Women',
                        type: 'bar',
                        x: f_bins.map((e) => -e.count),
                        y: f_bins.map((e) => e.minNum),
                        marker: { color: 'seagreen' },
                        text: f_bins.map((e) => e.count),
                        textcolor: 'black',
                        hoverinfo: 'text',
                        orientation: 'h'
                    };
                    let data = [trace1, trace2];
                    Plotly.newPlot("popPyramid", data, {
                        title: 'Population pyramid',
                        xaxis: {

                            type: 'linear',
                            title: { text: 'Number' },
                        },
                        yaxis: {
                            type: 'linear',
                            range: [-5, 95],
                            title: { text: 'Age' },
                            autorange: true
                        },
                        bargap: 0.1,
                        barmode: 'relative',
                        autosize: true
                    })
                })
            })
    }

    // draw location treemap
    async function plotLocationTree() {

        axios.post(api + "/flask/csvfile", {
            dir: selectedLogDir, d: selectedDay.toString(),
            type: '_location_info', columns: "parent_id|children_ids|id|name"
        })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data)//.castAll(Array(5).fill(Number))
                    var data = [
                        {
                            type: "treemap", //sunburst
                            ids: sub_df.toArray('id'),
                            labels: sub_df.toArray('name'),
                            parents: sub_df.toArray('parent_id').map((e) => {
                                if (e == -1) {
                                    return ""
                                } else {
                                    return e
                                }
                            })
                        }
                    ];

                    Plotly.newPlot("locTree", data, {
                        title: 'Location Tree Structure',
                        width: 800,
                        height: 800
                    })
                })
            })
    }

    return (
        <div>
            <div className="results-page">
                <h1>Demographic analysis</h1>
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

                 {/* ====================================================================================== Demographic information */}
                 <div>
                    <h4>Demographic information</h4>
                    <Grid container spacing={0} padding='30px'>
                        <Grid container xs={6}>
                            <div id="popPyramid"></div>
                        </Grid>

                        <Grid container xs={6}>
                            <div id="distributionpeople"></div>
                        </Grid>
                    </Grid>
                    <div id="locTree"></div>

                </div>

        </div>
    )
}


export default ResultsDemographicsPage;