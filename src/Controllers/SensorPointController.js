import SensorPointRepository from "../Repositories/SensorPointRepository.js";
import SensorPointService from "../Services/SensorPointService.js";
import DiscordPointsService from "../Services/DiscordPointsService.js";

class SensorPointController {
    constructor() {
        const sensorPointRepository = new SensorPointRepository();
        this.sensorPointService = new SensorPointService(sensorPointRepository);
        this.discordPointsService = new DiscordPointsService();
    }

    async setDataSteam(req, res) {
        const { key_steam, id_user_steam } = req.body;
    
        console.log('key_steam:', key_steam);
        console.log('id_user_steam:', id_user_steam);
    
        if (!key_steam || !id_user_steam) {
          return res.status(400).json({ error: 'La clave de Steam y el ID de usuario son obligatorios.' });
        }
    
        try {
          const result = await this.sensorPointService.setDataSteam(key_steam, id_user_steam);
    
          if (result) {
            return res.status(200).json({ message: 'Datos de Steam guardados exitosamente.' });
          } else {
            return res.status(400).json({ error: 'Los datos de Steam no pudieron ser guardados.' });
          }
        } catch (error) {
          console.error('Error al guardar datos de Steam:', error.message);
          return res.status(500).json({ error: 'Error interno del servidor.' });
        }
      }

    async getHoursPlayed(req, res) {
        try {
            const response = await this.sensorPointService.getHoursPlayed();
            res.status(200).json({
                message: 'Horas jugadas obtenidas exitosamente.',
                data: response
            });
        } catch (error) {
            console.error('Error al obtener las horas jugadas:', error.message);
            res.status(500).json({
                message: 'Error interno del servidor al obtener las horas jugadas.',
                error: error.message
            });
        }
    }
    
    async saveSensorPoint(req, res) {
        try {
            const response = await this.sensorPointService.saveSensorPoint();
            res.status(200).json({
                message: 'Punto de sensor guardado exitosamente.',
                data: response
            });
        } catch (error) {
            console.error('Error al guardar el punto de sensor:', error.message);
            res.status(500).json({
                message: 'Error interno del servidor al guardar el punto de sensor.',
                error: error.message
            });
        }
    }
    
    async getAllSensorPoints(req, res) {
        try {
            const { tipe_sensor } = req.body;
            console.log(tipe_sensor);
    
            // Validación de entrada
            if (!tipe_sensor || typeof tipe_sensor !== 'string') {
                return res.status(400).json({
                    message: 'El campo "tipe_sensor" es obligatorio y debe ser una cadena de texto.'
                });
            }
            console.log("Hola!!!!!!!!!!!");
            const response = await this.sensorPointService.getAllSensorPoints(tipe_sensor);
            res.status(200).json({
                message: 'Puntos de sensor obtenidos exitosamente.',
                data: response
            });
        } catch (error) {
            console.error('Error al obtener los puntos de sensor:', error.message);
            res.status(500).json({
                message: 'Error interno del servidor al obtener los puntos de sensor.',
                error: error.message
            });
        }
    }    

    async getAllPoints(req, res) {
        try {
            const response = await this.sensorPointService.getAllPoint();
            res.status(200).json({
                message: 'Puntos obtenidos exitosamente.',
                data: response
            });
        } catch (error) {
            console.error('Error al obtener los puntos del senso.', error.message);
            res.status(500).json({
                message: 'Error interno del servidor al obtener los puntos del sensor.',
                error: error.message
            });
        }
    }
    
    // Método para recibir y enviar puntos desde Discord a LifeSyncGames
    async sendPointsController(req, res) {
        try {
            // Obtener los datos enviados desde el cliente
            const { points, id_attributes, id_players } = req.body;

            // Validar parámetros
            if (typeof points !== 'number' || !id_attributes || !id_players) {
                return res.status(400).json({
                    error: "Parámetros inválidos. Se requiere points (number), id_attributes y id_players",
                });
            }

            // Enviar puntos al servidor usando el servicio correspondiente
            await this.sensorPointService.sendPointsToServerStackAndReddit(points,
                id_attributes,
                id_players);

            // Enviar respuesta de éxito
            res.json({success: true, message: "Puntos enviados correctamente al servidor.",});

        } catch (error) {
            console.error("Error en sendPointsController:", error.message);
            res.status(500).json({ error: "Ocurrió un error al enviar los puntos al servidor.", });
        }
    }
    /*
    async sendPointsController(req, res) {
        try {
            // Obtener los datos enviados desde el cliente a través del body de la solicitud
            const { points, id_attributes } = req.body;

            // Validar que los parámetros obligatorios estén presentes y sean del tipo correcto
            if (typeof points !== 'number' || !id_attributes) {
            return res.status(400).json({ error: "Parámetros inválidos. Se requiere points (number), id_attributes" });
            }

            // Obtener el id_player correspondiente al id_discord
            const id_player = await this.discordPointsService.getIdPlayerByDiscordId(req.body.id_discord);

            // Enviar los puntos usando el servicio correspondiente
            await this.sensorPointService.sendPointsToServerStackAndReddit(points,
            id_attributes,
            String(id_player)
            );

            // Enviar respuesta al cliente
            res.json({ success: true, message: "Puntos enviados correctamente al servidor." });

        } catch (error) {
            console.error("Error en sendPointsController:", error.message);
            res.status(500).json({ error: "Ocurrió un error al enviar los puntos al servidor." });
        }
    }
    */

}

export default SensorPointController;
