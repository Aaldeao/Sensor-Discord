import React, { useEffect, useState } from "react";

export default function DiscordView() {
  const [discordYaVinculado, setDiscordYaVinculado] = useState(false);
  const [loading, setLoading] = useState(true);

  // Verifica si el usuario ya está vinculado a Discord
  useEffect(() => {
    fetch("http://localhost:8080/users/discord/checkUser")
      .then((res) => res.json())
      .then((data) => {
        setDiscordYaVinculado(data.discordLinked);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error al verificar el estado de Discord:", error);
        setLoading(false);
      });
  }, []);

  if (loading) return <p>Cargando...</p>;

  return (
    <div>
      <h1> Sensor de discord </h1>

      {/* Si el usuario no está vinculado a Discord, muestra el botón para vincularse*/}
      {!discordYaVinculado && (
        <>
          <p>Vincula tu cuenta de LifeSync Games con discord</p>
          <a href="http://localhost:666/login">
            <button>Discord</button>
          </a>
        </>
      )}
    </div>
  );
}
