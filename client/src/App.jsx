//3rd party imports
import React, { useState, useEffect } from 'react';
import Spinner from './components/Spinner.jsx'

const App = () =>{
  const [shows,setShows] = useState([]);

  useEffect(async ()=>{
    const res = await fetch('/shows')
    await res.json()
    console.log(res)
  }, [])

  if(!shows){
    return <Spinner />
  }

  return(
    <div>
      Shows
    </div>
  )
};

export default App;
