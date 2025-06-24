import DiscordService from "../Services/DiscordService.js";

class DiscordController {
  constructor() {
    this.discordService = new DiscordService();
  }

  // Metodo que dirige al usuario a la URL de autenticación de Discord
  login = (req, res) => {
    const url = this.discordService.getAuthUrl();
    res.redirect(url);
  };

  // Metodo que procesa el callback de Discord tras la autenticación
  callback = async (req, res) => {
    const { code } = req.query;

    if (!code) {
      console.log("No realizó la autenticación con Discord");
      return res.redirect("http://localhost:6969/DiscordView?autenticado=false");
    }


    try {
      const userData = await this.discordService.processCallback(code);
      console.log("Autenticación exitosa con Discord:", userData);
      res.redirect("http://localhost:6969/DiscordView?autenticado=true");

    } catch (error) {
      console.error("Error en el callback de Discord:", error.message);
      res.status(500).json({ error: "Error al autenticar con Discord" });
    }
  };

  // Metodo que verifica si el usuario ya está vinculado a Discord
  checkStatus = async (req, res) => {
    try {
      const status = await this.discordService.checkUserDiscord();
      res.status(200).json(status);
    } catch (error) {
      console.error("Error al verificar el estado de Discord:", error.message);
      res.status(500).send("Error al verificar el estado de Discord.");
    }
  };

}

export default DiscordController;