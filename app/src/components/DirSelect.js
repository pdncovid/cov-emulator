import React, { useState, useRef, useEffect } from "react";
import axios from 'axios'
import { api } from '../utils/constants';
import { csvJSON, csv2JSONarr, strip_text } from "../utils/files";

import Grid from '@material-ui/core/Grid';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';

import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';

import Button from '@material-ui/core/Button';

import DataFrame from 'dataframe-js';
import randomColor from "randomcolor";
const DirSelect = ({ onSelect, onAnalyzePeople, onDayChange, getLocsArr, getPeopleArr, getMovementArr, getGroupOptionsArr }) => {

    const [dirs, setDirs] = useState([]);
    const [selectedLogDir, setSelectedLogDir] = useState('');

    const [days, setDays] = useState([]);
    const [selectedDay, setSelectedDay] = useState('');

    const [people, setPeople] = useState([]);

    const [selectedPeople, setSelectedPeople] = useState([]);
    const [peopleCheckedState, setPeopleCheckedState] = React.useState({});

    function refreshDirs() {
        axios.get(api + '/flask/dirs').then(response => {
            setDirs(response.data.message.split(','))
        }).catch(error => {
            console.log(error)
        })
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
        onAnalyzePeople(_selectedPeople);
    }

    const handleDayChange = (event) => {
        setSelectedDay(event.target.value);
        onDayChange(event.target.value);
    }

    function onDirChange(event) {
        let _selectedLogDir = event.target.value;
        setSelectedLogDir(_selectedLogDir);

        // loading number of days
        axios.post(api + '/flask/n_days', { dir: _selectedLogDir }).then(response => {
            let _days = response.data.message.split('|')
            console.log("Days " + _days)
            setDays(_days)
        })

        // Loading Locations
        axios.post(api + "/flask/csvfile", { dir: _selectedLogDir, type: 'location_classes.csv' })
            .then(function (response) {
                let data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    console.log(_df);
                    getLocsArr(_df.select('l_class').toArray().map(e => e[0]));
                })
            })

        // Loading People
        axios.post(api + "/flask/csvfile", { dir: _selectedLogDir, type: 'person_classes.csv' })
            .then(function (response) {
                let data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    console.log(_df);
                    var peopleArr = _df.select('p_class').toArray().map(e => e[0])
                    peopleArr.forEach(element => {
                        peopleCheckedState[element] = true;
                    });
                    setPeople(peopleArr);
                    setSelectedPeople(peopleArr);
                    getPeopleArr(peopleArr);
                })

            })

        // Loading Movement
        axios.post(api + "/flask/csvfile", { dir: _selectedLogDir, type: 'movement_classes.csv' })
            .then(function (response) {
                let data = response.data.data;
                csv2JSONarr(data, (pr) => { }).then((json_data) => {
                    var _df = new DataFrame(json_data)
                    console.log(_df);
                    getMovementArr(_df.select('m_class').toArray().map(e => e[0]));
                })
            })

        // loading grouping options
        axios.post(api + '/flask/possible_groups', { dir: _selectedLogDir }).then(response => {
            getGroupOptionsArr(response.data.data)
        })

        onSelect(_selectedLogDir);
    }

    return (
        <React.Fragment>
            <Grid container spacing={0} padding='30px'>
                <FormControl variant="outlined" style={{ padding: 20, width: 200 }}>
                    <InputLabel id="select-day">Selected Log</InputLabel>
                    <Select
                        labelId="select-log-label"
                        id="select-log"
                        value={selectedLogDir}
                        onChange={onDirChange}
                        label="Selected Log"
                    >
                        {dirs.map((e) => {
                            return (<MenuItem value={e} key={e}>{e}</MenuItem>);
                        })}

                    </Select>
                    <Button onClick={refreshDirs}>Refresh</Button>
                </FormControl>

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

                <FormGroup row style={{ maxWidth: 1000, padding: 30 }}>
                    {people.map((p) => {
                        return (
                            <FormControlLabel
                                control={<Checkbox checked={peopleCheckedState[p]} onChange={handlePeopleCheckChange} name={p} key={p} />}
                                label={p}
                            />
                        )
                    })}

                    <Button onClick={handleAnalyzePeopleClick}>Analyze only selected people</Button>
                </FormGroup>
            </Grid>






            <br />
            <hr class="rounded" />
        </React.Fragment>
    );
};
export default DirSelect;