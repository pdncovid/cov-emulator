import React, { useState, useRef, useEffect } from "react";
import { makeStyles, useTheme } from '@material-ui/core/styles';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';
import Alert from "react-bootstrap/Alert";
import randomColor from "randomcolor";
import InputLabel from '@material-ui/core/InputLabel';
import Select from '@material-ui/core/Select';
import FormControl from '@material-ui/core/FormControl';
import { Stage, Layer, Line, Text } from "react-konva";
import Grid from "../components/grid";
import { ExportToCsv } from 'export-to-csv';
function ProbDensePage() {
    const classes = useStyles();
    const [initialLoad, setInitialLoad] = useState(true);
    const stageEl = React.createRef();
    const layerEl = React.createRef();
    const csvLink = React.createRef();
    const getRandomInt = max => {
        return Math.floor(Math.random() * Math.floor(max));
    };

    var canvas_width = 1500;
    var canvas_height = 600;
    var gs_y = 500;
    var gs_x = 60;
    const x_axis_distance_grid_lines = 1.1;
    const y_axis_distance_grid_lines = 0.5;

    const [selectedLines, setSelectedLines] = React.useState([]);
    const [highlightedLines, setHighlightedLines] = React.useState([]);
    const [selectedPerson, setSelectedPerson] = React.useState(0);
    const [selectedLoc, setSelectedLoc] = React.useState(0);
    const [allData, setAllData] = React.useState({});

    const [isDown, setIsDown] = React.useState(false);
    const [consoleText, setConsoleText] = React.useState("HSW");
    const [lines, setLines] = React.useState([]);

    const [prevX, setprevX] = React.useState(0);
    const [prevY, setprevY] = React.useState(0);
    const [posx, setposx] = React.useState(0);
    const [posy, setposy] = React.useState(0);

    const people = ['CommercialWorker', 'Student'];
    const locs = ['Home', 'CommercialZone'];
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

    function init_line(p, l, data) {
        var _line = Array(24 * 60 * 2).fill(0);
        for (var i = 0; i < 24 * 60; i++) {
            _line[i * 2] = convertx2px(i / 60);
            _line[i*2+1] = converty2py(data[i])
        }
        let to_add = {
            points: _line,
            stroke: randomColor(),
            strokeWidth: 5,
            lineCap: 'round',
            lineJoin: 'round',
            key: [p, l],
            value: data,
        };
        for (let i=0;i<lines.length;i++){
            if (lines.key == [p,l]){
                lines[i] = to_add;
                return;      
            }
        }
        lines.push(to_add);
    }
    useEffect(() => {

        console.log("Initializing Prob page")

        console.log(stageEl.current.getContainer().getBoundingClientRect())
        
        for (let i=0;i<people.length;i++){
            for (let j=0;j<locs.length;j++){
                allData[[i,j]] = Array(24 * 60).fill(0);
            }
        }

        // window.onscroll = () => {
        //     posx = Math.round(stageEl.current.getContainer().getBoundingClientRect().left * 1000) / 1000;
        //     posy = Math.round(stageEl.current.getContainer().getBoundingClientRect().top * 1000) / 1000;
        // }
    }, [initialLoad])



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
                allData[element.key] = element.value;
            });
        }
        if (res == 'move') {
            setposx(Math.round(stageEl.current.getContainer().getBoundingClientRect().left * 1000) / 1000);
            setposy(Math.round(stageEl.current.getContainer().getBoundingClientRect().top * 1000) / 1000);
            var _consoleText = "pX=" + e.evt.clientX + " pY=" + e.evt.clientY + " X=" + convertpx2x(e.evt.clientX) + " Y=" + convertpy2y(e.evt.clientY) + "\n";
            _consoleText += "posX=" + posx + " posY=" + posy
            _consoleText += "pX'=" + convertx2px(convertpx2x(e.evt.clientX)) + " pY'=" + converty2py(convertpy2y(e.evt.clientY))
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
                    _val = lines[p_idx].value
                    break
                }
            }

            console.log(x,y, x1,x2, lines[p_idx])
            for (var i = x1; i <= x2; i++) {
                var _y = prevY + (y - prevY) * (i - x1) / (x2 - x1);
                _y = Math.min(_y, 1);
                _line[2 * i + 1] = converty2py(_y);
                _val[i] = _y;
                if (isNaN(_line[2 * i + 1])) {
                    _line[2 * i + 1] = 0;
                }

            }
            for (var i = x2; i <= x1; i++) {
                var _y = y - (y - prevY) * (i - x2) / (x1 - x2);
                _y = Math.min(_y, 1);
                _line[2 * i + 1] = converty2py(_y);
                _val[i] = _y;
                if (isNaN(_line[2 * i + 1])) {
                    _line[2 * i + 1] = 0;
                }

            }
            lines[p_idx].value = _val;
            stageEl.current.children[1].children[p_idx].setPoints(_line);
        }
        // setLines(arrlines);
    }

    const handlePersonClick = function (id, e) {
        // console.log(id)
        setSelectedPerson(id);
    }

    const handleLocClick = function (id, e) {

        setSelectedLoc(id);
        for (var i = 0; i < selectedLines.length; i++) {
            if (selectedLines[i][0] == selectedPerson && selectedLines[i][1] == id) {
                console.log("Exists")
                return
            }
        }
        selectedLines.push([selectedPerson, id]);
        init_line(selectedPerson, id, allData[[selectedPerson, id]]);
        // console.log(id, selectedLoc)
        console.log(selectedLines)
    }

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
        
        
        for (let i = 0; i<highlightedLines.length; i += 1) {
            for (let j =0;j<selectedLines.length;j++){
                if (selectedLines[j] == highlightedLines[i]){
                    selectedLines.splice(j, 1);
                }
            }
            for (let j =0;j<lines.length;j++){
                if (lines[j].key == highlightedLines[i]){
                    lines.splice(j, 1);
                }
            }
            
        }
        console.log(selectedLines)
    };

    const handleSaveClick = (event) => {
        const options = { 
            filename:'probLocPersonTime',
            fieldSeparator: ',',
            quoteStrings: '"',
            decimalSeparator: '.',
            showLabels: true, 
            showTitle: false,
            useTextFile: false,
            useBom: true,
            useKeysAsHeaders: true,
            // headers: ['Column 1', 'Column 2', etc...] <-- Won't work with useKeysAsHeaders present!
          };

       
        var data_to_download = []
        for (var index = 0; index < lines.length; index++) {
            let record_to_download = {'person':people[lines[index].value[0]], 'location':locs[lines[index].value[1]]}
            for (var colIndex = 0; colIndex < lines[index].points.length/2; colIndex++) {
                record_to_download[colIndex] = lines[index].value[colIndex]
            }
            data_to_download.push(record_to_download)
        }
        console.log(data_to_download,csvLink)
        
        const csvExporter = new ExportToCsv(options);
        csvExporter.generateCsv(data_to_download);
        
    }
    const handleLoadClick = (event) => {

    }

    return (
        <div className="prob-page">
            <h1>Set up probability density of staying in each location</h1>


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
                <Grid canvas_width={canvas_width} canvas_height={canvas_height}
                    x_axis_distance_grid_lines={x_axis_distance_grid_lines} y_axis_distance_grid_lines={y_axis_distance_grid_lines}
                    gs_y={gs_y} gs_x={gs_x}
                    convertx2px={convertx2px} converty2py={converty2py} />
                <Layer ref={layerEl}>
                    {lines.map((line, i) => {
                        return (
                            <Line
                                key={i}
                                {...line}
                            />
                        );
                    })}
                </Layer>
            </Stage>

            <Alert>
                {consoleText}
            </Alert>

            <h2>People</h2>
            <ButtonGroup variant="text" color="primary" aria-label="text primary button group">
                {people.map((bt, i) => {
                    return (<Button variant="contained" key={i} onClick={(e) => handlePersonClick(i, e)}>{bt}</Button>)
                })}
            </ButtonGroup>



            <h2>Location</h2>
            <ButtonGroup variant="text" color="primary" aria-label="text primary button group">
                {locs.map((bt, i) => {
                    return (<Button variant="contained" key={i} onClick={(e) => handleLocClick(i, e)}>{bt}</Button>)
                })}
            </ButtonGroup>


            <h2>Selected lines</h2>
            <FormControl className={classes.formControl}>
                <InputLabel shrink htmlFor="select-multiple-native">
                    Selected lines
                </InputLabel>
                <Select
                    multiple
                    native
                    value={highlightedLines}
                    onChange={handleSelectedListClick}

                    inputProps={{
                        id: 'select-multiple-native',
                    }}
                >
                    {selectedLines.map((element) => (
                        <option key={people[element[0]] + "-" + locs[element[1]]} value={element}>
                            {people[element[0]] + "-" + locs[element[1]]}
                        </option>
                    ))}
                </Select>
            </FormControl>
            <Button variant="contained" onClick={(e) => handleRemoveClick(e)}>Remove</Button>
            <Button variant="contained" onClick={(e) => handleSaveClick(e)}>Save</Button>
            <Button variant="contained" onClick={(e) => handleLoadClick(e)}>Load</Button>

            
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