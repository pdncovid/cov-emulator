import React, { useState, useRef, useEffect } from "react";
import { makeStyles, useTheme } from '@material-ui/core/styles';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';
import ToggleButton from '@material-ui/lab/ToggleButton';
import ToggleButtonGroup from '@material-ui/lab/ToggleButtonGroup';
import Radio from '@material-ui/core/Radio';
import RadioGroup from '@material-ui/core/RadioGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import FormControl from '@material-ui/core/FormControl';
import FormLabel from '@material-ui/core/FormLabel';
import Typography from '@material-ui/core/Typography';
import Slider from '@material-ui/core/Slider';
import Grid from '@material-ui/core/Grid';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import InputLabel from '@material-ui/core/InputLabel';

import Snackbar from '@material-ui/core/Snackbar';
import IconButton from '@material-ui/core/IconButton';
import CloseIcon from '@material-ui/icons/Close';

import DataFrame from 'dataframe-js';

import * as Plotly from 'plotly.js';

import Table from "../components/table"
import axios from 'axios'
import { api } from '../utils/constants';
import { csvJSON, csv2JSONarr, strip_text } from "../utils/files";

import Alert from "react-bootstrap/Alert";
import randomColor from "randomcolor";
import { Stage, Layer, Line, Text } from "react-konva";
import MyGrid from "../components/grid";
import { ExportToCsv } from 'export-to-csv';

function loadData(csvFileName, setDataFunc, setColumnsFunc) {
    axios.post(api + "/flask/csvfile", { dir: '', type: csvFileName })
        .then(function (response) {
            let data = response.data.data;
            csv2JSONarr(data, (pr) => { }).then((json_data) => {
                var _data = []
                var _columns = []
                for (var i in json_data) {
                    _columns.push({
                        Header: i,
                        accessor: i,
                    })
                }
                for (var i = 0; i < json_data[_columns[0].accessor].length; i++) {
                    var _row = {}
                    for (var col in _columns) {
                        _row[_columns[col].accessor] = json_data[_columns[col].accessor][i]
                    }
                    _data.push(_row)
                }
                setColumnsFunc(_columns)
                setDataFunc(_data)

            })
        })

}




