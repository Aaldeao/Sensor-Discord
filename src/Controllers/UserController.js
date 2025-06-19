import UserService from '../Services/UserService.js';
import UserRepository from '../Repositories/UserRepository.js';

class UserController {
  constructor() {
    // Crear una instancia de UserRepository
    const userRepository = new UserRepository();

    // Pasar el repositorio a UserService
    this.userService = new UserService(userRepository);
  }

  async createUser(req, res) {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ error: 'El email y la contraseña son obligatorios.' });
    }

    try {
      const user = await this.userService.createUser(email, password);
      console.log('Usuario creado:', user);
      if (user) {
        
        res.status(201).json({ message: 'Usuario creado exitosamente.', user });
      } else {
        res.status(400).json({ error: 'El usuario no pudo ser creado.' });
      }
    } catch (error) {
      console.error('Error al crear usuario:', error.message);
      res.status(500).json({ error: 'Error interno del servidor.' });
    }
  }

  async getAllUsers(req, res) {
    try {
      const users = await this.userService.getAllUsers();

      if (users.length) {
        res.status(201).json(users);
      } else {
        res.status(404).json({ error: 'No se encontraron usuarios.' });
      }
    } catch (error) {
      console.error('Error al obtener usuarios:', error.message);
      res.status(500).json({ error: 'Error interno del servidor.' });
    }
  }

  async userCheckDB(req, res) {
    try {
      const users = await this.userService.getAllUsers(); // Llama al servicio para obtener todos los usuarios
      if (users.length > 0) {
        return res.status(200).json({ message: 'Ya existe un usuario.' });
      }
      return res.status(404).json({ error: 'No existen usuarios.' });
    } catch (error) {
      console.error('Error al verificar usuarios:', error.message);
      return res.status(500).json({ error: 'Error interno del servidor.' });
    }
  }

  async userCheckSteam(req, res) {
    try {
      const users = await this.userService.getAllUsers();
      // Validar si no hay usuarios
      if (!users || users.length === 0) {
        return res.status(404).json({ error: 'No hay usuarios en la base de datos.' });
      } else {
        if (users[0].key_steam && users[0].id_user_steam != null) {
          return res.status(200).json({ message: 'Usuario con clave de steam.' });
        }
        return res.status(404).json({ error: 'No existe usuario con clave de steam.' });
      }
    } catch (error) {
      onsole.error('Error al verificar usuarios:', error.message);
      return res.status(500).json({ error: 'Error interno del servidor.' });
    }
  }
}


export default UserController;