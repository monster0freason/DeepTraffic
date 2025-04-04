// import React, { useEffect, useState } from 'react';
// import { Typography, Box } from '@mui/material';
// import LaneStats from './LaneStats';
// import axios from 'axios';

// const Dashboard = () => {
//   const [lanesData, setLanesData] = useState({
//     lane1: { color: 'red', totalVehicles: 0, cars: 0, trucks: 0, bikes: 0, buses: 0, gst: 0 },
//     lane2: { color: 'red', totalVehicles: 0, cars: 0, trucks: 0, bikes: 0, buses: 0, gst: 0 },
//     lane3: { color: 'red', totalVehicles: 0, cars: 0, trucks: 0, bikes: 0, buses: 0, gst: 0 },
//     lane4: { color: 'red', totalVehicles: 0, cars: 0, trucks: 0, bikes: 0, buses: 0, gst: 0 },
//   });

//   const fetchLaneData = async () => {
//     try {
//       const response = await axios.get('http://localhost:5006/get_lane_status');
//       const data = response.data;
      
//       // Update the lanesData state based on the response
//       setLanesData(prevLanesData => {
//         const updatedLaneData = { ...prevLanesData };
        
//         Object.keys(data).forEach(lane => {
//           updatedLaneData[lane] = {
//             color: data[lane].color,
//             totalVehicles: data[lane].densities.total_density || 0,
//             cars: data[lane].densities.car_density || 0,
//             trucks: data[lane].densities.truck_density || 0,
//             bikes: data[lane].densities.bikes_density || 0,
//             buses: data[lane].densities.bus_density || 0,
//             gst: data[lane].gst || 0,
//           };
//         });
        
//         return updatedLaneData;
//       });
//     } catch (error) {
//       console.error("Error fetching lane data:", error);
//     }
//   };

//   useEffect(() => {
//     // Fetch lane data initially
//     fetchLaneData();
    
//     const interval = setInterval(() => {
//       // Check if any lane's gst has reached zero
//       const shouldFetch = Object.values(lanesData).some(lane => lane.gst === 0);
//       if (shouldFetch) {
//         fetchLaneData();
//       }
//     }, 1000); // Check every second
    
//     // Clean up interval on component unmount
//     return () => clearInterval(interval);
//   }, [lanesData]); // Add lanesData to the dependency array

//   return (
//     <Box display="flex" margin={0} padding='5px' flexDirection="column" height="100%" sx={{ backgroundColor: '#263238' }}>
//       <Typography variant="h4" gutterBottom align="center" sx={{ color: '#20B2AA' }}>
//         Smart Traffic Management System
//       </Typography>
      
//       {/* First Row: Two LaneStats */}
//       <Box display="flex" justifyContent="space-between" sx={{ marginTop: '20px' }}>
//         <Box display="flex" flexDirection="column" flex={1} marginRight="10px">
//           <LaneStats laneData={lanesData.lane1} path="/vid1.mp4" />
//         </Box>
//         <Box display="flex" flexDirection="column" flex={1}>
//           <LaneStats laneData={lanesData.lane2} path="/vid5.mp4" />
//         </Box>
//       </Box>
      
//       {/* Second Row: Two LaneStats */}
//       <Box display="flex" justifyContent="space-between" sx={{ marginTop: '10px' }}>
//         <Box display="flex" flexDirection="column" flex={1} marginRight="10px">
//           <LaneStats laneData={lanesData.lane3} path="/vid3.mp4" />
//         </Box>
//         <Box display="flex" flexDirection="column" flex={1}>
//           <LaneStats laneData={lanesData.lane4} path="/vid4.mp4" />
//         </Box>
//       </Box>
//     </Box>
//   );
// };

// export default Dashboard;


// Dashboard.jsx
import React, { useEffect, useState } from 'react';
import LaneStats from './LaneStats';
import axios from 'axios';

const Dashboard = () => {
  const [lanesData, setLanesData] = useState({
    lane1: { color: 'red', totalVehicles: 0, cars: 0, trucks: 0, bikes: 0, buses: 0, gst: 0, name: 'North Lane' },
    lane2: { color: 'red', totalVehicles: 0, cars: 0, trucks: 0, bikes: 0, buses: 0, gst: 0, name: 'East Lane' },
    lane3: { color: 'red', totalVehicles: 0, cars: 0, trucks: 0, bikes: 0, buses: 0, gst: 0, name: 'South Lane' },
    lane4: { color: 'red', totalVehicles: 0, cars: 0, trucks: 0, bikes: 0, buses: 0, gst: 0, name: 'West Lane' },
  });

  const fetchLaneData = async () => {
    try {
      const response = await axios.get('http://localhost:5006/get_lane_status');
      const data = response.data;
      
      // Update the lanesData state based on the response
      setLanesData(prevLanesData => {
        const updatedLaneData = { ...prevLanesData };
        
        Object.keys(data).forEach(lane => {
          updatedLaneData[lane] = {
            ...prevLanesData[lane], // Keep the lane name
            color: data[lane].color,
            totalVehicles: data[lane].densities.total_density || 0,
            cars: data[lane].densities.car_density || 0,
            trucks: data[lane].densities.truck_density || 0,
            bikes: data[lane].densities.bikes_density || 0,
            buses: data[lane].densities.bus_density || 0,
            gst: data[lane].gst || 0,
          };
        });
        
        return updatedLaneData;
      });
    } catch (error) {
      console.error("Error fetching lane data:", error);
    }
  };

  useEffect(() => {
    // Fetch lane data initially
    fetchLaneData();
    
    const interval = setInterval(() => {
      // Check if any lane's gst has reached zero
      const shouldFetch = Object.values(lanesData).some(lane => lane.gst === 0);
      if (shouldFetch) {
        fetchLaneData();
      }
    }, 1000); // Check every second
    
    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, [lanesData]); // Add lanesData to the dependency array

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Smart Traffic Management System</h1>
          <p className="dashboard-subtitle">Real-time traffic monitoring and control</p>
        </div>
        <div className="dashboard-timestamp">
          {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </div>
      </div>
      
      <div className="lanes-grid">
        <LaneStats laneData={lanesData.lane1} videoPath="/vid5.mp4" />
        <LaneStats laneData={lanesData.lane2} videoPath="/vid3.mp4" />
        <LaneStats laneData={lanesData.lane3} videoPath="/vid4.mp4" />
        <LaneStats laneData={lanesData.lane4} videoPath="/vid1.mp4" />
      </div>
    </div>
  );
};

export default Dashboard;

