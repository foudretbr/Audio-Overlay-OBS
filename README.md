# Deezer OBS Widget

A lightweight, standalone widget that displays your currently playing Deezer track (from the Desktop app) directly in OBS Studio. No API tokens, no browser extensions, and no complex setup required.

*Read this documentation in [English](#english) or [Français](#français).*

---

## English

### Description
This tool intercepts the Windows System Media Transport Controls (SMTC) to capture what Deezer is currently playing. It generates a local, responsive web widget that you can easily integrate into OBS Studio as a Browser source.

### Features
* **Standalone Executable:** No Python installation needed.
* **Background Process:** Runs silently in the system tray.
* **Real-time Sync:** Accurately captures track name, artist, album cover, and playback progress in real-time.
* **Clean UI:** Responsive, dark-themed design matching the official Deezer branding.

### How to Use
1. Download the latest `deezer_obs.exe` from the **Releases** tab on this repository.
2. Double-click the executable to run it.
   * *Note: Windows Defender SmartScreen might flag the file as unrecognized because it lacks a digital signature. Click "More info" and then "Run anyway".*
3. A notification will appear, and a purple play icon will show up in your system tray (bottom right of your screen).
4. Open OBS Studio and add a new **Browser** source.
5. Set the URL to `http://localhost:8055`.
6. Set the **Width to 800** and **Height to 600**.
7. Click OK. The widget will appear and adjust itself properly.

### Requirements
* Windows 10 or Windows 11.
* Deezer Desktop App.

### How to Close
To completely stop the background process, right-click the purple icon in your system tray and select **Exit / Quitter**.

---

## Français

### Description
Cet outil intercepte le système de contrôle média de Windows (SMTC) pour récupérer la musique en cours de lecture sur Deezer. Il génère un widget web local et responsive que vous pouvez facilement intégrer dans OBS Studio via une source Navigateur.

### Fonctionnalités
* **Exécutable autonome :** Aucune installation de Python n'est requise.
* **Arrière-plan :** Fonctionne silencieusement en fond via la zone de notification.
* **Synchronisation en temps réel :** Récupère le nom du titre, l'artiste, la pochette d'album et la progression de la barre de lecture en temps réel.
* **Interface épurée :** Design sombre et responsive reprenant les codes visuels officiels de Deezer.

### Comment l'utiliser
1. Téléchargez la dernière version de `deezer_obs.exe` dans l'onglet **Releases** de ce dépôt.
2. Double-cliquez sur l'exécutable pour le lancer.
   * *Note : Windows Defender SmartScreen peut bloquer le fichier par précaution car il n'a pas de signature numérique payante. Cliquez sur "Informations complémentaires" puis sur "Exécuter quand même".*
3. Une notification apparaîtra et une icône de lecture violette s'affichera dans votre barre des tâches (en bas à droite).
4. Ouvrez OBS Studio et ajoutez une nouvelle source **Navigateur**.
5. Définissez l'URL sur `http://localhost:8055`.
6. Définissez la **Largeur sur 800** et la **Hauteur sur 600**.
7. Cliquez sur OK. Le widget apparaîtra sur votre scène.

### Prérequis
* Windows 10 ou Windows 11.
* Application bureau Deezer.

### Comment fermer l'application
Pour arrêter complètement le processus, faites un clic-droit sur l'icône violette dans votre barre des tâches et sélectionnez **Exit / Quitter**.
