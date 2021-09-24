import React, { useState, useRef } from "react"
// var PythonShell = require('python-shell');
function HomePage() {
  // PythonShell.runString('x=1+1;print(x)', null, function (err) {
  //   if (err) throw err;
  //   console.log('finished');
  // });
  const { exec } = require('child_process');
  console.log(exec)
  const ls = exec('dir', function (error, stdout, stderr) {
    if (error) {
      console.log(error.stack);
      console.log('Error code: '+error.code);
      console.log('Signal received: '+error.signal);
    }
    console.log('Child Process STDOUT: '+stdout);
    console.log('Child Process STDERR: '+stderr);
  });
  return (
    <div className="home-page">
      <h1>Home Page</h1>
    </div>
  );
}
export default HomePage;