import sqlite3 from "sqlite3";
import axios from "axios";
import UserService from "./UserService.js";

// Clase para la lógica de los puntos acumulados por los usuarios en Discord
class DiscordPointsService {
  constructor() {
    this.userService = new UserService();
    this.db = new sqlite3.Database("./Sensores-LifeSyncGames.db");
  }

  // Obtiene los puntos acumulados hoy por un usuario en Discord
  async discordPointsToday(id_discord) {
    // Calcula la fecha actual restando 4 horas para ajustar la zona horaria
    const today = new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString().slice(0, 10);

     // Consulta los puntos en la tabla bot_discord para el usuario y la fecha actual
    return new Promise((resolve, reject) => {
      this.db.get(
        "SELECT puntos FROM bot_discord WHERE usuario_id = ? AND fecha = ?",
        [id_discord, today],
        (err, row) => {
          if (err) return reject(err);
          resolve(row ? row.puntos : 0);
        }
      );
    });
  }
/*// Obtiene el id_player de un usuario a partir de su id_discord
  async getIdPlayerByDiscordId(id_discord) {
    try {
      const query = `SELECT id_players FROM users WHERE id_discord = ?`;
      
      // Ejecuta la consulta para obtener el id_player
      const result = await new Promise((resolve, reject) => {
        this.db.get(query, [id_discord], (err, row) => {
          if (err) return reject(err);
          resolve(row);
        });
      });

      // Retorna el id_player si se encuentra, o null si no hay coincidencias
      return result ? result.id_players : null;

    } catch (error) {
      console.error('Error al obtener id_player por id_discord:', error.message);
      throw error;
    }
  }
*/
}

export default DiscordPointsService