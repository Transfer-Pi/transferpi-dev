import React from 'react';
import axios from 'axios';

import UserLogo from './icons/user.svg';
import PILogo from './icons/PI.svg';
import PlusLogo from './icons/plus.svg';
import CloseLogo from './icons/close.svg';

import './App.css';

const Card = (props) =>{
  return (
    <div className="card" key={props.i}>
      {
        props.labels.map((l,j)=>{
          return (
            <div className="row" key={j}>
              <div className="col label">
                {l}
              </div>
              <div className="col colon">
                :
              </div>
              <div className="col values">
                {props.row[l]}
              </div>
            </div>
          )
        })
      }
    </div>
  )
}
const New = (props) =>{

  const AddButton = (props) =>{
    return(
      <div className="card new">
        <img src={PlusLogo} alt="plus-logo" style={{height:"64px",width:"64px"}} onClick={loadForm} />
      </div>
    )
  }

  const NewForm = (props) =>{
    return (
      <div className="card">
        <div className="newform">
          <input type="text" placeholder="file" />
          <input type="text" placeholder="type" />
        </div>
      </div>
    )
  }

  let [render,renderState] = React.useState({
    component:<AddButton />
  })

  function loadForm(){
    renderState({
      component:<NewForm />
    })  
  }

  return(
    <div>
      {
        render.component
      }
    </div>
  )
}

function App() {
  let labels = ['filename','token','type','md5','time','url']
  let [data,dataState] = React.useState({
    tokens:[]
  })

  async function fetch(){
    await axios({
      url:"http://localhost:2121/file/GET_TOKENS",
      method:"GET",
    }).then(response=>{
      dataState({
        tokens:response.data.tokens
      })
    })
  }

  React.useEffect(()=>{
    fetch()
  },[])

  return (
    <section>
        <div className="notification-bar">

        </div>
        <div className="container">
          <div className="nav-bar">
            <div className='logo'>
              <a href="http://transferpi.tk" target="#">
                <img src={PILogo} alt="Logo" />
              </a>
            </div>
            <div className='logo'>
              <img src={UserLogo} alt="Logo" />
            </div>
          </div>
          <div className="tron">
            <New />  
            {data.tokens.map((row,i)=>{
              return <Card row={row} i={i} labels={labels} />
            })}
          </div>
        </div>
        <div className="footer">

        </div>
    </section>
  );
}

export default App;
