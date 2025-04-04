// import React from 'react';
// import { Box } from '@mui/material';
// import CCTVFeed from './CCTVFeed';
// import TrafficSignal from './TrafficSignal';
// import VehicleCounter from './VehicleCounter';

// function LaneStats({ laneData, path }) {
//   const { color, totalVehicles, cars, trucks, bikes, buses, gst } = laneData; // Destructure laneData to get all values
  
//   return (
//     <div>
//       <Box 
//         display="flex" 
//         flexGrow={1} 
//         justifyContent="space-between" 
//         sx={{ marginTop: '20px', padding: '10px' }}
//       >
//         <Box 
//           flex={1} 
//           display="flex" 
//           flexDirection="column" 
//           marginRight="10px"
//           height="100%"
//           sx={{ padding: '0px', backgroundColor: '#263238' }}
//         >
//           <CCTVFeed vid_path={path}/>
//         </Box>
//         <Box display="flex" flexDirection="column" width='40%'>
//           <Box 
//             flex={1} 
//             display="flex" 
//             flexDirection="column"  
//             marginBottom="10px"
//             height="50%"
//             sx={{ padding: '0px', backgroundColor: '#263238' }}
//           >
//             <TrafficSignal color={color} gst={gst} />
//           </Box>
//           <Box 
//             flex={1} 
//             display="flex" 
//             flexDirection="column"  
//             height="50%"
//             sx={{ padding: '0px', backgroundColor: '#263238' }}
//           >
//             <VehicleCounter 
//               total={totalVehicles} 
//               cars={cars} 
//               trucks={trucks} 
//               bikes={bikes} 
//               buses={buses} 
//             />
//           </Box>
//         </Box>
//       </Box>
//     </div>
//   );
// }

// export default LaneStats;


// LaneCard.jsx
import React from 'react';
import CCTVFeed from './CCTVFeed';
import TrafficSignal from './TrafficSignal';
import VehicleCounter from './VehicleCounter';

const LaneStats = ({ laneData, videoPath }) => {
  const { color, totalVehicles, cars, trucks, bikes, buses, gst, name } = laneData;
  
  return (
    <div className="lane-card">
      <div className="lane-card-header">
        <h3 className="lane-card-title">{name}</h3>
      </div>
      
      <div className="lane-content">
        <div className="cctv-feed-container">
          <CCTVFeed videoPath={videoPath} />
        </div>
        
        <div className="traffic-stats-container">
          <TrafficSignal color={color} gst={gst} />
          <VehicleCounter 
            total={totalVehicles} 
            cars={cars} 
            trucks={trucks} 
            bikes={bikes} 
            buses={buses} 
          />
        </div>
      </div>
    </div>
  );
};

export default LaneStats;

