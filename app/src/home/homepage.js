import React, { useState, useEffect, useRef } from "react"
import axios from 'axios'
import { api } from '../utils/constants';
import { csvJSON, csv2JSONarr, csv2arr, strip_text } from "../utils/files";
import Table from "../components/table"

import DataFrame from 'dataframe-js';

import Box from '@material-ui/core/Box';
import TextField from '@material-ui/core/TextField';
import Grid from '@material-ui/core/Grid';
import MenuItem from '@material-ui/core/MenuItem';
import Slider from '@material-ui/core/Slider';
import FormControl from '@material-ui/core/FormControl';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import Button from '@material-ui/core/Button';
import { Checkbox, Typography } from "@material-ui/core";

import Tree from 'react-d3-tree';
function loadData(csvFileName, setDataFunc) {
  axios.post(api + "/flask/csvfile", { dir: '', type: csvFileName })
    .then(function (response) {
      let data = response.data.data;
      csv2JSONarr(data, (pr) => { }).then((json_data) => {
        var _data = []
        var _columns = Object.keys(json_data)
        for (var i = 0; i < json_data[_columns[0]].length; i++) {
          var _row = {}
          for (var col in json_data) {
            _row[col] = json_data[col][i]
          }
          _data.push(_row)
        }
        setDataFunc(_data)
      })
    })

}

