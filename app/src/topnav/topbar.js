import React from "react";
import { Navbar, Nav, NavItem ,NavDropdown} from 'react-bootstrap'
// import "./TopBar.css";
import { withRouter } from "react-router-dom";
function TopBar({ location }) {
  const pathname = location.pathname;
  return (
    <Navbar bg="dark" expand="lg" variant="dark">
      <Navbar.Brand href="/home">COV19Sim</Navbar.Brand>
      <Navbar.Collapse id="basic-navbar-nav">
        <Nav className="mr-auto">
          <Nav.Link href="/home" active={pathname == "/"}>Run</Nav.Link>
          <Nav.Link href="/prob" active={pathname == "/"}>Set matrices</Nav.Link>
          <Nav.Link href="/results" active={pathname == "/"}>Disease Analysis</Nav.Link>
          <Nav.Link href="/results2" active={pathname == "/"}>Mobility Analysis</Nav.Link>
          <Nav.Link href="/results3" active={pathname == "/"}>Performance Analysis</Nav.Link>
          <Nav.Link href="/resultsdemo" active={pathname == "/"}>Demographic Analysis</Nav.Link>
          <Nav.Link href="/resultsse" active={pathname == "/"}>SocioEconomic Analysis</Nav.Link>
        </Nav>
      </Navbar.Collapse>
    </Navbar>
  );
}
export default withRouter(TopBar);