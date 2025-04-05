
// CCTVFeed.jsx
import React from 'react';

const CCTVFeed = ({ videoPath }) => {
  return (
    <div className="cctv-feed">
      <video autoPlay loop muted>
        <source src={videoPath} type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      
      <div className="cctv-feed-overlay">
        <div className="cctv-feed-overlay-dot"></div>
        <span className="cctv-feed-overlay-text">Live Feed</span>
      </div>
    </div>
  );
};

export default CCTVFeed;

