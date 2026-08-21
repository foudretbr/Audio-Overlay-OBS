# Audio Overlay OBS (Spotify & Deezer)

A lightweight, standalone widget that displays your currently playing Spotify or Deezer track (from their Desktop apps) directly in OBS Studio. No API tokens, no browser extensions, and no complex setup required.

*Read this documentation in [English](#english) or [Français](#français).*

---

## English

### Description
This tool intercepts the Windows System Media Transport Controls (SMTC) to capture what is currently playing. It specifically targets Spotify and Deezer, completely ignoring other audio sources like web browsers (YouTube) or video players. It generates a local, responsive web widget that you can easily integrate into OBS Studio as a Browser source.

### Features
* **Standalone Executable:** No Python installation needed.
* **Background Process:** Runs silently in the system tray with auto-startup capabilities.
* **Targeted Capture:** Only reacts to Spotify and Deezer desktop applications.
* **Real-time Sync:** Accurately captures track name, artist, album cover, and playback progress in real-time.
* **Dynamic UI:** Responsive, dark-themed design featuring a progress bar that automatically changes color based on the active source (Green for Spotify, Purple for Deezer).
* **Auto-Update:** Seamless, built-in updater to ensure you always have the latest version.

### How to Use
1. Download the latest `audio_overlay_obs.exe` from the **Releases** tab on this repository.
2. Double-click the executable to run it.
   * *Note: Windows Defender SmartScreen might flag the file as unrecognized because it lacks a paid digital signature. Click "More info" and then "Run anyway".*
3. A notification will appear, and a dark play icon will show up in your system tray (bottom right of your screen).
4. Open OBS Studio and add a new **Browser** source.
5. Set the URL to `http://localhost:8055`.
6. Set the **Width to 800** and **Height to 600**.
7. Click OK. The widget will appear and adjust itself properly.

### Requirements
* Windows 10 or Windows 11.
* Spotify and/or Deezer Desktop App.

### How to Close or Update
Right-click the icon in your system tray to check for updates, enable run-at-startup, or select **Exit / Quitter** to close the application.

---

## Français

### Description
Cet outil intercepte le système de contrôle média de Windows (SMTC) pour récupérer la musique en cours de lecture. Il cible spécifiquement Spotify et Deezer, ignorant complètement les autres sources audio comme les navigateurs web (YouTube) ou les lecteurs vidéo. Il génère un widget web local et responsive que vous pouvez facilement intégrer dans OBS Studio via une source Navigateur.

### Fonctionnalités
* **Exécutable autonome :** Aucune installation de Python n'est requise.
* **Arrière-plan :** Fonctionne silencieusement en fond via la zone de notification avec option de démarrage automatique.
* **Capture ciblée :** Réagit uniquement aux applications de bureau Spotify et Deezer.
* **Synchronisation en temps réel :** Récupère le nom du titre, l'artiste, la pochette d'album et la progression de la lecture en temps réel.
* **Interface dynamique :** Design sombre et responsive avec une barre de progression qui adapte automatiquement sa couleur selon la source (Vert pour Spotify, Violet pour Deezer).
* **Mise à jour automatique :** Système intégré et transparent pour toujours bénéficier de la dernière version.

### Comment l'utiliser
1. Téléchargez la dernière version de `audio_overlay_obs.exe` dans l'onglet **Releases** de ce dépôt.
2. Double-cliquez sur l'exécutable pour le lancer.
   * *Note : Windows Defender SmartScreen peut bloquer le fichier par précaution car il ne possède pas de signature numérique payante. Cliquez sur "Informations complémentaires" puis sur "Exécuter quand même".*
3. Une notification apparaîtra et une icône de lecture sombre s'affichera dans votre barre des tâches (en bas à droite).
4. Ouvrez OBS Studio et ajoutez une nouvelle source **Navigateur**.
5. Définissez l'URL sur `http://localhost:8055`.
6. Définissez la **Largeur sur 800** et la **Hauteur sur 600**.
7. Cliquez sur OK. Le widget apparaîtra sur votre scène.

### Prérequis
* Windows 10 ou Windows 11.
* Application de bureau Spotify et/ou Deezer.

### Comment fermer ou mettre à jour l'application
Faites un clic-droit sur l'icône dans votre barre des tâches pour rechercher des mises à jour, activer le démarrage avec Windows, ou sélectionnez **Exit / Quitter** pour fermer l'application.