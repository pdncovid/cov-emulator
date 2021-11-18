import React, { useState, useRef, useEffect } from "react";
import axios from 'axios'
import { api } from '../utils/constants';
import { strip_text } from "../utils/files";

import FormHelperText from '@material-ui/core/FormHelperText';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';

import InputLabel from '@material-ui/core/InputLabel';
import MenuItem from '@material-ui/core/MenuItem';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';

import Button from '@material-ui/core/Button';

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

    const handleAnalyzePeopleClick = (e) =>{
        let _selectedPeople = [];
        people.forEach(element => {
            if (peopleCheckedState[element]) {
                _selectedPeople.push(element)
            }
        });
        setSelectedPeople(_selectedPeople)
        onAnalyzePeople(_selectedPeople);
    }

    const handleDayChange =(event) =>{
        setSelectedDay(event.target.value);
        onDayChange(event.target.value);
    }

    function onDirChange(event) {
        let _selectedLogDir = event.target.value;
        setSelectedLogDir(_selectedLogDir);

        // loading number of days
        axios.post(api + '/flask/n_days', { dir: _selectedLogDir }).then(response => {
            let _days = response.data.message.split(',')
            setDays(_days)
        }).catch(error => {
            console.log(error)
        })

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

                getLocsArr(locs_str, _LCC);
                console.log(locs_str, _LCC);
            })
            .catch(function (response) {
                console.log(response);
            });

        // Loading People
        axios.post(api + "/flask/textfile", { dir: _selectedLogDir, filename: 'people.txt' })
            .then(function (response) {
                const data = response.data.data;
                var people_str = data.split("\n").map((e) => strip_text(e));
                people_str.forEach(element => {
                    peopleCheckedState[element] = true;
                });
                setPeople(people_str);
                setSelectedPeople(people_str);

                getPeopleArr(people_str);
                console.log(people_str);
            })
            .catch(function (response) {
                console.log(response);
            });

        // Loading Movement
        axios.post(api + "/flask/textfile", { dir: _selectedLogDir, filename: 'movement.txt' })
            .then(function (response) {
                //handle success
                const data = response.data.data;
                var movement_str = data.split("\n");

                getMovementArr(movement_str);
                console.log(movement_str);
            })
            .catch(function (response) {
                //handle error
                console.log(response);
            });

        // loading grouping options
        axios.post(api + '/flask/possible_groups', { dir: _selectedLogDir }).then(response => {
             getGroupOptionsArr(response.data.data)
        }).catch(err => { console.log(err) })

        onSelect(_selectedLogDir);
    }

    return (
        <React.Fragment>
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
        </React.Fragment>
    );
};
export default DirSelect;