// import React from 'react';
// import { Card, CardContent, Typography } from '@mui/material';

// const VehicleCounter = ({ total, cars, trucks, bikes, buses }) => {
//   return (
//     <Card style={{
//         height:'100%',
//         backgroundColor:'#455A64'
//     }}>
//       <CardContent>
//         <Typography color='#B2DFDB' variant="h6">Unique Vehicle Count</Typography>
//         <Typography color='#B2DFDB'>Total Vehicles: {total}</Typography>
//         <Typography color='#B2DFDB'>Cars: {cars}</Typography>
//         <Typography color='#B2DFDB'>Trucks: {trucks}</Typography>
//         <Typography color='#B2DFDB'>Bikes: {bikes}</Typography>
//         {buses > 0 && <Typography color='#B2DFDB'>Buses: {buses}</Typography>}
//       </CardContent>
//     </Card>
//   );
// };

// export default VehicleCounter;



// VehicleCounter.jsx
import React from 'react';

const VehicleCounter = ({ total, cars, trucks, bikes, buses }) => {
  return (
    <div className="vehicle-counter-card">
      <div className="vehicle-counter-header">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z" />
          <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1v-1h3a1 1 0 001-1v-3.05a2.5 2.5 0 010-4.9V4a1 1 0 00-1-1H3z" />
        </svg>
        Vehicle Stats
      </div>
      
      <div className="vehicle-counter-grid">
        <div className="vehicle-counter-item vehicle-counter-total">
          <div className="vehicle-counter-value">{total}</div>
          <div className="vehicle-counter-label">Total Vehicles</div>
        </div>
        
        <div className="vehicle-counter-item">
          <div className="vehicle-counter-value">{cars}</div>
          <div className="vehicle-counter-label">Cars</div>
        </div>
        
        <div className="vehicle-counter-item">
          <div className="vehicle-counter-value">{trucks}</div>
          <div className="vehicle-counter-label">Trucks</div>
        </div>
        
        <div className="vehicle-counter-item">
          <div className="vehicle-counter-value">{bikes}</div>
          <div className="vehicle-counter-label">Bikes</div>
        </div>
        
        {buses > 0 && (
          <div className="vehicle-counter-item">
            <div className="vehicle-counter-value">{buses}</div>
            <div className="vehicle-counter-label">Buses</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default VehicleCounter;