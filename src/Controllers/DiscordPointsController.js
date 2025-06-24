import DiscordPointsService from "../Services/DiscordPointsService.js";
import UserService from "../Services/UserService.js";

// Clase para manejar la lógica de los puntos acumulados por los usuarios en Discord
class DiscordPointsController {
  constructor() {
    this.service = new DiscordPointsService();
    this.userService = new UserService();
  }

  // Método para manejar la solicitud de los puntos acumulados hoy por un usuario en Discord
  pointsToday = async (req, res) => {
    try {
      const puntos = await this.service.discordPointsToday(req.params.id_discord);
      res.json({ puntos });
    } catch (error) {
      console.error("Error al obtener puntos:", error.message);
      res.status(500).json({ error: "Error al consultar puntos." });
    }
  };
}

export default DiscordPointsController;
