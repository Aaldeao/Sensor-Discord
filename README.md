# Sensor-LifeSync-Games-Discord  

🌐 Available in: [Español](#-español) | [English](#-english)  

---

## 🇪🇸 Español  

**LifeSync-Games** es una iniciativa enfocada en el **desarrollo responsable de videojuegos**.  

A través de sensores, se registran tus actividades del mundo real y se convierten en **puntos**, los cuales puedes utilizar dentro del juego.  

Este repositorio contiene el **bot de Discord** diseñado para capturar la actividad social de los usuarios dentro del servidor de Discord de LifeSync-Games, como la realización de quizzes mediante comandos, respuestas y reacciones de otros usuarios a sus mensajes, transformando dichas interacciones en puntos que se asignan a la dimensión social de su cuenta en **LifeSync-Games**.  


---

## ✨ Características principales  

- 🤖 **Bot de Discord como sensor externo**.  
- 📊 Registro de la actividad social de los usuarios en el servidor de Discord de LifeSync-Games.  
- 📝 Captura de:  
  - Realización de quizzes (activados mediante comandos y respondidos con emojis).
  - Respuestas de otros usuarios a sus mensajes.  
  - Reacciones de otros usuarios a sus mensajes.  
- 🎮 **Quizzes temáticos** (se activan mediante comandos):
  - Cities: Skylines.  
  - Tecnología.  
  - Informática.
- 📌 **Comandos principales**:  
  - `$cities` → Quiz sobre Cities: Skylines.  
  - `$technology` → Quiz sobre tecnología.  
  - `$informatics` → Quiz sobre informática.  
  - `$LSG` → Consultar puntos acumulados.  
  - `$help` → Mostrar lista de comandos disponibles.  
- ⏳ **Control de uso**:  
  - Límite diario de uso de comandos.  
  - Máximo de **15 puntos diarios por usuario** para evitar abusos.  

---

## 📥 Instalación  

### 🔹 Instalación de la aplicación de sensores con el bot  

1. Descarga este repositorio y extráelo.  
2. Abre la carpeta **Sensor-Discord** en **Visual Studio**.  
3. Copia y pega el **token del bot** en el archivo `tokensecrets.py` (se encuentra en la sección 🔑 token del bot).  
4. Recuerda que el token, por temas de seguridad, está dividido con la indicación **(Borra esto)**. Debes borrar esos fragmentos para que funcione correctamente.  
5. Antes de ejecutar, instala las dependencias necesarias desde la terminal (debes tener **Python** y **Node.js** instalados):
   ```
   pip install requests
   pip install discord.py
   npm install
   ```
6. Para levantar la aplicación de sensores con el bot de Discord:
   ```
   npm run start 
   ```
7. Es esencial tener en ejecución los servicios LifeSync-Games en tu máquina para poder utilizar la aplicación de sensores (**ver instalación en el siguiente sección**).  

---

### 🔹 Instalación de servicios de LifeSync-Games:  

Para instalar los servicios de [**LifeSync-Games**](https://github.com/BlendedGames-bGames/bGames-dev-services), accede al repositorio correspondiente en GitHub y sigue las instrucciones de instalación.  

Se recomienda utilizar **Docker** para desplegar los servicios de forma sencilla y rápida.

---

## 🔑 Token del Bot
Para ejecutar el bot, copia y pega el siguiente token en el archivo tokensecrets.py.
Está dividido por seguridad:
   ```
   MTM4MzE1Nzg1ODg1NzkxMDM1Mg(Borra esto).GP5RIU.(Borra esto)lK16Vp6F8JVs2Gq3Dx-tByBH3fETCC3dVPtn1w
   ```

---

## 🇬🇧 English  

**LifeSync-Games** is an initiative focused on the **responsible development of video games**.  

Through sensors, your real-world activities are recorded and converted into **points**, which you can use within the game.  

This repository contains the **Discord bot** designed to capture users’ social activity within the LifeSync-Games Discord server, such as completing quizzes via commands, replies, and reactions from other users to their messages, transforming these interactions into points assigned to the social dimension of their **LifeSync-Games** account.  

---

### ✨ Main Features  

- 🤖 **Discord bot as an external sensor**.  
- 📊 Logs users’ social activity in the LifeSync-Games Discord server.  
- 📝 Captures:  
  - Quizzes (triggered by commands and answered with emojis).  
  - Replies from other users to their messages.  
  - Reactions from other users to their messages.  
- 🎮 **Themed quizzes** (triggered via commands):  
  - Cities: Skylines.  
  - Technology.  
  - Informatics.  
- 📌 **Main commands**:  
  - `$cities` → Cities: Skylines quiz.  
  - `$technology` → Technology quiz.  
  - `$informatics` → Informatics quiz.  
  - `$LSG` → Check accumulated points.  
  - `$help` → Show the list of available commands.  
- ⏳ **Usage control**:  
  - Daily limit on command usage.  
  - Maximum of **15 points per user per day** to prevent abuse.  

---

### 📥 Installation  

#### 🔹 Sensor application with the bot  

1. Download and extract this repository.  
2. Open the **Sensor-Discord** folder in **Visual Studio**.  
3. Copy and paste the **bot token** into the `tokensecrets.py` file (see 🔑 Bot Token section).  
4. Remember that for security reasons, the token is split with the indication **(Delete this)**. You must remove those fragments for it to work properly.  
5. Before running, install the required dependencies from the terminal (you must have **Python** and **Node.js** installed):
   ```
   pip install requests
   pip install discord.py
   npm install
   ```
6. To run the sensor application with the Discord bot:
   ```
   npm run start 
   ```
7. LifeSync-Games services must be running on your machine to use the sensor application (see installation in the next section).

---

#### 🔹 Installation of LifeSync-Games services  

To install the [**LifeSync-Games services**](https://github.com/BlendedGames-bGames/bGames-dev-services), go to the corresponding GitHub repository and follow the installation instructions.  

It is recommended to use **Docker** for quick and easy deployment.

---

### 🔑 Bot Token  

To run the bot, copy and paste the following token into the `tokensecrets.py` file.  
It is split for security reasons:
   ```
   MTM4MzE1Nzg1ODg1NzkxMDM1Mg(Delete this).GP5RIU.(Delete this)lK16Vp6F8JVs2Gq3Dx-tByBH3fETCC3dVPtn1w
   ```