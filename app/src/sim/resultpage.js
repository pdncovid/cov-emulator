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

function ResultsPage() {


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


    const [infectionTreeData, setInfectionTreeData] = useState({ name: 'ROOT' });
    const [infectionTreeColor, setInfectionTreeColor] = useState("0");


    const [infectionsData3D, setInfectionsData3D] = useState([]);
    const [infectionsLayout3D, setInfectionsLayout3D] = useState([]);

    const [contactData3D, setContactData3D] = useState([]);
    const [contactLayout3D, setContactLayout3D] = useState([]);

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


    const [nodeX, setNodeX] = useState(30);
    const [nodeY, setNodeY] = useState(30);


    useEffect(() => {
    }, [initialLoad])

    useEffect(() => {
        drawStatesInDay()
    }, [selectedDay])

    useEffect(() => {
        plotInfectionGraph();
        drawCovidStateTimeline();

        plotInfectionTree()

        processPieData()
        plotPersonClassContacts();
        plotLocationClassContacts();
    }, [selectedLogDir])


    useEffect(() => {
        drawStatesInDay()
    }, [selectedState])
    // useEffect(() => {
    //     onContactTimelineChange();
    // }, [checkNormalize, checkRatio])


    const handleSelectDir = function (_selectedLogDir) {
        
        getColors(_selectedLogDir)

    }

    const handleDayChange = function (_day) {
        setSelectedDay(_day);
    }

    const handleAnalyzePeopleClick = (_selectedPeople) => {


        axios.post(api + "/flask/setpeopleclasses", { dir: selectedLogDir, classes: _selectedPeople.join(',') })
            .then(function (response) {
                plotInfectionGraph();
                drawCovidStateTimeline();
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
            dir: selectedLogDir, d: '0',
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
                    axios.post(api + "/flask/textfile", { dir: selectedLogDir, filename: 'people.txt' })
                        .then(function (response) {
                            var people_str = response.data.data.split("\n").map((e) => strip_text(e));

                            grp.aggregate((g, pc) => {
                                try {
                                    pc = pc['person_class']
                                    pieLabels.push(people_str[pc])
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
                           setpeoplePieData(pieData)
                        })

                })
            })
    }
    // ===========================================================================================================================================
    // draw covid data timeline
    async function drawCovidStateTimeline() {
        // loading number of days
        axios.post(api + '/flask/n_days', { dir: selectedLogDir }).then(response => {
            let _days = response.data.message

            let _data = []

            for (let day = 0; day < _days; day++) {
                axios.post(api + "/flask/csvfile", { dir: selectedLogDir, d: day.toString(), type: '_cov_info' })
                    .then(function (response) {
                        //handle success
                        const data = response.data.data;
                        csv2JSONarr(data, (pr) => { }).then((json_data) => {
                            var _df = new DataFrame(json_data)
                            _df = _df.castAll(Array(_df.listColumns().length).fill(Number))
                            console.log("Covid data", _df)
                            let _x = _df.select("time").toArray().map((e) => e[0] / 1440)
                            let _df_arr = _df.toArray()
                            let _df_col = _df.listColumns()
                            for (var i = 0; i < _x.length; i++) {
                                var datum = { t: parseFloat(_x[i]) }
                                for (var j = 0; j < _df_col.length; j++) {
                                    datum[_df_col[j]] = _df_arr[i][j]
                                }
                                _data.push(datum)
                            }


                            if (day == _days - 1) {
                                _data.sort(function (a, b) {
                                    return ((a.t < b.t) ? -1 : ((a.t == b.t) ? 0 : 1));
                                });
                                console.log(_data)
                                let traces = []
                                _df_col.forEach(col => {
                                    if (col == "time")
                                        return
                                    var trace1 = {
                                        x: _data.map((e) => e.t),
                                        y: _data.map((e) => e[col]),
                                        name: col,
                                        mode: 'line',
                                    };
                                    traces.push(trace1)
                                })
                                Plotly.newPlot("stateTimeline", traces, {
                                    title: 'Variation of states of the population with time',
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
                                        showexponent: 'all'
                                    }
                                })
                            }
                        });
                    });

            };
            // console.log("STATE TIMELINE", _stateTimelineData)
            // setStateTimelineData(_stateTimelineData);


        }).catch(error => {
            console.log(error)
        })





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
                        xaxis: { title: 'Age' },
                        yaxis: { title: "Number of people in state - " + selectedState },
                    })
                });
            });
    }


    // draw infection tree (sunburst)
    async function plotInfectionGraph() {
        axios.post(api + "/flask/infectiontree", { dir: selectedLogDir })
            .then(function (response) {
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
                    })


                });

            })
            .catch(function (response) {
                console.log(response);
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
                const data = response.data.json;
                const json_data = JSON.parse(data)
                setInfectionTreeData(json_data);

            })
            .catch(function (response) {
                console.log(response);
            });

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
                        let group_names = _df.listColumns();
                        let x = []
                        let y = []
                        let z = []
                        let v = []
                        let heatMap = []
                        let _df_arr = _df.toArray()
                        let count_df_arr = count_df.toArray().map((e) => e[0].split(' '))
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
                            title: 'Number of New Infections for each group',
                            width: 800,
                            height: 800,
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
                                    xaxis: 'x',
                                    yaxis: yaxis,
                                    legendgroup: axis
                                })
                                hist_traces.push({
                                    x: vals.filter((e) => e > 0),
                                    xaxis: 'x',
                                    yaxis: yaxis,
                                    name: group_names[Y],
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
                        for (var X = 0; X < group_names.length; X++) {
                            var temp = new Array(_df_arr[X][0].split(' ').length).fill(0);
                            for (var Y = 0; Y < group_names.length; Y++) {
                                var vals = _df_arr[Y][X].split(' ').map(parseFloat)
                                for (var i = 0; i < vals.length; i++) {
                                    temp[i] += vals[i];
                                }
                            }
                            ratio_traces.push({
                                y: temp,
                                name: group_names[X],
                                type: "bar"
                            })
                        }
                        Plotly.newPlot("infectionsTime2D", line_traces, {
                            title: 'Number of new infections for each group throughout time',
                            width: 800,
                            height: 800,
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
                        })
                        Plotly.newPlot("infectionsHist2D", hist_traces, {
                            title: 'Frequency of new infections per day for each group',
                            width: 800,
                            height: 800,
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
                        })
                        Plotly.newPlot("infectionsHeatMap2D", [{
                            x: group_names,
                            y: group_names,
                            z: heatMap,
                            type: 'heatmap'
                        }], {
                            title: 'Average number of disease transmissions from infected group per day \n(normalized by number of infected people in each group)',
                            width: 800,
                            height: 800,
                            yaxis: {
                                tickangle: -45,
                                automargin: true,
                            },
                            autosize: false,
                            // margin: {
                            //     l: 50,
                            //     r: 50,
                            //     b: 100,
                            //     t: 100,
                            //     pad: 4
                            //   },

                        })

                        console.log(ratio_traces)
                        Plotly.newPlot("infectionsCount", ratio_traces, {
                            title: '# of new infections for each group throughout time',
                            width: 800,
                            height: 800,
                            barmode: "stack",
                            bargap: 0,
                            xaxis: {
                                title: 'Days',
                            },
                            yaxis: {
                                title: '# of new infections',
                            },

                        })
                        // console.log(ratio_traces)
                        for (var i = 0; i < ratio_traces.length; i++) {
                            for (var j = 1; j < ratio_traces[i]['y'].length; j++) {
                                if (isNaN(ratio_traces[i]['y'][j - 1]))
                                    continue
                                ratio_traces[i]['y'][j] += ratio_traces[i]['y'][j - 1]
                            }
                            console.log(ratio_traces[i])
                        }
                        Plotly.newPlot("infectionsCountCumSum", ratio_traces, {
                            title: '# of infections for each group throughout time',
                            width: 800,
                            height: 800,
                            barmode: "stack",
                            bargap: 0,
                            xaxis: {
                                title: 'Days',
                            },
                            yaxis: {
                                title: '# of infections',
                            },
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
                            title: '% of infections for each group throughout time',
                            width: 800,
                            height: 800,
                            barmode: "stack",
                            bargap: 0,
                            xaxis: {
                                title: 'Days',
                            },
                            yaxis: {
                                title: '% of infections',
                            },
                        })
                        console.log("heatmap", heatMap)
                    })
                });
            })
    }

    // plot number of contacts grouped
    function plotNumberOfContacts() {
        axios.post(api + "/flask/contacts", { dir: selectedLogDir, group_by: selectedGroup })
            .then(function (response) {
                const contactData = response.data.contacts;
                const countData = response.data.count;
                csv2JSONarr(contactData, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    console.log("Contacts", _df)
                    csv2JSONarr(countData, (pr) => { }).then((json_data) => {
                        var count_df = new DataFrame(json_data)
                        console.log("Contact group count", count_df)
                        let count_df_arr = count_df.select('count').toArray().map((e) => e[0])
                        let group_names = _df.listColumns();
                        let x = []
                        let y = []
                        let z = []
                        let v = []
                        let heatMap = []
                        let _df_arr = _df.toArray()
                        var max_v = 0;
                        console.log(_df, _df_arr)
                        for (var X = 0; X < group_names.length; X++) {
                            heatMap.push([])
                            for (var Y = 0; Y < group_names.length; Y++) {
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
                            width: 800,
                            height: 800,
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
                                    xaxis: 'x',
                                    yaxis: yaxis,
                                    legendgroup: axis
                                })
                                hist_traces.push({
                                    x: vals,
                                    xaxis: 'x',
                                    yaxis: yaxis,
                                    name: group_names[Y],
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
                        Plotly.newPlot("contactTime2D", line_traces, {
                            title: 'Number of contacts for each group throughout time',
                            width: 800,
                            height: 1500,
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
                                rows: group_names.length,
                                columns: 1,
                                pattern: 'independent',
                            },
                            xaxis: {
                                title: 'Days',
                            },
                        })
                        Plotly.newPlot("contactHist2D", hist_traces, {
                            title: 'Frequency of contacts per day for each group',
                            width: 800,
                            height: 1500,
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
                                title: 'Number of contacts',
                            },
                        })
                        Plotly.newPlot("contactHeatMap2D", [{
                            x: group_names,
                            y: group_names,
                            z: heatMap,
                            type: 'heatmap'
                        }], {
                            title: 'Avg contacts per person in each group',
                            width: 800,
                            height: 800,
                            yaxis: {
                                tickangle: -45,
                                automargin: true,
                            },

                        })
                    })


                });



            })
    }

    function plotPersonClassContacts() {

        axios.post(api + "/flask/personcontacts", { dir: selectedLogDir })
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

        axios.post(api + "/flask/locationcontacts", { dir: selectedLogDir })
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
            var p_index = peoplePieData[0].labels.indexOf(trace.name)
            var p_count = peoplePieData[0].values[p_index]

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

    const exportAllImages = () => {
        Plotly.toImage('distributionpeople', { format: 'png', width: 800, height: 600 })
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
                    />
                </div>

                <Button onClick={exportAllImages} variant="contained" color="primary">Save All Images</Button>




                {/* ===================================================================================== COVID-19 Spread Analysis */}
                <div>
                    <h4>COVID-19 Infection Spread Analysis</h4>
                    <Grid container spacing={0} padding='30px'>
                        <Grid container xs={6}>
                            <div id="stateTimeline"></div>
                        </Grid>


                        <Grid container xs={5}  >

                            <div id="statesDay"></div>
                        </Grid>
                    </Grid>
                    <Grid container xs={1}>
                        <Select
                            id="select-state"
                            value={selectedState}
                            onChange={(e) => { setSelectedState(e.target.value) }}
                            width={300}
                        >
                            {stateOptions.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}

                        </Select>
                    </Grid>


                    <br />
                    <hr class="rounded" />
                    <div style={{ height: '50px' }}></div>
                    {/* ===================================================================================== COVID-19 Infection Analysis */}

                    <div id="infectionGraph"></div>

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
                            width: '90em', height: '40em', margin: '0 auto', padding: '15px', border: 'black 5px solid'
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
                    <div class='container'>
                        <Select
                            id="select-group"
                            value={selectedGroup}
                            onChange={(e) => { setSelectedGroup(e.target.value) }}
                            label="Selected Log"
                            width={300}
                        >
                            {groupOptions.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}

                        </Select>
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
                        <Grid container xs={6}>
                            <div id="contactTime2D"></div>
                        </Grid>
                        <Grid container xs={6}>
                            <div id="contactHist2D"></div>
                        </Grid>
                    </Grid>

                    <br />

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
                        <FormGroup center>
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
        </div>
    );
}


export default ResultsPage;