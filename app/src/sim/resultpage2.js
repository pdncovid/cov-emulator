import React, { useState, useRef, useEffect } from "react";

import Grid from '@material-ui/core/Grid';

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
function ResultsPage2() {
    const [dirs, setDirs] = useState([]);
    const [days, setDays] = useState([]);
    const [locs, setLocs] = useState([]);
    const [people, setPeople] = useState([]);
    const [movement, setMovement] = useState([]);
    const [peopleClassColors, setPeopleClassColor] = useState({});
    const [locationClassColor, setLocationClassColor] = useState({});
    const [movementClassColor, setMovementClassColor] = useState({});
    const [groupOptions, setGroupOptions] = useState([]);

    const [selectedLogDir, setSelectedLogDir] = useState('');
    const [selectedDay, setSelectedDay] = useState('');


    const [mapData, setMapData] = useState([]);
    const [mapLayout, setMapLayout] = useState([]);
    const [mapFrames, setMapFrames] = useState([]);
    const [timeText, setTimeText] = useState('');


    const [nodeX, setNodeX] = useState(30);
    const [nodeY, setNodeY] = useState(30);
    const [locationTreeData, setLocationTreeData] = useState({ name: 'ROOT' });

    const [timeLen, setTimeLen] = useState(1);
    const [timeIdx, setTimeIdx] = useState(0);


    const [locHistData, setLocHistData] = useState([]);
    const [locHistLayout, setLocHistLayout] = useState([]);
    const [routeHistData, setRouteHistData] = useState([]);
    const [routeHistLayout, setRouteHistLayout] = useState([]);
    const [moveHistData, setMoveHistData] = useState([]);
    const [moveHistLayout, setMoveHistLayout] = useState([]);

    const [unstagedPeople, setUnstagedPeople] = useState([]);
    const [stagedPeople, setStagedPeople] = useState([]);
    const [selectedUnstagedPeople, setSelectedUnstagedPeople] = useState([]);
    const [selectedStagedPeople, setSelectedStagedPeople] = useState([]);
    const [personPathData, setPersonPathData] = useState([]);
    const [personPathLayout, setPersonPathLayout] = useState([]);
    const [personPathData2, setPersonPathData2] = useState([]);
    const [personPathLayout2, setPersonPathLayout2] = useState([]);
    const [personPathFrames, setPersonPathFrames] = useState([]);
    const [showShapes, setShowShapes] = useState(true);

    const getLocsArr = (arr) => { setLocs(arr) }
    const getPeopleArr = (arr) => { setPeople(arr) }
    const getMovementArr = (arr) => { setMovement(arr) }
    const getGroupOptionsArr = (arr) => { setGroupOptions(arr) }

    // import colors
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

    //draw person path
    useEffect(() => {
        drawPersonPath()
    }, [stagedPeople])


    async function drawLocationDensity() {


        //loading density info
        axios.post(api + "/flask/LocationPeopleCountSurfaceHandler", { dir: selectedLogDir, day: selectedDay.toString(), time: timeText })
            .then(function (response) {
                const data = response.data.data;
                csv2arr(data, (pr) => { }).then((arr) => {
                    var x = arr.map((e) => e[e.length - 2])
                    var y = arr.map((e) => e[e.length - 1])
                    arr = arr.map((e) => e.splice(0, e.length - 2))
                    // var cols = _df.listColumns();
                    // _df = _df.restructure(cols.slice(cols.length/2).concat(
                    //     cols.splice(cols.length/2, cols.length)
                    // ))
                    console.log(arr)
                    let plotData = [{
                        type: 'surface',
                        z: arr,
                        contours: {
                            z: {
                                show: true,
                                usecolormap: true,
                                highlightcolor: "#42f462",
                                project: { z: true }
                            }
                        }
                    }]

                    setMapData(plotData)
                    setMapLayout({
                        title: 'Density of people',
                        width: 1200,
                        height: 800,
                        scene: {
                            xaxis: {
                                title: 'x',
                                // ticktext:x.filter((v,i)=>i%Math.floor(x.length/10)==0),
                                // tickvals:[...Array(Array(x.length).keys()).filter((v,i)=>i%Math.floor(x.length/10)==0)]
                            },
                            yaxis: {
                                title: 'y',
                                // ticktext:y.filter((v,i)=>i%Math.floor(y.length/10)==0),
                                // tickvals:[...Array(Array(y.length).keys()).filter((v,i)=>i%Math.floor(y.length/10)==0)]
                            }
                        }
                    })
                })
            });
    }

    // draw location tree
    const renderNode = ({ nodeDatum, toggleNode, t }) => (
        <g>
            <circle r="5" x="-5" onClick={toggleNode} fill={locationClassColor[nodeDatum.attributes?.class]} stroke={locationClassColor[nodeDatum.attributes?.class]} />
            <text fill="black" strokeWidth="1" x="20">
                ID: {nodeDatum.name}
            </text>
            {/* {nodeDatum.attributes?.n && (
                <text fill="black" strokeWidth="1" x="20" dy="20">
                    n: {nodeDatum.attributes?.n[timeIdx] + " " +timeIdx}
                </text>
            )} */}
            {nodeDatum.attributes?.n[timeIdx] > 0 && (
                <rect
                    height={nodeDatum.attributes?.n[timeIdx] * 8}
                    width="10"
                    x="-5"
                    fill={locationClassColor[nodeDatum.attributes?.class]}
                    stroke={locationClassColor[nodeDatum.attributes?.class]}
                />
            )}
        </g>
    );

    const getDynamicPathClass = ({ source, target }, orientation) => {
        if (!target.children) {
            // Target node has no children -> this link leads to a leaf node.
            return 'link__leaf';
        }

        // Style it as a link connecting two branch nodes by default.
        return 'link__branch';
    };

    async function plotLocationTree(_day) {
        axios.post(api + "/flask/locationtree", { dir: selectedLogDir, day: _day.toString() })
            .then(function (response) {
                const data = response.data.json;
                setTimeLen(response.data.timeLen)
                setTimeIdx(0)
                const json_data = JSON.parse(data)
                setLocationTreeData(json_data);

            })
            .catch(function (response) {
                console.log(response);
            });
    }

    // draw paths and animation of person moving on coordinate plane
    async function drawPersonPath() {
        let _selected = stagedPeople.map((e) => parseInt(e.split(' ')[0]))
        axios.post(api + '/flask/peoplepath', { dir: selectedLogDir, day: selectedDay, people: _selected.join(',') }).
            then(response => {
                csv2JSONarr(response.data.data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data)
                    let cast = []
                    sub_df.listColumns().forEach((e) => {
                        cast.push(Number)
                    })
                    sub_df = sub_df.castAll(cast)
                    console.log(sub_df)
                    let grp = sub_df.groupBy("person")
                    var data1 = [];
                    var data2 = [];

                    var t;
                    grp.aggregate((g, p) => {
                        try {
                            p = p['person']
                            t = g.select('x').toArray().map((d, i) => i)
                            if (_selected.indexOf(p) != -1) {
                                var trace1 = {
                                    x: g.select('x').toArray().map((e) => e[0]),
                                    y: g.select('y').toArray().map((e) => e[0]),
                                    name: p,
                                    mode: 'line',
                                    id: t
                                };
                                data1.push(trace1);
                                // data2.push({x:trace1["x"],y:[],id:t,mode:'line'})
                                data2.push({
                                    ...trace1,
                                    transforms: [{
                                        type: 'filter',
                                        operation: '<=',
                                        target: t,
                                        value: 0.0
                                    },
                                    {
                                        type: 'filter',
                                        operation: '>',
                                        target: t,
                                        value: 0.0
                                    }]
                                })
                            }
                        } catch (error) {

                        }
                    });
                    setPersonPathData(data1);
                    setPersonPathData2(data2);

                    getEnvMapShapes(t)

                    setPersonPathFrames(t.map(t => ({
                        name: t,
                        data: data2.map((e) => ({ 'transforms[0].value': t, 'transforms[1].value': Math.max(0, t - 3) }))
                    })))
                });
            }).catch(error => {
                console.log(error)
            })




    }

    // get environment map shapes and update layouts
    async function getEnvMapShapes(t) {

        axios.post(api + "/flask/locationData", { dir: selectedLogDir, day: selectedDay.toString() })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    console.log(_df)
                    // _df = _df.withColumn('timesteps', row => row.get('timesteps').split('|').map(e => parseInt(e)));
                    let shapes = [];
                    _df.map((row) => {
                        try {
                            var trace1 = {
                                type: 'circle',
                                xref: 'x',
                                yref: 'y',
                                fillcolor: locationClassColor[parseInt(row.get('class'))].replace(/[^,]+(?=\))/, '0.1'),//'rgba(50, 171, 96, 0.1)',
                                x0: row.get('x') - row.get('radius'),
                                y0: row.get('y') - row.get('radius'),
                                x1: parseFloat(row.get('x')) + parseFloat(row.get('radius')),
                                y1: parseFloat(row.get('y')) + parseFloat(row.get('radius')),
                                line: {
                                    color: 'rgba(0, 0, 0, 0)'
                                }
                            };
                            shapes.push(trace1);
                        } catch (err) {
                            console.log(err)
                        }

                    })
                    if (!showShapes)
                        shapes = []
                    setPersonPathLayout({
                        barmode: 'stack',
                        title: 'Path took by the selected person',
                        shapes: shapes,
                        height: 800,
                        width: 800,
                        xaxis: {
                            showgrid: false, // thin lines in the background
                            zeroline: false, // thick line at x=0
                            visible: false,  // numbers below
                        },
                        yaxis: {
                            showgrid: false, // thin lines in the background
                            zeroline: false, // thick line at x=0
                            visible: false,  // numbers below
                        }

                    });

                    setPersonPathLayout2({
                        shapes: shapes,
                        height: 800,
                        width: 800,
                        xaxis: {
                            showgrid: false, // thin lines in the background
                            zeroline: false, // thick line at x=0
                            visible: false,  // numbers below
                        },
                        yaxis: {
                            showgrid: false, // thin lines in the background
                            zeroline: false, // thick line at x=0
                            visible: false,  // numbers below
                        },
                        updatemenus: [{
                            type: 'buttons',
                            xanchor: 'left',
                            yanchor: 'top',
                            direction: 'right',
                            x: 0,
                            y: 0,
                            pad: { t: 60 },
                            showactive: false,
                            buttons: [{
                                label: 'Play',
                                method: 'animate',
                                args: [null, {
                                    transition: { duration: 0 },
                                    frame: { duration: 20, redraw: false },
                                    mode: 'immediate',
                                    fromcurrent: true,
                                }]
                            }, {
                                label: 'Pause',
                                method: 'animate',
                                args: [[null], {
                                    frame: { duration: 0, redraw: false },
                                    mode: 'immediate',
                                }]
                            }]
                        }],
                        sliders: [{
                            currentvalue: {
                                prefix: 't = ',
                                xanchor: 'right'
                            },
                            pad: { l: 130, t: 30 },
                            transition: {
                                duration: 0,
                            },
                            steps: t.map(t => ({
                                label: t,
                                method: 'animate',
                                args: [[t], {
                                    frame: { duration: 0, redraw: false },
                                    mode: 'immediate',
                                }]
                            }))
                        }]
                    });




                });

            })
            .catch(function (response) {
                console.log(response);
            });
    }


    // show initialized route histogram for the given day
    async function processRouteHist(_day) {
        axios.post(api + "/flask/RouteLocationHist", { dir: selectedLogDir, day: _day.toString() })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    _df = _df.withColumn('time', row => row.get('time').split('|').map(e => parseInt(e)));
                    console.log(_df)
                    let gData = [];
                    var timesteps = [...Array(1440).keys()].map((t) => '' + Math.floor((t) / 60).toString().padStart(2, '0') + ':' + ((t) % 60).toString().padStart(2, '0'))
                    _df.map((row) => {
                        try {
                            var trace1 = {
                                x: timesteps,
                                y: row.get('time'),
                                name: row.get('group'),
                                type: "bar",
                                width: 3,
                                marker: { color: locationClassColor[locs.indexOf(row.get('group'))].replace(/[^,]+(?=\))/, '1.0') },
                                // xbins: { size: 5, },
                            };
                            gData.push(trace1);

                        } catch (err) {
                            console.log(err)
                        }

                    })

                    setRouteHistData(gData);
                    setRouteHistLayout({
                        barmode: 'stack',
                        bargap: 0.0,
                        height: 800,
                        width: 1000,
                        title: 'Histogram of planned visits during the day',
                        xaxis: {
                            title: 'Time',
                            // showticklabels: true,
                            // ticktext:timesteps.map((t)=>''+Math.floor((t)/60)+':'+(t)%60),
                            // tickvals:timesteps,
                            // tickformat: "%H:%M:%S s",
                        },
                        yaxis: {
                            title: 'Number of people',
                        },
                        legend: {

                            orientation: "h",
                        }
                    })

                });

            })
            .catch(function (response) {
                console.log(response);
            });
    }

    // show actual places visited during the day histogram
    async function plotActualLocationHist(_day) {
        axios.post(api + "/flask/ActualLocationHist", { dir: selectedLogDir, day: _day, groupBy: 'current_location_class' })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    _df = _df.withColumn('time', row => row.get('time').split('|').map(e => parseInt(e)));
                    console.log(_df)
                    let gData = [];
                    var timesteps = [...Array(1440).keys()].map((t) => '' + Math.floor((t) / 60).toString().padStart(2, '0') + ':' + ((t) % 60).toString().padStart(2, '0'))
                    _df.map((row) => {
                        try {
                            var trace1 = {
                                x: timesteps,
                                y: row.get('time'),
                                name: row.get('group'),
                                type: "bar",
                                width: 5,
                                marker: { color: locationClassColor[locs.indexOf(row.get('group'))].replace(/[^,]+(?=\))/, '1.0') },
                                // xbins: { size: 5, },
                            };
                            gData.push(trace1);

                        } catch (err) {
                            console.log(err)
                        }

                    })

                    setLocHistData(gData);
                    setLocHistLayout({
                        barmode: 'stack',
                        bargap: 0,
                        height: 800,
                        width: 1000,
                        title: 'Histogram of visited places during the day',
                        xaxis: {
                            title: 'Time',
                            // showticklabels: true,
                            // ticktext:timesteps.map((t)=>''+Math.floor((t)/60)+':'+(t)%60),
                            // tickvals:timesteps,
                            // tickformat: "%H:%M:%S s",
                        },
                        yaxis: {
                            title: 'Number of people',
                        },
                        legend: {

                            orientation: "h",
                        }
                    })

                });

            })
            .catch(function (response) {
                console.log(response);
            });
    }

    // show histogram of movement methods  used in the day
    async function processMoveHist(_day) {

        axios.post(api + "/flask/ActualLocationHist", { dir: selectedLogDir, day: _day.toString(), groupBy: 'current_movement_class' })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    _df = _df.withColumn('time', row => row.get('time').split('|').map(e => parseInt(e)));
                    console.log(_df)
                    let gData = [];
                    var timesteps = [...Array(1440).keys()].map((t) => '' + Math.floor((t) / 60).toString().padStart(2, '0') + ':' + ((t) % 60).toString().padStart(2, '0'))
                    _df.map((row) => {
                        try {
                            var trace1 = {
                                x: timesteps,
                                y: row.get('time'),
                                name: row.get('group'),
                                type: "bar",
                                width: 5,
                                marker: { color: movementClassColor[movement.indexOf(row.get('group'))].replace(/[^,]+(?=\))/, '1.0') },
                                // xbins: { size: 5, },
                            };
                            gData.push(trace1);

                        } catch (err) {
                            console.log(err)
                        }

                    })

                    setMoveHistData(gData);
                    setMoveHistLayout({
                        barmode: 'stack',
                        bargap: 0.0,
                        height: 600,
                        width: 1000,
                        title: 'Histogram of used movement methods during the day',
                        xaxis: {
                            title: 'Time',
                            // showticklabels: true,
                            // ticktext:timesteps.map((t)=>''+Math.floor((t)/60)+':'+(t)%60),
                            // tickvals:timesteps,
                            // tickformat: "%H:%M:%S s",
                        },
                        yaxis: {
                            title: 'Number of people',
                        }
                    })

                });

            })
            .catch(function (response) {
                console.log(response);
            });

    }


    // event handlers
    const handleSelectDir = function (_selectedLogDir) {
        getColors(_selectedLogDir)
    }

    const handleDayChange = function (_day) {
        setSelectedDay(_day);

        plotActualLocationHist(_day);
        processRouteHist(_day);
        processMoveHist(_day)


        axios.post(api + "/flask/csvfile", {
            dir: selectedLogDir, d: _day.toString(),
            type: '_person_info', columns: "person|person_class"
        })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data).castAll(Array(2).fill(Number))
                    //set person list for the person path name list
                    let person_class = sub_df.toArray('person_class').map((e) => people[e])
                    let person_id = sub_df.toArray('person')
                    var arr = [];
                    person_id.forEach((e, i) => {
                        arr.push(e + " " + person_class[i])
                    });
                    setUnstagedPeople(arr);
                    setStagedPeople([]);
                    setSelectedUnstagedPeople([])
                    setSelectedStagedPeople([])
                })
            })


    }

    const handleAnalyzePeopleClick = (_selectedPeople) => {


        axios.post(api + "/flask/setpeopleclasses", { dir: selectedLogDir, classes: _selectedPeople.join(',') })
            .then(function (response) {
                //handle success

            })
            .catch(function (response) {
                //handle error
                console.log(response);
            });
    }
    function onTimeTextChange(event) {
        setTimeText(event.target.value);
    };

    function onDrawClick(event) {
        drawLocationDensity()
    }

    const handleSliderChangeNodeX = function (event, newValue) {
        setNodeX(newValue);
    };
    const handleSliderChangeNodeY = function (event, newValue) {
        setNodeY(newValue);
    };
    const handleSliderChangeTimeIdx = function (event, newValue) {
        setTimeIdx(newValue);
    };

    // Daily personal mobility path analysis
    const handleUnstagedClick = function (event) {
        const { options } = event.target;
        const value = [];
        for (let i = 0, l = options.length; i < l; i += 1) {
            if (options[i].selected) {
                value.push(options[i].value);
            }
        }
        setSelectedUnstagedPeople(value);
    }
    const handleStagedClick = function (event) {
        const { options } = event.target;
        const value = [];
        for (let i = 0, l = options.length; i < l; i += 1) {
            if (options[i].selected) {
                value.push(options[i].value);
            }
        }
        setSelectedStagedPeople(value);
    }
    const handleAddtoStageClick = function (event) {
        var _unstagedPeople = []; unstagedPeople.forEach((e => _unstagedPeople.push(e)));
        var _stagedPeople = []; stagedPeople.forEach((e => _stagedPeople.push(e)));
        selectedUnstagedPeople.forEach(element => {
            _stagedPeople.push(element)
            _unstagedPeople.splice(_unstagedPeople.indexOf(element), 1)

        });
        setUnstagedPeople(_unstagedPeople)
        setStagedPeople(_stagedPeople)
        setSelectedUnstagedPeople([])
    }
    const handleAddtoUnstageClick = function (event) {
        var _unstagedPeople = []; unstagedPeople.forEach((e => _unstagedPeople.push(e)));
        var _stagedPeople = []; stagedPeople.forEach((e => _stagedPeople.push(e)));
        selectedStagedPeople.forEach(element => {
            _stagedPeople.splice(_stagedPeople.indexOf(element), 1)
            _unstagedPeople.push(element)
        });
        setUnstagedPeople(_unstagedPeople)
        setStagedPeople(_stagedPeople)
        setSelectedStagedPeople([])
    }

    return (
        <div>
            <div className="results-page">
                <h1>Sim results page 2</h1>
            </div>
            <DirSelect
                onSelect={handleSelectDir}
                onAnalyzePeople={handleAnalyzePeopleClick}
                onDayChange={handleDayChange}
                getLocsArr={getLocsArr}
                getPeopleArr={getPeopleArr}
                getMovementArr={getMovementArr}
                getGroupOptionsArr={getGroupOptionsArr}
                getDirs={setDirs}
                getDays={setDays}
            />
            {/* =================================================================================== Daily mobility data analysis */}
            <div>
                <h4>Daily mobility data analysis</h4>
                <Plot
                    data={locHistData}
                    layout={locHistLayout}
                />
                <Plot
                    data={routeHistData}
                    layout={routeHistLayout}

                />
                <br />
                <Plot
                    data={moveHistData}
                    layout={moveHistLayout}
                />
            </div>
            
            {/* =================================================================================== Paths */}
            <div>
                <h4>Daily personal mobility data analysis</h4>

                <Grid container
                    direction="row"
                    justifyContent="center"
                    alignItems="center"
                >
                    <FormControl>

                        <InputLabel shrink htmlFor="select-multiple-people">
                            Select people that need to show
                        </InputLabel>

                        <Select
                            multiple
                            native
                            value={selectedUnstagedPeople}
                            onChange={handleUnstagedClick}

                            inputProps={{
                                id: 'select-multiple-native',
                            }}
                        >
                            {unstagedPeople.map((element) => (
                                <option key={element} value={element}>
                                    {element}
                                </option>
                            ))}
                        </Select>
                    </FormControl>


                    <Grid>
                        <Grid
                            container
                            direction="column"
                            justifyContent="center"
                            alignItems="center"
                        >

                            <Button variant="contained" color="primary" onClick={handleAddtoStageClick}>{">>"}</Button>
                            <Button variant="contained" color="primary" onClick={handleAddtoUnstageClick}>{"<<"}</Button>
                        </Grid>
                    </Grid>
                    <FormControl >
                        <InputLabel shrink htmlFor="select-multiple-people">
                            Selected people
                        </InputLabel>
                        <Select
                            multiple
                            native
                            value={selectedStagedPeople}
                            onChange={handleStagedClick}

                            inputProps={{
                                id: 'select-multiple-native',
                            }}
                        >
                            {stagedPeople.map((element) => (
                                <option key={element} value={element}>
                                    {element}
                                </option>
                            ))}
                        </Select>
                    </FormControl>
                    <FormControlLabel control={<Checkbox value={showShapes} onChange={() => { setShowShapes(!showShapes) }} defaultChecked />} label="Show Shapes" />

                </Grid>


                <Plot
                    data={personPathData}
                    layout={personPathLayout}
                />

                <Plot
                    data={personPathData2}
                    layout={personPathLayout2}
                    frames={personPathFrames}

                />


            </div>

            {/* =================================================================================================== map */}
            <Grid container rowSpacing={10} columnSpacing={{ xs: 10, sm: 20, md: 30 }}>
                <Grid item xs={3}>
                    <Grid container spacing={2} alignItems="center" padding='10px'>
                        <Grid item xs={8}>
                            <TextField id="outlined-basic" label="Time of day" variant="outlined"
                                onChange={onTimeTextChange}
                                value={timeText} />
                        </Grid>
                        <Grid item xs={8}>
                            <Button onClick={onDrawClick}>Draw location density</Button>
                        </Grid>
                    </Grid>
                </Grid>

                <Grid item xs={10}>
                    <Plot
                        data={mapData}
                        layout={mapLayout}
                        frames={mapFrames}
                    />
                </Grid>
            </Grid>

            <br />
            <div style={{ height: '50px' }}></div>
            {/* =================================================================================================== tree */}
            <Grid container spacing={10} alignItems="center" padding='30px'>
                <Grid item xs={12}>
                    <Typography>Location Tree</Typography>
                    <Button onClick={() => plotLocationTree(selectedDay)}>Draw tree</Button>
                </Grid>
                <Grid container rowSpacing={10} columnSpacing={{ xs: 10, sm: 20, md: 30 }}>
                    <Grid item xs={4}>
                        <Typography>Node X</Typography>
                    </Grid>

                    <Grid item xs={4}>
                        <Typography>Node Y</Typography>
                    </Grid>
                    <Grid item xs={4}>
                        <Typography>Time step</Typography>
                    </Grid>

                    <Grid item xs={4}>
                        <Slider
                            style={{ width: '250px' }}
                            aria-label="Node X"
                            value={nodeX}
                            onChange={handleSliderChangeNodeX}
                            valueLabelDisplay="auto"
                            // step={1}
                            // marks
                            min={1}
                            max={110}
                        />
                    </Grid>
                    <Grid item xs={4}>
                        <Slider
                            style={{ width: '250px' }}
                            aria-label="Node Y"
                            value={nodeY}
                            onChange={handleSliderChangeNodeY}
                            valueLabelDisplay="auto"
                            // step={1}
                            // marks
                            min={1}
                            max={110}
                        />
                    </Grid>
                    <Grid item xs={4}>
                        <Slider
                            style={{ width: '250px' }}
                            aria-label="Time step"
                            value={timeIdx}
                            onChange={handleSliderChangeTimeIdx}
                            valueLabelDisplay="auto"
                            // step={1}
                            // marks
                            min={0}
                            max={timeLen - 1}
                        />
                    </Grid>
                </Grid>

                <div id="treeWrapper" style={{
                    width: '70em', height: '50em', margin: '0 auto', padding: '15px', border: 'black 5px solid'
                }}>
                    <Tree
                        data={locationTreeData}
                        renderCustomNodeElement={(nodeDatum, toggleNode) => renderNode(nodeDatum, toggleNode, timeIdx)}
                        orientation="vertical"
                        nodeSize={{ x: nodeX, y: nodeY }}
                        pathClassFunc={getDynamicPathClass}
                    />

                </div>


            </Grid>




        </div>
    )
}


export default ResultsPage2;