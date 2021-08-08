import React from "react";
import Navbar from "react-bootstrap/Navbar";
import Nav from "react-bootstrap/Nav";
import NavDropdown from "react-bootstrap/NavDropdown";
// import "./TopBar.css";
import { withRouter } from "react-router-dom";
function TopBar({ location }) {
  const pathname = location.pathname;
  return (
    <Navbar bg="primary" expand="lg" variant="dark">
      <Navbar.Brand href="/home">COV19Sim</Navbar.Brand>
      {/* <Navbar.Toggle aria-controls="basic-navbar-nav" /> */}
      <Navbar.Collapse id="basic-navbar-nav">
        <Nav className="mr-auto">
          <Nav.Link href="/home" active={pathname == "/"}>
            Home
          </Nav.Link>
          <Nav.Link href="/prob" active={pathname == "/"}>
            Prob
          </Nav.Link>
          <Nav.Link href="/results" active={pathname == "/"}>
            Results
          </Nav.Link>
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
}
export default withRouter(TopBar);