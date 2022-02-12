import React, { useState, useRef, useEffect } from "react";

import { Layer, Line, Text } from "react-konva";
const MyGrid = ({ canvas_width, canvas_height, x_axis_distance_grid_lines, y_axis_distance_grid_lines, gs_y, gs_x, convertx2px, converty2py, }) => {


    const [initialLoad, setInitialLoad] = useState(true);
    const [grid, setGrid] = React.useState([]);
    const [tick, setTicks] = React.useState([]);
    const [tickText, setTickTexts] = React.useState([]);

    // const container = document.getElementById("container");

    var x_axis_starting_point = { number: 1, suffix: '' };
    var y_axis_starting_point = { number: 1, suffix: '' };


    var num_lines_x = Math.floor(canvas_height / gs_y);
    var num_lines_y = Math.floor(canvas_width / gs_x);


    useEffect(() => {
        var _grid = [];
        var _ticks = [];
        var _tickTexts = [];
        console.log('Drawing grid');
        // grid lines along Y-axis
        for (var i = 0; i <= num_lines_y; i++) {
            var lineWidth = 1;
            // If line represents Y-axis draw in different color
            if (i == Math.floor(y_axis_distance_grid_lines))
                var strokeStyle = "#000000";
            else
                var strokeStyle = "#e9e9e9";
            var xl = gs_x * i + (y_axis_distance_grid_lines - Math.floor(y_axis_distance_grid_lines)) * gs_x;
            if (i == num_lines_y) {
                var points = [xl, 0, xl, canvas_height];
            }
            else {
                var points = [xl + 0.5, 0, xl + 0.5, canvas_height];
            }
            _grid.push({
                points: points,
                stroke: strokeStyle,
                strokeWidth: lineWidth,
                lineCap: 'round',
                lineJoin: 'round',
            });
        }
        // grid lines along X-axis
        for (var i = 0; i <= num_lines_x; i++) {
            var lineWidth = 2;

            // If line represents X-axis draw in different color
            if (i == Math.floor(x_axis_distance_grid_lines))
                var strokeStyle = "#000000";
            else
                var strokeStyle = "#e9e9e9";
            var yl = gs_y * i + (x_axis_distance_grid_lines - Math.floor(x_axis_distance_grid_lines)) * gs_y;
            if (i == num_lines_x) {
                var points = [0, yl, canvas_width, yl];
            }
            else {
                var points = [0, yl + 0.5, canvas_width, yl + 0.5];
            }
            _grid.push({
                points: points,
                stroke: strokeStyle,
                strokeWidth: lineWidth,
                lineCap: 'round',
                lineJoin: 'round',
            });
        }


        var lineWidth = 1;
        var strokeStyle = "#000000";
        // Ticks marks along the positive X-axis
        for (var i = 1; i < (num_lines_y - y_axis_distance_grid_lines); i++) {

            // Draw a tick mark 6px long (-3 to 3)
            var points = [convertx2px(i) + 0.5, converty2py(0) - 3, convertx2px(i) + 0.5, converty2py(0) + 3];
    
            _ticks.push({ points: points, stroke: strokeStyle, strokeWidth: lineWidth, lineCap: 'round', lineJoin: 'round', });
            // Text value at that point
            _tickTexts.push({
                x: convertx2px(i) - 2, y: converty2py(0) + 15, text: x_axis_starting_point.number * i + x_axis_starting_point.suffix, fontSize: 9, fontFamily: 'Arial', fill: 'black',
            });
        }

        // Ticks marks along the negative X-axis
        for (var i = 1; i < y_axis_distance_grid_lines; i++) {

            // Draw a tick mark 6px long (-3 to 3)
            var points = [convertx2px(-i) + 0.5, converty2py(0) - 3, convertx2px(-i) + 0.5, converty2py(0) + 3];
            
            _ticks.push({ points: points, stroke: strokeStyle, strokeWidth: lineWidth, lineCap: 'round', lineJoin: 'round', });

            // Text value at that point
            _tickTexts.push({
                x: convertx2px(-i) + 3,
                y: converty2py(0) + 15,
                text: -x_axis_starting_point.number * i + x_axis_starting_point.suffix,
                fontSize: 9,
                fontFamily: 'Arial',
                fill: 'black',
            });
        }

        // Ticks marks along the positive Y-axis
        // Positive Y-axis of graph is negative Y-axis of the canvas
        for (var i = 1; i < (num_lines_x - x_axis_distance_grid_lines); i++) {

            // Draw a tick mark 6px long (-3 to 3)
            var points = [convertx2px(0) - 3, converty2py(i) + 0.5, convertx2px(0) + 3, converty2py(i) + 0.5];
            
            _ticks.push({ points: points, stroke: strokeStyle, strokeWidth: lineWidth, lineCap: 'round', lineJoin: 'round', });

            // Text value at that point
            _tickTexts.push({
                x: convertx2px(0) + 8,
                y: converty2py(i) + 3,
                text: -y_axis_starting_point.number * i + y_axis_starting_point.suffix,
                fontSize: 9,
                fontFamily: 'Arial',
                fill: 'black',
            });
        }

        // Ticks marks along the negative Y-axis
        // Negative Y-axis of graph is positive Y-axis of the canvas
        for (var i = 1; i < x_axis_distance_grid_lines; i++) {

            // Draw a tick mark 6px long (-3 to 3)
            var points = [convertx2px(0) + -3, converty2py(-i) + 0.5, convertx2px(0) + 3, converty2py(-i) + 0.5];
            
            _ticks.push({ points: points, stroke: strokeStyle, strokeWidth: lineWidth, lineCap: 'round', lineJoin: 'round', });


            // Text value at that point
            _tickTexts.push({
                x: convertx2px(0) + 8,
                y: converty2py(-i) + 3,
                text: y_axis_starting_point.number * i + y_axis_starting_point.suffix,
                fontSize: 9,
                fontFamily: 'Arial',
                fill: 'black',
            });
        }

        setGrid(_grid)
        setTicks(_ticks)
        setTickTexts(_tickTexts)
    }, [gs_y,gs_x])



    //   React.useEffect(() => {
    //     if (isSelected) {
    //       trRef.current.setNode(shapeRef.current);
    //       trRef.current.getLayer().batchDraw();
    //     }
    //   }, [isSelected]);

    return (
        <Layer >

            {grid.map((g, i) => {
                return (
                    <Line
                        key={i}
                        {...g}
                    />
                );
            })}
            {tick.map((g, i) => {
                return (
                    <Line
                        key={i}
                        {...g}
                    />
                );
            })}
            {tickText.map((t, i) => {
                return (
                    <Text
                        key={i}
                        {...t}
                    />
                );
            })}


        </Layer>
    );
};
export default MyGrid;