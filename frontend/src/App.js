import React, { useState, useEffect } from "react"
import './App.css';

const App = () => {
  // const [query, setQuery] = useState("");
  const [evals, setEvals] = useState("");
  const [profEvals, setProfEvals] = useState("");
  const [profs, setProfs] = useState("");
  const [loggedIn, setLoggedIn] = useState(false);

  const [queryType, setQueryType] = useState("")

  const [classname, setClassname] = useState("");
  const [classcode, setClasscode] = useState("");
  const [quarter, setQuarter] = useState("");
  const [year, setYear] = useState("");
  const [professor, setProfessor] = useState("");
  const [overall, setOverall] = useState("");
  const [overallSearch, setOverallSearch] = useState("");


  useEffect(() => {
    let ignore = false;
    
    if (!ignore)
      credCheck();
    console.log(loggedIn);
    // if (!loggedIn)
    //   login();

    return () => { ignore = true; };
  },[]);

  const credCheck = () => {
    try {
      fetch("https://backend.ratemyscu.bryan.cf/", {
        credentials: 'include'
      })
        .then(response => {
          return response.json();
        })
        .then(data => {
          console.log(data);
          if (data.status === "loggedout")
            setLoggedIn(false);
          if (data.status === "loggedin")
            setLoggedIn(true);
          console.log(loggedIn);

        }).catch(error => {
          console.log(error);
        });
    } catch (err) {
      alert(err);
    }
  }

  const login = () => {
    window.location.href = "https://backend.ratemyscu.bryan.cf/login";
  }

  const fetchData = () => {
    let bodyJSON = {};

    var hasParam = false;

    if (classname !== '') {
      bodyJSON.classname = classname;
      hasParam = true;
    }
    if (classcode !== '') {
      bodyJSON.classcode = classcode;
      hasParam = true;
    }
    if (quarter !== '') {
      bodyJSON.quarter = quarter;
      hasParam = true;
    }
    if (year !== '') {
      bodyJSON.year = year;
      hasParam = true;
    }
    if ((overall !== "") && (overallSearch !== "")) {
      bodyJSON.overall = overall;
      bodyJSON.overallSearch = overallSearch;
      hasParam = true;
    }
    if (professor !== '') {
      bodyJSON.professor = professor;
      // if (hasParam)
      //   ;
    }
    const requestOptions = {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(bodyJSON),
        credentials: 'include'
      };

    var fetched;

    try {
      fetch("https://backend.ratemyscu.bryan.cf/getEvals", requestOptions)
        .then(response => {
          return response.json();
        })
        .then(data => {
          console.log(data);
          setProfs("");
          setEvals("");
          if (queryType === "profs")
            setProfEvals(data.result);
          else
            setEvals(data.result);
        }).catch(error => {
          console.log(error);
        });
    } catch (err) {
      alert(err);
    }
  
    if(queryType === "profs") {
      console.log(queryType);
      aggregate();
    }
  }

  function groupBy(arr) {
    console.log("grouped");
    return arr.reduce((memo, x) => {
      if (!memo[x['professor']]) { memo[x['professor']] = []; }
      memo[x['professor']].push(x);
      console.log(memo);
      return memo;
    }, {});
  }

  const aggregate = () => {
    console.log("aggregate");
    console.log(profEvals);
    var profsGrouped = groupBy(profEvals);
    console.log("grouped"+profsGrouped);

    let profList = [];

    let i = 0;
    Object.entries(profsGrouped).forEach(prof => {
      const [name, evals] = prof;
        var sum;
        var num = 0;
        evals.forEach(evalu => {
          sum += evalu.overall;
          num++;
          console.log(num);
        });
        let avg = sum/num;
        console.log(avg);
        profList.push({ "id" : i, "name" : name, "score" : avg });
        i++;
      });

      setProfs(profList);
      console.log(profsList);
    }

  const handleSubmit = (event) => {
    event.preventDefault();
    fetchData();
  }

  const toggle = (n, e) => {

    var button = e.currentTarget;

    button.classList.toggle("active");

    var content = button.nextElementSibling;
    if (content.style.maxHeight){
      content.style.maxHeight = null;
    } else {
      content.style.maxHeight = content.scrollHeight + "px";
    }
    if (n > 0) {
      var parentOne = content.parentElement.parentElement.parentElement;
      parentOne.style.maxHeight = parseInt(
        parentOne.style.maxHeight.substr(0, parentOne.style.maxHeight.length-2)) 
        + content.scrollHeight + "px";
      if (n === 2) {
        var parentTwo = parentOne.parentElement.parentElement.parentElement;
        parentTwo.style.maxHeight = parseInt(
          parentTwo.style.maxHeight.substr(0, parentTwo.style.maxHeight.length-2)) 
          + parseInt(parentOne.scrollHeight) 
          + parseInt(content.scrollHeight) + "px";
      }
    }
  }

  return (
    <>
      <div>
        
        <h1>Rate My SCU</h1>

        {!loggedIn && (
          <>
            <h3>Login with your SCU email</h3>
            <button onClick={(event) => login()}>Login</button>
          </>
        )}

        {loggedIn && (
          <>

        <label> Show: 
          <select style={{"margin": "0 38px"}} onChange={(e) => setQueryType(e.target.value)}>
            <option value="evals">Class Evaluations</option>
            <option value="profs">Professor Scores</option>
          </select>
        </label>

        <form onSubmit={handleSubmit}>
          <ul>
            <li>Search for one or more of the below:</li>
            <li>
              <label>Professor: 
                <input type="text" style={{"margin": "0 27px"}}
                  value={professor} onChange={(e) => setProfessor(e.target.value)}/>
              </label>
            </li>
            <li>
              <label>Class Name: 
                <input type="text" style={{"margin": "0 10px"}}
                  value={classname} onChange={(e) => setClassname(e.target.value)}/>
              </label>
            </li>
            <li>
              <label>Class Code: 
                <input type="text" style={{"margin": "0 16px"}}
                  value={classcode} onChange={(e) => setClasscode(e.target.value)}/>
              </label>
            </li>
            <li>
              <label>Quarter: 
                <select style={{"margin": "0 38px"}} onChange={(e) => setQuarter(e.target.value)}>
                  <option value="">Select Quarter</option>
                  <option value="Fall">Fall</option>
                  <option value="Winter">Winter</option>
                  <option value="Spring">Spring</option>
                  <option value="Summer">Summer</option>
                </select>
              </label>
            </li>
            <li>
              <label>Year: 
                <select style={{"margin": "0 63px"}} onChange={(e) => setYear(e.target.value)}>
                  <option value="">Select Year</option>
                  <option value="2018">2018</option>
                  <option value="2019">2019</option>
                  <option value="2020">2020</option>
                  <option value="2021">2021</option>
                  <option value="2022">2022</option>
                  <option value="2023">2023</option>
                </select>
              </label>
            </li>
            <li>
              <label>Overall: 
                <select style={{"margin": "0 16px 0 43px"}} onChange={(e) => setOverallSearch(e.target.value)}>
                  <option value="greaterThan">Greater Than</option>
                  <option value="equals">Equals</option>
                  <option value="lesserThan">Less Than</option>
                </select>
                <select onChange={(e) => setOverall(e.target.value)}>
                  <option value="">Select Overall Score</option>
                  <option value="1">1</option>
                  <option value="2">2</option>
                  <option value="3">3</option>
                  <option value="4">4</option>
                  <option value="5">5</option>
                </select>
              </label>
            </li>
          </ul>

          <input type="submit"/>
        </form>
        </>)}
              </div>

      <div>
        {profs.length > 0 && (
          <>
            <ul>
              {profs.map(prof => (
                <>
                  <li class="flex-container" key={prof.id}>
                    <div class="flex-2">{prof.name}</div>
                    <div class="flex-2">{prof.score}</div>
                  </li>
                </>
              ))}            
            </ul>
          </>
        )}
        {evals.length > 0 && (
          <ul>
            {evals.map(evalu => (
              <>
                <li key={evalu.id}>
                  <button class="collapsible flex-container" onClick={(event) => toggle(0, event)}>
                    <div class="flex-6">{evalu.quarter}</div>
                    <div class="flex-6">{evalu.year}</div>
                    <div class="flex-6">{evalu.classcode}</div>
                    <div class="flex-6">{evalu.classname}</div>
                    <div class="flex-6">{evalu.professor}</div>
                    <div class="flex-6">Overall Score: {evalu.overall}</div>
                  </button>
                  <div class="content">
                    <ul>
                      <li key={evalu.id} class="flex-container">
                        <div class="flex-3">{evalu.numstudents} Students</div>
                        <div class="flex-3">{evalu.numresponses} Reponses</div>
                        <div class="flex-3">{Math.round(10000*evalu.numresponses/evalu.numstudents)/100}% Response Rate</div>
                      </li>
                      <li key={evalu.id}>
                        <button class="collapsible" onClick={(event) => toggle(1, event)}>Hours Spent: </button>
                        <div class="content flex-container">
                          <div class="flex-7">0-1: {evalu.hours[0]}%</div>
                          <div class="flex-7">2-3: {evalu.hours[1]}%</div>
                          <div class="flex-7">4-5: {evalu.hours[2]}%</div>
                          <div class="flex-7">6-7: {evalu.hours[3]}%</div>
                          <div class="flex-7">8-10: {evalu.hours[4]}%</div>
                          <div class="flex-7">11-14: {evalu.hours[5]}%</div>
                          <div class="flex-7">15+: {evalu.hours[6]}%</div>              
                        </div>
                      </li> 
                      <li key={evalu.id}>
                        <button class="collapsible" onClick={(event) => toggle(1, event)}>Metrics: </button>
                        <div class="content">
                          <ul>    
                            {evalu.stats.stats.map(stat => (
                              <li key={evalu.id}>
                                <button class="collapsible" onClick={(event) => toggle(2, event)}>{stat.desc}</button>
                                <div class="content flex-container">
                                  <div class="flex-4">n: {stat.n}</div>
                                  <div class="flex-4">average: {stat.avg}</div>
                                  <div class="flex-4">median: {stat.med}</div>
                                  <div class="flex-4">standard deviation: {stat.dev}</div>
                                </div>
                              </li>
                            ))}
                          </ul>
                        </div>
                        </li>
                    </ul>
                  </div>
                </li> 
              </>
            ))}
          </ul>
        )}
      </div>
    </>
  );
}

export default App;