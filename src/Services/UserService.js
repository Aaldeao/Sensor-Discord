import axios from 'axios';
import UserModel from '../Models/UserModel.js'; // Modelo del usuario
import UserRepository from '../Repositories/UserRepository.js'; // Repositorio del usuario

class UserService {
  constructor(userRepository) {
    this.userRepository = userRepository;
    this.httpClient = axios.create();
  }

  /**
 * Crea un nuevo usuario en la base de datos local si existe en la API externa y la contraseña coincide.
 * 
 * Esta función hace una llamada a un servicio bGames para obtener los datos del usuario
 * mediante su correo electrónico. Si la respuesta es exitosa y la contraseña es válida,
 * se guarda el usuario en la base de datos local.
 * 
 * @param {string} email - Correo electrónico del usuario.
 * @param {string} password - Contraseña del usuario.
 * @returns {Promise<number>} Retorna 1 si el usuario fue creado correctamente, 0 en caso contrario.
 */

  async createUser(email, password) {
    const apiUrl = `http://localhost:3010/player_by_email/${email}`;

    try {
      // Llamada a la API externa
      const response = await this.httpClient.get(apiUrl);

      if (response.status === 200) {
        const userFromApi = response.data; // Datos del usuario desde la API

        // Validar si el usuario existe y la contraseña coincide
        if (userFromApi && userFromApi.password === password) {
          console.log(`Nombre: ${userFromApi.name}`);
          console.log(`Email: ${userFromApi.email}`);
          console.log(`ID: ${userFromApi.id_players}`);

          // Crear una instancia de UserModel
          const user = new UserModel(
            userFromApi.id_players,
            userFromApi.name,
            userFromApi.email,
            userFromApi.password,
            userFromApi.key_steam || null, // Opcional
            userFromApi.id_user_steam || null, // Opcional
            userFromApi.id_reddit || null // Opcional
          );

          // Guardar el usuario en el repositorio
          await UserRepository.createUser(user);
          //await this.sensorPointService.saveSensorPointReddit(); // Guarda el primer puntos al
          console.log('Usuario guardado en la base de datos');
          return 1; // Usuario encontrado y guardado
        } else {
          return 0; // Usuario no encontrado o contraseña incorrecta
        }
      } else {
        return 0; // Error en la respuesta de la API
      }
    } catch (error) {
      console.error('Error al llamar a la API:', error.message);
      return 0; // Error durante la llamada a la API
    }
  }

  async getAllUsers() {
    try {
      const users = await UserRepository.getUsers(); // Llamar al método estático del repositorio
      return users; // Retornar la lista de usuarios
    } catch (error) {
      console.error('Error al obtener usuarios:', error.message);
      throw new Error('No se pudieron obtener los usuarios.');
    }
  }
}



export default UserService;