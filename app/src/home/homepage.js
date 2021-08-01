import React, { useState, useRef } from "react";
import ButtonGroup from "react-bootstrap/ButtonGroup";
import Button from "react-bootstrap/Button";
// import "./HomePage.css";
import { Stage, Layer } from "react-konva";
// import Rectangle from "./Rectangle";
import Circle from "../components/circle";
// import { addLine } from "./line";
// import { addTextNode } from "./textNode";
// import Image from "./Image";
// const uuidv1 = require("uuid/v1");

function HomePage() {
  const [rectangles, setRectangles] = useState([]);
  const [circles, setCircles] = useState([]);
  const [images, setImages] = useState([]);
  const [selectedId, selectShape] = useState(null);
  const [shapes, setShapes] = useState([]);
  const [, updateState] = React.useState();
  const stageEl = React.createRef();
  const layerEl = React.createRef();
  const fileUploadEl = React.createRef();
  const getRandomInt = max => {
    return Math.floor(Math.random() * Math.floor(max));
  };

  return (
    <div className="home-page">
      <h1>Home Page</h1>
      <ButtonGroup>
        <Button variant="secondary">
          Rectangle
        </Button>
        <Button variant="secondary" >
          Circle
        </Button>
        <Button variant="secondary">
          Line
        </Button>
        <Button variant="secondary">
          Erase
        </Button>
        <Button variant="secondary" >
          Text
        </Button>
        <Button variant="secondary" >
          Image
        </Button>
        <Button variant="secondary" >
          Undo
        </Button>
      </ButtonGroup>
      
      <Stage
        width={window.innerWidth * 0.9}
        height={window.innerHeight - 150}
        ref={stageEl}
        onMouseDown={e => {
          // deselect when clicked on empty area
          const clickedOnEmpty = e.target === e.target.getStage();
          if (clickedOnEmpty) {
            selectShape(null);
          }
        }}
      >
        <Layer ref={layerEl}>
          
          {circles.map((circle, i) => {
            return (
              <Circle
                key={i}
                shapeProps={circle}
                isSelected={circle.id === selectedId}
                onSelect={() => {
                  selectShape(circle.id);
                }}
                onChange={newAttrs => {
                  const circs = circles.slice();
                  circs[i] = newAttrs;
                  setCircles(circs);
                }}
              />
            );
          })}
          
        </Layer>
      </Stage>
    </div>
  );
}
export default HomePage;