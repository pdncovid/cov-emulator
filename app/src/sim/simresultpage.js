import React, { useState, useRef, useEffect } from "react";

import Plot from 'react-plotly.js';
import { csvJSON } from "../utils/files";

import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';


import * as dfd from "danfojs/src/index";

function ResultsPage() {

    const [initialLoad, setInitialLoad] = useState(true);

    var layout = {
        barmode: 'stack',
        title: 'Histogram of visited places during the day',
        xaxis: {
            title: 'Time (minutes)',
            range: [0, 1440],
            titlefont: {
                family: 'Arial, sans-serif',
                size: 18,
                color: 'lightgrey'
            },
            showticklabels: true,
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
    };

    const [locs, setLocs] = useState([]);
    const [people, setPeople] = useState([]);
    const [movement, setMovement] = useState([]);

    const [logs, setLogs] = useState([]);
    const [days, setDays] = useState([0]);

    const [locHistData, setLocHistData] = useState([]);

    const [selectedLog, setSelectLog] = useState('');
    const [selectedDay, setSelectDay] = useState(0);

    const [loadedDf, setLoadedDf] = useState([]);

    useEffect(() => {
    }, [initialLoad])

    useEffect(() => {
        try {
            loadedDf.loc({ columns: ["loc_class", "time"] })
            console.log(loadedDf.size);
        } catch {
            return;
        }


        let sub_df = loadedDf.loc({ columns: ["loc_class", "time"] })
        console.log("Clipping for values on day " + selectedDay + " " + selectedDay * 1440 + "<t<" + (selectedDay + 1) * 1440 + " only.")
        sub_df = sub_df.query({ column: "time", is: ">=", to: selectedDay * 1440 })
        sub_df = sub_df.query({ column: "time", is: "<", to: (selectedDay + 1) * 1440 })
        console.log("Clipping done.")


        let grp = sub_df.groupby(["loc_class"])

        var data = [];
        locs.forEach((lc, i) => {
            try {
                console.log(lc + " " + (i + 1) + "/" + locs.length + " : Searching for time")
                // let query_df = sub_df.query({ column: "loc_class", is: "==", to: i })
                console.log()
                var trace1 = {
                    x: grp.col_dict[i].map((e) => e[1] % 1440),
                    name: lc,
                    type: "histogram",
                };
                data.push(trace1);
            } catch (error) {
                console.log(lc + " : nothing in dataset")
            }

        });
        setLocHistData(data);
    }, [loadedDf, selectedDay, logs])

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
                    var people_str = data.split("\n");
                    // var people_dic = {}
                    // for (let j = 0; j < people_str.length; j++) {
                    //     people_dic[people_str[j]] = j;
                    // }
                    setPeople(people_str);
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

        var log_files = []
        const to_ignore = ["locs.txt", "people.txt", "movement.txt"]

        for (let i = 0; i < files.length; i++) {
            if (to_ignore.indexOf(files[i].name) == -1) {
                log_files.push(files[i]);
            }
        }
        console.log(log_files);
        setLogs(log_files);
    }

    const handleLogChange = (event) => {
        setSelectLog(event.target.value);
        logs.forEach(element => {
            if (element.name == event.target.value) {
                console.log("Loading CSV!");
                const reader = new FileReader();
                reader.onload = (evt) => {
                    const data = evt.target.result;

                    let json_data = csvJSON(data);
                    var _df = new dfd.DataFrame(json_data)
                    let int_cols = ["person", "location", "person_class", "loc_class", "cur_movement", "cur_tar_idx", "route_len", "time"];
                    int_cols.forEach(element => {
                        _df = _df.astype({
                            column: element,
                            dtype: "int32"
                        })
                    });
                    setLoadedDf(_df)
                    console.log("Loading COMPLETE!");

                    let _days = []
                    for (let d = 0; d <= Math.floor(_df.time.max() / 1440); d++) {
                        _days.push(d);
                    }
                    setDays(_days);
                    setSelectDay(0);

                };
                reader.readAsText(element);
            }
        });

    };

    const handleDayChange = (event) => {
        setSelectDay(event.target.value)
    }



    return (
        <div className="results-page">
            <h1>Sim results page</h1>
            <input directory="" webkitdirectory="" type="file" onChange={(event) => handleSelectDir(event)} />
            <div>
                <FormControl variant="outlined" style={{ minWidth: 120 }}>
                    <InputLabel id="select-log">Selected Log</InputLabel>
                    <Select
                        labelId="select-log-label"
                        id="select-log"
                        value={selectedLog}
                        onChange={handleLogChange}
                        label="Selected Log"
                    >
                        {logs.map((e) => {
                            return (<MenuItem value={e.name} key={e.name}>{e.name}</MenuItem>);
                        })}

                    </Select>
                </FormControl>
                <FormControl variant="outlined" style={{ minWidth: 120 }}>
                    <InputLabel id="select-log">Selected Day</InputLabel>
                    <Select
                        labelId="select-log-label"
                        id="select-log"
                        value={selectedDay}
                        onChange={handleDayChange}
                        label="Selected Day"
                    >
                        {days.map((e) => {
                            return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                        })}

                    </Select>
                </FormControl>
            </div>
            <Plot
                data={locHistData}
                layout={layout}
            />

            <Plot
                data={[
                    {
                        x: [1, 2, 3],
                        y: [2, 6, 3],
                        type: 'scatter',
                        mode: 'lines+markers',
                        marker: { color: 'red' },
                    },
                    { type: 'bar', x: [1, 2, 3], y: [2, 5, 3] },
                ]}
                layout={{ width: 320, height: 240, title: 'A Fancy Plot' }}
            />

        </div>
    );
}
export default ResultsPage;