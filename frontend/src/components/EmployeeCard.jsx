
import { useState } from 'react'

function EmployeeCard(props) {

  const [showDetails, setShowDetails] = useState(false)

  return (
    <div>
      <h2>{props.name}</h2>

      <button onClick={() => setShowDetails(!showDetails)}>
        {showDetails ? 'Hide Details' : 'Show Details'}
      </button>

      {showDetails && (
        <div>
          <p>Department: {props.department}</p>
          <p>Role: {props.role}</p>
        </div>
      )}
    </div>
  )
}

export default EmployeeCard



