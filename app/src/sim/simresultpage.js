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

import DataFrame from 'dataframe-js';

function ResultsPage() {

    const [initialLoad, setInitialLoad] = useState(true);
    const [loadprogress, setLoadprogress] = useState(0);

    const [locs, setLocs] = useState([]);
    const [people, setPeople] = useState([]);
    const [movement, setMovement] = useState([]);

    const [selectedPeople, setSelectedPeople] = useState([]);
    const [peopleCheckedState, setPeopleCheckedState] = React.useState({});

    const [days, setDays] = useState([]);
    const [selectedDay, setSelectedDay] = useState('');
    const [day_logs, setDayLogs] = useState([]);
    const [person_info_logs, setPersonInfoLogs] = useState([]);
    const [cov_info_logs, setCovInfoLogs] = useState([]);

    const [unstagedPeople, setUnstagedPeople] = useState([]);
    const [stagedPeople, setStagedPeople] = useState([]);
    const [selectedUnstagedPeople, setSelectedUnstagedPeople] = useState([]);
    const [selectedStagedPeople, setSelectedStagedPeople] = useState([]);


    const [locHistData, setLocHistData] = useState([]);
    const [moveHistData, setMoveHistData] = useState([]);
    const [peoplePieData, setPeoplePieData] = useState([]);
    const [routeHistData, setRouteHistData] = useState([]);
    const [popPyramidData, setPopPyramidData] = useState([]);
    const [personPathData, setPersonPathData] = useState([]);
    const [stateTimelineData, setStateTimelineData] = useState([]);



    const [loadedDf, setLoadedDf] = useState([]);
    const [loadedPersonDf, setLoadedPersonDf] = useState([]);

    const [processedDf, setProcessedDf] = useState([]);
    const [processedPersonDf, setProcessedPersonDf] = useState([]);

    useEffect(() => {
    }, [initialLoad])

    //processLocHist
    useEffect(() => {
        try {
            processedDf.select("loc_class")
        } catch {
            return;
        }
        var sub_df = processedDf;
        processLocHist(sub_df)
        processMoveHist(sub_df)

    }, [processedDf])

    //processRouteHist
    //processPieChart
    useEffect(() => {
        try {
            processedPersonDf.select("person")
        } catch {
            return;
        }
        var sub_df = processedPersonDf;
        processRouteHist(sub_df)
        processPieChart(sub_df)
        processPopPyramid(sub_df)
    }, [processedPersonDf])

    //set selected people ids
    useEffect(() => {
        try {
            processedPersonDf.select("person")
        } catch {
            return;
        }
        let person_class = processedPersonDf.select('person_class').toArray().map((e) => people[e[0]])
        let person_id = processedPersonDf.select('person').toArray().map((e) => e[0])
        var arr = [];
        person_id.forEach((e, i) => {
            arr.push(e + " " + person_class[i])
        });
        setUnstagedPeople(arr);
        setStagedPeople([]);
        setSelectedUnstagedPeople([])
        setSelectedStagedPeople([])
    }, [processedPersonDf])

    //draw person path
    useEffect(() => {
        try {
            processedDf.select("loc_class")
        } catch {
            return;
        }
        drawPersonPath(processedDf)
    }, [stagedPeople])

    useEffect(() => {
        var cov_df = null;
        cov_info_logs.forEach(file => {
            console.log("loading " + file.name);
            loadfile(file).then(_df => {
                _df = _df.castAll(Array(_df.listColumns().length).fill(Number))
                // console.log("Dropping missing values")
                // _df = _df.dropMissingValues();
                // console.log("Dropping missing values: DONE")

                
                // if (cov_df == null) {
                //     cov_df = _df;
                // } else {
                //     cov_df = cov_df.join(_df, _df.listColumns(), 'outer')
                // }
                drawCovidStateTimeline(_df)
            }, (error) => { });

        });

        // console.log(cov_df) // not initialized!!!
    }, [cov_info_logs])

    async function drawCovidStateTimeline(df) {
        let _x = df.select("time").toArray().map((e) => e[0]/1440)
        df.listColumns().forEach(col => {
            if (col == "time" || col == "") {
            } else {
                var is_found = false;
                stateTimelineData.forEach(trace => {
                    if (trace.name == col) {
                        trace.x=trace.x.concat(_x)
                        trace.y=trace.y.concat(df.select(col).toArray().map((e) => e[0]))
                        is_found = true;
                    }
                });
                if (is_found == false) {
                    var trace1 = {
                        x: _x,
                        y: df.select(col).toArray().map((e) => e[0]),
                        name: col,
                        mode: 'line',
                    };
                    stateTimelineData.push(trace1)
                }
            }
        });
        console.log(stateTimelineData)
        setStateTimelineData([...stateTimelineData]);
    }

    async function processLocHist(sub_df) {
        sub_df = sub_df.restructure(["loc_class", "time", "person_class"])

        console.log("grouping")
        let grp = sub_df.groupBy("loc_class")
        var data = [];
        grp.aggregate((g, lc) => {
            try {
                lc = lc['loc_class']
                console.log("Agg time in " + locs[lc])

                var trace1 = {
                    x: g.select('time').toArray().map((e) => e[0] % 1440),
                    name: locs[lc],
                    type: "histogram",
                };
                data.push(trace1);
            } catch (error) {

            }
        });
        setLocHistData(data);
    }
    async function processMoveHist(sub_df) {
        sub_df = sub_df.restructure(["cur_movement", "time", "person_class"])

        console.log("grouping")
        let grp = sub_df.groupBy("cur_movement")

        var data = [];
        grp.aggregate((g, lc) => {
            try {
                lc = lc['cur_movement']
                console.log("Agg time in " + movement[lc])

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
    }
    async function processRouteHist(sub_df) {
        sub_df = sub_df.restructure(["person", "route", "person_class"])

        // sub_df = sub_df.map(row => row.set('route', row.get('route')))

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





    }
    async function processPieChart(sub_df) {
        console.log("loading data for pie chart of people")
        var pieData = [];
        var pieLabels = [];

        sub_df = sub_df.restructure(["person_class", "person"])

        console.log("Grouping")
        var grp = sub_df.groupBy("person_class")
        grp.aggregate((g, pc) => {
            try {
                pc = pc['person_class']
                console.log("Agg count in " + pc + " " + people[pc])
                pieLabels.push(people[pc])
                try {
                    pieData.push(g.count())

                } catch (error) {
                    pieData.push(0)
                }
            } catch (error) {

            }
        });
        console.log(pieData, pieLabels)
        setPeoplePieData([{ type: 'pie', values: pieData, labels: pieLabels }]);


    }
    async function processPopPyramid(sub_df) {
        sub_df = sub_df.restructure(["person_class", "gender", "age"])

        let m_bins = hist(sub_df.where(row => row.get('gender') == 1).select('age').toArray().map((e) => e[0]), 10, 10);
        let f_bins = hist(sub_df.where(row => row.get('gender') == 0).select('age').toArray().map((e) => e[0]), 10, 10);
        console.log(f_bins)
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
    }

    async function drawPersonPath(sub_df) {
        sub_df = sub_df.restructure(["person", "time", "x", "y"])
        console.log("grouping")
        let grp = sub_df.groupBy("person")
        var data = [];
        let _selected = stagedPeople.map((e) => parseInt(e.split(' ')[0]))
        console.log(_selected, stagedPeople)
        grp.aggregate((g, p) => {
            try {
                p = p['person']
                if (_selected.indexOf(p) != -1) {
                    var trace1 = {
                        x: g.select('x').toArray().map((e) => e[0]),
                        y: g.select('y').toArray().map((e) => e[0]),
                        name: p,
                        mode: 'line',
                    };
                    data.push(trace1);
                }
            } catch (error) {

            }
        });
        setPersonPathData(data);
    }



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

        let map = {}
        for (let i = 0; i < people.length; i++) {
            map[i] = false;
        }
        for (let i = 0; i < _selectedPeople.length; i++) {
            map[people.indexOf(_selectedPeople[i])] = true;
            console.log("selected person class " + _selectedPeople[i])
        }
        let sub_df = loadedPersonDf.where(row => map[row.get('person_class')] == true)
        setProcessedPersonDf(sub_df)
        let sub_df2 = loadedDf.where(row => map[row.get('person_class')] == true)
        setProcessedDf(sub_df2)
    }

    // file loading

    function loadfile(file) {
        return new Promise((resolve, reject) => {
            console.log("Loading - " + file);
            const reader = new FileReader();
            reader.onload = (evt) => {
                const data = evt.target.result;
                // setTimeout(() => {
                csv2JSONarr(data, (pr) => {
                    // setTimeout(() => {
                    // setLoadprogress(pr);
                    // }, 100);

                }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    console.log("Loading COMPLETE!");
                    resolve(_df)
                });
                // }, 10);

                // let int_cols = ["person", "location", "person_class", "loc_class", "cur_movement", "cur_tar_idx", "route_len", "time"];
                // int_cols.forEach(element => {
                //     _df = _df.astype({
                //         column: element,
                //         dtype: "int32"
                //     })
                // });



            };
            reader.readAsText(file);
            // console.log(file)
            // DataFrame.fromCSV("http://localhost:3000/data/"+file.webkitRelativePath).then(df => {
            //     console.log(df)
            //     resolve(df)
            // });
        });

    }

    const handleSelectDir = function (event) {
        const files = event.target.files;
        console.log(files);

        // Loading Locations
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.name == "locs.txt") {
                const reader = new FileReader();
                reader.onload = (evt) => {
                    const data = evt.target.result;
                    var locs_str = data.split("\n");
                    // var locs_dic = {}
                    // for (let j = 0; j < locs_str.length; j++) {
                    //     locs_dic[locs_str[j]] = j;
                    // }
                    setLocs(locs_str);
                    console.log(locs_str);

                };
                reader.readAsText(file);
                break;
            }
        }

        // Loading People
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.name == "people.txt") {
                const reader = new FileReader();
                reader.onload = (evt) => {
                    const data = evt.target.result;
                    var people_str = data.split("\n").map((e) => strip_text(e));
                    // var people_dic = {}
                    // for (let j = 0; j < people_str.length; j++) {
                    //     people_dic[people_str[j]] = j;
                    // }
                    people_str.forEach(element => {
                        peopleCheckedState[element] = true;
                    });
                    setPeople(people_str);
                    setSelectedPeople(people_str);
                    console.log(people_str);

                };
                reader.readAsText(file);
                break;
            }
        }

        // Loading Movement
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            if (file.name == "movement.txt") {
                const reader = new FileReader();
                reader.onload = (evt) => {
                    const data = evt.target.result;
                    var movement_str = data.split("\n");
                    // var movement_dic = {}
                    // for (let j = 0; j < movement_str.length; j++) {
                    //     movement_dic[movement_str[j]] = j;
                    // }
                    setMovement(movement_str);
                    console.log(movement_str);

                };
                reader.readAsText(file);
                break;
            }
        }

        var day_log_files = []
        var person_info_log_files = []
        var cov_info_log_files = []
        const to_ignore = ["locs.txt", "people.txt", "movement.txt"]

        for (let i = 0; i < files.length; i++) {
            if (to_ignore.indexOf(files[i].name) != -1) {
                continue
            }
            if (files[i].name.search("person_info") != -1) {
                person_info_log_files.push(files[i])
                continue
            }
            if (files[i].name.search("cov_info") != -1) {
                cov_info_log_files.push(files[i])
                continue
            }
            day_log_files.push(files[i]);
        }
        var _days = []
        for (let i = 0; i < day_log_files.length; i++) {
            _days.push(i);
        }

        console.log(day_log_files, person_info_log_files);
        setDays(_days)
        setPersonInfoLogs(person_info_log_files)
        setCovInfoLogs(cov_info_log_files)
        setDayLogs(day_log_files);
        setLoadedDf([])
        setLoadedPersonDf([])
    }
    const handleDayChange = function (event) {
        console.log(event.target)
        setSelectedDay(event.target.value);
        loadLog(padZeros(event.target.value.toString(), 5) + '.csv')
        loadPersonLog(padZeros(event.target.value.toString(), 5) + '_person_info.csv')
    }

    const loadLog = async (filename) => {
        console.log("Loading file " + filename);
        day_logs.forEach(element => {
            if (element.name == filename) {
                let promise = loadfile(element)
                promise.then(_df => {
                    _df = _df.castAll(Array(_df.listColumns().length).fill(Number))
                    console.log("Dropping missing values")
                    _df = _df.dropMissingValues();
                    console.log("Dropping missing values: DONE")
                    setLoadedDf(_df);
                    setProcessedDf(_df);
                    // let _days = []
                    // for (let d = 0; d <= Math.floor(_df.stat.max('time') / 1440); d++) {
                    //     _days.push(d);
                    // }
                    // setDays(_days);
                    // setSelectDay(0);
                    // setLoadprogress(0);
                }, (error) => { });

            }
        });

    };
    const loadPersonLog = async (filename) => {
        console.log("Loading file " + filename);
        person_info_logs.forEach(element => {
            if (element.name == filename) {
                loadfile(element).then(_df => {
                    let cast = []
                    _df.listColumns().forEach((e) => {
                        if (e == "route" || e == "character_vector") {
                            cast.push(String)
                        } else {
                            cast.push(Number)
                        }
                    })
                    _df = _df.castAll(cast)
                    console.log("Dropping missing values")
                    _df = _df.dropMissingValues();
                    console.log("Dropping missing values: DONE")
                    setLoadedPersonDf(_df);
                    setProcessedPersonDf(_df);
                    // setLoadprogress(0);
                }, (error) => { });

            }
        });

    };


    // Daily personal mobility data analysis

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
            _unstagedPeople.splice(_unstagedPeople.indexOf(element),1)
            
        });
        setUnstagedPeople(_unstagedPeople)
        setStagedPeople(_stagedPeople)
        setSelectedUnstagedPeople([])
    }
    const handleAddtoUnstageClick = function (event) {
        var _unstagedPeople = []; unstagedPeople.forEach((e => _unstagedPeople.push(e)));
        var _stagedPeople = []; stagedPeople.forEach((e => _stagedPeople.push(e)));
        selectedStagedPeople.forEach(element => {
            _stagedPeople.splice(_stagedPeople.indexOf(element),1)
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
                    <input directory="" webkitdirectory="" type="file" onChange={(event) => handleSelectDir(event)} />

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
                    <h4>Person info analysis</h4>
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
                        layout={{
                            barmode: 'stack',
                            title: 'Path took by the selected person',
                            xaxis: {
                                showticklabels: true,
                                tickangle: 'auto',
                                exponentformat: 'e',
                                showexponent: 'all'
                            },
                            yaxis: {
                                showticklabels: true,
                                exponentformat: 'e',
                                showexponent: 'all'
                            }
                        }}
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