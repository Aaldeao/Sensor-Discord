import React from "react";
import "../styles/Sidebar.css";
import bgames from "../assets/bgames_icon.png";

function Sidebar({ setCurrentView }) {
  return (
    <div className="sidebar">
      <div className="logo">
        <img src={bgames} alt="Logo" />
      </div>
      <button className="button">
        Discord Data
      </button>
      <button className="button" disabled>
        Reddit Data
      </button>
      <button className="button" disabled>
        Steam Data
      </button>
      <button className="button" disabled>
        StackOverflow Data
      </button>
    </div>
  );
}

export default Sidebar;

