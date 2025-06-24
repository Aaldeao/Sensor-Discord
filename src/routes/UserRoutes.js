import express from 'express';
import UserController from '../Controllers/UserController.js';
import PointsBgamesController from '../Controllers/PointsBgamesController.js';
import SensorPointController from '../Controllers/SensorPointController.js';
import SensorStackOverflowController from '../Controllers/SensorStackOverflowController.js';
import SensorRedditController from '../Controllers/SensorRedditController.js';
import DiscordController from "../Controllers/DiscordController.js"; // Discord
import DiscordPointsController from '../Controllers/DiscordPointsController.js'; // Discord

const router = express.Router();
const userController = new UserController();
const pointsBgamesController = new PointsBgamesController();
const sensorPointController = new SensorPointController();
const sensorStackOverflowController = new SensorStackOverflowController();
const sensorRedditController = new SensorRedditController();
const discordController = new DiscordController(); // Discord
const discordPointsController = new DiscordPointsController(); // Discord

// Ruta para crear un usuario
router.post('/create', (req, res) => userController.createUser(req, res));
router.get('/all', (req, res) => userController.getAllUsers(req, res));
router.get('/check', (req, res) => userController.userCheckDB(req, res));
router.post('/steam', (req, res) => sensorPointController.setDataSteam(req, res));
router.get('/checkSteam', (req, res) => userController.userCheckSteam(req, res));
router.get('/points', (req, res) => pointsBgamesController.savePointsBgames(req, res));
router.get('/hoursSteam', (req, res) => sensorPointController.getHoursPlayed(req, res));
router.get('/savePoint', (req, res) => sensorPointController.saveSensorPoint(req, res));
router.get('/savePointReddit', (req, res) => sensorRedditController.saveSensorPointReddit(req, res));
router.get('/savePointStack', (req, res) => sensorStackOverflowController.saveSensorPointStackOverflowt(req, res));
router.post('/allPoints', (req, res) => sensorPointController.getAllSensorPoints(req, res));
router.post('/all-points', (req, res) => sensorPointController.getAllPoints(req, res));
router.post('/stack', (req, res) => sensorStackOverflowController.getReputation(req, res));
router.get('/reddit', (req, res) => sensorRedditController.getKarma(req, res));
router.get('/callback',(req, res) => sensorRedditController.checkUserReddit(req, res));
router.get('/check-reddit-user',(req, res) => sensorRedditController.checkUserRedditDB(req, res));
router.get('/check-stack-overflow-user',(req, res) => sensorStackOverflowController.checkUserStackOverflowDB(req, res));
router.get('/callback-stack-overflow',(req, res) => sensorStackOverflowController.checkUserStackOverflow(req, res));
router.get("/discord/checkUser", discordController.checkStatus); // Ruta para verificar si un usuario ya tiene vinculada su cuenta de Discord
router.get("/puntosDiscord/:id_discord", (req, res) => discordPointsController.pointsToday(req, res)); // Ruta para obtener los puntos acumulados hoy por un usuario en Discord
router.put("/sendPointsDiscord", (req, res) => sensorPointController.sendPointsController(req, res));  // Ruta para enviar a LifeSync Games los puntos ganados por el usuario en Discord
// Exporta el router como default
export default router;