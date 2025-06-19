import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import "../styles/Dashboard.css";
import "../styles/ButtonBackDashView.css";
import RedditView from "./RedditView.jsx";
import OverflowView from "./OverflowView.jsx";
import SteamLogin from "./SteamLogin.jsx";
import Sidebar from "../Components/Sidebar.jsx";
import personeIcon from "../assets/person.png";

function Dashboard() {
  const [points, setPoints] = useState({
    social: 0,
    fisica: 0,
    afectivo: 0,
    cognitivo: 0,
    linguistico: 0,
  });
  const prevPointsRef = useRef(points); // Referencia para guardar puntos anteriores
  const firstLoadRef = useRef(true);    // Detecta si es la primera carga

  const [currentView, setCurrentView] = useState("default");
  const [errorMessage, setErrorMessage] = useState("");
  const [user, setUser] = useState({ name: "" });
  

  const fetchPoints = async () => {
    try {
      const response = await axios.get("http://localhost:8080/users/points");

      if (response.status === 200) {
        const pointsData = response.data;
        setErrorMessage("bGames server is running.");

        const newPoints = {
          social: pointsData.find((p) => p.name === "Social")?.data || 0,
          fisica: pointsData.find((p) => p.name === "Fisica")?.data || 0,
          afectivo: pointsData.find((p) => p.name === "Afectivo")?.data || 0,
          cognitivo: pointsData.find((p) => p.name === "Cognitivo")?.data || 0,
          linguistico: pointsData.find((p) => p.name === "Linguistico")?.data || 0,
        };

        const prevPoints = prevPointsRef.current;

        // Detectar si alguno de los puntos aumentó
        const increased = Object.keys(newPoints).some(
          (key) => newPoints[key] > prevPoints[key]
        );
        
        // Solo mostramos alerta si NO es la primera carga
        if (increased && !firstLoadRef.current) {
          alert("You have earned bGames points!");
        }
        
        firstLoadRef.current = false; // Marca que ya pasamos la primera carga

        prevPointsRef.current = newPoints; // Actualiza los puntos anteriores
        setPoints(newPoints);
      } else {
        setErrorMessage("The points could not be obtained.");
      }
    } catch (error) {
      setErrorMessage("Error communicating with the server.");
    }
  };

  useEffect(() => {
  const fetchUser = async () => {
    try {
      const response = await axios.get("http://localhost:8080/users/all");

      if (response.status === 201) {
        const user = response.data[0];

        if (user) {
          setUser({ name: user.name });
        } else {
          setErrorMessage("No users found.");
        }
      } else {
        setErrorMessage("The user could not be obtained.");
      }
    } catch (error) {
      setErrorMessage("Error communicating with the server to obtain a user.");
    }
  };

  fetchPoints();
  fetchUser();

  // Ejecuta fetchPoints cada 10 segundos
  const interval = setInterval(() => {
    fetchPoints();
  }, 60000); // cada 10 segundos

  return () => clearInterval(interval); // Limpiar intervalo si se desmonta
}, []);


  const handleSetView = (view) => {
    setCurrentView(view); // Cambia a la nueva vista
  };

  const handleGoBack = () => {
    fetchPoints(); // Llama a fetchPoints antes de cambiar la vista
    setCurrentView("default"); // Siempre regresa al dashboard
  };

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <Sidebar setCurrentView={handleSetView} />

      {/* Main Content */}
      <div className="main-content">
        {currentView === "reddit" && (
          <>
            <button onClick={handleGoBack} className="back-button">Back</button>
            <RedditView />
          </>
        )}
        {currentView === "overflow" && (
          <>
            <button onClick={handleGoBack} className="back-button">Back</button>
            <OverflowView />
          </>
        )}
        {currentView === "steam" && (
          <>
            <button onClick={handleGoBack} className="back-button">Back</button>
            <SteamLogin />
          </>
        )}
        {currentView === "default" && (
          <>
            <div className="header">
              <div className="profile">
                <span>{user.name}</span>
                <div className="avatar">
                  <img src={personeIcon} alt="avatar" />
                </div>
              </div>
            </div>

            <div className="points-section">
              <h2>Your Points:</h2>
              {errorMessage && <p className="error-message">{errorMessage}</p>}
              <div className="points-grid">
                <div className="point-item">Social: <span>{points.social}</span></div>
                <div className="point-item">Fisica: <span>{points.fisica}</span></div>
                <div className="point-item">Afectivo: <span>{points.afectivo}</span></div>
                <div className="point-item">Cognitivo: <span>{points.cognitivo}</span></div>
                <div className="point-item">Linguistico: <span>{points.linguistico}</span></div>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default Dashboard;





