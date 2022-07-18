import React, { useState, useRef, useEffect } from "react";
// import * as d3 from d3;

import Grid from '@material-ui/core/Grid';
import * as Plotly from 'plotly.js';
import Plot from 'react-plotly.js';
import { csvJSON, csv2JSONarr, strip_text } from "../utils/files";
import { hist, padZeros } from "../utils/functions";

import { styled } from '@material-ui/core/styles';

import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';

import FormLabel from '@material-ui/core/FormLabel';
import Radio from '@material-ui/core/Radio';
import RadioGroup from '@material-ui/core/RadioGroup';
import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import Tooltip from "@material-ui/core/Tooltip";

import Typography from '@material-ui/core/Typography';
import Slider from '@material-ui/core/Slider';
import Checkbox from '@material-ui/core/Checkbox';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import Tree from 'react-d3-tree';
import './nodestyles.css'

import randomColor from "randomcolor";

import DirSelect from "../components/DirSelect";

import DataFrame from 'dataframe-js';
import axios from 'axios'
import { api } from '../utils/constants';
import { Box, Menu, TextField } from "@material-ui/core";

function ResultsPage() {
    const height = 500;
    const width = 700;

    const [dirs, setDirs] = useState([]);
    const [days, setDays] = useState([]);

    const [initialLoad, setInitialLoad] = useState(true);
    const [loadprogress, setLoadprogress] = useState(0);

    const [locs, setLocs] = useState([]);
    const [people, setPeople] = useState([]);
    const [movement, setMovement] = useState([]);
    const [groupOptions, setGroupOptions] = useState([]);

    const [selectedLogDir, setSelectedLogDir] = useState('');
    const [selectedDay, setSelectedDay] = useState('');

    const [selectedGroup, setSelectedGroup] = useState('');
    const [selectedState, setSelectedState] = useState(1);

    const [peoplePieData, setpeoplePieData] = useState([]);

    const [peopleClassColors, setPeopleClassColor] = useState({});
    const [locationClassColor, setLocationClassColor] = useState({});
    const [movementClassColor, setMovementClassColor] = useState({});

    const [stateOptions, setStateOptions] = useState([1, 2, 3, 4]);
    const [timelineOptions, setTimelineOptions] = useState([]);
    const [selectedTimelineOptions, setSelectedTimelineOptions] = useState({});

    const [stagedLogDirs, setStagedLogDirs] = useState([]);
    const [selectedUnstagedLogDirs, setSelectedUnstagedLogDirs] = useState([]);
    const [selectedStagedLogDirs, setSelectedStagedLogDirs] = useState([]);


    const [infectionTreeData, setInfectionTreeData] = useState({ name: 'ROOT' });
    const [infectionTreeColor, setInfectionTreeColor] = useState("0");


    const [infectionsData3D, setInfectionsData3D] = useState([]);
    const [infectionsLayout3D, setInfectionsLayout3D] = useState([]);

    const [contactData3D, setContactData3D] = useState([]);
    const [contactLayout3D, setContactLayout3D] = useState([]);
    const [groupNames, setGroupNames] = useState([]);
    const [contactHistTraces, setContactHistTraces] = useState([]);
    const [contactLineTraces, setContactLineTraces] = useState([]);

    const [contactLocHistData, setContactLocHistData] = useState([]);
    const [contactLocHistLayout, setContactLocHistLayout] = useState([]);
    const [contactPeopleHistData, setContactPeopleHistData] = useState([]);
    const [contactPeopleHistLayout, setContactPeopleHistLayout] = useState([]);
    const [contactPeopleTimeData, setContactPeopleTimeData] = useState([]);
    const [contactPeopleTimeLayout, setContactPeopleTimeLayout] = useState([]);
    const [contactLocationTimeData, setContactLocationTimeData] = useState([]);
    const [contactLocationTimeLayout, setContactLocationTimeLayout] = useState([]);

    const [checkNormalize, setCheckNormalize] = useState(false);
    const [checkRatio, setCheckRatio] = useState(false);


    const [nodeX, setNodeX] = useState(5);
    const [nodeY, setNodeY] = useState(30);


    useEffect(() => {
        axios.get(api + '/flask/dirs').then(response => {
            setDirs(response.data.message.split(','))
        }).catch(error => {
            console.log(error)
        })
    }, [initialLoad])

    useEffect(() => {
        drawStatesInDay()
        processPieData()
    }, [selectedDay])

    useEffect(() => {
        plotInfectionTree()
        plotVariantTimeline()
    }, [selectedLogDir])


    useEffect(() => {
        drawStatesInDay()
    }, [selectedState])
    // useEffect(() => {
    //     onContactTimelineChange();
    // }, [checkNormalize, checkRatio])


    const handleSelectDir = function (_selectedLogDir) {

        getColors(_selectedLogDir)
        setStagedLogDirs([_selectedLogDir])


    }

    const handleDayChange = function (_day) {
        setSelectedDay(_day);
    }

    const handleAnalyzePeopleClick = (_selectedPeople) => {


        axios.post(api + "/flask/setpeopleclasses", { dir: selectedLogDir, classes: _selectedPeople.join(',') })
            .then(function (response) {

            })
            .catch(function (response) {
                //handle error
                console.log(response);
            });
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
    // get the population occupation pie data
    async function processPieData() {
        console.log("loading data for pie chart of people")
        axios.post(api + "/flask/csvfile", {
            dir: selectedLogDir, d: selectedDay,
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
                    setpeoplePieData({ labels: pieLabels, values: pieData })
                    // })

                })
            })
    }
    // ===========================================================================================================================================
    // draw covid data timeline
    async function drawCovidStateTimeline() {
        let _line_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf',
            'rgb(255, 50,100)', 'rgb(200, 100,50)', 'rgb(250, 0,100)', 'rgb(50, 50,255)', 'rgb(0, 255,100)', 'rgb(50, 150,0)', 'rgb(50, 150,50)',]
        let _line_types = ["solid", "dot", "dash", "dashdot", "longdash", "longdashdot"]
        var _line_type_i = 0
        console.log(selectedTimelineOptions)
        axios.post(api + "/flask/peoplestatetimeline", {
            dir: stagedLogDirs.join('#'),
            parameters: Object.keys(selectedTimelineOptions).filter(e => selectedTimelineOptions[e]).join("#"),
            end_only: true,
            window: 3,
            group_curves: document.getElementById("group_curves_cb").checked,
            plot_checkp: document.getElementById("plot_checkp_cb").checked
        })
            .then(function (response) {
                var _max = 0;
                const data = response.data.data;

                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var df = new DataFrame(json_data)
                    // df = df.castAll(Array(df.listColumns().length).fill(Number))
                    console.log("Covid data", df)
                    let _x = df.select("time").toArray().map((e) => e[0])
                    let _df_arr = df.toArray()
                    let _df_col = df.listColumns()
                    let _data = []
                    for (var i = 0; i < _x.length; i++) {
                        var datum = {}
                        for (var j = 0; j < _df_col.length; j++) {
                            datum[_df_col[j]] = _df_arr[i][j]
                        }
                        _data.push(datum)
                    }

                    _df_col.splice(_df_col.indexOf('time'), 1)
                    _df_col.splice(_df_col.indexOf('Type'), 1)

                    if (timelineOptions.length == 0) {
                        setTimelineOptions(_df_col)
                    }
                    _data.sort(function (a, b) {
                        return ((parseFloat(a.time) < parseFloat(b.time)) ? -1 : ((parseFloat(a.time) == parseFloat(b.time)) ? 0 : 1));
                    });
                    console.log(_data, _df_col)

                    let traces = []
                    var shapes = []
                    var annotations = []
                    // if (append) {
                    //     var prev_data = document.getElementById("stateTimeline").data
                    //     var _prev_log = ''
                    //     prev_data.forEach(element => {
                    //         traces.push(element)
                    //         if (element.dir_name != _prev_log) {
                    //             _prev_log = element.dir_name
                    //             _line_type_i++
                    //         }
                    //     });
                    // }
                    var grouped = df.groupBy("Type")
                    grouped.aggregate((_df, dir) => {
                        dir = dir["Type"]
                        console.log("Type", dir, _df)
                        _df_col.forEach(col => {
                            if (col == "time")
                                return
                            if (col.indexOf("Re") != -1) {
                                var trace1 = {
                                    x: _df.select('time').toArray().map((e) => parseFloat(e)),
                                    y: _df.select(col).toArray().map((e) => parseFloat(e)),
                                    name: col,
                                    dir_name: dir,
                                    legendgroup: dir,
                                    showlegend: _line_type_i == 0,
                                    mode: 'lines',
                                    line: { dash: _line_types[_line_type_i], color: _line_colors[_df_col.indexOf(col)] },
                                    visible: true,
                                    yaxis: 'y2',
                                }
                            } else {
                                var trace1 = {
                                    x: _df.select('time').toArray().map((e) => parseFloat(e)),
                                    y: _df.select(col).toArray().map((e) => parseFloat(e)),
                                    name: col,
                                    dir_name: dir,
                                    legendgroup: dir,
                                    showlegend: _line_type_i == 0,
                                    mode: 'lines',
                                    line: { dash: _line_types[_line_type_i], color: _line_colors[_df_col.indexOf(col)] },
                                    visible: true,
                                }
                            }

                            var tmp_max = Math.max(_max, ...trace1.y)
                            if (!isNaN(tmp_max))
                                _max = tmp_max
                            console.log(_max)
                            traces.push(trace1)
                        })

                        traces.push({
                            x: [0, 0], y: [0, 0], visible: 'true', mode: 'lines', marker: {},
                            dir_name: dir, name: dir,
                            line: { dash: _line_types[_line_type_i], color: 'black' }
                        })

                        console.log(traces)
                        axios.post(api + "/flask/load_args", { dir: dir }).then(response => {
                            var args = response.data
                            var addedContainmentEvents = Object.values(JSON.parse(args.addedContainmentEvents))
                            var addedGatheringEvents = Object.values(JSON.parse(args.addedGatheringEvents))
                            var addedVaccinationEvents = Object.values(JSON.parse(args.addedVaccinationEvents))

                            var dx = 1
                            addedContainmentEvents.forEach(e => {
                                var x = parseFloat(e.startday)
                                shapes.push({
                                    type: 'line', x0: x, y0: 0, x1: x, y1: _max,
                                    line: {
                                        color: 'rgb(55, 128, 191)',
                                        width: 3,
                                        dash: 'dashdot'
                                    }
                                })
                                annotations.push({
                                    x: x - dx,
                                    y: _max / 2,
                                    xref: 'x',
                                    yref: 'y',
                                    text: e.containment_strategy,
                                    textangle: -90,
                                    showarrow: false,

                                })
                            })

                            addedGatheringEvents.forEach(e => {
                                var x = parseFloat(e.day) - 1
                                shapes.push({
                                    type: 'line', x0: x, y0: 0, x1: x, y1: _max,
                                    line: {
                                        color: 'rgb(55, 128, 191)',
                                        width: 3,
                                        dash: 'dotted'
                                    }
                                })
                                annotations.push({
                                    x: x - dx,
                                    y: _max / 2,
                                    xref: 'x',
                                    yref: 'y',
                                    text: "Gathering",
                                    textangle: -90,
                                    showarrow: false,

                                })
                            })
                            addedVaccinationEvents.forEach(e => {
                                var x = parseFloat(e.day)
                                shapes.push({
                                    type: 'line', x0: x, y0: 0, x1: x, y1: _max,
                                    line: {
                                        color: 'rgb(55, 128, 191)',
                                        width: 3,
                                        dash: 'dotted'
                                    }
                                })
                                annotations.push({
                                    x: x - dx,
                                    y: _max / 2,
                                    xref: 'x',
                                    yref: 'y',
                                    text: "Vaccine for age " + e.min_age + " to " + e.max_age,
                                    textangle: -90,
                                    showarrow: false,

                                })
                            })
                        })
                        if (!document.getElementById("plot_checkp_cb").checked)
                            shapes = []
                        annotations = []
                        _line_type_i++
                        Plotly.newPlot("stateTimeline", traces, {
                            title: '',
                            height: height,
                            width: width,
                            shapes: shapes,
                            annotations: annotations,
                            legend: {
                                x: 0.05,
                                y: 1,
                                orientation: "v",
                                traceorder: "grouped",
                            },
                            xaxis: {
                                title: 'Time (days)',
                                showticklabels: true,
                                tickangle: 'auto',
                                exponentformat: 'e',
                                showexponent: 'all'
                            },
                            yaxis: {
                                title: 'Number of people',
                                showticklabels: true,
                                exponentformat: 'e',
                                showexponent: 'all',
                                visible: true,
                                // visible: false
                            },
                            yaxis2: {
                                title: 'Reproduction number',
                                overlaying: 'y',
                                side: 'left',
                                // visible: true,
                                visible: false
                            }
                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'kandy_simulation',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            editable: true
                        })
                    })


                });

            });



    }

    async function drawStatesInDay() {
        axios.post(api + "/flask/csvfile", { dir: selectedLogDir, d: selectedDay.toString(), type: '_person_info' })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    // _df = _df.castAll(Array(_df.listColumns().length).fill(Number))
                    console.log("Person data", selectedDay, _df)

                    var traces = []

                    var grouped = _df.groupBy('person_class')
                    grouped.aggregate((g, pc) => {
                        try {
                            pc = pc['person_class']

                            // console.log(g.filter(row=>row.get('state')==selectedState ))
                            traces.push({
                                x: g.filter(row => row.get('state') == selectedState).select('age').toArray().map((e) => e[0]),
                                name: people[pc],
                                marker: { color: peopleClassColors[pc].replace(/[^,]+(?=\))/, '1.0') },
                                type: 'histogram',
                            })

                        } catch (error) {

                        }
                    });
                    Plotly.newPlot("statesDay", traces, {
                        barmode: 'stack',
                        height: height,
                        width: width,
                        xaxis: { title: 'Age' },
                        yaxis: { title: "Number of people in state - " + selectedState },
                    }, {
                        toImageButtonOptions: {
                            format: 'svg',
                            filename: 'states_in_day',
                            height: height,
                            width: width,
                            scale: 1
                        },
                        editable: true
                    })
                });
            });
    }

    // draw infection tree
    const renderRectSvgNode = ({ nodeDatum, toggleNode }) => {
        var color = "black"
        if (infectionTreeColor == "0") {
            color = peopleClassColors[nodeDatum.attributes?.class_number]
        } else if (infectionTreeColor == "1") {
            if (nodeDatum.attributes?.infected_loc_class != "-1")
                color = locationClassColor[nodeDatum.attributes?.infected_loc_class]
        }
        // var tooltip = d3.select("body")
        //                 .append("div")
        //                 .attr("class", "my-tooltip")//add the tooltip class
        //                 .style("position", "absolute")
        //                 .style("z-index", "10")
        //                 .style("visibility", "hidden");
        // console.log(color,nodeDatum.class_number)
        // const HtmlTooltip = styled(({ className, ...props }) => (
        //     <Tooltip {...props} classes={{ popper: className }} />
        // ))(({ theme }) => ({
        //     [`& .${tooltipClasses.tooltip}`]: {
        //         backgroundColor: '#f5f5f9',
        //         color: 'rgba(0, 0, 0, 0.87)',
        //         maxWidth: 220,
        //         fontSize: theme.typography.pxToRem(12),
        //         border: '1px solid #dadde9',
        //     },
        // }));
        const mins2time = (mins) => {
            return Math.floor(mins / 60) + ":" + mins % 60
        }
        return (
            <g>
                <Tooltip
                    title={
                        <React.Fragment>
                            <Typography color="inherit">Details of {nodeDatum.name}</Typography>
                            <em>{"Occupation:"}</em> <b>{people[nodeDatum.attributes?.class_number]}</b><br />
                            <em>{"Infected Day:"}</em> <b>{Math.ceil(nodeDatum.attributes?.infect_time / 1440)}</b><br />
                            <em>{"Infected Time:"}</em> <b>{mins2time(nodeDatum.attributes?.infect_time % 1440)}</b><br />
                            <em>{"Infected Location:"}</em> <b>{nodeDatum.attributes?.infected_loc}</b><br />
                            <em>{"Infected Location type:"}</em> <b>{locs[nodeDatum.attributes?.infected_loc_class]}</b><br />
                        </React.Fragment>
                    }>
                    <circle r="4" x="-4" fill={color} stroke="none" onClick={toggleNode} />
                </Tooltip>

            </g>
        );
    }

    const getDynamicPathClass = ({ source, target }, orientation) => {

        // const BlueOnGreenTooltip = withStyles({
        //     tooltip: {
        //       color: "lightblue",
        //       backgroundColor: "green"
        //     }
        //   })(Tooltip);
        if (!target.children) {
            // Target node has no children -> this link leads to a leaf node.
            return 'linkbranch';
        }

        // Style it as a link connecting two branch nodes by default.
        return 'linkleaf';
    };

    async function plotInfectionTree() {
        axios.post(api + "/flask/infectiontree", { dir: selectedLogDir })
            .then(function (response) {
                const json = response.data.json;
                const json_data = JSON.parse(json)
                setInfectionTreeData(json_data);

                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data)
                    console.log("infection tree", sub_df)

                    Plotly.newPlot("infectionGraph", [
                        {
                            type: "sunburst", //sunburst
                            ids: sub_df.toArray('id'),
                            labels: sub_df.toArray('id'),
                            parents: sub_df.toArray('parent'),
                            value: sub_df.toArray('time')
                        }
                    ], {
                        title: 'Infection tree',
                        height: height,
                        width: width,
                    }, {
                        toImageButtonOptions: {
                            format: 'svg',
                            filename: 'infection_tree',
                            height: height,
                            width: width,
                            scale: 1
                        },
                        editable: true
                    })
                    csv2JSONarr(response.data.inf_occ_count, (pr) => { }).then((json_data) => {
                        console.log(json_data, people)
                        Plotly.newPlot("infectionOccupationBar", [
                            {
                                x: json_data[""].map(e => people[e]),
                                y: json_data["parents_class"],
                                type: 'bar'
                            }
                        ], {
                            title: "",
                            height: height,
                            width: width,
                            xaxis: {
                                tickangle: -45,
                                automargin: true,
                            },
                            yaxis: {
                                title: "Infections per person in the group"
                            },
                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'infected_occupations_hist',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            editable: true
                        })
                    })

                    csv2JSONarr(response.data.inf_loc_count, (pr) => { }).then((json_data) => {
                        console.log(json_data, locs)
                        Plotly.newPlot("infectionLocationBar", [
                            {
                                x: json_data[""].map(e => locs[e]),
                                y: json_data["infected_loc_class"],

                                type: 'bar'
                            }
                        ], {
                            title: "",
                            height: height,
                            width: width,
                            xaxis: {
                                tickangle: -45,
                                automargin: true,
                            },
                            yaxis: {
                                title: "Infections"
                            },
                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'infected_locations_hist',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            editable: true
                        })
                    })
                });

            })
            .catch(function (response) {
                console.log(response);
            });

    }


    // plot infection state timeline
    async function plotInfectionStateTimeline() {
        axios.post(api + "/flask/infectionstatetimeline", { dir: selectedLogDir }).then(response => {
            const data = response.data.data
            csv2JSONarr(data, () => { }).then(json => {
                var df = new DataFrame(json)
                console.log(df)
                const [people, n_days] = df.dim()
                const _days = df.listColumns()

                Plotly.newPlot("infection-state-timeline", [{
                    x: Array(people).keys(),
                    y: _days,
                    z: df.toArray(),
                    type: 'heatmap'
                }], {
                    title: '',
                    height: height,
                    width: width,
                    yaxis: {
                        tickangle: -45,
                        automargin: true,
                    },
                    autosize: false,
                }, {
                    toImageButtonOptions: {
                        format: 'svg',
                        filename: 'infection_state_2d',
                        height: height,
                        width: width,
                        scale: 1
                    },
                    editable: true
                })

                var m = df.toArray()

                var time_dict = {}
                for (let pid = 0; pid < people; pid++) {
                    var unique = m[pid].filter((v, i, a) => a.indexOf(v) === i)
                    unique.forEach((e) => {
                        if (!time_dict.hasOwnProperty(e))
                            time_dict[e] = []

                        time_dict[e].push(_days[m[pid].indexOf(e)] - _days[m[pid].indexOf('3')])
                    })
                }
                var violin_data = []
                var key2name = { '1': 'Susceptible', '3': 'Infected', '4': 'Infectious', '5': 'Mild', '6': 'Severe', '7': 'Critical', '9': 'Recovered', '10': 'Dead' }
                for (let key in time_dict) {
                    if (key == '1')
                        continue
                    violin_data.push({
                        // y0: key,
                        x: time_dict[key].filter((e) => !isNaN(e)),
                        hoveron: "points+kde",
                        meanline: {
                            visible: true
                        },
                        // legendgroup: "M",
                        // scalegroup: "M",
                        points: "all",
                        pointpos: -0.9,
                        box: {
                            visible: true
                        },
                        jitter: 0,
                        scalemode: "count",
                        marker: {
                            line: {
                                width: 2,
                                // color: "#8dd3c7"
                            },
                            symbol: "line-ns"
                        },
                        showlegend: true,
                        // side: "negative",
                        type: "violin",
                        name: key2name[key],
                        span: [
                            0
                        ],
                        // line: {
                        //     color: "#8dd3c7"
                        // },
                        orientation: "h"
                    })
                }
                console.log(violin_data)
                Plotly.newPlot("infection-state-violin", violin_data,
                    {
                        title: "",
                        height: height,
                        width: width,
                        xaxis: {
                            title: "Number of days"
                        },
                        yaxis: {
                            tickangle: -45,
                            automargin: true,
                            zeroline: false,
                            showgrid: true
                        },
                        violingap: 0,
                        violingroupgap: 0,
                        violinmode: "overlay",
                        legend: {
                            x: 0.85,
                            y: 0.1,
                            traceorder: "normal",

                        }
                    }, {
                    toImageButtonOptions: {
                        format: 'svg',
                        filename: 'infection_state_violin',
                        height: height,
                        width: width,
                        scale: 1
                    },
                    editable: true
                })


            })
        })
    }

    // plot variant timeline
    async function plotVariantTimeline() {
        axios.post(api + "/flask/variants", { dir: selectedLogDir }).then(response => {
            const data = response.data.df_norm
            csv2JSONarr(data, (pr) => { }).then((json_data) => {
                var _df = new DataFrame(json_data)
                var traces = []
                var cols = _df.listColumns()
                for (var i = 0; i < cols.length; i++) {
                    traces.push(
                        {
                            y: _df.select(cols[i]).toArray().map(e => e[0]),
                            name: cols[i],
                            type: "bar",
                        }
                    )
                }
                console.log(traces)
                Plotly.newPlot("variantTimeline", traces, {
                    height: height,
                    width: width,
                    barmode: 'stack',
                    bargap: 0,
                    xaxis: {
                        title: 'Day',
                    },
                    showlegend: true,
                }, {
                    toImageButtonOptions: {
                        format: 'svg',
                        filename: 'variant_ratio_variation',
                        height: height,
                        width: width,
                        scale: 1
                    },
                    editable: true
                })
            })
        })
    }

    // plot new infections grouped
    function plotNewInfections() {
        axios.post(api + "/flask/newinfections", { dir: selectedLogDir, group_by: selectedGroup })
            .then(function (response) {
                const infectionsData = response.data.infections;
                const countData = response.data.count;
                csv2JSONarr(infectionsData, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    csv2JSONarr(countData, (pr) => { }).then((json_data) => {
                        var count_df = new DataFrame(json_data)
                        console.log("Infection data", _df, "count data", count_df)

                        let group_names = _df.listColumns();
                        let x = []
                        let y = []
                        let z = []
                        let v = []
                        let heatMap = []
                        let _df_arr = _df.toArray()
                        let count_df_arr = count_df.select('infected').toArray().map((e) => e[0].split(' '))
                        var max_v = 0;
                        console.log(_df, _df_arr, count_df_arr)
                        for (var X = 0; X < group_names.length; X++) {
                            heatMap.push([])
                            var source_count = count_df_arr[X].map((e) => parseInt(e)).map((e) => e == 0 ? e + 1 : e)
                            for (var Y = 0; Y < group_names.length; Y++) {
                                var vals = _df_arr[X][Y].split(' ')//.map(Math.log)
                                var avg_infections = 0;
                                for (var t = 0; t < vals.length; t++) { //vals.reduce((a, b) => parseInt(a) + parseInt(b), 0)
                                    avg_infections += vals[t] / source_count[t]
                                }
                                heatMap[heatMap.length - 1].push(avg_infections / vals.length)
                                for (var Z = 0; Z < vals.length; Z++) {
                                    x.push(X)
                                    y.push(Y)
                                    z.push(Z)
                                    v.push(vals[Z])
                                    max_v = Math.max(max_v, vals[Z])
                                }
                            }
                        }

                        let plotData = [{
                            type: 'volume',
                            x: x,
                            y: y,
                            z: z,
                            value: v,
                            colorscale: 'RdBu',
                            isomin: 0,
                            isomax: max_v,
                            opacity: 0.1,
                            surface: { count: 300 },
                        }]

                        setInfectionsData3D(plotData)
                        setInfectionsLayout3D({
                            // title: 'Number of New Infections for each group',
                            height: height,
                            width: width,
                            scene: {
                                xaxis: {
                                    title: '',
                                    ticktext: _df.listColumns(),
                                    tickvals: [...Array(_df.listColumns().length).keys()]
                                },
                                yaxis: {
                                    title: '',
                                    ticktext: _df.listColumns(),
                                    tickvals: [...Array(_df.listColumns().length).keys()]
                                },
                                zaxis: {
                                    title: 'Day',
                                }
                            }
                        })
                        Plotly.newPlot("infectionsHeatMap2D", [{
                            x: group_names,
                            y: group_names,
                            z: heatMap,
                            type: 'heatmap'
                        }], {
                            // title: 'Average number of disease transmissions from infected group per day \n(normalized by number of infected people in each group)',
                            height: height,
                            width: width,
                            yaxis: { tickangle: -45, automargin: true, title: "Transmitted group" },
                            xaxis: { title: "Received group", tickangle: -45, automargin: true, },
                            autosize: false,
                            // margin: {
                            //     l: 50,
                            //     r: 50,
                            //     b: 100,
                            //     t: 100,
                            //     pad: 4
                            //   },

                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'transmission_distribution_',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            // editable: true
                        })

                        var line_traces = [];
                        var hist_traces = [];
                        var ratio_traces = [];
                        var axis = 1;
                        var subplots = [];
                        var annotations = []
                        for (var X = 0; X < group_names.length; X++) {
                            var yaxis = 'y' + axis
                            if (axis == 1) {
                                yaxis = 'y'
                            }

                            for (var Y = 0; Y < group_names.length; Y++) {
                                var vals = _df_arr[X][Y].split(' ')//.map(Math.log)
                                line_traces.push({
                                    y: vals,
                                    name: group_names[Y],
                                    type: "line",
                                    marker: { color: selectedGroup == 'person_class' ? peopleClassColors[group_names[Y]].replace(/[^,]+(?=\))/, '1.0') : '' },
                                    xaxis: 'x',
                                    yaxis: yaxis,
                                    legendgroup: axis
                                })
                                hist_traces.push({
                                    x: vals.filter((e) => e > 0),
                                    xaxis: 'x',
                                    yaxis: yaxis,
                                    name: group_names[Y],
                                    marker: { color: selectedGroup == 'person_class' ? peopleClassColors[group_names[Y]].replace(/[^,]+(?=\))/, '1.0') : '' },
                                    type: "histogram",
                                    legendgroup: axis
                                })
                            }
                            subplots.push(['x' + yaxis])
                            annotations.push({
                                text: group_names[X],
                                showarrow: false,
                                align: 'center',
                                x: 0.1,
                                y: 0.9,
                                xref: 'paper',
                                yref: yaxis + " domain",
                            })
                            axis++
                        }



                        Plotly.newPlot("infectionsTime2D", line_traces, {
                            // title: 'Number of new infections for each group throughout time',
                            height: height,
                            width: width,
                            annotations: [...annotations, {
                                y: 0.5,
                                x: -0.1,
                                xref: 'paper',
                                yref: 'paper',
                                text: 'Number of infections',
                                showarrow: false,
                                textangle: -90
                            }],
                            grid: {
                                subplots: subplots,
                                rows: group_names.length,
                                columns: 1,
                                pattern: 'independent',
                            },
                            xaxis: {
                                title: 'Days',
                            },
                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'new_infections_group_time',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            // editable: true
                        })
                        Plotly.newPlot("infectionsHist2D", hist_traces, {
                            // title: 'Frequency of new infections per day for each group',
                            height: height,
                            width: width,
                            barmode: 'stack',
                            annotations: [...annotations, {
                                y: 0.5,
                                x: -0.1,
                                xref: 'paper',
                                yref: 'paper',
                                text: 'Frequency',
                                showarrow: false,
                                textangle: -90
                            }], grid: {
                                subplots: subplots,
                                rows: group_names.length,
                                columns: 1,
                                pattern: 'independent',
                            },
                            xaxis: {
                                title: 'Number of new infections',
                            },
                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'hist_new_infections_group_time',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            // editable: true
                        })
                        var p_count = count_df.select('total_count').toArray().map((e) => e[0])
                        for (var X = 0; X < group_names.length; X++) {
                            var temp = new Array(_df_arr[X][0].split(' ').length).fill(0);
                            for (var Y = 0; Y < group_names.length; Y++) {
                                var vals = _df_arr[Y][X].split(' ').map(parseFloat)
                                for (var i = 0; i < vals.length; i++) {
                                    temp[i] += vals[i];
                                }
                            }
                            // normalize by # of people in each class
                            for (var i = 0; i < temp.length; i++) {
                                temp[i] /= p_count[X]
                            }
                            ratio_traces.push({
                                y: temp,
                                name: group_names[X],
                                marker: { color: selectedGroup == 'person_class' ? peopleClassColors[group_names[X]].replace(/[^,]+(?=\))/, '1.0') : '' },
                                type: "bar"
                            })
                        }
                        console.log(ratio_traces)
                        Plotly.newPlot("infectionsCount", ratio_traces, {
                            height: height,
                            width: width,
                            barmode: "stack",
                            bargap: 0,
                            xaxis: {
                                title: 'Days',
                            },
                            yaxis: {
                                title: 'New infections per person',
                            },

                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'new_infections_day_norm',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            editable: true
                        })

                        for (var i = 0; i < ratio_traces.length; i++) {
                            for (var j = 1; j < ratio_traces[i]['y'].length; j++) {
                                if (isNaN(ratio_traces[i]['y'][j - 1]))
                                    continue
                                ratio_traces[i]['y'][j] += ratio_traces[i]['y'][j - 1]
                            }
                            console.log(ratio_traces[i])
                        }
                        Plotly.newPlot("infectionsCountCumSum", ratio_traces, {
                            // title: '# of infections for each group throughout time per person',
                            height: height,
                            width: width,
                            barmode: "stack",
                            bargap: 0,
                            xaxis: {
                                title: 'Days',
                            },
                            yaxis: {
                                title: 'Cumulative infections',
                            },
                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'cum_infections',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            editable: true
                        })
                        for (var j = 0; j < ratio_traces[0].y.length; j++) {
                            var tot = 0
                            for (var i = 0; i < ratio_traces.length; i++) {
                                if (isNaN(ratio_traces[i].y[j]))
                                    continue
                                tot += ratio_traces[i].y[j]
                            }
                            if (tot == 0)
                                continue
                            for (var i = 0; i < ratio_traces.length; i++) {
                                ratio_traces[i].y[j] = 100 * ratio_traces[i].y[j] / tot
                            }
                        }
                        Plotly.newPlot("infectionsCountCumSumRatio", ratio_traces, {
                            // title: '% of infections for each group throughout time per person',
                            height: height,
                            width: width,
                            barmode: "stack",
                            bargap: 0,
                            xaxis: {
                                title: 'Days',
                            },
                            yaxis: {
                                title: '% of infections',
                            },
                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'infection_ratio_variation',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            editable: true
                        })
                        console.log("heatmap", heatMap)
                    })
                });
            })
    }

    // plot number of contacts grouped
    function plotNumberOfContacts() {
        axios.post(api + "/flask/contacts", {
            dir: selectedLogDir, group_by1: document.getElementById("select-group1").textContent,
            group_by2: document.getElementById("select-group2").textContent, start_day: document.getElementById("cstart_day").value, end_day: document.getElementById("cend_day").value
        })
            .then(function (response) {
                const contactData = response.data.contacts;
                const countData = response.data.count;
                const index = response.data.index;
                csv2JSONarr(contactData, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    console.log("Contacts", _df)
                    csv2JSONarr(countData, (pr) => { }).then((json_data) => {
                        var count_df = new DataFrame(json_data)
                        console.log("Contact group count", count_df)
                        let count_df_arr = count_df.select('count').toArray().map((e) => e[0] + 1)
                        let group_names2 = _df.listColumns();
                        let group_names1 = index;
                        setGroupNames(group_names1)
                        let x = []
                        let y = []
                        let z = []
                        let v = []
                        let heatMap = []
                        let _df_arr = _df.toArray()
                        var max_v = 0;
                        console.log(_df, _df_arr)
                        for (var X = 0; X < group_names1.length; X++) {
                            heatMap.push([])
                            for (var Y = 0; Y < group_names2.length; Y++) {
                                var vals = _df_arr[X][Y].split(' ')//.map(Math.log)
                                var tot_con = 0
                                for (var Z = 0; Z < vals.length; Z++) {
                                    x.push(X)
                                    y.push(Y)
                                    z.push(Z)
                                    v.push(vals[Z])
                                    max_v = Math.max(max_v, vals[Z])
                                    tot_con += parseInt(vals[Z])
                                }
                                heatMap[heatMap.length - 1].push(tot_con / count_df_arr[X] / vals.length)
                            }
                        }
                        console.log("heatmap", heatMap)
                        let plotData = [{
                            type: 'volume',
                            x: x,
                            y: y,
                            z: z,
                            value: v,
                            colorscale: 'RdBu',
                            isomin: 0,
                            isomax: max_v,
                            opacity: 0.1,
                            surface: { count: 300 },
                        }]

                        setContactData3D(plotData)
                        setContactLayout3D({
                            title: 'Number of contacts for each group',
                            width: width,
                            height: height,
                            scene: {
                                xaxis: {
                                    title: '',
                                    ticktext: _df.listColumns(),
                                    tickvals: [...Array(_df.listColumns().length).keys()]
                                },
                                yaxis: {
                                    title: '',
                                    ticktext: _df.listColumns(),
                                    tickvals: [...Array(_df.listColumns().length).keys()]
                                },
                                zaxis: {
                                    title: 'Day',
                                }
                            }
                        })

                        var line_traces = [];
                        var hist_traces = [];
                        var axis = 1;
                        var subplots = [];
                        var annotations = []
                        for (var X = 0; X < group_names1.length; X++) {
                            var yaxis = 'y' + axis
                            if (axis == 1) {
                                yaxis = 'y'
                            }
                            for (var Y = 0; Y < group_names2.length; Y++) {
                                var vals = _df_arr[X][Y].split(' ')//.map(Math.log)
                                line_traces.push({
                                    y: vals,
                                    name: group_names2[Y],
                                    type: "line",
                                    xaxis: 'x',
                                    yaxis: yaxis,
                                    legendgroup: group_names1[X]
                                })
                                hist_traces.push({
                                    x: vals,
                                    xaxis: 'x',
                                    yaxis: yaxis,
                                    name: group_names2[Y],
                                    type: "histogram",
                                    legendgroup: group_names1[X]
                                })
                            }
                            subplots.push(['x' + yaxis])
                            annotations.push({
                                text: group_names1[X],
                                showarrow: false,
                                align: 'center',
                                x: 0.1,
                                y: 0.9,
                                xref: 'paper',
                                yref: yaxis + " domain",
                            })
                            axis++
                        }
                        setContactHistTraces(hist_traces)
                        setContactLineTraces(line_traces)
                        Plotly.newPlot("contactTime2D", line_traces, {
                            title: 'Number of contacts for each group throughout time',
                            width: width,
                            height: height * 2,
                            annotations: [...annotations, {
                                y: 0.5,
                                x: -0.1,
                                xref: 'paper',
                                yref: 'paper',
                                text: 'Number of contacts',
                                showarrow: false,
                                textangle: -90
                            }],
                            grid: {
                                subplots: subplots,
                                rows: group_names1.length,
                                columns: 1,
                                pattern: 'independent',
                            },
                            xaxis: {
                                title: 'Days',
                            },
                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'contacts_throughout_time',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            // editable: true
                        })
                        Plotly.newPlot("contactHist2D", hist_traces, {
                            title: 'Frequency of contacts per day for each group',
                            width: width,
                            height: height * 2,
                            barmode: 'stack',
                            annotations: [...annotations, {
                                y: 0.5,
                                x: -0.1,
                                xref: 'paper',
                                yref: 'paper',
                                text: 'Frequency',
                                showarrow: false,
                                textangle: -90
                            }], grid: {
                                subplots: subplots,
                                rows: group_names1.length,
                                columns: 1,
                                pattern: 'independent',
                            },
                            xaxis: {
                                title: 'Number of contacts',
                            },
                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'contacts_freq',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            // editable: true
                        })

                        Plotly.newPlot("contactHeatMap2D", [{
                            x: group_names1,
                            y: group_names2,
                            z: heatMap,
                            type: 'heatmap'
                        }], {
                            title: 'Avg contacts per person in each group',
                            width: width,
                            height: height,
                            yaxis: {
                                tickangle: -45,
                                automargin: true,
                            },

                        }, {
                            toImageButtonOptions: {
                                format: 'svg',
                                filename: 'contacts_avg',
                                height: height,
                                width: width,
                                scale: 1
                            },
                            // editable: true
                        })
                    })


                });



            })
    }

    function plotPersonClassContacts() {

        axios.post(api + "/flask/personcontacts", { dir: selectedLogDir, start_day: document.getElementById("cstart_day").value, end_day: document.getElementById("cend_day").value })
            .then((response) => {
                const data = response.data.contacts;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data);
                    var data = [];
                    var subplots = [];
                    var axis = 1;
                    var annotations = [];
                    _df.map((row) => {
                        var _data = row.get('contacts').split(' ');
                        var yaxis = 'y' + axis
                        if (axis == 1) {
                            yaxis = 'y'
                        }
                        data.push({
                            x: _data,
                            x_original: _data,
                            xaxis: 'x',
                            yaxis: yaxis,
                            name: row.get('person_class'),
                            marker: { color: peopleClassColors[row.get('person_class')] },
                            type: "histogram",
                        })
                        annotations.push({
                            text: row.get('person_class'),
                            showarrow: false,
                            align: 'center',
                            x: 0.1,
                            y: 0.9,
                            xref: 'paper',
                            yref: yaxis + " domain",
                        })
                        subplots.push(['x' + yaxis])
                        axis += 1
                    })
                    var layout = {
                        title: 'Distribution of daily contacts for given person classes',
                        width: 800,
                        height: 800,
                        showlegend: false,
                        annotations: [...annotations, {
                            y: 0.5,
                            x: -0.1,
                            xref: 'paper',
                            yref: 'paper',
                            text: 'Frequency',
                            showarrow: false,
                            textangle: -90
                        }],
                        xaxis: { title: 'Number of contacts' },
                        // barmode: "stack",
                        grid: {
                            subplots: subplots,
                            rows: data.length,
                            columns: 1,
                            pattern: 'independent',
                        }
                    };
                    setContactPeopleHistData(data)
                    setContactPeopleHistLayout(layout)

                    // ==========================================================================
                    var data2 = [];
                    _df.map((row) => {
                        var daily_total = row.get('daily_total').split(' ')
                        daily_total = daily_total.splice(0, daily_total.length - 1)
                        data2.push({
                            y: daily_total,
                            y_original: Array.from(daily_total),
                            name: row.get('person_class'),
                            marker: { color: peopleClassColors[row.get('person_class')].replace(/[^,]+(?=\))/, '1.0') },
                            type: "line",
                        })
                    })
                    var layout2 = {
                        title: 'Variation of contacts of each person class with time',
                        width: 800,
                        height: 800,
                        barmode: "stack",
                        bargap: 0,
                        xaxis: {
                            title: "Simulation Days"
                        },
                        yaxis: {
                            title: "Total number of contacts"
                        },

                    };
                    setContactPeopleTimeData(data2)
                    setContactPeopleTimeLayout(layout2)

                });
            });
    }

    function plotLocationClassContacts() {

        axios.post(api + "/flask/locationcontacts", { dir: selectedLogDir, start_day: document.getElementById("cstart_day").value, end_day: document.getElementById("cend_day").value })
            .then((response) => {
                const data = response.data.contacts;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data);
                    var data = [];
                    var axis = 1;
                    var subplots = [];
                    var annotations = [];
                    _df.map((row) => {
                        var _data = row.get('contacts').split(' ');
                        var yaxis = 'y' + axis
                        if (axis == 1) {
                            yaxis = 'y'
                        }
                        data.push({
                            x: _data,
                            x_original: _data,
                            xaxis: 'x',
                            yaxis: yaxis,
                            name: row.get('location_class'),
                            marker: { color: locationClassColor[row.get('location_class')].replace(/[^,]+(?=\))/, '1.0') },
                            type: "histogram",
                        })
                        annotations.push({
                            text: row.get('location_class'),
                            showarrow: false,
                            align: 'center',
                            x: 0.1,
                            y: 0.9,
                            xref: 'paper',
                            yref: yaxis + " domain",
                        })
                        subplots.push(['x' + yaxis])
                        axis += 1
                    })
                    var layout = {
                        title: 'Distribution of daily contacts for given location classes',
                        width: 800,
                        height: 800,
                        showlegend: false,
                        annotations: [...annotations, {
                            y: 0.5,
                            x: -0.1,
                            xref: 'paper',
                            yref: 'paper',
                            text: 'Frequency',
                            showarrow: false,
                            textangle: -90
                        }],
                        xaxis: { title: 'Number of contacts' },
                        grid: {
                            subplots: subplots,
                            rows: data.length,
                            columns: 1,
                            pattern: 'independent',
                        }
                    };
                    setContactLocHistData(data)
                    setContactLocHistLayout(layout)
                    // ==========================================================================
                    var data2 = [];
                    _df.map((row) => {
                        var daily_total = row.get('daily_total').split(' ');
                        daily_total = daily_total.splice(0, daily_total.length - 1)
                        data2.push({
                            y: daily_total,
                            y_original: Array.from(daily_total),
                            name: row.get('location_class'),
                            marker: { color: locationClassColor[row.get('location_class')].replace(/[^,]+(?=\))/, '1.0') },
                            type: "line",
                        })
                    })
                    var layout2 = {
                        title: 'Variation of contacts of each location class with time',
                        width: 800,
                        height: 800,
                        barmode: "stack",
                        bargap: 0,
                        xaxis: {
                            title: "Simulation Days"
                        },
                        yaxis: {
                            title: "Total number of contacts"
                        },

                    };
                    setContactLocationTimeData(data2)
                    setContactLocationTimeLayout(layout2)
                });
            });
    }

    // event handlers
    const handleSliderChangeNodeX = function (event, newValue) {
        setNodeX(newValue);
    };
    const handleSliderChangeNodeY = function (event, newValue) {
        setNodeY(newValue);
    };

    const handleCheckedZeroContacts = (event) => {
        var _temp = [];
        if (!event.target.checked) {
            contactLocHistData.forEach((trace) => {
                trace['x'] = trace['x_original'].filter(item => item > '0')
                _temp.push(trace)
            })
        } else {
            contactLocHistData.forEach((trace) => {
                trace['x'] = [...trace['x_original']]
                _temp.push(trace)
            })
        }
        setContactLocHistData(_temp)

        var _temp2 = [];
        if (!event.target.checked) {
            contactPeopleHistData.forEach((trace) => {
                trace['x'] = trace['x_original'].filter(item => item > '0')
                _temp2.push(trace)
            })
        } else {
            contactPeopleHistData.forEach((trace) => {
                trace['x'] = [...trace['x_original']]
                _temp2.push(trace)
            })
        }
        setContactPeopleHistData(_temp2)
    }


    const handleCheckedNormalize = (event) => {
        if (checkNormalize)
            return
        setCheckNormalize(true)

        var _temp = []
        contactPeopleTimeData.forEach((trace) => {
            var p_index = peoplePieData.labels.indexOf(trace.name)
            var p_count = peoplePieData.values[p_index]

            trace['y'] = trace['y'].map(item => item / p_count)
            _temp.push(trace)
        })

        contactPeopleTimeLayout["yaxis"]["title"] = "Average contacts per person"
        setContactPeopleTimeData(_temp)

    }

    const handleCheckedShowRatio = (event) => {
        var _temp = [...contactPeopleTimeData];
        for (var t = 0; t < _temp[0]['y'].length; t++) {
            var tot_t = 0
            _temp.forEach((trace) => {
                tot_t += parseFloat(trace['y'][t])
            })
            _temp.forEach((trace) => {
                trace['y'][t] /= tot_t * 0.01
                // trace['y'][t] = trace['y'][t].toString()
            })
        }

        console.log(_temp)

        let _temp2 = [...contactLocationTimeData];
        for (var t = 0; t < _temp2[0]['y'].length; t++) {
            var tot_t = 0
            _temp2.forEach((trace) => {
                tot_t += parseFloat(trace['y'][t])
            })
            _temp2.forEach((trace) => {
                trace['y'][t] /= tot_t * 0.01
                // trace['y'][t] = trace['y'][t].toString()
            })
        }

        contactPeopleTimeLayout["yaxis"]["title"] = "Percentage of contacts"
        contactLocationTimeLayout["yaxis"]["title"] = "Percentage of contacts"
        setContactPeopleTimeData(_temp)
        setContactLocationTimeData(_temp2)
    }

    const handleCheckedStackVertically = (event) => {
        var _temp = [];
        if (!event.target.checked) {
            contactLocationTimeData.forEach((trace) => {
                trace['type'] = 'line'
                _temp.push(trace)
            })
        } else {
            contactLocationTimeData.forEach((trace) => {
                trace['type'] = 'bar'
                _temp.push(trace)
            })
        }
        setContactLocationTimeData(_temp)
        var _temp2 = [];
        if (!event.target.checked) {
            contactPeopleTimeData.forEach((trace) => {
                trace['type'] = 'line'
                _temp2.push(trace)
            })
        } else {
            contactPeopleTimeData.forEach((trace) => {
                trace['type'] = 'bar'
                _temp2.push(trace)
            })
        }
        setContactPeopleTimeData(_temp2)

    }

    const handleResetTimeline = (event) => {
        setCheckRatio(false)
        setCheckNormalize(false)
        var _temp = []
        contactPeopleTimeData.forEach((trace) => {
            trace['y'] = [...trace['y_original']]
            _temp.push(trace)
        })
        var _temp2 = []
        contactLocationTimeData.forEach((trace) => {
            trace['y'] = [...trace['y_original']]
            _temp2.push(trace)
        })
        contactPeopleTimeLayout["yaxis"]["title"] = "Total contacts"
        contactLocationTimeLayout["yaxis"]["title"] = "Total contacts"
        setContactPeopleTimeData(_temp)
        setContactLocationTimeData(_temp2)
    }

    const handleInfectionTreeColorChange = (event) => {
        setInfectionTreeColor(event.target.value);
    }


    return (
        <div>
            <div className="results-page">
                <h1>Sim results page</h1>

                {loadprogress != 0 && <CircularProgress variant="determinate" value={loadprogress} />}
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
                        getDirs={setDirs}
                        getDays={setDays}
                    />
                </div>


                {/* ===================================================================================== COVID-19 Spread Analysis */}
                <div>
                    <h4>COVID-19 Infection Spread Analysis</h4>
                    <Grid container spacing={0} padding='30px'>

                        <Grid container xs={12}>
                            <Grid xs={12}>
                                <div style={{ paddingTop: 5 }} id="stateTimeline"></div>
                            </Grid>

                            <Grid xs={12}>
                                <Grid xs={12}>
                                    <FormGroup row>
                                        {timelineOptions.map((p) => {
                                            return (
                                                <FormControlLabel
                                                    control={<Checkbox
                                                        checked={selectedTimelineOptions[p]}
                                                        onChange={(event) => {
                                                            var newOptions = { ...selectedTimelineOptions, [event.target.name]: event.target.checked }
                                                            var graphDiv = document.getElementById('stateTimeline')
                                                            var visible_true = []
                                                            var visible_false = []
                                                            for (var i = 0; i < graphDiv.data.length; i++) {
                                                                if (newOptions[graphDiv.data[i].name] || !timelineOptions.includes(graphDiv.data[i].name))
                                                                    visible_true.push(i)
                                                                else
                                                                    visible_false.push(i)

                                                            }
                                                            Plotly.update(graphDiv, { 'visible': false }, {}, visible_false)
                                                            Plotly.update(graphDiv, { 'visible': true }, {}, visible_true)

                                                            setSelectedTimelineOptions(newOptions);
                                                        }}
                                                        name={p}
                                                        key={p} />}
                                                    label={p}
                                                />
                                            )
                                        })}
                                    </FormGroup>
                                </Grid>
                            </Grid>
                            <Grid container xs={12} direction="row">
                                {/* <Grid container xs={1}>
                                        <Typography >Add from log</Typography>
                                    </Grid> */}
                                <Grid item xs={2}><Button variant="contained" onClick={() => drawCovidStateTimeline()}>Plot</Button></Grid>
                                <Grid container xs={2}>
                                    <FormControlLabel
                                        label={"Group curves"}
                                        control={<Checkbox id="group_curves_cb"
                                        />}
                                    />
                                    <FormControlLabel
                                        label={"Plot checkpoints"}
                                        control={<Checkbox id="plot_checkp_cb"
                                        />}
                                    />
                                </Grid>


                                <Grid container
                                    direction="row"
                                    justifyContent="center"
                                    alignItems="center"
                                >
                                    <FormControl>
                                        <InputLabel shrink htmlFor="select-multiple-people">
                                            All logs
                                        </InputLabel>
                                        <Select
                                            multiple
                                            native
                                            value={selectedUnstagedLogDirs}
                                            onChange={(event) => {
                                                const { options } = event.target;
                                                const value = [];
                                                for (let i = 0, l = options.length; i < l; i += 1) {
                                                    if (options[i].selected && !stagedLogDirs.includes(options[i].value)) {
                                                        value.push(options[i].value);
                                                    }
                                                }
                                                setSelectedUnstagedLogDirs(value);
                                            }}

                                            inputProps={{
                                                id: 'select-multiple-native',
                                            }}
                                        >
                                            {dirs.map((element) => (
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

                                            <Button variant="contained" color="primary" onClick={(event) => {
                                                var _unstaged = []; dirs.forEach((e => _unstaged.push(e)));
                                                var _staged = []; stagedLogDirs.forEach((e => _staged.push(e)));
                                                selectedUnstagedLogDirs.forEach(element => {
                                                    _staged.push(element); //_unstaged.splice(_unstaged.indexOf(element), 1);
                                                });
                                                // setUnstagedPeople(_unstaged)
                                                setStagedLogDirs(_staged)
                                                setSelectedUnstagedLogDirs([])
                                            }}>{">>"}</Button>
                                            <Button variant="contained" color="primary" onClick={(event) => {
                                                setStagedLogDirs(stagedLogDirs.filter((e) => { return !selectedStagedLogDirs.includes(e) }))
                                                setSelectedStagedLogDirs([])

                                                var graphDiv = document.getElementById("stateTimeline")
                                                var indices = []
                                                for (var i = 0; i < graphDiv.data.length; i++) {
                                                    if (selectedStagedLogDirs.includes(graphDiv.data[i].dir_name))
                                                        indices.push(i)
                                                }
                                                Plotly.deleteTraces(graphDiv, indices)
                                            }}>{"<<"}</Button>
                                        </Grid>
                                    </Grid>

                                    <FormControl >
                                        <InputLabel shrink htmlFor="select-multiple-people">
                                            Selected Logs
                                        </InputLabel>
                                        <Select
                                            multiple
                                            native
                                            value={selectedStagedLogDirs}
                                            onChange={(event) => {
                                                const { options } = event.target;
                                                const value = [];
                                                for (let i = 0, l = options.length; i < l; i += 1) {
                                                    if (options[i].selected && options[i].value != selectedLogDir) {
                                                        value.push(options[i].value);
                                                    }
                                                }
                                                setSelectedStagedLogDirs(value);
                                            }}

                                            inputProps={{
                                                id: 'select-multiple-native',
                                            }}
                                        >
                                            {stagedLogDirs.map((element) => (
                                                <option key={element} value={element}>
                                                    {element}
                                                </option>
                                            ))}
                                        </Select>
                                    </FormControl>
                                </Grid>

                            </Grid>


                        </Grid>


                        <div id="statesDay"></div>

                        <div id="variantTimeline"></div>



                        <Grid xs={12}>
                            <Grid container xs={4}>
                                <Typography >Filter by state</Typography>
                            </Grid>
                            <Grid xs={4}>
                                <Select
                                    id="select-state"
                                    value={selectedState}
                                    onChange={(e) => { setSelectedState(e.target.value) }}

                                >
                                    {stateOptions.map((e) => {
                                        return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                                    })}

                                </Select>
                            </Grid>
                        </Grid>

                    </Grid>



                    <br />
                    <hr class="rounded" />
                    <div style={{ height: '50px' }}></div>
                    {/* ===================================================================================== COVID-19 Infection Analysis */}

                    <div id="infectionGraph"></div>
                    <div id="infectionLocationBar"></div>
                    <div id="infectionOccupationBar"></div>

                    <Grid container spacing={0} padding='30px'>
                        <Grid container rowSpacing={1} columnSpacing={{ xs: 1 }}>
                            <Grid container>
                                <Grid item xs={2}>
                                    <Typography>Node X</Typography>
                                </Grid>

                                <Grid item xs={1}>
                                    <Slider
                                        style={{ width: '250px', height: ' 10px' }}
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
                            </Grid>

                            <Grid container>
                                <Grid item xs={2}>
                                    <Typography>Node Y</Typography>
                                </Grid>
                                <Grid item xs={1}>
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
                            </Grid>
                            <Grid container>
                                <Grid item xs={2}>
                                    <Typography>Color</Typography>
                                </Grid>
                                <Grid item xs={6}>
                                    <RadioGroup
                                        aria-label="gender"
                                        defaultValue="female"
                                        name="radio-buttons-group"
                                        row
                                        value={infectionTreeColor}
                                        onChange={handleInfectionTreeColorChange}
                                    >
                                        <FormControlLabel value="0" control={<Radio />} label="By occupation" />
                                        <FormControlLabel value="1" control={<Radio />} label="By infected location" />
                                        {/* <FormControlLabel value="2" control={<Radio />} label="Other" /> */}
                                    </RadioGroup>
                                </Grid>
                            </Grid>
                        </Grid>


                        <div id="treeWrapper" style={{
                            width: '70em', height: '40em', margin: '0 auto', padding: '15px', border: 'black 5px solid'
                        }} >
                            <Tree
                                data={infectionTreeData}
                                renderCustomNodeElement={renderRectSvgNode}
                                orientation="vertical"
                                nodeSize={{ x: nodeX, y: nodeY }}
                                pathClassFunc={getDynamicPathClass}
                            />

                        </div>


                    </Grid>

                    <br />
                    <hr class="rounded" />
                    <div style={{ height: '50px' }}></div>


                    <Box>
                        <Typography>Infection state timeline</Typography>
                        <Button onClick={() => plotInfectionStateTimeline()}>Plot infection state timeline</Button>
                        <div id="infection-state-timeline"></div>
                        <div id="infection-state-violin"></div>
                    </Box>


                    <div class='container'>
                        <Select
                            id="select-group"
                            value={selectedGroup}
                            onChange={(e) => { setSelectedGroup(e.target.value) }}
                            width={300}
                        >
                            {groupOptions.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}

                        </Select>
                        <Button onClick={plotNewInfections}>Plot Infection Graphs</Button>
                    </div>


                    <Grid container spacing={0}>
                        <Grid container xs={6}>
                            <Plot
                                data={infectionsData3D}
                                layout={infectionsLayout3D}
                                config={{
                                    toImageButtonOptions: {
                                        format: 'svg',
                                        filename: 'infectionsHeatMap3D',
                                        height: height,
                                        width: width,
                                        scale: 1
                                    }, editable: true
                                }}
                            />
                        </Grid>
                        <Grid container xs={6}>
                            <div id="infectionsHeatMap2D"></div>
                        </Grid>
                        <Grid container xs={6}>
                            <div id="infectionsTime2D"></div>
                        </Grid>
                        <Grid container xs={6}>
                            <div id="infectionsHist2D"></div>
                        </Grid>
                        <Grid container xs={6}>
                            <div id="infectionsCount"></div>
                        </Grid>
                        <Grid container xs={6}>
                            <div id="infectionsCountCumSum"></div>
                        </Grid>
                        <Grid container xs={6}>
                            <div id="infectionsCountCumSumRatio"></div>
                        </Grid>
                    </Grid>


                </div>

                <br />
                <div style={{ height: '50px' }}></div>
                <hr class="rounded" />

                {/* ===================================================================================== COVID-19 Contact Analysis */}
                <div>
                    <h4>COVID-19 Contact Analysis</h4>
                    <TextField id="cstart_day" label="Start day" />
                    <TextField id="cend_day" label="End day" />
                    <div class='container'>
                        {/* <Select
                            id="select-group1"
                            // value={selectedGroup}
                            // onChange={(e) => { textContent = (e.target.value) }}
                            label="Selected Log"
                        >
                            {groupOptions.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}

                        </Select> */}
                        <TextField select label="select-group1" id="select-group1">
                            {groupOptions.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}
                        </TextField>
                        <TextField select label="select-group2" id="select-group2">
                            {groupOptions.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}
                        </TextField>
                        {/* <Select
                            id="select-group2"
                            // value={selectedGroup}
                            // onChange={(e) => { textContent = (e.target.value) }}
                            label="Selected Log"
                        >
                            {groupOptions.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}

                        </Select> */}

                        <Button onClick={plotNumberOfContacts}>Plot Contact Graphs</Button>
                    </div>
                    <br />
                    <Grid container spacing={0}>
                        <Grid container xs={6}>
                            <Plot
                                data={contactData3D}
                                layout={contactLayout3D}
                            />
                        </Grid>
                        <Grid container xs={6}>
                            <div id="contactHeatMap2D"></div>
                        </Grid>

                        <Grid container xs={12} alignContent="stretch" alignItems="stretch">
                            <Grid item xs={12}>
                                <Select id="select-contact-group" label="Filter by group" onChange={(e) => {
                                    var histTraces = []
                                    var lineTraces = []
                                    contactHistTraces.forEach((t) => {
                                        if (t.legendgroup == e.target.value)
                                            histTraces.push({ ...t, yaxis: 'y', legendgroup: null })
                                    })
                                    contactLineTraces.forEach((t) => {
                                        if (t.legendgroup == e.target.value)
                                            lineTraces.push({ ...t, yaxis: 'y', legendgroup: null })
                                    })
                                    Plotly.newPlot("contactTime2D", lineTraces, {
                                        title: 'Number of contacts for each group throughout time',
                                        width: width,
                                        height: height,
                                        xaxis: { title: 'Days' },
                                    })
                                    Plotly.newPlot("contactHist2D", histTraces, {
                                        width: width,
                                        height: height,
                                        xaxis: { title: 'Days' },
                                    })
                                }}>
                                    {groupNames.map((e) => { return (<MenuItem value={e} key={e}>{e}</MenuItem>); })}
                                </Select>
                            </Grid>
                        </Grid>


                        <Grid container xs={6}>
                            <div id="contactTime2D"></div>
                        </Grid>
                        <Grid container xs={6}>
                            <div id="contactHist2D"></div>
                        </Grid>
                    </Grid>

                    <br />
                    {/* ===================================================================================== COVID-19 Person Location Contact Analysis */}
                    <h4>COVID-19 Contact Analysis for different agent & location classes</h4>
                    <Button onClick={() => { plotPersonClassContacts(); plotLocationClassContacts(); }}>Plot</Button>
                    <div class='container'>
                        <FormGroup center>
                            <FormControlLabel control={<Checkbox onChange={handleCheckedZeroContacts} defaultChecked />} label="Consider 0 contacts" />
                        </FormGroup>
                    </div>
                    <Grid container spacing={0} padding='30px'>
                        <Grid container xs={6}>
                            <Plot
                                data={contactLocHistData}
                                layout={contactLocHistLayout}
                            />
                        </Grid>

                        <Grid container xs={6}>
                            <Plot
                                data={contactPeopleHistData}
                                layout={contactPeopleHistLayout}
                            />
                        </Grid>
                    </Grid>

                    <br />
                    <div class='container'>
                        <FormGroup row>
                            <FormControlLabel control={<Checkbox onChange={handleCheckedStackVertically} />} label="Stack vertically" />
                            <FormControlLabel control={<Button variant="contained" onClick={handleCheckedNormalize}>Normalize by population (only population class)</Button>} />
                            <FormControlLabel control={<Button variant="contained" onClick={handleCheckedShowRatio}>Show as a ratio</Button>} />
                            <FormControlLabel control={<Button variant="outlined" onClick={handleResetTimeline}>RESET</Button>} />

                        </FormGroup>
                    </div>
                    <Grid container spacing={0} padding='30px'>
                        <Grid container xs={6}>
                            <Plot
                                data={contactLocationTimeData}
                                layout={contactLocationTimeLayout}
                            />
                        </Grid>

                        <Grid container xs={6}>
                            <Plot
                                data={contactPeopleTimeData}
                                layout={contactPeopleTimeLayout}
                            />
                        </Grid>
                    </Grid>
                </div>


                <br />
                <div style={{ height: '50px' }}></div>
                <hr class="rounded" />
            </div>
        </div >
    );
}


export default ResultsPage;