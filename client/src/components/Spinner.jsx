import React, { useState } from 'react';


export default function Spinner(){
  const [speed, setSpeed] = useState(5)

  return(
    <div className="spinner-container">
      <div className="spinner" style={{animation: `spin ${speed}s linear infinite`}}></div>
      <p>Loading..</p>
    </div>
  )
}