function HomePage() {
  const [initialLoad] = useState(true);
  const [peopleClassColors, setPeopleClassColor] = useState({});
  const [locationClassColor, setLocationClassColor] = useState({});
  const [movementClassColor, setMovementClassColor] = useState({});

  const [containmentStrategy, setContainmentStrategy] = useState('NONE')
  const [testingStrategy, setTestingStrategy] = useState('HOSPITAL')
  const [loadLogDirs, setLoadLogDirs] = useState(['NONE'])
  const [loadLogDir, setLoadLogDir] = useState('NONE')

  const [loadLogDays, setLoadLogDays] = useState([])
  const [loadLogDay, setLoadLogDay] = useState(0)

  const containmentStrategies = ['NONE', 'LOCKDOWN', 'QUARANTINE', 'QUARANTINECENTER', 'ROSTER']
  const testingStrategies = ['NONE', 'HOSPITAL']

  const [nodeX, setNodeX] = useState(30);
  const [nodeY, setNodeY] = useState(30);
  const [locationTreeData, setLocationTreeData] = useState({ name: '0' });
  const [locationTreeDataArr, setLocationTreeDataArr] = useState([]);
  const [spawnChildren, setSpawnChildren] = useState(true)
  const [locationTypes, setLocationTypes] = useState([])
  const [selectedLocationType, setSelectedLocationType] = useState('')

  const [locationdata, setlocationData] = useState([])
  const [persondata, setpersonData] = useState([])
  const [movementdata, setmovementData] = useState([])

  const [personPercentData, setPersonPercentData] = useState([])
  const [skippersonPageReset, setSkippersonPageReset] = useState(false)

  const [addedGatheringEvents, setAddedGatheringEvents] = useState([])
  const [selectedGatheringEvents, setSelectedGatheringEvents] = useState([])

  const [addedVaccinationEvents, setAddedVaccinationEvents] = useState([])
  const [selectedVaccinationEvents, setSelectedVaccinationEvents] = useState([])

  function refreshDirs() {
    axios.get(api + '/flask/dirs').then(response => {
      setLoadLogDirs(["NONE", ...response.data.message.split(',')])
    }).catch(error => {
      console.log(error)
    })
  }

  useEffect(() => {
    // loading number of days
    if (loadLogDir == "NONE") {
      setLoadLogDays([])
      setLoadLogDay(0)
      return
    }
    axios.post(api + '/flask/n_days', { dir: loadLogDir }).then(response => {
      let _days = response.data.message.split('|')
      setLoadLogDays(_days)
    })
  }, [loadLogDir])

  useEffect(() => {
    console.log('ASDASD', persondata)
    if (persondata.length > 0)
      setPersonPercentData(persondata.map((e) => { return { 'p_class': e['p_class'], 'percentage': 0 } }))
  }, [persondata])

  useEffect(()=>{
    var tmp = []
    function dfs(r){
      tmp.push({name:r.name,class:r.class})
      if (r.children==undefined)
        return
      r.children.forEach(element => {
        dfs(element)
      });
    }
    dfs(locationTreeData)
    setLocationTreeDataArr(tmp)
  }, [locationTreeData])

  useEffect(() => {
    refreshDirs()
    getColors()
    loadData('location_classes.csv', setlocationData)
    loadData('person_classes.csv', setpersonData)
    loadData('movement_classes.csv', setmovementData)
  }, [initialLoad])

  // import colors
  async function getColors() {
    axios.post(api + "/flask/get_colors", { dir: '' })
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
          setPeopleClassColor(_people_colors)
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
          setLocationClassColor(_location_colors)
          setLocationTypes(Object.keys(_location_colors).filter((e) => isNaN(e)))
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
          setMovementClassColor(_movement_colors)
        })
      })
  }

  const add2Tree = (id2add) => {
    function newNode(_class, _id) {
      return { name: _id, class: _class }
    }

    function find(tree, id, toAddClass) {
      if (tree.name == id) {
        var newId = ''
        if (tree.children == undefined) {
          newId = tree.name + ".0"
          tree.children = []
        } else {
          newId = tree.name + "." + tree.children.length
        }
        if (tree.name == locationTreeData.name && locationTreeData.children.length != 0)
          return
        tree.children = [...tree.children, newNode(toAddClass, newId)]
        if (spawnChildren) {


          var spawnStr = locationdata.find((e) => e.l_class == toAddClass)['default_spawns']
          if (spawnStr != '') {
            spawnStr = spawnStr.split('|')
            spawnStr.forEach((e) => {
              var tmp = e.split('#')
              console.log("Add spwn ", tmp[0], tmp[1])
              for (var i = 0; i < parseInt(tmp[1]); i++) {
                find(tree, newId, tmp[0])
              }
            })
          }

        }
      }
      if (tree.children != undefined) {
        tree.children.forEach(subtree => {
          find(subtree, id, toAddClass)

        });
      }
    }

    find(locationTreeData, id2add, selectedLocationType)
  }

  const onNodeClick = (nodeDatum, toggleNode) => {
    add2Tree(nodeDatum.name)
    if (locationTreeData.name == '0')
      setLocationTreeData({ ...locationTreeData.children[0] })
    else
      setLocationTreeData({ ...locationTreeData })
  }

  // draw location tree
  const renderNode = ({ nodeDatum, toggleNode }) => (
    <g>
      <circle r="5" x="-5" onClick={() => onNodeClick(nodeDatum, toggleNode)} fill={locationClassColor[nodeDatum.class]} stroke={locationClassColor[nodeDatum.class]} />
      {/* <text fill="black" strokeWidth="1" x="20">
        ID: {nodeDatum.name}
      </text> */}
    </g>
  );

  // run simulation
  const runSim = ()=>{
    axios.post(api + "/flask/run", { dir: '' })
  }
  return (
    <div className="home-page">
      <Box component="form"
        sx={{
          '& .MuiTextField-root': { m: 1, width: '25ch' },
          border: '1px dashed grey'
        }}
        noValidate
        autoComplete="off"
        style={{ margin: 10, padding: 10 }}>
        <Typography variant="h4">Simulation parameters</Typography>
        <div>
          <TextField label="Name" id="name" sx={{ m: 1, width: '25ch' }} />
        </div>

        <div>
          <TextField label="Initial infected %" id="inf-initial" type="number" sx={{ m: 1, width: '25ch' }} />
          <TextField label="Simulation days" id="sim-days" type="number" sx={{ m: 1, width: '25ch' }} />
        </div>

        <div>
          <TextField label="Infection radius" id="inf-radius" type="number" sx={{ m: 1, width: '25ch' }} />
          <TextField label="Common fever probability" id="common-fever-p" type="number" sx={{ m: 1, width: '25ch' }} />
        </div>

        <div>
          <TextField select label="Containment strategy" id="containment-strategy" value={containmentStrategy} onChange={(e) => setContainmentStrategy(e.target.value)} variant="standard">
            {containmentStrategies.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
          </TextField>
          <TextField label="Number of roster groups" id="roster-groups" disabled={containmentStrategy != "ROSTER"} type="number" sx={{ m: 1, width: '25ch' }} />
        </div>

        <div>
          <TextField select label="Testing strategy" id="testing-strategy" value={testingStrategy} onChange={(e) => setTestingStrategy(e.target.value)} variant="standard">
            {testingStrategies.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
          </TextField>
          <TextField label="Number of test centers" id="n-test-centers" disabled={testingStrategy == "NONE"} type="number" sx={{ m: 1, width: '25ch' }} />
          <TextField label="Coverage radius of test centers" id="r-test-centers" disabled={testingStrategy == "NONE"} type="number" sx={{ m: 1, width: '25ch' }} />
        </div>

        <div>
          <TextField select label="Load from log" id="load-log-name" value={loadLogDir} onChange={(e) => setLoadLogDir(e.target.value)} variant="standard">
            {loadLogDirs.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
          </TextField>
          <TextField select label="Loading log day" id="load-log-day" disabled={loadLogDir == "NONE"} value={loadLogDay} onChange={(e) => setLoadLogDay(e.target.value)} variant="standard">
            {loadLogDays.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
          </TextField>
        </div>
      </Box>

      {(loadLogDir == "NONE") && <Box sx={{ border: '1px dashed grey' }} style={{ margin: 10, padding: 10 }}>
        <div>
          <Typography variant="h5">Environment builder</Typography>
          <div id="treeWrapper" style={{
            width: '90em', height: '40em', margin: '0 auto', padding: '15px', border: 'black 5px solid'
          }} >
            <Grid container xs={12}>
              <Grid container xs={6}>
                <Grid container xs={6}>
                  <Grid item xs={12}><Typography>Node X</Typography></Grid>
                  <Grid item xs={12}>
                    <Slider
                      style={{ width: '250px' }}
                      aria-label="Node X"
                      value={nodeX}
                      onChange={(event, newValue) => setNodeX(newValue)}
                      valueLabelDisplay="auto"
                      min={1}
                      max={110}
                    />
                  </Grid>
                </Grid>

                <Grid container xs={6}>
                  <Grid item xs={12}><Typography>Node Y</Typography></Grid>
                  <Grid item xs={12}>
                    <Slider
                      style={{ width: '250px' }}
                      aria-label="Node Y"
                      value={nodeY}
                      onChange={(event, newValue) => setNodeY(newValue)}
                      valueLabelDisplay="auto"
                      min={1}
                      max={110}
                    />
                  </Grid>
                </Grid>
              </Grid>
              <Grid container xs={2}>
                <Grid item xs={2}><Checkbox checked={spawnChildren} onClick={() => setSpawnChildren(!spawnChildren)}></Checkbox></Grid>
                <Grid item xs={10}><Typography>Spawn Children</Typography></Grid>
              </Grid>

              <Grid container xs={4}>
                <TextField select label="Select type" id="add-loc-type" value={selectedLocationType} onChange={(e) => setSelectedLocationType(e.target.value)} variant="standard">
                  {locationTypes.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
                </TextField>
              </Grid>

            </Grid>
            <Tree
              data={locationTreeData}
              renderCustomNodeElement={(nodeDatum, toggleNode) => renderNode(nodeDatum, toggleNode)}
              orientation="vertical"
              nodeSize={{ x: nodeX, y: nodeY }}
            />


          </div>

        </div>

        <div>
          <Typography variant="h5">Demography</Typography>

          <Grid item xs={12}>
            <Table
              columns={[{ Header: 'Class', accessor: 'p_class' }, { Header: 'Percentage', accessor: 'percentage' }]}
              data={personPercentData}
              updateMyData={(rowIndex, columnId, value) => {
                // We also turn on the flag to not reset the page
                setSkippersonPageReset(true)
                setPersonPercentData(old =>
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
            />
          </Grid>
        </div>
      </Box>}




      <Box sx={{ border: '1px dashed grey' }} style={{ margin: 10, padding: 10 }}>
        <Typography variant="h4" gutterBottom>Add Events</Typography>
        <div>
          <Typography variant="h6">Add Gathering event</Typography>
          <Grid container xs={12}>
            <Grid item xs={4}>
              <FormControl >
                <InputLabel shrink>Added events</InputLabel>
                <Select
                  multiple
                  native
                  value={selectedGatheringEvents}
                  style={{ width: 400 }}
                  onChange={(e) => { setSelectedGatheringEvents(e.target.options.filter((e) => e.selected).map((e) => e.value)) }}
                >
                  {addedGatheringEvents.map((e) => (<option key={e} value={e}>{e}</option>))}
                </Select>
                <Button onClick={() => { }}>Remove</Button>
              </FormControl>
            </Grid>

            <Grid container xs={8}>
              <Grid item xs={3}>
                <TextField select label="place" id="gathering-place-name">
                  {locationTreeDataArr.filter((e)=>e.class=="GatheringPlace").map((e)=>(<option key={e.name} value={e.name}>{e.name}</option>))}
                </TextField>
              </Grid>
              <Grid item xs={1}><TextField type="number" label="day" id="gathering-place-day"/></Grid>
              <Grid item xs={2}><TextField type="time" label="time" id="gathering-place-time"/></Grid>
              <Grid item xs={2}><TextField type="number" label="duration" id="gathering-place-duration"/></Grid>
              <Grid item xs={1}><TextField type="number" label="capacity" id="gathering-place-capacity"/></Grid>
              <Grid item xs={1}><TextField label="criteria" id="gathering-place-criteria"/></Grid>
              <Grid item xs={2}><Button>Add</Button></Grid>
            </Grid>
          </Grid>

        </div>

        <div>
          <Typography variant="h6">Add Vaccination event</Typography>
          <Grid container xs={12}>
            <Grid item xs={4}>
              <FormControl >
                <InputLabel shrink>Added events</InputLabel>
                <Select
                  multiple
                  native
                  value={selectedVaccinationEvents}
                  style={{ width: 400 }}
                  onChange={(e) => { setSelectedVaccinationEvents(e.target.options.filter((e) => e.selected).map((e) => e.value)) }}
                >
                  {addedVaccinationEvents.map((e) => (<option key={e} value={e}>{e}</option>))}
                </Select>
                <Button onClick={() => { }}>Remove</Button>
              </FormControl>
            </Grid>

            <Grid container xs={8}>
              <Grid item xs={1}><TextField type="number" label="day" id="vaccination-start-day"/></Grid>
              <Grid item xs={2}><TextField type="number" label="min age" id="vaccination-min-age"/></Grid>
              <Grid item xs={1}><TextField type="number" label="max age" id="vaccination-max-age"/></Grid>
              <Grid item xs={2}><Button>Add</Button></Grid>
            </Grid>
          </Grid>
        </div>

        {/* <div>
          <Typography variant="h6">Add Testing event</Typography>
          <Grid container xs={12}>
            <Grid item xs={4}>
              <FormControl >
                <InputLabel shrink>Added events</InputLabel>
                <Select
                  multiple
                  native
                  value={selectedTestingEvents}
                  style={{ width: 400 }}
                  onChange={(e) => { setSelectedTestingEvents(e.target.options.filter((e) => e.selected).map((e) => e.value)) }}
                >
                  {addedTestingEvents.map((e) => (<option key={e} value={e}>{e}</option>))}
                </Select>
                <Button onClick={() => { }}>Remove</Button>
              </FormControl>
            </Grid>

            <Grid container xs={8}>
              <Grid item xs={3}><TextField label="place" /></Grid>
              <Grid item xs={1}><TextField type="number" label="day" /></Grid>
              <Grid item xs={2}><TextField type="time" label="time" /></Grid>
              <Grid item xs={2}><TextField type="number" label="duration" /></Grid>
              <Grid item xs={1}><TextField type="number" label="capacity" /></Grid>
              <Grid item xs={2}><Button>Add</Button></Grid>
            </Grid>
          </Grid>
        </div> */}
      </Box>
      <Grid item xs={10}>
        <Button variant="contained" onClick={runSim}>Run</Button>
      </Grid>

    </div>
  );
}
export default HomePage; 