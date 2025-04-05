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
  
  const [cycleStatus, setCycleStatus] = useState('stopped');
  const [refreshing, setRefreshing] = useState(false);

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
            bikes: data[lane].densities.motorcycle_density || 0,
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
  
  const handleForceRefresh = async () => {
    try {
      setRefreshing(true);
      const response = await axios.post('http://localhost:5006/force_refresh');
      if (response.status === 200) {
        console.log('Cache cleared successfully. New data will be fetched in the next cycle.');
      }
    } catch (error) {
      console.error('Error forcing refresh:', error);
    } finally {
      setRefreshing(false);
    }
  };
  
  const toggleTrafficCycle = async () => {
    try {
      if (cycleStatus === 'stopped') {
        const response = await axios.post('http://localhost:5006/start_cycle');
        if (response.status === 200) {
          setCycleStatus('running');
        }
      } else {
        const response = await axios.post('http://localhost:5006/stop_cycle');
        if (response.status === 200) {
          setCycleStatus('stopped');
        }
      }
    } catch (error) {
      console.error('Error toggling traffic cycle:', error);
    }
  };

  useEffect(() => {
    // Fetch lane data initially
    fetchLaneData();
    
    // Start traffic cycle automatically
    const startCycle = async () => {
      try {
        const response = await axios.post('http://localhost:5006/start_cycle');
        if (response.status === 200) {
          setCycleStatus('running');
        }
      } catch (error) {
        console.error('Error starting traffic cycle:', error);
      }
    };
    
    startCycle();
    
    const interval = setInterval(() => {
      fetchLaneData();
    }, 1000); // Check every second
    
    // Clean up interval on component unmount
    return () => clearInterval(interval);
  }, []); // Only run once on component mount

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">Smart Traffic Management System</h1>
          <p className="dashboard-subtitle">Real-time traffic monitoring and control</p>
        </div>
        <div className="dashboard-controls">
          <button 
            onClick={toggleTrafficCycle}
            className={`control-button ${cycleStatus === 'running' ? 'stop' : 'start'}`}
          >
            {cycleStatus === 'running' ? 'Stop' : 'Start'} Traffic Cycle
          </button>
          <button 
            onClick={handleForceRefresh}
            className="control-button refresh"
            disabled={refreshing}
          >
            {refreshing ? 'Refreshing...' : 'Force Refresh Data'}
          </button>
          <div className="dashboard-timestamp">
            {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </div>
        </div>
      </div>
      
      <div className="lanes-grid">
        <LaneStats laneData={lanesData.lane1} videoPath="/vid2.mp4" />
        <LaneStats laneData={lanesData.lane2} videoPath="/vid5.mp4" />
        <LaneStats laneData={lanesData.lane3} videoPath="/vid4.mp4" />
        <LaneStats laneData={lanesData.lane4} videoPath="/vid1.mp4" />
      </div>
    </div>
  );
};

export default Dashboard;