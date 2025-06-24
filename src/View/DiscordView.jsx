import React, { useEffect, useState, useRef } from "react";

export default function DiscordView() {
  const [discordYaVinculado, setDiscordYaVinculado] = useState(false);
  const [loading, setLoading] = useState(true);
  const [puntos, setPuntos] = useState(null);
  const [idDiscord, setIdDiscord] = useState("");
  
  // Verifica si el usuario ya vinculo su cuenta de Discord
  useEffect(() => {
    fetch("http://localhost:8080/users/discord/checkUser")
      .then((res) => res.json())
      .then((data) => {
        setDiscordYaVinculado(data.discordLinked);
        setIdDiscord(data.id_discord || "");
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error al verificar el estado de Discord:", error);
        setLoading(false);
      });
  }, []);

  // Si el usuario ya vinculo su cuenta de Discord, comienza a consultar los puntos cada segundo.
  useEffect(() => {
    let interval;
    if (discordYaVinculado && idDiscord) {
      const fetchPuntos = () => {
        fetch(`http://localhost:8080/users/puntosDiscord/${idDiscord}`)
          .then((res) => res.json())
          .then((puntosData) => {
            
            const nuevosPuntos = puntosData.puntos;
            setPuntos(nuevosPuntos);
            
            // Si alcanza o supera 15 puntos, detiene el intervalo.
            if (nuevosPuntos >= 15) {
              clearInterval(interval);
            }
          })
          .catch((error) =>
            console.error("Error al obtener los puntos:", error)
          );
      };

      fetchPuntos(); // Llama la función una vez inmediatamente
      interval = setInterval(fetchPuntos, 1000); // Luego la llama cada segundo.
    }

    // Limpia el intervalo
    return () => clearInterval(interval);
  }, [discordYaVinculado, idDiscord]);

  // Mensaje de carga por si tarda
  if (loading) return <p>Cargando ...</p>;

  return (
    <div>
      {/* Titulo de la pagina */}
      <h1>Sensor de Discord</h1>

      {/* Si el usuario no vinculo su cuenta de Discord, muestra el boton para vincular */}
      {!discordYaVinculado ? (
        <>
          <p>Vincula tu cuenta de LifeSync Games con Discord</p>
          <a href="http://localhost:666/login">
            <button>Vincular con Discord</button>
          </a>
        </>
      ) : (
        <>
          {/* Si el usuario ya vinculó su cuenta de Discord, muestra los puntos que va obteniendo en el día */}
          <p>
            <strong>Puntos acumulados hoy:</strong>{" "}
            {puntos !== null ? puntos : "Cargando tus puntos obtenidos..."}
          </p>

          {/* Si alcanzó los 15 puntos o más, muestra un mensaje de logro */}
          {puntos >= 15 && (
            <p>
              🎉 ¡Has alcanzado los 15 puntos diarios! ¡Buen trabajo!
            </p>
          )}
        </>
      )}
    </div>
  );


  //const [mensajeConfirmacion, setMensajeConfirmacion] = useState("");
//const [puntosAnteriores, setPuntosAnteriores] = useState(null);
/*
  const prevPuntosRef = useRef(null); // Referencia para almacenar los puntos anteriores

  // Funcion para enviar puntos a LifeSync Games
  const enviarPuntosAlServidor = (puntos, puntosAnteriores, idDiscord) => {
    const puntosDiferencia = puntos - puntosAnteriores;
    if (puntosDiferencia <= 0) return;

    // Estructura de datos para enviar
    const payload = {
      points: puntosDiferencia,
      id_attributes: "0",
      id_discord: idDiscord,
    };

    // Envia los puntos mediante una peticion PUT
    fetch("http://localhost:8080/users/sendPointsDiscord", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((res) => {
        // Si todo sale bien enviar los puntos, muestra mensaje de confirmación
        if (res.ok) {
          console.log("Puntos enviados correctamente:", payload);
          setMensajeConfirmacion("✅ Tus puntos se han agregado correctamente a la dimensión social.");
        } else { // Si hay un error, mostrar mensaje de error
          res.text().then((text) => {
            console.error(`Error al enviar puntos: ${res.status} - ${text}`);
            setMensajeConfirmacion("❌ Hubo un error al enviar los puntos.");
          });
        }
      })
      .catch((error) => {
        console.error("Excepción al enviar puntos al servidor externo:", error);
        setMensajeConfirmacion("❌ Error al conectar con LifeSync Games.");
      });
  };

  {Muestra el mensaje de cuando se ha agregado los puntos a la dimension }
  {mensajeConfirmacion && (<p>{mensajeConfirmacion}</p>)}
  */
}
