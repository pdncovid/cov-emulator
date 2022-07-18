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
import { Checkbox, FormControlLabel, Typography } from "@material-ui/core";

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
  const [loadLogDay, setLoadLogDay] = useState('0')

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

  const [addedVariantEvents, setAddedVariantEvents] = useState([
    { id: 0, name: "Base", day: "0", transmittable: "0.5", severity: "0.5" },
    { id: 1, name: "Delta", day: "1", transmittable: "0.4", severity: "0.9" },
  ])
  const [selectedVariantEvents, setSelectedVariantEvents] = useState([])

  const [addedContainmentEvents, setAddedContainmentEvents] = useState([])
  const [selectedContainmentEvents, setSelectedContainmentEvents] = useState([])

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

    loadSim()
  }, [loadLogDir])

  useEffect(() => {
    if (persondata.length > 0)
      setPersonPercentData([...persondata.map((e) => { return { 'p_class': e['p_class'], 'percentage': e['default_percentage'], 'ipercentage': 0 } })])
  }, [persondata])

  useEffect(() => {
    var tmp = []
    function dfs(r) {
      tmp.push({ name: r.name, class: r.class })
      if (r.children == undefined)
        return
      r.children.forEach(element => {
        dfs(element)
      });
    }
    dfs(locationTreeData)
    console.log(locationTreeData, JSON.stringify(locationTreeData))
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

  // load parameters from log
  const loadSim = () => {
    axios.post(api + "/flask/load_args", { dir: loadLogDir }).then(response => {
      var args = response.data
      console.log(args)
      document.getElementById("name").value = args.name
      // document.getElementById("inf_initial").value = args.inf_initial
      document.getElementById("sim_days").value = args.sim_days
      document.getElementById("inf_radius").value = args.inf_radius
      document.getElementById("common_fever_p").value = args.common_fever_p
      // setContainmentStrategy(args.containment_strategy)
      // document.getElementById("roster_groups").value = args.roster_groups
      setTestingStrategy(args.testing_strategy)
      document.getElementById("n_test_centers").value = args.n_test_centers
      document.getElementById("r_test_centers").value = args.r_test_centers

      setPersonPercentData(Object.values(JSON.parse(args.personPercentData)))

      setAddedVariantEvents(Object.values(JSON.parse(args.addedVariantEvents)))
      setAddedContainmentEvents(Object.values(JSON.parse(args.addedContainmentEvents)))
      setAddedGatheringEvents(Object.values(JSON.parse(args.addedGatheringEvents)))
      setAddedVaccinationEvents(Object.values(JSON.parse(args.addedVaccinationEvents)))


      document.getElementById("social_distance").value = args.social_distance
      document.getElementById("hygiene_p").value = args.hygiene_p

      document.getElementById("base_transmission_p").value = args.base_transmission_p
      document.getElementById("incubation_days").value = args.incubation_days
    })

    axios.post(api + '/flask/textfile', { dir: loadLogDir, filename: 'tree.data' }).then(response => {
      setLocationTreeData(JSON.parse(response.data.data))
    })
  }

  // run simulation
  const runSim = () => {
    axios.post(api + "/flask/run", {
      name: document.getElementById("name").value,
      // inf_initial: document.getElementById("inf_initial").value,
      sim_days: document.getElementById("sim_days").value,
      inf_radius: document.getElementById("inf_radius").value,
      common_fever_p: document.getElementById("common_fever_p").value,
      // containment_strategy: containmentStrategy,
      // roster_groups: document.getElementById("roster_groups").value,
      testing_strategy: testingStrategy,
      n_test_centers: document.getElementById("n_test_centers").value,
      r_test_centers: document.getElementById("r_test_centers").value,
      load_log_day: loadLogDay,
      load_log_name: document.getElementById("load_log_name").textContent,
      locationTreeData: locationTreeData,
      personPercentData: personPercentData.reduce((dict, el, index) => (dict[index] = el, dict), {}),
      addedContainmentEvents: addedContainmentEvents.reduce((dict, el, index) => (dict[index] = el, dict), {}),
      addedGatheringEvents: addedGatheringEvents.reduce((dict, el, index) => (dict[index] = el, dict), {}),
      addedVaccinationEvents: addedVaccinationEvents.reduce((dict, el, index) => (dict[index] = el, dict), {}),
      addedVariantEvents: addedVariantEvents.reduce((dict, el, index) => (dict[index] = el, dict), {}),
      social_distance: document.getElementById("social_distance").value,
      hygiene_p: document.getElementById("hygiene_p").value,
      incubation_days: document.getElementById("incubation_days").value,
      base_transmission_p: document.getElementById("base_transmission_p").value,
      log_fine_details: document.getElementById("log_fine_details").checked ? 1 : 0,
      analyze_infect_contacts_only: document.getElementById("analyze_infect_contacts_only").checked ? 1 : 0,
    })
  }
  return (
    <div className="home-page">

      <Box component="form"
        sx={{
          '& .MuiTextField-root': { m: 1, width: '25ch' },
          border: '1px dashed grey'
        }}>

        <div>
          <Typography variant="h5">Load from previous simulation</Typography>
          <TextField select label="Load from" id="load_log_name" value={loadLogDir} onChange={(e) => setLoadLogDir(e.target.value)} variant="standard">
            {loadLogDirs.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
          </TextField>
          <TextField select label="Loading day" id="load_log_day" disabled={loadLogDir == "NONE"} value={loadLogDay} onChange={(e) => setLoadLogDay(e.target.value)} variant="standard">
            {loadLogDays.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
          </TextField>
        </div>

      </Box>

      <Box component="form"
        sx={{
          '& .MuiTextField-root': { m: 1, width: '25ch' },
          border: '1px dashed grey'
        }}
        noValidate
        autoComplete="off"
        style={{ margin: 10, padding: 10 }}>
        <div>
          <Typography>Simulation parameters</Typography>
          <TextField label="Name" id="name" sx={{ m: 1, width: '25ch' }} defaultValue={"Test"} />
          <TextField label="Simulation days" id="sim_days" type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"60"} />
        </div>

        <div>
          <Typography>Disease variant parameters</Typography>
          <TextField label="Infection radius" id="inf_radius" type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"1"} />
          <TextField label="Incubation days" id="incubation_days" type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"4.5"} />
          <TextField label="Base transmission probability" id="base_transmission_p" type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"0.1"} />
        </div>

        <div>
          <TextField label="Common fever probability" id="common_fever_p" type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"0.01"} />
        </div>

        {/* <div>
          <Typography>Containment parameters</Typography>
          <TextField select label="Containment strategy" id="containment_strategy" value={containmentStrategy} onChange={(e) => setContainmentStrategy(e.target.value)} variant="standard">
            {containmentStrategies.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
          </TextField>
          <TextField label="Number of roster groups" id="roster_groups" disabled={containmentStrategy != "ROSTER"} type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"1"} />
        </div> */}

        <div>
          <Typography>Testing parameters</Typography>
          <TextField select label="Testing strategy" id="testing_strategy" value={testingStrategy} onChange={(e) => setTestingStrategy(e.target.value)} variant="standard">
            {testingStrategies.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
          </TextField>
          <TextField label="Number of test centers (not used)" id="n_test_centers" disabled={testingStrategy == "NONE"} type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"3"} />
          <TextField label="Coverage radius of test centers" id="r_test_centers" disabled={testingStrategy == "NONE"} type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"100"} />
        </div>

        <div>
          <Typography>Social distancing parameters</Typography>
          {/* <Checkbox></Checkbox> */}
          <TextField label="Social Distance (Override)" id="social_distance" type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"-1"} />
          {/* <Checkbox></Checkbox> */}
          <TextField label="Unhygenic probability (Override)" id="hygiene_p" type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"-1"} />
        </div>



      </Box>





      <Box sx={{ border: '1px dashed grey' }} style={{ margin: 10, padding: 10 }}>
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
              columns={[{ Header: 'Class', accessor: 'p_class' }, { Header: 'Percentage', accessor: 'percentage' }, , { Header: 'Infected Percentage', accessor: 'ipercentage' }]}
              data={personPercentData}
              updateMyData={(rowIndex, columnId, value) => {
                // We also turn on the flag to not reset the page
                setSkippersonPageReset(true)
                setPersonPercentData(old =>
                  old.map((row, index) => {
                    if (index === rowIndex) {
                      return { ...old[rowIndex], [columnId]: value, }
                    }
                    return row
                  })
                )
              }}
              skipPageReset={skippersonPageReset}
            />
          </Grid>
        </div>
      </Box>



      <Box sx={{ border: '1px dashed grey' }} style={{ margin: 10, padding: 10 }}>
        <Typography variant="h4" gutterBottom>Add Events</Typography>

        <div>
          <Typography variant="h6">Add Variant Start Event</Typography>
          <Grid container xs={12}>
            <Grid item xs={4}>
              <FormControl >
                <InputLabel shrink>Added events</InputLabel>
                <Select
                  multiple
                  native
                  style={{ width: 400 }}
                  onChange={
                    (e) => {
                      const { options } = e.target;
                      const value = [];
                      for (let i = 0, l = options.length; i < l; i += 1) {
                        if (options[i].selected) {
                          value.push(options[i].id);
                        }
                      }
                      console.log(value)
                      setSelectedVariantEvents(value)
                    }}
                >
                  {addedVariantEvents.map((e) => (<option key={e.id} id={e.id}>{e.name + " " + e.day + " " + e.transmittable + " " + e.severity}</option>))}
                </Select>
                <Button variant="contained" onClick={() => {
                  var vals = []
                  for (let e in addedVariantEvents) {
                    var isRemove = false
                    for (let s in selectedVariantEvents) {
                      if (addedVariantEvents[e].id == selectedVariantEvents[s]) {
                        isRemove = true
                        break
                      }
                    }
                    if (!isRemove)
                      vals.push(addedVariantEvents[e])
                  }
                  console.log(addedVariantEvents, selectedVariantEvents, vals)
                  setSelectedVariantEvents([])
                  setAddedVariantEvents(vals)
                }}>Remove</Button>
              </FormControl>
            </Grid>

            <Grid container xs={8}>
              <Grid item xs={1}><TextField label="name" id="variant-name" /></Grid>
              <Grid item xs={1}><TextField type="number" label="day" id="variant-start-day" /></Grid>
              <Grid item xs={2}><TextField type="number" label="transmittable" id="variant-transmittable" /></Grid>
              <Grid item xs={1}><TextField type="number" label="severity" id="variant-severity" /></Grid>
              <Grid item xs={2}><Button variant="contained" onClick={() => {
                setAddedVariantEvents([...addedVariantEvents, {
                  id: addedVariantEvents.length,
                  name: document.getElementById("variant-name").value,
                  day: document.getElementById("variant-start-day").value,
                  transmittable: document.getElementById("variant-transmittable").value,
                  severity: document.getElementById("variant-severity").value,
                }])
              }}>Add</Button></Grid>
            </Grid>
          </Grid>
        </div>


        <div>
          <Typography variant="h6">Add Containement event</Typography>
          <Grid container xs={12}>
            <Grid item xs={4}>
              <FormControl >
                <InputLabel shrink>Added events</InputLabel>
                <Select
                  multiple
                  native
                  style={{ width: 400 }}
                  onChange={(e) => {
                    const { options } = e.target;
                    const value = [];
                    for (let i = 0, l = options.length; i < l; i += 1) {
                      if (options[i].selected) {
                        value.push(options[i].id);
                      }
                    }
                    console.log(value)
                    setSelectedContainmentEvents(value)
                  }}
                >
                  {addedContainmentEvents.map((e) => (<option key={e.id} id={e.id}>{e.startday + ' ' + e.containment_strategy + ' ' + e.roster_groups}</option>))}
                </Select>
                <Button variant="contained" onClick={() => {
                  var vals = []
                  for (let e in addedContainmentEvents) {
                    var isRemove = false
                    for (let s in selectedContainmentEvents) {
                      if (addedContainmentEvents[e].id == selectedContainmentEvents[s]) {
                        isRemove = true
                        break
                      }
                    }
                    if (!isRemove)
                      vals.push(addedContainmentEvents[e])
                  }
                  setSelectedContainmentEvents([])
                  setAddedContainmentEvents(vals)
                }}>Remove</Button>
              </FormControl>
            </Grid>

            <Grid container xs={8}>
              <Grid item xs={2}><TextField type="number" label="start day" id="containment-start-day" /></Grid>
              <Grid item xs={3}><TextField select label="Containment strategy" id="containment_strategy" value={containmentStrategy} onChange={(e) => setContainmentStrategy(e.target.value)} variant="standard">
                {containmentStrategies.map((e) => (<MenuItem key={e} value={e}>{e}</MenuItem>))}
              </TextField></Grid>
              <Grid item xs={2}><TextField label="Number of roster groups" id="roster_groups" disabled={containmentStrategy != "ROSTER"} type="number" sx={{ m: 1, width: '25ch' }} defaultValue={"1"} /></Grid>
              <Grid item xs={2}><Button variant="contained" onClick={() => {
                setAddedContainmentEvents([...addedContainmentEvents, {
                  id: addedContainmentEvents.length,
                  startday: document.getElementById("containment-start-day").value,
                  containment_strategy: document.getElementById("containment_strategy").textContent,
                  roster_groups: document.getElementById("roster_groups").value,
                }])
              }}>Add</Button></Grid>
            </Grid>
          </Grid>

        </div>

        <div>
          <Typography variant="h6">Add Gathering event</Typography>
          <Grid container xs={12}>
            <Grid item xs={4}>
              <FormControl >
                <InputLabel shrink>Added events</InputLabel>
                <Select
                  multiple
                  native
                  style={{ width: 400 }}
                  onChange={(e) => {
                    const { options } = e.target;
                    const value = [];
                    for (let i = 0, l = options.length; i < l; i += 1) {
                      if (options[i].selected) {
                        value.push(options[i].id);
                      }
                    }
                    console.log(value)
                    setSelectedGatheringEvents(value)
                  }}
                >
                  {addedGatheringEvents.map((e) => (<option key={e.id} id={e.id}>{e.id + ' ' + e.day + ' ' + e.time + ' ' + e.name}</option>))}
                </Select>
                <Button variant="contained" onClick={() => {
                  var vals = []
                  for (let e in addedGatheringEvents) {
                    var isRemove = false
                    for (let s in selectedGatheringEvents) {
                      if (addedGatheringEvents[e].id == selectedGatheringEvents[s]) {
                        isRemove = true
                        break
                      }
                    }
                    if (!isRemove)
                      vals.push(addedGatheringEvents[e])
                  }
                  setSelectedGatheringEvents([])
                  setAddedGatheringEvents(vals)
                }}>Remove</Button>
              </FormControl>
            </Grid>

            <Grid container xs={8}>
              <Grid item xs={3}>
                <TextField select label="place" id="gathering-place-name">
                  {locationTreeDataArr.filter((e) => e.class == "GatheringPlace").map((e) => (<option key={e.name} value={e.name}>{e.name}</option>))}
                </TextField>
              </Grid>
              <Grid item xs={2}><TextField type="number" label="day" id="gathering-place-day" /></Grid>
              <Grid item xs={2}><TextField type="time" label="time" id="gathering-place-time" /></Grid>
              <Grid item xs={2}><TextField type="number" label="duration (hrs)" id="gathering-place-duration" /></Grid>
              <Grid item xs={1}><TextField type="number" label="capacity" id="gathering-place-capacity" /></Grid>
              <Grid item xs={2}><TextField label="criteria" id="gathering-place-criteria" /></Grid>
              <Grid item xs={2}><Button variant="contained" onClick={() => {
                var tmp = [...addedGatheringEvents]
                locationTreeDataArr.filter((e) => e.class == "GatheringPlace").forEach(e => {
                  tmp.push({
                    id: tmp.length,
                    name: e.name,
                    day: document.getElementById("gathering-place-day").value,
                    time: document.getElementById("gathering-place-time").value,
                    duration: document.getElementById("gathering-place-duration").value,
                    capacity: document.getElementById("gathering-place-capacity").value,
                    criteria: document.getElementById("gathering-place-criteria").value,
                  })
                })
                setAddedGatheringEvents(tmp)
              }}>Add All</Button></Grid>
              <Grid item xs={2}><Button variant="contained" onClick={() => {
                setAddedGatheringEvents([...addedGatheringEvents, {
                  id: addedGatheringEvents.length,
                  name: document.getElementById("gathering-place-name").textContent,
                  day: document.getElementById("gathering-place-day").value,
                  time: document.getElementById("gathering-place-time").value,
                  duration: document.getElementById("gathering-place-duration").value,
                  capacity: document.getElementById("gathering-place-capacity").value,
                  criteria: document.getElementById("gathering-place-criteria").value,
                }])
              }}>Add</Button></Grid>


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
                  style={{ width: 400 }}
                  onChange={
                    (e) => {
                      const { options } = e.target;
                      const value = [];
                      for (let i = 0, l = options.length; i < l; i += 1) {
                        if (options[i].selected) {
                          value.push(options[i].id);
                        }
                      }
                      console.log(value)
                      setSelectedVaccinationEvents(value)
                    }}
                >
                  {addedVaccinationEvents.map((e) => (<option key={e.id} id={e.id}>{e.day + ' ' + e.min_age + ' ' + e.max_age}</option>))}
                </Select>
                <Button variant="contained" onClick={() => {
                  var vals = []
                  for (let e in addedVaccinationEvents) {
                    var isRemove = false
                    for (let s in selectedVaccinationEvents) {
                      if (addedVaccinationEvents[e].id == selectedVaccinationEvents[s]) {
                        isRemove = true
                        break
                      }
                    }
                    if (!isRemove)
                      vals.push(addedVaccinationEvents[e])
                  }
                  console.log(addedVaccinationEvents, selectedVaccinationEvents, vals)
                  setSelectedVaccinationEvents([])
                  setAddedVaccinationEvents(vals)
                }}>Remove</Button>
              </FormControl>
            </Grid>

            <Grid container xs={8}>
              <Grid item xs={1}><TextField type="number" label="day" id="vaccination-start-day" /></Grid>
              <Grid item xs={2}><TextField type="number" label="min age" id="vaccination-min-age" /></Grid>
              <Grid item xs={1}><TextField type="number" label="max age" id="vaccination-max-age" /></Grid>
              <Grid item xs={2}><Button variant="contained" onClick={() => {
                setAddedVaccinationEvents([...addedVaccinationEvents, {
                  id: addedVaccinationEvents.length,
                  day: document.getElementById("vaccination-start-day").value,
                  min_age: document.getElementById("vaccination-min-age").value,
                  max_age: document.getElementById("vaccination-max-age").value,
                }])
              }}>Add</Button></Grid>
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


      <Grid container xs={12}>
        <Grid item xs={3}>
          <FormControlLabel
            label={"Log fine details"}
            control={<Checkbox id="log_fine_details"
            />}
          />
          <FormControlLabel
            label={"Analyze infected contacts only"}
            control={<Checkbox id="analyze_infect_contacts_only"
            />}
          />
        </Grid>
        <Grid item xs={3}>
          <Button variant="contained" onClick={runSim}>Run</Button>
        </Grid>
      </Grid>

    </div>
  );
}
export default HomePage; 