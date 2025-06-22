import express from "express";
import DiscordController from "../src/Controllers/DiscordController.js";

// Crea una instancia de Express y define el puerto
const app = express();
const PORT = 666;

const discordController = new DiscordController();

app.get("/login", discordController.login.bind(discordController)); // Ruta para realizar la autenticación con Discord
app.get("/callback", discordController.callback.bind(discordController)); // Ruta de callback que recibe el código de autorización

// Inicia el servidor en el puerto especificado
app.listen(PORT, () => {
  console.log(`Servidor escuchando en http://localhost:${PORT}`);
});
