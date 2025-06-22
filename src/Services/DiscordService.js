import axios from "axios";
import dotenv from "dotenv";
import UserRepository from "../Repositories/UserRepository.js";
import UserModel from "../Models/UserModel.js";

dotenv.config();

// Clase para manejar la autenticación y vinculación con Discord
class DiscordService {
  constructor() {
    this.clientId = "1383157858857910352";
    this.clientSecret = "Bl-K_x251kj3NL8MC86CkYLWuBLczU9d";
    this.redirectUri = "http://localhost:666/callback";
  }

  // Genera la URL de autenticación para Discord
  getAuthUrl() {
    return `https://discord.com/api/oauth2/authorize?client_id=${this.clientId}&redirect_uri=${encodeURIComponent(this.redirectUri)}&response_type=code&scope=identify`;
  }

  // Procesa el codigo recibido tras la autenticación
  async processCallback(code) {
    const tokenResponse = await axios.post(
      "https://discord.com/api/oauth2/token",
      new URLSearchParams({
        client_id: this.clientId,
        client_secret: this.clientSecret,
        grant_type: "authorization_code",
        code,
        redirect_uri: this.redirectUri,
      }),
      { headers: { "Content-Type": "application/x-www-form-urlencoded" } }
    );

    // Extrae el token de acceso
    const accessToken = tokenResponse.data.access_token;

    // Obtiene los datos del usuario de Discord
    const userResponse = await axios.get("https://discord.com/api/users/@me", {
      headers: { Authorization: `Bearer ${accessToken}` },
    });

    const discordData = userResponse.data; // Datos del usuario de Discord

    // Busca al usuario en la base de datos
    const users = await UserRepository.getUsers();
    let user = users[0];
    
    // Guarda el ID de Discord
    user.id_discord = discordData.id;
    await UserRepository.updateUser(user);
    console.log("Usuario actualizado con ID de Discord");

    return discordData;
  }

  // Verifica si el usuario ya está vinculado a Discord
  async checkUserDiscord() {
    const users = await UserRepository.getUsers();
    const user = users[0];

    const tieneIdDiscord= user.id_discord && user.id_discord !== 'null' && user.id_discord.trim() !== '';
    
    if (tieneIdDiscord) {
      console.log('El usuario tiene cuenta vinculada con Discord');
      return true;
    }

    console.log('El usuario NO tiene cuenta en Steam');
    return false;
  }

}

export default DiscordService;