function ProbDensePage() {
    const classes = useStyles();
    const [initialLoad, setInitialLoad] = useState(true);
    const stageEl = React.createRef();
    const layerEl = React.createRef();
    // const csvLink = React.createRef();

    var canvas_width = 1000;
    var canvas_height = 500;

    const [gs_y, setGSY] = useState(400);
    const [gs_x, setGSX] = useState(30);
    var x_axis_distance_grid_lines = (canvas_height - 40) / gs_y;
    var y_axis_distance_grid_lines = 0.5 / (gs_x / 60);

    const [snackopen, setSnackOpen] = React.useState(false);

    const [matrixNames, setMatrixNames] = useState([]);

    const [selectedLines, setSelectedLines] = useState([]);
    const [highlightedLines, setHighlightedLines] = useState([]);
    const [selectedPerson, setSelectedPerson] = useState('');
    const [selectedLoc, setSelectedLoc] = useState('');
    const [allData, setAllData] = useState({});
    const [updateHeatmap, setUpdateHeatMap] = useState(false)

    const [isDown, setIsDown] = useState(false);
    const [consoleText, setConsoleText] = useState("HSW");
    const [lines, setLines] = useState([]);
    // const lines = useRef([]);

    const [prevX, setprevX] = useState(0);
    const [prevY, setprevY] = useState(0);
    const [posx, setposx] = useState(0);
    const [posy, setposy] = useState(0);


    const [selectedCopyFromClass, setSelectedCopyFromClass] = useState('');
    const [selectedCopyToClass, setSelectedCopyToClass] = useState('');

    const [people, setpeople] = useState([]);
    const [locs, setlocs] = useState(['_home', '_w_home', '_work']);

    // table states
    const [locationcolumns, setlocationColumns] = useState([])
    const [locationdata, setlocationData] = useState([])
    const [skiplocationPageReset, setSkiplocationPageReset] = useState(false)

    const [personcolumns, setpersonColumns] = useState([])
    const [persondata, setpersonData] = useState([])
    const [skippersonPageReset, setSkippersonPageReset] = useState(false)

    const [movementcolumns, setmovementColumns] = useState([])
    const [movementdata, setmovementData] = useState([])
    const [skipmovementPageReset, setSkipmovementPageReset] = useState(false)

    const columns = [{ Header: 'person', accessor: 'person' }, { Header: 'location', accessor: 'location' }]
    for (let time = 0; time < 60 * 24; time++) {
        columns.push({ Header: time.toString(), accessor: time.toString() })
    }


    const convertpx2x = function (px) {
        return (px - (y_axis_distance_grid_lines * gs_x) - posx) / gs_x;
    }
    const convertpy2y = function (py) {
        return -(py - (x_axis_distance_grid_lines * gs_y) - posy) / gs_y;
    }
    const convertx2px = function (x) {
        return (x * gs_x) + (y_axis_distance_grid_lines * gs_x)
    }
    const converty2py = function (y) {
        return -(y * gs_y) + (x_axis_distance_grid_lines * gs_y)
    }


    useEffect(() => {

        console.log("Initializing Prob page")
        console.log("loading people, location classes");
        loadData('location_classes.csv', setlocationData, setlocationColumns)
        loadData('person_classes.csv', setpersonData, setpersonColumns)
        loadData('movement_classes.csv', setmovementData, setmovementColumns)

        refreshClasses()

    }, [initialLoad])


    useEffect(() => {
        if (updateHeatmap) {
            var graphDiv = document.getElementById("matrixHeatMap")
            var _data = []
            var _ylabels = []
            var _xlabels = []
            selectedLines.forEach(key => {
                _data.push(allData[key])
                _ylabels.push(key.toString())
                _xlabels = [...Array(allData[key].length).keys()]
            })
            // if (graphDiv.data == undefined) {
            console.log("heatmap", _data, graphDiv)
            Plotly.newPlot(graphDiv, [{
                x: _xlabels,
                y: _ylabels,
                z: _data,
                type: 'heatmap'
            }], {
                title: 'Selected location-person pairs',
                width: 800,
                height: 600,
                yaxis: {
                    tickangle: -45,
                    automargin: true,
                },
                autosize: false,

            })
            // } else {
            //     console.log("heatmap update", _data, graphDiv.data)
            //     Plotly.update(graphDiv, { x: _xlabels, y: _ylabels, z: _data, }, {} )
            // }
            setUpdateHeatMap(false)
        }
    }, [updateHeatmap])

    useEffect(() => {
        let ps = []
        let ls = [];
        while (lines.length > 0) {
            ps.push(lines[0].key[0]);
            ls.push(lines[0].key[1]);
            removeLine(lines[0].key.toString());
        }
        for (let i = 0; i < ps.length; i++) {
            addLine(ps[i], ls[i])
        }


    }, [gs_x, gs_y])

    useEffect(() => {
        for (var p_idx = 0; p_idx < lines.length; p_idx++) {
            lines[p_idx].values = allData[lines[p_idx].key]
            var points = lines[p_idx].points
            for (var i=0;i<points.length/2;i++){
                lines[p_idx].points[2 * i + 1] = converty2py(lines[p_idx].values[i])
            }            
        }
        setUpdateHeatMap(true)

    }, [allData])

    React.useEffect(() => {
        setSkiplocationPageReset(false)
    }, [locationdata])
    React.useEffect(() => {
        setSkippersonPageReset(false)
    }, [persondata])
    React.useEffect(() => {
        setSkipmovementPageReset(false)
    }, [movementdata])


    function refreshClasses() {
        // load matrix names
        axios.get(api + "/flask/matrix_names").then((response) => {
            setMatrixNames(response.data.data.split('|'))
        })
        // Loading Locations
        axios.post(api + "/flask/csvfile", { dir: '', type: 'location_classes.csv' })
            .then(function (response) {
                let data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    _df.select('l_class').toArray().map(e => e[0]).forEach((e) => {
                        if (e.length > 0) {
                            if (locs.indexOf(strip_text(e)) == -1)
                                addLoc(e);
                        }
                    })

                    // Loading People
                    axios.post(api + "/flask/csvfile", { dir: '', type: 'person_classes.csv' })
                        .then(function (response) {
                            let data = response.data.data;
                            csv2JSONarr(data, (pr) => { }).then((json_data) => {
                                var _df = new DataFrame(json_data)
                                console.log(_df);
                                _df.select('p_class').toArray().map(e => e[0]).forEach(element => {
                                    if (element.length > 0) {
                                        if (people.indexOf(strip_text(element)) == -1)
                                            addPerson(element);
                                    }
                                })
                                var _allData = {}
                                for (let i = 0; i < people.length; i++) {
                                    for (let j = 0; j < locs.length; j++) {
                                        // console.log("Initializing array for ", people[i], locs[j], i, j)
                                        _allData[[people[i], locs[j]]] = Array(24 * 60).fill(0);
                                    }
                                }
                                setAllData(_allData)
                            })

                        })
                })
            })


    }

    function saveData(csvFileName, toSaveData) {
        axios.post(api + "/flask/savecsvfile", { dir: '', filename: csvFileName, data: JSON.stringify(toSaveData) }).then((response) => {
            console.log(response)
            if (response.data.status == "Success") {
                setSnackOpen(true)
            }
        }
        )

    }

    function findxy(res, e) {

        if (res == 'down') {
            setIsDown(true)
            var coordx = convertpx2x(e.evt.clientX);
            var coordy = convertpy2y(e.evt.clientY);
            setprevX(coordx);
            setprevY(coordy);
            // update(coordx, coordy);
        }
        if (res == 'up' || res == "out") {
            setIsDown(false)
            lines.forEach(element => {
                allData[element.key] = element.values;
            });
        }
        if (res == 'move') {
            setposx(Math.round(stageEl.current.getContainer().getBoundingClientRect().left * 1000) / 1000);
            setposy(Math.round(stageEl.current.getContainer().getBoundingClientRect().top * 1000) / 1000);
            var _consoleText = ""
            // _consoleText +="pX=" + e.evt.clientX + " pY=" + e.evt.clientY 
            _consoleText += " Hours=" + parseInt(100 * convertpx2x(e.evt.clientX)) / 100
            _consoleText += " P=" + parseInt(100 * convertpy2y(e.evt.clientY)) / 100
            // _consoleText += "posX=" + posx + " posY=" + posy
            // _consoleText += "pX'=" + convertx2px(convertpx2x(e.evt.clientX)) + " pY'=" + converty2py(convertpy2y(e.evt.clientY))
            setConsoleText(_consoleText);
            // console.log(res, isDown)
            if (isDown) {

                var coordx = convertpx2x(e.evt.clientX);
                var coordy = convertpy2y(e.evt.clientY);
                update(coordx, coordy);
                setprevX(coordx);
                setprevY(coordy);


            }
        }
    }

    function update(x, y) {
        var x1 = Math.floor(prevX * 60);
        var x2 = Math.floor(x * 60);
        for (let l_idx = 0; l_idx < highlightedLines.length; l_idx++) {
            var _line;
            var _val;
            let p_idx = 0;
            for (p_idx = 0; p_idx < lines.length; p_idx++) {
                if (lines[p_idx].key == highlightedLines[l_idx]) {
                    _line = lines[p_idx].points
                    _val = lines[p_idx].values
                    break
                }
            }
            if (_line == undefined) {
                console.log("ERROR");
            }
            // console.log(x, y, x1, x2, lines[p_idx])
            for (var i = x1; i <= x2; i++) {
                var _y;
                if (x1 == x2) {
                    _y = y;
                } else {
                    _y = prevY + (y - prevY) * (i - x1) / (x2 - x1);
                }

                _y = Math.min(_y, 1);
                _y = Math.max(_y, 0);
                if (2 * i + 1 >= _line.length)
                    continue
                _line[2 * i + 1] = converty2py(_y);
                _val[i] = _y;
                if (isNaN(_line[2 * i + 1])) {
                    _line[2 * i + 1] = 0;
                }

            }
            for (var i = x2; i <= x1; i++) {
                var _y;
                if (x1 == x2) {
                    _y = y;
                } else {
                    _y = prevY + (y - prevY) * (i - x1) / (x2 - x1);
                }
                _y = Math.min(_y, 1);
                _y = Math.max(_y, 0);
                if (2 * i + 1 >= _line.length)
                    continue
                _line[2 * i + 1] = converty2py(_y);
                _val[i] = _y;
                if (isNaN(_line[2 * i + 1])) {
                    _line[2 * i + 1] = 0;
                }

            }
            lines[p_idx].values = _val;
            allData[lines[p_idx].key] = _val
            stageEl.current.children[1].children[p_idx].setPoints(_line);
        }
        setUpdateHeatMap(true)
    }

    function init_line(p, l, data) {
        // console.log("Initializing line for " + p + " " + l)
        var _line = Array(24 * 60 * 2).fill(0);
        for (var i = 0; i < 24 * 60; i++) {
            _line[i * 2] = convertx2px(i / 60);
            _line[i * 2 + 1] = converty2py(data[i])
        }
        let to_add = {
            points: _line,
            stroke: randomColor(),
            strokeWidth: 5,
            lineCap: 'round',
            lineJoin: 'round',
            key: [p, l],
            values: data,
        };
        return to_add;

    }

    function addLine(p, l) {
        if (p == undefined || l == undefined) {
            console.log("Person or location not selected")
            return
        }
        console.log("Adding line ", p, l, selectedLines);
        for (var i = 0; i < selectedLines.length; i++) {
            if (selectedLines[i][0] == p && selectedLines[i][1] == l) {
                console.log("Exists")
                return
            }
        }
        selectedLines.push([p, l]);

        if (allData.hasOwnProperty([p, l]) && allData[[p, l]] != undefined) {
            const line = init_line(p, l, allData[[p, l]]);

            for (let i = 0; i < lines.length; i++) {
                if (lines[i].key[0] == p && lines[i].key[1] == l) {
                    lines[i] = line;
                    return
                }
            }
            lines.push(line);
        } else {
            console.log("ERROR", allData);
            return
        }
        setUpdateHeatMap(true)

    }

    function removeLine(pl_key) {
        console.log("removing line " + pl_key)
        let _selectedLines = selectedLines;
        let _lines = lines;
        let _highlightedLines = highlightedLines;

        for (let j = 0; j < selectedLines.length; j++) {
            if (_selectedLines[j] == pl_key) {
                _selectedLines.splice(j, 1);
            }
        }
        for (let j = 0; j < lines.length; j++) {
            if (_lines[j].key == pl_key) {
                _lines.splice(j, 1);
            }
        }
        for (let j = 0; j < highlightedLines.length; j++) {
            if (_highlightedLines[j] == pl_key) {
                _highlightedLines.splice(j, 1);
            }
        }
        setSelectedLines(_selectedLines)
        setHighlightedLines(_highlightedLines)
        setLines(_lines)

    }

    function addLoc(element) {
        element = strip_text(element)
        if (element == 'Cemetery') {
            return;
        }
        locs.push(element);
        setlocs(locs.sort(function (a, b) {
            return a.localeCompare(b);
        }));

    }

    function addPerson(element) {
        element = strip_text(element)
        people.push(element);
        setpeople(people.sort(function (a, b) {
            return a.localeCompare(b);
        }))
    }

    const handlePersonClick = function (e) {

        setSelectedPerson(e.target.value);
    }

    const handleLocClick = function (e) {
        setSelectedLoc(e.target.value);
        addLine(selectedPerson, e.target.value)
    }

    const handleAddAllLocsClick = (event) => {

        for (let i = 0; i < locs.length; i += 1) {
            addLine(selectedPerson, locs[i]);
        }
    };


    const handleAddAllPeopleClick = (event) => {

        for (let i = 0; i < people.length; i += 1) {
            addLine(people[i], selectedLoc);
        }
    };

    const handleSelectedListClick = (event) => {
        const { options } = event.target;
        const value = [];
        for (let i = 0, l = options.length; i < l; i += 1) {
            if (options[i].selected) {
                value.push(options[i].value);
            }
        }
        setHighlightedLines(value);
    };

    const handleRemoveClick = (event) => {
        while (highlightedLines.length > 0) {
            removeLine(highlightedLines[0]);
        }
    };

    const handleSaveClick = (event) => {
        // const options = {
        //     filename: mode + 'LocPersonTime',
        //     fieldSeparator: ',',
        //     quoteStrings: '',
        //     decimalSeparator: '.',
        //     showLabels: true,
        //     showTitle: false,
        //     useTextFile: false,
        //     useBom: true,
        //     useKeysAsHeaders: true,
        //     // headers: ['Column 1', 'Column 2', etc...] <-- Won't work with useKeysAsHeaders present!
        // };


        var data_to_download = []
        for (let p = 0; p < people.length; p++) {
            for (let l = 0; l < locs.length; l++) {
                let record_to_download = { 'person': people[p], 'location': locs[l] }
                if (!allData.hasOwnProperty([people[p], locs[l]])) {
                    console.log(people[p], locs[l], "is not in Data!")
                    continue
                }
                for (var t = 0; t < allData[[people[p], locs[l]]].length; t++) {
                    record_to_download[t] = allData[[people[p], locs[l]]][t]
                }
                data_to_download.push(record_to_download)
            }


        }
        console.log("SAVE", data_to_download)

        // saveData("test.csv", data_to_download)
        saveData(document.getElementById("select-matrix").value, data_to_download)

        // const csvExporter = new ExportToCsv(options);
        // csvExporter.generateCsv(data_to_download);

    }
    const handleLoadClick = (e) => {
        // const file = e.target.files[0];
        // const reader = new FileReader();
        // reader.onload = (evt) => {
        // const bstr = evt.target.result;
        // const data = csvJSON(bstr);
        axios.post(api + "/flask/csvfile", { dir: '', type: e.target.value }).then(function (response) {
            let data = response.data.data;
            csv2JSONarr(data, (pr) => { }).then((data) => {
                var df = new DataFrame(data)
                var personlocation = df.select('person', 'location')
                df = df.toArray()
                console.log("Loaded", df)
                var _allData = {};
                for (let i = 0; i < df.length; i++) {
                    if (personlocation.getRow(i).get('person') == undefined || personlocation.getRow(i).get('location') == undefined) {
                        continue
                    }
                    let person = personlocation.getRow(i).get('person');
                    let location = personlocation.getRow(i).get('location');
                    let p = people.indexOf(person);
                    let l = locs.indexOf(location);
                    // console.log(data[i]['person'], p, data[i]['location'], l, people, locs)
                    if (p == -1) {
                        addPerson(person);
                        p = people.length - 1;
                    }
                    if (l == -1) {
                        addLoc(location);
                        l = locs.length - 1;
                    }

                    let arr = [];
                    for (let t = 0; t < 60 * 24; t++) {
                        arr.push(parseFloat(df[i][t]));
                    }
                    _allData[[person, location]] = arr;



                }
                for (let i = 0; i < people.length; i++) {
                    for (let j = 0; j < locs.length; j++) {
                        if (_allData.hasOwnProperty([people[i], locs[j]])) {
                            continue
                        }
                        _allData[[people[i], locs[j]]] = Array(24 * 60).fill(0);
                    }
                }

                console.log(_allData)
                setAllData(_allData)
            })
        })
        // reader.readAsText(file);
    }
    const handleSliderChange = (event, newValue) => {
        setGSX(newValue);
    };

    const handleCopyClick = (event) => {
        for (var l = 0; l < locs.length; l++) {
            let arr = [];
            for (let t = 0; t < 60 * 24; t++) {
                if (!allData.hasOwnProperty([selectedCopyFromClass, locs[l]])) {
                    console.log("Error when copying ", selectedCopyFromClass, locs[l])
                    continue
                }
                arr.push(parseFloat(allData[[selectedCopyFromClass, locs[l]]][t]));
            }
            allData[[selectedCopyToClass, locs[l]]] = arr;
        }
    }
    const handleClose = (event, reason) => {
        if (reason === 'clickaway') {
            return;
        }
        setSnackOpen(false);
    };

    return (
        <div className="prob-page" >
            <Snackbar
                open={snackopen}
                autoHideDuration={6000}
                onClose={handleClose}
                message="Saved"
                action={(
                    <React.Fragment>
                        <IconButton size="small" aria-label="close" color="inherit" onClick={handleClose}                        >
                            <CloseIcon fontSize="small" />
                        </IconButton>
                    </React.Fragment>
                )}
            />

            <Grid container xs={12} direction="column" alignContent="center">
                <Grid container direction="row" xs={12} spacing={3} style={{padding:10}}>
                    
                    <Grid item xs={4}>
                        <Typography>Zoom</Typography>
                        <Slider
                            onChange={handleSliderChange}
                            aria-labelledby="gs-slider"
                            valueLabelDisplay="auto"
                            step={1}
                            marks
                            min={30}
                            max={600}
                        />
                    </Grid>
                    <Grid item xs={4}>
                        <Button variant="contained" onClick={(e) => handleSaveClick(e)}>Save</Button>
                        <Button variant="contained" onClick={(e) => refreshClasses()}>Refresh Classes</Button>
                        <Select
                            native
                            onChange={(e) => handleLoadClick(e)}
                            style={{ width: 300 }}
                            id="select-matrix"

                        >
                            {matrixNames.map((element) => (
                                <option key={element} value={element}>
                                    {element}
                                </option>
                            ))}
                        </Select>
                        {/* <input
                            type="file"
                            accept=".csv,.xlsx,.xls"
                            onChange={handleLoadClick}
                            style={{ padding: 10 }}
                        /> */}

                    </Grid>
                </Grid>

                <Grid container xs={12}>
                    <Grid container xs={6}>
                        <Stage
                            width={canvas_width}
                            height={canvas_height}
                            ref={stageEl}
                            onMouseDown={e => {
                                findxy('down', e);
                            }}
                            onMouseMove={e => {
                                findxy('move', e);
                            }}
                            onMouseUp={e => {
                                findxy('up', e);
                            }}
                            onMouseOut={e => {
                                findxy('out', e);
                            }}
                        >
                            <MyGrid canvas_width={canvas_width}
                                canvas_height={canvas_height}
                                x_axis_distance_grid_lines={x_axis_distance_grid_lines}
                                y_axis_distance_grid_lines={y_axis_distance_grid_lines}
                                gs_y={gs_y}
                                gs_x={gs_x}
                                convertx2px={convertx2px}
                                converty2py={converty2py} />
                            <Layer ref={layerEl}>
                                {lines.map((line, i) => {
                                    return (
                                        <Line key={i} {...line} />
                                    );
                                })}
                            </Layer>
                        </Stage>

                    </Grid>
                    <Grid container xs={6}>
                        <div id="matrixHeatMap"></div>
                    </Grid>
                </Grid>

            </Grid>

            <Alert>
                {consoleText}
            </Alert>


            <Grid container direction="row" xs={10} style={{ paddingLeft: 50 }} spacing={0} >
                <Grid direction="row" xs={6} style={{ outline: "dashed 1px black", padding: 30 }}>
                    <Grid container direction="row" alignItems="center" xs={12} >
                        <Grid xs={6}>
                            <Typography><h2>Staged lines</h2></Typography>
                        </Grid>
                        <Grid xs={6} >
                            <Button variant="contained" onClick={(e) => handleRemoveClick(e)}>Remove</Button>
                        </Grid>
                    </Grid>
                    <Grid xs={12} >
                        <FormControl className={classes.formControl}>
                            <InputLabel shrink htmlFor="select-multiple-native">
                                Select lines to edit
                            </InputLabel>
                            <Select
                                multiple
                                native
                                value={highlightedLines}
                                onChange={handleSelectedListClick}
                                style={{ width: 300 }}

                            >
                                {selectedLines.map((element) => (
                                    <option key={element[0] + "-" + element[1]} value={element}>
                                        {element[0] + "-" + element[1]}
                                    </option>
                                ))}
                            </Select>
                        </FormControl>
                    </Grid>

                    <Grid container xs={12} spacing={0}
                        direction="row"
                        justifyContent="center"
                        alignItems="center">
                        <Typography>Copy From </Typography>
                        <Select
                            value={selectedCopyFromClass}
                            onChange={(e) => { setSelectedCopyFromClass(e.target.value) }}
                            style={{ width: 100 }}
                        >
                            {people.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}

                        </Select>
                        <Typography> To </Typography>
                        <Select
                            value={selectedCopyToClass}
                            onChange={(e) => { setSelectedCopyToClass(e.target.value) }}
                            style={{ width: 100 }}
                        >
                            {people.map((e) => {
                                return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                            })}

                        </Select>
                        <Button variant="outlined" onClick={handleCopyClick}>Copy</Button>
                    </Grid>
                </Grid>


                <Grid container xs={6} direction="row" rowSpacing={1} style={{ paddingLeft: 50 }} >
                    <Grid container xs={12} direction="row" style={{ outline: "dashed 1px black" }}>
                        <Grid container xs={8} direction="row" >
                            <h3 style={{ margin: 5 }}>People</h3>
                            <Select
                                value={selectedPerson}
                                onChange={handlePersonClick}
                                style={{ width: 300 }}

                            >
                                {people.map((element) => (
                                    <option key={element} value={element}>
                                        {element}
                                    </option>
                                ))}
                            </Select>
                        </Grid>
                        <Grid container xs={4} >

                            <Button variant="contained" onClick={(e) => handleAddAllLocsClick(e)}>Add all locations for {selectedPerson}</Button>
                        </Grid>
                    </Grid>

                    <Grid container xs={12} direction="row" style={{ outline: "dashed 1px black" }}>
                        <Grid container xs={8} direction="row" >
                            <h3 style={{ margin: 5 }}>Location</h3>
                            <Select
                                value={selectedLoc}
                                onChange={handleLocClick}
                                style={{ width: 300 }}

                            >
                                {locs.map((element) => (
                                    <option key={element} value={element}>
                                        {element}
                                    </option>
                                ))}
                            </Select>
                        </Grid>
                        <Grid container xs={4}>

                            <Button variant="contained" onClick={(e) => handleAddAllPeopleClick(e)}>Add all people in {selectedLoc}</Button>
                        </Grid>
                    </Grid>
                </Grid>
            </Grid>

            <h2>Location Classes</h2>
            <Table
                columns={locationcolumns}
                data={locationdata}
                updateMyData={(rowIndex, columnId, value) => {
                    // We also turn on the flag to not reset the page
                    setSkiplocationPageReset(true)
                    setlocationData(old =>
                        old.map((row, index) => {
                            if (index === rowIndex) {
                                return {
                                    ...old[rowIndex],
                                    [columnId]: value,
                                }
                            }
                            return row
                        })
                    )
                }}
                skipPageReset={skiplocationPageReset}
                addNewRow={() => {
                    setSkiplocationPageReset(true)
                    setlocationData(old => [...old, locationcolumns.reduce((dict, el, idx) => (dict[el] = "", dict), {})])
                }}
                onSave={() => {
                    saveData('location_classes.csv', locationdata)
                }}
            />

            <h2>Person Classes</h2>
            <Table
                columns={personcolumns}
                data={persondata}
                updateMyData={(rowIndex, columnId, value) => {
                    // We also turn on the flag to not reset the page
                    setSkippersonPageReset(true)
                    setpersonData(old =>
                        old.map((row, index) => {
                            if (index === rowIndex) {
                                return {
                                    ...old[rowIndex],
                                    [columnId]: value,
                                }
                            }
                            return row
                        })
                    )
                }}
                skipPageReset={skippersonPageReset}
                addNewRow={() => {
                    setSkippersonPageReset(true)
                    setpersonData(old => [...old, personcolumns.reduce((dict, el, idx) => (dict[el] = "", dict), {})])
                }}
                onSave={() => {
                    saveData('person_classes.csv', persondata)
                }}

            />

            <h2>Movement Classes</h2>
            <Table
                columns={movementcolumns}
                data={movementdata}
                updateMyData={(rowIndex, columnId, value) => {
                    // We also turn on the flag to not reset the page
                    setSkipmovementPageReset(true)
                    setmovementData(old =>
                        old.map((row, index) => {
                            if (index === rowIndex) {
                                return {
                                    ...old[rowIndex],
                                    [columnId]: value,
                                }
                            }
                            return row
                        })
                    )
                }}
                skipPageReset={skipmovementPageReset}
                addNewRow={() => {
                    setSkipmovementPageReset(true)
                    setmovementData(old => [...old, movementcolumns.reduce((dict, el, idx) => (dict[el] = "", dict), {})])
                }}
                onSave={() => {
                    saveData('movement_classes.csv', movementdata)
                }}
            />

        </div>
    );
}


const useStyles = makeStyles((theme) => ({
    formControl: {
        margin: theme.spacing(1),
        minWidth: 120,
        maxWidth: 300,
    },
    chips: {
        display: 'flex',
        flexWrap: 'wrap',
    },
    chip: {
        margin: 2,
    },
    noLabel: {
        marginTop: theme.spacing(3),
    },
}));

export default ProbDensePage;