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
import {api} from '../utils/constants';
import DirSelect from "../components/DirSelect";
function ResultsPage2() {
    const [locs, setLocs] = useState([]);
    const [people, setPeople] = useState([]);
    const [movement, setMovement] = useState([]);
    const [locClassColors, setLocClassColors] = useState({});
    const [groupOptions, setGroupOptions] = useState([]);

    const [selectedLogDir, setSelectedLogDir] = useState('');
    const [selectedDay, setSelectedDay] = useState('');

    
    const [mapData, setMapData] = useState([]);
    const [mapLayout, setMapLayout] = useState([]);
    const [mapFrames, setMapFrames] = useState([]);

    const handleSelectDir = function (_selectedLogDir) {
        setSelectedLogDir(_selectedLogDir);
    }

    const handleDayChange = function (_day) {
        setSelectedDay(_day);
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


    const getLocsArr=(arr,_LCC) => {setLocs(arr);setLocClassColors(_LCC)}
    const getPeopleArr=(arr) => {setPeople(arr)}
    const getMovementArr=(arr) => {setMovement(arr)}
    const getGroupOptionsArr=(arr) => {setGroupOptions(arr)}

    async function drawLocationDensity() {

        axios.post(api + "/flask/locationData", { dir: selectedLogDir, day: selectedDay.toString() })
            .then(function (response) {
                const data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    console.log(_df)
                    // _df = _df.withColumn('timesteps', row => row.get('timesteps').split('|').map(e => parseInt(e)));
                    let t = [...Array(1440).keys()]
                    let loc_shapes = [];
                    // loading location info
                    _df.map((row) => {
                        try {
                            var trace1 = 
                            {
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
                            loc_shapes.push(trace1);
                        } catch (err) {
                            console.log(err)
                        }
                        return row;

                    })
                    
                    let freq_shapes = []
                    //loading density info
                    axios.post(api + "/flask/LocationPeopleCountHandler", { dir: selectedLogDir, day: selectedDay.toString() })
                        .then(function (response) {
                            const data = response.data.data;
                            csv2JSONarr(data, (pr) => { }).then((json_data) => {
                                var df_freq = new DataFrame(json_data)
                                console.log(df_freq)
                                df_freq.map((row) => {
                                    // console.log(row.get('id'))
                                    var loc = _df.find({'id': row.get('id')});
                                    try {
                                        var _a = loc.length 
                                    }catch (err){
                                        return row;
                                    }
                                    var x = parseFloat(loc.get('x'));
                                    var y = parseFloat(loc.get('y'));
                                    var f = parseFloat(row.get('0'));
                                    // console.log(loc.get('id'), x, y ,f)
                                    var trace1 = 
                                        {
                                            type: 'rect',
                                            fillcolor: 'rgba(1, 0, 0, 0.5)',//locClassColors[parseInt(row.get('class'))]
                                            x0: x-1,
                                            y0: y,
                                            x1: x+1,
                                            y1: y+f*2,
                                            line: {
                                                color: 'rgba(0, 0, 0, 0)'
                                            }
                                        };
                                        freq_shapes.push(trace1);
                                })

                                setMapLayout({
                                    barmode: 'stack',
                                    title: 'People density on each location',
                                    shapes: [...loc_shapes, ...freq_shapes],
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

                                // setMapFrames(t.map(t => ({
                                //     name: t,
                                //     layout: ({'shapes': [..., ...]})
                                // })))
                            })
                        });
                    

                    setMapData([])
                    

                    




                });

            })
            .catch(function (response) {
                console.log(response);
            });
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
            />

            <div>
                <Button onClick={drawLocationDensity}>Draw location density</Button>
                <Plot
                            data={mapData}
                            layout={mapLayout}
                            frames={mapFrames}
                        />
            </div>
        </div>
    )
}


export default ResultsPage2;