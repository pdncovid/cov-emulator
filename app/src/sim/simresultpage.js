import React, { useState, useRef, useEffect } from "react";

import Grid from '@material-ui/core/Grid';

import Plot from 'react-plotly.js';
import { csvJSON, csv2JSONarr, strip_text } from "../utils/files";
import { hist, padZeros } from "../utils/functions";

import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';

import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import { ConsoleLog } from "react-console-log";

import randomColor from "randomcolor";

import DataFrame from 'dataframe-js';
import axios from 'axios'

function ResultsPage() {

    const api = "http://localhost:5000"

    const [initialLoad, setInitialLoad] = useState(true);
    const [loadprogress, setLoadprogress] = useState(0);

    const [locs, setLocs] = useState([]);
    const [people, setPeople] = useState([]);
    const [movement, setMovement] = useState([]);

    const [selectedPeople, setSelectedPeople] = useState([]);
    const [peopleCheckedState, setPeopleCheckedState] = React.useState({});

    const [dirs, setDirs] = useState([]);
    const [selectedLogDir, setSelectedLogDir] = useState('');
    const [days, setDays] = useState([]);
    const [selectedDay, setSelectedDay] = useState('');
    const [day_logs, setDayLogs] = useState([]);
    const [person_info_logs, setPersonInfoLogs] = useState([]);
    const [location_info_logs, setLocationInfoLogs] = useState([]);

    const [selectedGroup, setSelectedGroup] = useState('');
    const [groupOptions, setGroupOptions] = useState([]);

    const [cov_info_logs, setCovInfoLogs] = useState([]);

    const [unstagedPeople, setUnstagedPeople] = useState([]);
    const [stagedPeople, setStagedPeople] = useState([]);
    const [selectedUnstagedPeople, setSelectedUnstagedPeople] = useState([]);
    const [selectedStagedPeople, setSelectedStagedPeople] = useState([]);


    const [locHistData, setLocHistData] = useState([]);
    const [routeHistData, setRouteHistData] = useState([]);
    const [moveHistData, setMoveHistData] = useState([]);

    const [peoplePieData, setPeoplePieData] = useState([]);
    const [popPyramidData, setPopPyramidData] = useState([]);
    const [locTreeData, setLocTreeData] = useState([]);

    const [stateTimelineData, setStateTimelineData] = useState([]);
    const [infectionGraphData, setInfectionGraphData] = useState([]);
    const [contactHistData, setContactHistData] = useState([]);

    const [personPathData, setPersonPathData] = useState([]);
    const [personPathLayout, setPersonPathLayout] = useState([]);
    const [personPathData2, setPersonPathData2] = useState([]);
    const [personPathLayout2, setPersonPathLayout2] = useState([]);
    const [personPathFrames, setPersonPathFrames] = useState([]);


    // const [loadedDf, setLoadedDf] = useState([]);
    // const [loadedPersonDf, setLoadedPersonDf] = useState([]);
    const [loadedLocationDf, setLoadedLocationDf] = useState([]);

    const [processedDf, setProcessedDf] = useState([]);
    const [processedPersonDf, setProcessedPersonDf] = useState([]);
    const [locClassColors, setLocClassColors] = useState({});


    useEffect(() => {
        refreshDirs();
    }, [initialLoad])

    // plotActualLocationHist
    useEffect(() => {
        plotActualLocationHist();
        processRouteHist();
        processPieChart()
        processPopPyramid()
        processMoveHist()

        plotLocationTree()
    }, [selectedDay])

    useEffect(() => {
        plotInfectionGraph();
        drawCovidStateTimeline();
    }, [selectedLogDir])

    //draw person path
    useEffect(() => {
        drawPersonPath()
    }, [stagedPeople])


    function refreshDirs() {
        axios.get(api + '/flask/dirs').then(response => {
            setDirs(response.data.message.split(','))
        }).catch(error => {
            console.log(error)
        })
    }

    const handleSelectDir = function (event) {
        // const files = event.target.files;
        // console.log(event.target)
        let _selectedLogDir = event.target.value
        setSelectedLogDir(_selectedLogDir);
        // setLoadedDf([])
        // setLoadedPersonDf([])
        setProcessedDf([])
        setProcessedPersonDf([])

        // Loading Locations
        axios.post(api + "/flask/textfile", { dir: _selectedLogDir, filename: 'locs.txt' })
            .then(function (response) {
                //handle success
                const data = response.data.data;
                var locs_str = data.split("\n");

                let _LCC = {};
                var r = () => Math.random() * 256 >> 0;
                locs_str.forEach((i, e) => {
                    var _rc = `rgba(${r()}, ${r()}, ${r()}, 0.3)`;
                    _LCC[i] = _rc;
                    _LCC[e] = _rc;
                })
                setLocClassColors(_LCC)
                setLocs(locs_str);
                console.log(locs_str, _LCC);
            })
            .catch(function (response) {
                //handle error
                console.log(response);
            });

        // Loading People
        axios.post(api + "/flask/textfile", { dir: _selectedLogDir, filename: 'people.txt' })
            .then(function (response) {
                //handle success
                const data = response.data.data;
                var people_str = data.split("\n").map((e) => strip_text(e));
                people_str.forEach(element => {
                    peopleCheckedState[element] = true;
                });
                setPeople(people_str);
                setSelectedPeople(people_str);
                console.log(people_str);
            })
            .catch(function (response) {
                //handle error
                console.log(response);
            });

        // Loading Movement
        axios.post(api + "/flask/textfile", { dir: _selectedLogDir, filename: 'movement.txt' })
            .then(function (response) {
                //handle success
                const data = response.data.data;
                var movement_str = data.split("\n");
                setMovement(movement_str);
                console.log(movement_str);
            })
            .catch(function (response) {
                //handle error
                console.log(response);
            });

        // loading number of days
        axios.post(api + '/flask/n_days', { dir: _selectedLogDir }).then(response => {
            let _days = response.data.message.split(',')
            setDays(_days)

            setPersonInfoLogs(_days.map((e) => padZeros(e, 5) + '_person_info.csv'))
            setLocationInfoLogs(_days.map((e) => padZeros(e, 5) + '_location_info.csv'))
            setCovInfoLogs(_days.map((e) => padZeros(e, 5) + '_cov_info.csv'))
            setDayLogs(_days.map((e) => padZeros(e, 5) + '.csv'));
        }).catch(error => {
            console.log(error)
        })

        // loading grouping options
        axios.post(api + '/flask/possible_groups', { dir: _selectedLogDir }).then(response => {
            setGroupOptions(response.data.data)
        }).catch(err => { console.log(err) })

    }
    const handleDayChange = function (event) {
        setSelectedDay(event.target.value);
        // loadLog(padZeros(event.target.value.toString(), 5) + '.csv')
        // loadPersonLog(padZeros(event.target.value.toString(), 5) + '_person_info.csv')
        // loadLocationLog(padZeros(event.target.value.toString(), 5) + '_location_info.csv')
    }


    // select people classes and filter
    const handlePeopleCheckChange = (event) => {
        setPeopleCheckedState({ ...peopleCheckedState, [event.target.name]: event.target.checked });
    };

    const handleAnalyzePeopleClick = (e) => {

        let _selectedPeople = [];
        people.forEach(element => {
            if (peopleCheckedState[element]) {
                _selectedPeople.push(element)
            }
        });
        setSelectedPeople(_selectedPeople)
        axios.post(api + "/flask/setpeopleclasses", { dir: selectedLogDir, classes: _selectedPeople.join(',') })
            .then(function (response) {
                //handle success
                plotActualLocationHist();
                processRouteHist();
                processPieChart()
                processPopPyramid()
                processMoveHist()

                plotLocationTree()
                plotInfectionGraph();
                drawCovidStateTimeline();
            })
            .catch(function (response) {
                //handle error
                console.log(response);
            });
    }

    // // file loading
    // function loadfile(logDir, day, type) {
    //     return new Promise((resolve, reject) => {
    //         axios.post(api + "/flask/csvfile", { dir: logDir, d: day.toString(), type: type })
    //             .then(function (response) {
    //                 //handle success
    //                 const data = response.data.data;
    //                 csv2JSONarr(data, (pr) => {
    //                     // setTimeout(() => {
    //                     // setLoadprogress(pr);
    //                     // }, 100);

    //                 }).then((json_data) => {
    //                     var _df = new DataFrame(json_data)
    //                     // console.log("Loading COMPLETE!");
    //                     resolve(_df)
    //                 });

    //             })
    //             .catch(function (response) {
    //                 //handle error
    //                 console.log(response);
    //                 reject();
    //             });
    //     });
    // }
    // const loadLog = async (filename) => {

    //     loadfile(selectedLogDir, filename).then(_df => {
    //         _df = _df.castAll(Array(_df.listColumns().length).fill(Number))
    //         console.log("Dropping missing values")
    //         _df = _df.dropMissingValues();
    //         // console.log("Dropping missing values: DONE")
    //         // setLoadedDf(_df);
    //         setProcessedDf(_df);
    //         // let _days = []
    //         // for (let d = 0; d <= Math.floor(_df.stat.max('time') / 1440); d++) {
    //         //     _days.push(d);
    //         // }
    //         // setDays(_days);
    //         // setSelectDay(0);
    //         // setLoadprogress(0);
    //     }, (error) => { });

    // };
    // const loadPersonLog = async (filename) => {
    //     console.log("Loading file " + filename);
    //     loadfile(selectedLogDir, filename).then(_df => {
    //         let cast = []
    //         _df.listColumns().forEach((e) => {
    //             if (e == "route" || e == "character_vector") {
    //                 cast.push(String)
    //             } else {
    //                 cast.push(Number)
    //             }
    //         })
    //         _df = _df.castAll(cast)
    //         console.log("Dropping missing values")
    //         _df = _df.dropMissingValues();
    //         // console.log("Dropping missing values: DONE")
    //         // setLoadedPersonDf(_df);
    //         setProcessedPersonDf(_df);
    //         // setLoadprogress(0);
    //     }, (error) => { });
    // };
    // const loadLocationLog = async (filename) => {
    //     console.log("Loading file " + filename);
    //     loadfile(selectedLogDir, filename).then(_df => {
    //         let cast = []
    //         _df.listColumns().forEach((e) => {
    //             if (e == "exit" || e == "children_ids" || e == "name") {
    //                 cast.push(String)
    //             } else {
    //                 cast.push(Number)
    //             }
    //         })
    //         _df = _df.castAll(cast)
    //         console.log("Dropping missing values")
    //         _df = _df.dropMissingValues();

    //         setLoadedLocationDf(_df);
    //     }, (error) => { });
    // };

    // draw covid data timeline

    async function drawCovidStateTimeline() {
        // loading number of days
        axios.post(api + '/flask/n_days', { dir: selectedLogDir }).then(response => {
            let _days = response.data.message.split(',')
            for (let day = 0; day < _days.length; day++) {
                axios.post(api + "/flask/csvfile", { dir: selectedLogDir, d: day.toString(), type: '_cov_info' })
                    .then(function (response) {
                        //handle success
                        const data = response.data.data;
                        csv2JSONarr(data, (pr) => { }).then((json_data) => {
                            var _df = new DataFrame(json_data)
                            _df = _df.castAll(Array(_df.listColumns().length).fill(Number))
                            let _x = _df.select("time").toArray().map((e) => e[0] / 1440)
                            _df.listColumns().forEach(col => {
                                if (col == "time" || col == "") {
                                } else {
                                    var is_found = false;
                                    stateTimelineData.forEach(trace => {
                                        if (trace.name == col) {
                                            trace.x = trace.x.concat(_x)
                                            trace.y = trace.y.concat(_df.select(col).toArray().map((e) => e[0]))
                                            is_found = true;
                                        }
                                    });
                                    if (is_found == false) {
                                        var trace1 = {
                                            x: _x,
                                            y: _df.select(col).toArray().map((e) => e[0]),
                                            name: col,
                                            mode: 'line',
                                        };
                                        stateTimelineData.push(trace1)
                                    }
                                }
                            });
                            setStateTimelineData([...stateTimelineData]);
                        });
                    });

            };
        }).catch(error => {
            console.log(error)
        })





    }

    // show actual places visited during the day histogram
    async function plotActualLocationHist() {
        axios.post(api + "/flask/ActualLocationHist", { dir: selectedLogDir, day: selectedDay.toString(), groupBy: 'current_location_class' })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    console.log(_df)
                    _df = _df.withColumn('timesteps', row => row.get('timesteps').split('|').map(e => parseInt(e)));
                    let gData = [];
                    _df.map((row) => {
                        try {
                            var trace1 = {
                                x: row.get('timesteps'),
                                name: row.get('group'),
                                type: "histogram",
                            };
                            gData.push(trace1);
                            setLocHistData(gData);
                        } catch (err) {
                            console.log(err)
                        }

                    })



                });

            })
            .catch(function (response) {
                console.log(response);
            });

        // sub_df = sub_df.restructure(["current_location_class", "time", "person_class"])
        // let grp = sub_df.groupBy("current_location_class")
        // var data = [];
        // grp.aggregate((g, lc) => {
        //     try {
        //         lc = lc['current_location_class']
        //         console.log("Agg time in " + locs[lc])

        //         var trace1 = {
        //             x: g.select('time').toArray().map((e) => e[0] % 1440),
        //             name: locs[lc],
        //             type: "histogram",
        //         };
        //         data.push(trace1);
        //     } catch (error) {

        //     }
        // });
        // setLocHistData(data);
    }


    // show initialized route histogram for the given day
    async function processRouteHist() {
        axios.post(api + "/flask/csvfile", {
            dir: selectedLogDir, d: selectedDay.toString(),
            type: '_person_info', columns: "person|route"
        })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data)
                    let data = {}
                    locs.forEach(element => {
                        data[element] = []
                    });
                    sub_df.select('route').toArray().forEach((e) => {
                        let locations = e[0].split(' ').map((e) => parseInt(e));
                        locations.forEach((loc, t) => {
                            data[locs[loc]].push(t);
                        });
                    })

                    var routedata = [];
                    locs.forEach(loc => {
                        if (data[loc].length > 0) {
                            var trace1 = {
                                x: data[loc],
                                name: loc,
                                type: "histogram",
                                xbins: { size: 1, },
                                nbinsx: 288,
                            };

                            routedata.push(trace1);
                        }
                    })
                    setRouteHistData(routedata);
                });

            })
            .catch(function (response) {
                console.log(response);
            });

        // sub_df = sub_df.restructure(["person", "route", "person_class"])
    }

    // show hostogram of movement methods  used in the day
    async function processMoveHist() {
        axios.post(api + "/flask/csvfile", {
            dir: selectedLogDir, d: selectedDay.toString(),
            type: '', columns: "current_movement_class|time|person_class"
        })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data).castAll(Array(4).fill(Number))
                    let grp = sub_df.groupBy("current_movement_class")

                    var data = [];
                    grp.aggregate((g, lc) => {
                        try {
                            lc = lc['current_movement_class']
                            var trace1 = {
                                x: g.select('time').toArray().map((e) => e[0] % 1440),
                                name: movement[lc],
                                type: "histogram",
                            };
                            data.push(trace1);
                        } catch (error) {

                        }
                    });
                    setMoveHistData(data);
                })
            })

    }

    // show the population pie chart
    async function processPieChart() {
        console.log("loading data for pie chart of people")


        axios.post(api + "/flask/csvfile", {
            dir: selectedLogDir, d: selectedDay.toString(),
            type: '_person_info', columns: "person|person_class"
        })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data).castAll(Array(3).fill(Number))

                    // setting people pie chart data
                    var grp = sub_df.groupBy("person_class")
                    var pieData = [];
                    var pieLabels = [];
                    grp.aggregate((g, pc) => {
                        try {
                            pc = pc['person_class']
                            pieLabels.push(people[pc])
                            try {
                                pieData.push(g.count())

                            } catch (error) {
                                pieData.push(0)
                            }
                        } catch (error) {

                        }
                    });
                    setPeoplePieData([{ type: 'pie', values: pieData, labels: pieLabels }]);

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

    // show population pyramid
    async function processPopPyramid() {
        axios.post(api + "/flask/csvfile", {
            dir: selectedLogDir, d: selectedDay.toString(),
            type: '_person_info', columns: "person_class|gender|age"
        })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data).castAll(Array(4).fill(Number))

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
                        hoverinfo: 'x',
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
                        hoverinfo: 'text',
                        orientation: 'h'
                    };
                    let data = [trace1, trace2];
                    setPopPyramidData(data);
                })
            })
    }

    // draw sunburst location graph
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

                    setLocTreeData(data);

                })
            })


    }
    // draw infection graph
    async function plotInfectionGraph() {
        axios.post(api + "/flask/infectiontree", { dir: selectedLogDir })
            .then(function (response) {
                const data = response.data.data;
                console.log(data)
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var sub_df = new DataFrame(json_data)
                    console.log(sub_df)
                    setInfectionGraphData([
                        {
                            type: "sunburst", //sunburst
                            ids: sub_df.toArray('id'),
                            labels: sub_df.toArray('id'),
                            parents: sub_df.toArray('parent'),
                            value: sub_df.toArray('time')
                        }
                    ]);


                });

            })
            .catch(function (response) {
                console.log(response);
            });


    }

    // plot number of contacts grouped
    function plotNumberOfContacts() {
        // axios.post(api + "/flask/n_contacts", { dir: selectedLogDir, group_by: selectedGroup })
        //     .then(function (response) {
        //         const data = response.data.n_contacts;
        //         console.log(data)
        //         csv2JSONarr(data, (pr) => { }).then((json_data) => {
        //             var _df = new DataFrame(json_data)
        //             let plotData = [{
        //                 type: 'bar',
        //                 x: _df.toArray('group'),
        //                 y: _df.toArray('n_contacts'),
        //             }]

        //             setContactHistData(plotData)

        //         });

        //     })
        //     .catch(function (response) {
        //         console.log(response);
        //     });

        axios.post(api + "/flask/contacts", { dir: selectedLogDir, group_by: selectedGroup })
            .then(function (response) {
                const data = response.data.contacts;
                console.log(data)
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    let plotData = [{
                        type: 'surface',
                        z: _df.toArray(),
                        contours: {
                            z: {
                                show: true,
                                usecolormap: true,
                                highlightcolor: "#42f462",
                                project: { z: true }
                            }
                        }
                    }]

                    setContactHistData(plotData)

                });

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
                        data: data2.map((e) => ({ 'transforms[0].value': t, 'transforms[1].value': Math.max(0, t - 10) }))
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
                            console.log(locClassColors[parseInt(row.get('class'))])
                            var trace1 = {
                                type: 'circle',
                                xref: 'x',
                                yref: 'y',
                                fillcolor: locClassColors[parseInt(row.get('class'))],//'rgba(50, 171, 96, 0.1)',
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

    const handleSelectGroup = (e) => {
        setSelectedGroup(e.target.value)
    }

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
                <h1>Sim results page</h1>

                {loadprogress != 0 && <CircularProgress variant="determinate" value={loadprogress} />}
                <div>
                    <h4>Select log location</h4>
                    {/* <input directory="" webkitdirectory="" type="file" onChange={(event) => handleSelectDir(event)} /> */}
                    <FormControl variant="outlined" style={{ padding: 20, width: 200 }}>
                        <InputLabel id="select-day">Selected Log</InputLabel>
                        <Select
                            labelId="select-log-label"
                            id="select-log"
                            value={selectedLogDir}
                            onChange={handleSelectDir}
                            label="Selected Log"
                        >
                            {dirs.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}

                        </Select>
                        <Button onClick={refreshDirs}>Refresh</Button>
                    </FormControl>
                    <FormGroup row style={{ maxWidth: 500, padding: 30 }}>
                        {people.map((p) => {
                            return (
                                <FormControlLabel
                                    control={<Checkbox checked={peopleCheckedState[p]} onChange={handlePeopleCheckChange} name={p} key={p} />}
                                    label={p}
                                />
                            )
                        })}

                        <Button variant="contained" color="primary" onClick={handleAnalyzePeopleClick}>Analyze only selected people</Button>
                    </FormGroup>
                </div>
                <FormControl variant="outlined" style={{ padding: 20, width: 200 }}>
                    <InputLabel id="select-day">Selected Day</InputLabel>
                    <Select
                        labelId="select-day-label"
                        id="select-day"
                        value={selectedDay}
                        onChange={handleDayChange}
                        label="Selected Day"
                    >
                        {days.map((e) => {
                            return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                        })}

                    </Select>
                </FormControl>

                <div>
                    <h4>Overall information</h4>
                    <Plot
                        data={peoplePieData}
                        layout={{
                            title: 'Distribution of people',
                        }}
                    // onLegendClick={handlePieLegendClick}
                    />
                    <Plot
                        data={popPyramidData}
                        layout={{
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
                        }}
                    />
                    <Plot
                        data={locTreeData}
                        layout={{
                            title: 'Location Tree Structure',
                            width: 800,
                            height: 800
                        }}
                    />
                </div>
                <div>
                    <h4>COVID-19 Spread Analysis</h4>
                    <Plot
                        data={stateTimelineData}
                        layout={{
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
                        }}
                    />
                    <Plot
                        data={infectionGraphData}
                        layout={{
                            title: 'Infection tree with time',
                        }}
                    />
                    <div>
                        <Plot
                            data={contactHistData}
                            layout={{
                                title: 'Number of contacts for each group',
                            }}
                        />
                        <Select
                            id="select-group"
                            value={selectedGroup}
                            onChange={handleSelectGroup}
                            label="Selected Log"
                        >
                            {groupOptions.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}

                        </Select>
                        <Button onClick={plotNumberOfContacts}>Plot N Contacts</Button>
                    </div>
                </div>
                <div>
                    <h4>Daily mobility data analysis</h4>
                    <Plot
                        data={locHistData}
                        layout={{
                            barmode: 'stack',
                            title: 'Histogram of visited places during the day',
                            xaxis: {
                                title: 'Time (minutes)',
                                showticklabels: true,
                                // tickformat: "%H:%M:%S s",
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
                        }}
                    />
                    <Plot
                        data={routeHistData}
                        layout={{
                            barmode: 'stack',
                            title: 'Histogram of planned visits in route during the day',
                            // bargroupgap: 0,
                            // bargap: 0,
                            xaxis: {
                                title: 'Time (hours)',
                                // range: [0, 1440*60*1000],
                                titlefont: {
                                    family: 'Arial, sans-serif',
                                    size: 18,
                                    color: 'lightgrey'
                                },
                                showticklabels: true,
                                // tickformat: "%H:%M:%S s",
                                tickangle: 'auto',
                                tickfont: {
                                    family: 'Old Standard TT, serif',
                                    size: 14,
                                    color: 'black'
                                },
                                exponentformat: 'e',
                                showexponent: 'all'
                            },
                            yaxis: {
                                title: 'Number of people',
                                titlefont: {
                                    family: 'Arial, sans-serif',
                                    size: 18,
                                    color: 'lightgrey'
                                },
                                showticklabels: true,
                                tickangle: 45,
                                tickfont: {
                                    family: 'Old Standard TT, serif',
                                    size: 14,
                                    color: 'black'
                                },
                                exponentformat: 'e',
                                showexponent: 'all'
                            }
                        }}
                    />
                    <br />
                    <Plot
                        data={moveHistData}
                        layout={{
                            barmode: 'stack',
                            title: 'Histogram of movement methods of people during the day',
                            xaxis: {
                                title: 'Time (minutes)',
                                // titlefont: {
                                //     family: 'Arial, sans-serif',
                                //     size: 18,
                                //     color: 'lightgrey'
                                // },
                                showticklabels: true,
                                // tickformat: "%H:%M:%S s",
                                tickangle: 'auto',
                                // tickfont: {
                                //     family: 'Old Standard TT, serif',
                                //     size: 14,
                                //     color: 'black'
                                // },
                                exponentformat: 'e',
                                showexponent: 'all'
                            },
                            yaxis: {
                                title: 'Number of people',
                                // titlefont: {
                                //     family: 'Arial, sans-serif',
                                //     size: 18,
                                //     color: 'lightgrey'
                                // },
                                showticklabels: true,
                                // tickangle: 45,
                                // tickfont: {
                                //     family: 'Old Standard TT, serif',
                                //     size: 14,
                                //     color: 'black'
                                // },
                                exponentformat: 'e',
                                showexponent: 'all'
                            }
                        }}
                    />

                </div>
                <br></br>


                <div>
                    <h4>Daily personal mobility data analysis</h4>

                    <Grid container
                        direction="row"
                        justifyContent="center"
                        alignItems="center"
                    >
                        <FormControl                             >
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

            </div>
            <br></br>
            <div>
                <ConsoleLog />
            </div>
        </div>
    );
}


export default ResultsPage;