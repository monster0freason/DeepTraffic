// import React, { useEffect, useState } from 'react';
// import { Card, CardContent, Typography } from '@mui/material';

// const TrafficSignal = ({ gst }) => {
//   const [remainingTime, setRemainingTime] = useState(gst);
//   const [color, setColor] = useState('red'); // Initial color

//   useEffect(() => {
//     setRemainingTime(gst); // Reset remaining time when gst changes
//     setColor('red'); // Reset color to red when gst changes
//   }, [gst]);

//   useEffect(() => {
//     // Set up the countdown timer
//     if (gst > 0) {
//       const timer = setInterval(() => {
//         setRemainingTime(prevTime => {
//           if (prevTime > 0) {
//             return prevTime - 1;
//           } else {
//             clearInterval(timer); // Stop the timer when it reaches zero
//             return 0;
//           }
//         });
//       }, 1000); // Decrease every second

//       // Clean up the interval on component unmount
//       return () => clearInterval(timer);
//     }
//   }, [gst]);

//   useEffect(() => {
//     // Update color based on remaining time
//     if (remainingTime > 0) {
//       if (remainingTime === 1) {
//         setColor('red'); // Switch to red at the end
//       } else if (remainingTime <= 3) {
//         setColor('yellow'); // Show yellow for the last 3 seconds
//       } else {
//         setColor('green'); // Green for the rest of the time
//       }
//     } else {
//       setColor('off'); // Signal off when time is up
//     }
//   }, [remainingTime]);

//   return (
//     <Card style={{
//       height: '100%',
//       backgroundColor: '#455A64'
//     }}>
//       <CardContent>
//         <Typography color='#B2DFDB' variant="h6">Traffic Signal</Typography>
//         <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
//           <div style={{ backgroundColor: color === 'red' ? 'red' : '#ccc', width: '50px', height: '50px', borderRadius: '50%', margin: '10px' }}></div>
//           <div style={{ backgroundColor: color === 'yellow' ? 'yellow' : '#ccc', width: '50px', height: '50px', borderRadius: '50%', margin: '10px' }}></div>
//           <div style={{ backgroundColor: color === 'green' ? 'green' : '#ccc', width: '50px', height: '50px', borderRadius: '50%', margin: '10px' }}></div>
//         </div>
//         <Typography color='#B2DFDB' variant="h5" align="center" style={{ marginTop: '20px' }}>
//           {remainingTime > 0 ? `${remainingTime} seconds` : 'Signal Off'}
//         </Typography>
//       </CardContent>
//     </Card>
//   );
// };

// export default TrafficSignal;


// TrafficSignal.jsx
import React, { useEffect, useState } from 'react';

const TrafficSignal = ({ gst }) => {
  const [remainingTime, setRemainingTime] = useState(gst);
  const [color, setColor] = useState('red'); // Initial color

  useEffect(() => {
    setRemainingTime(gst); // Reset remaining time when gst changes
    setColor('red'); // Reset color to red when gst changes
  }, [gst]);

  useEffect(() => {
    // Set up the countdown timer
    if (gst > 0) {
      const timer = setInterval(() => {
        setRemainingTime(prevTime => {
          if (prevTime > 0) {
            return prevTime - 1;
          } else {
            clearInterval(timer); // Stop the timer when it reaches zero
            return 0;
          }
        });
      }, 1000); // Decrease every second
      
      // Clean up the interval on component unmount
      return () => clearInterval(timer);
    }
  }, [gst]);

  useEffect(() => {
    // Update color based on remaining time
    if (remainingTime > 0) {
      if (remainingTime === 1) {
        setColor('red'); // Switch to red at the end
      } else if (remainingTime <= 3) {
        setColor('yellow'); // Show yellow for the last 3 seconds
      } else {
        setColor('green'); // Green for the rest of the time
      }
    } else {
      setColor('off'); // Signal off when time is up
    }
  }, [remainingTime]);

  return (
    <div className="traffic-signal-card">
      <div className="traffic-signal-header">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
          <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
        </svg>
        Traffic Signal
      </div>
      
      <div className="traffic-signal-lights">
        <div className={`traffic-signal-light red ${color === 'red' ? 'active' : 'inactive'}`}></div>
        <div className={`traffic-signal-light yellow ${color === 'yellow' ? 'active' : 'inactive'}`}></div>
        <div className={`traffic-signal-light green ${color === 'green' ? 'active' : 'inactive'}`}></div>
      </div>
      
      <div className="traffic-signal-timer">
        {remainingTime > 0 ? remainingTime : '0'}
      </div>
      <div className="traffic-signal-timer-label">
        {remainingTime > 0 ? 'seconds remaining' : 'waiting for next cycle'}
      </div>
    </div>
  );
};

export default TrafficSignal;