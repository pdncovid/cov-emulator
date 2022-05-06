<div id="top"></div>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]



<!-- PROJECT LOGO -->
<br />
 
<div align="center">
  <a href="https://github.com/pdncovid/cov-emulator">
    <img src="https://github.com/pdncovid/cov-emulator/images/logo.png" alt="Logo">
  </a>

  <h3 align="center">PanDemic SIMulator - PDSIM</h3>

  <p align="center">
    Realistic mobility and disease simulation!
    <br />
    <a href="https://github.com/pdncovid/cov-emulator"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/pdncovid/cov-emulator">View Demo</a>
    ·
    <a href="https://github.com/pdncovid/cov-emulator/issues">Report Bug</a>
    ·
    <a href="https://github.com/pdncovid/cov-emulator/issues">Request Feature</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project

![Product Name Screen Shot][product-screenshot]

There are many simulators to emulate a disease's spread within a population; however, there is a deficiency in the 
realistic movement in those simulations which neglects vital factors such as collisions when moving inside a building 
and contacts when moving in public transport systems. This PDSIM provides comprehensive set of tools to efficiently 
model complex environments and simulate a pandemic with realistic movement system. 

Main contributions of PDSIM are:
*  Hybrid Movement Model with more realistic motion simulation - Movement modeling at a particular location and when someone is moving in-between two locations imitates human-like motion and decision-making that generates natural movement paths.
*  The daily routine generator facilitated by the proposed motion model enables occupation-specific motion and routine generation. 
*  A novel location occupancy mechanic to determine how long someone stays at a given location simulates human motion more effectively and injects individualized randomness into the overall population motion. 
*  Transport system that integrates with the motion model to simulate the impact of public transport on disease propagation. 
*  Ability to simulate Super-Spreader events (Large gathering) and assess its impact. 
*  Implementation of testing and vaccination protocols coupled with the effective use of people's daily routine to enable a realistic testing and vaccination simulation.
*  Simulation of social distancing and hygiene (mask-wearing/hand sanitizing) of people with an attention to each individual.
*  Multiple types of containment policy simulation, where each policy categorically implements required actions only for the affected set of people. These containment measures work together with the motion model to address the variations in the containment in a collaborative manner. For example, quarantining a particular sector affects the people moving through that sector.
*  Detailed variant, environment, and person (age factors, immunity, hygiene, etc.) based disease transmission model. 

<p align="right">(<a href="#top">back to top</a>)</p>



### Built With

PDSIM was built using,
* [React.js](https://reactjs.org/)
* [JQuery](https://jquery.com)
* [Python]()
* [Numpy]()
* [Flask]()
* [Plotly.js]()
* [Matplotlib]()

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

Instructions on setting up your project locally.
To get a local copy up and running follow these steps.

### Prerequisites

Install following software. We recommend that you create a virtual environment for this, but it is not essential.

* Python 3.8.10 (65-bit)


* npm
  ```shell script
  npm install npm@latest -g
  ```

### Installation

Install PDSIM and associated dependencies.


1. Clone the repo and goto it's directory
   ```shell script
   git clone https://github.com/pdncovid/cov-emulator.git
   ```
2. Install NPM packages
   ```shell script
   npm install
   ```
3. Install python packages
   ```shell script
   pip install -e .
   ```

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- USAGE EXAMPLES -->
## Usage

Go to the backend/server folder and run the flask server using

```shell script
flask run
```

Start the node server which is located at app folder

```shell script
npm start
```

Use the UI to run specific simulations.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ROADMAP -->
<!--
## Roadmap

- [x] Add Changelog
- [x] Add back to top links
- [ ] Add Additional Templates w/ Examples
- [ ] Add "components" document to easily copy & paste sections of the readme
- [ ] Multi-language Support
    - [ ] Chinese
    - [ ] Spanish

See the [open issues](https://github.com/pdncovid/cov-emulator/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#top">back to top</a>)</p>
-->


<!-- CONTRIBUTING -->
## Contributing

If you have a suggestion that would make this better, please fork the repo and create a pull request.
You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the CC0 1.0 Universal License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Harshana - [@harshanaSW](https://twitter.com/harshanaSW) - harshana.w@eng.pdn.ac.lk

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Use this space to list resources you find helpful and would like to give credit to. I've included a few of my favorites to kick things off!

* AI4COVID group for the guidance and support.
* [Covasim](https://github.com/InstituteforDiseaseModeling/covasim) for the initial motivation when coding.

<p align="right">(<a href="#top">back to top</a>)</p>



<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/pdncovid/cov-emulator.svg?style=for-the-badge
[contributors-url]: https://github.com/pdncovid/cov-emulator/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/pdncovid/cov-emulator.svg?style=for-the-badge
[forks-url]: https://github.com/pdncovid/cov-emulator/network/members
[stars-shield]: https://img.shields.io/github/stars/pdncovid/cov-emulator.svg?style=for-the-badge
[stars-url]: https://github.com/pdncovid/cov-emulator/stargazers
[issues-shield]: https://img.shields.io/github/issues/pdncovid/cov-emulator.svg?style=for-the-badge
[issues-url]: https://github.com/pdncovid/cov-emulator/issues
[license-shield]: https://img.shields.io/github/license/pdncovid/cov-emulator.svg?style=for-the-badge
[license-url]: https://github.com/pdncovid/cov-emulator/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/harshanasumedha
[product-screenshot]: images/screenshot.png