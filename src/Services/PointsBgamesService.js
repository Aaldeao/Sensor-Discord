import PointsBgamesModel from '../Models/PointsBgamesModel.js';
import UserService from '../Services/UserService.js'; 
import axios from 'axios';

class PointsBgamesService {
    constructor() {
        this.httpClient = axios.create();
        this.pointsBgamesModel = this.pointsBgamesModel;
        this.userService = new UserService();
    }

    async savePointsBgames() {
        const user = await this.userService.getAllUsers();
        console.log('Usuario:', user);
        const apiUrl = `http://localhost:3001/player_all_attributes/${user[0].id_players}`;
      
        try {
          const response = await this.httpClient.get(apiUrl);
      
          if (response.status === 200) {
            // Transformar los datos de la API en instancias de PointsBgmaesModel
            const pointsBgamesFromApi = response.data;
            const pointsBgames = pointsBgamesFromApi.map((points) => {
              return {
                id_attributes: points.id_attributes,
                name: points.name,
                data: points.data,
              };
            });
      
            console.log('Puntos obtenidos:', pointsBgames);
            return pointsBgames; // Retornar los datos transformados
          } else {
            console.error('Error en la API: estado no esperado', response.status);
            return []; // Devuelve un array vacío si el estado no es 200
          }
        } catch (error) {
          console.error('Error al obtener datos de la API:', error.message);
          return []; // Manejo de errores: devolver un array vacío
        }
      }
}

export default PointsBgamesService;