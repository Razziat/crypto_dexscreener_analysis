# DexScreener Token Listener

## Introduction

Ce projet vise à automatiser la collecte d'informations sur les nouveaux tokens listés sur l'application mobile DexScreener. Il utilise Appium pour interagir avec l'application sur un appareil Android connecté, et récupère des données clé telles que les hashes des tokens sur leurs blockchains respectives, ainsi que des simulations d'achat pour analyser les performances potentielles.

## Table des Matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Configuration de l'Environnement](#configuration-de-lenvironnement)
4. [Utilisation](#utilisation)
   - [Récupérer les Derniers Tokens](#1-récupérer-les-derniers-tokens)
   - [Simuler des Achats et Récupérer les Hashes](#2-simuler-des-achats-et-récupérer-les-hashes)
   - [Mettre à Jour les Prix des Tokens](#3-mettre-à-jour-les-prix-des-tokens)
5. [Améliorations Futures](#améliorations-futures)
6. [Remarques](#remarques)

## Prérequis

Avant de commencer, assurez-vous d'avoir les éléments suivants installés sur votre système :

- **Python 3.x** : Assurez-vous que Python est installé et configuré sur votre machine.
- **ADB (Android Debug Bridge)** : Pour communiquer avec votre appareil Android.
- **Appium Server** : Pour automatiser les interactions avec l'application DexScreener.
- **Appium Inspector (facultatif)** : Pour inspecter l'interface utilisateur de l'application DexScreener.

## Installation

1. **Cloner le dépôt GitHub** :

   ```bash
   git clone https://github.com/Razziat/crypto_dexscreener_analysis.git
   cd votre-repo

    Installer les dépendances Python :

    pip install -r requirements.txt

    Assurez-vous que le fichier requirements.txt contient toutes les bibliothèques nécessaires, par exemple :
        appium-python-client
        selenium
        requests

Configuration de l'Environnement
1. Connecter votre Appareil Android

    Activer les Options pour Développeurs sur votre appareil Android.
    Activer le Débogage USB dans les options pour développeurs.
    Brancher votre téléphone à votre PC via un câble USB.
    Sélectionner le Mode MTP (Media Transfer Protocol) dans les options de connexion USB.

2. Configurer ADB

    Vérifier que votre appareil est reconnu :

    adb devices

    Vous devriez voir votre appareil listé avec un identifiant unique.

    Récupérer l'ID ADB de votre appareil pour le configurer dans le script. L'ID ressemble à ceci : 4672d93b.

3. Lancer le Serveur Appium

    Démarrer Appium Server sur le port 4725. Vous pouvez le faire via la ligne de commande ou l'interface graphique d'Appium.

4. Configurer Appium Inspector (Facultatif)

Appium Inspector n'est pas obligatoire pour exécuter les scripts, mais il peut être utile pour inspecter l'interface utilisateur.

    Lancer Appium Inspector.
    Configurer les paramètres de connexion :
        Remote Host : localhost
        Remote Port : 4725
        Remote Path : /wd/hub
    Importer la Configuration JSON :
        Copier le contenu du fichier json_for_appium.json fourni dans le projet.
        Coller le contenu dans le champ JSON Representation d'Appium Inspector.
    Démarrer la Session pour inspecter l'application DexScreener.

Utilisation
1. Récupérer les Derniers Tokens

Script : get_newest_tokens.py

Ce script permet de récupérer en temps réel les derniers tokens listés sur DexScreener et de les enregistrer dans un fichier.

Étapes :

    Lancer l'application DexScreener sur votre téléphone connecté.

    Sélectionner le Filtre "New Newest" pour afficher les tokens les plus récents.

    Exécuter le script :

    python3 get_newest_tokens.py

2. Simuler des Achats et Récupérer les Hashes

Script : dexscreenerlistener.py

Ce script interagit avec l'application DexScreener pour :

    Récupérer les 7 à 8 tokens les plus récents.
    Extraire les hashes correspondants sur leurs blockchains respectives.
    Préparer une simulation d'achat pour chaque token.

Étapes :

    Assurer que l'application DexScreener est ouverte sur votre téléphone avec le filtre "New Newest" sélectionné.

    Mettre à jour l'ID de l'appareil ADB dans le script dexscreenerlistener.py :

options.deviceName = 'votre_id_adb'

Lancer le script :

    python3 dexscreenerlistener.py

Résultats :

    Les informations des tokens sont enregistrées dans pair_hash.json.
    Les simulations d'achat sont enregistrées dans simulated_purchases.json.

3. Mettre à Jour les Prix des Tokens

Script : get_updated_token_price.py

Ce script n'interagit pas avec le téléphone. Il utilise l'API DexScreener pour :

    Récupérer les informations mises à jour des tokens.
    Comparer les prix actuels avec les prix d'achat simulés.
    Calculer les gains ou les pertes potentiels.
    Afficher des informations supplémentaires telles que la liquidité et la capitalisation boursière.

Étapes :

    Vérifier que simulated_purchases.json existe et contient les données générées par dexscreenerlistener.py.

    Exécuter le script :

    python3 get_updated_token_price.py

Résultats :

    Les résultats détaillés sont affichés dans le terminal.
    Les informations sont enregistrées dans purchase_results.json.

Améliorations Futures

    Refactorisation du Code : Séparer dexscreenerlistener.py en plusieurs fichiers pour améliorer la lisibilité et la maintenance.

    Optimisation des Performances :
        Réduire les Temps d'Attente : Ajuster les temps de sleep pour accélérer l'exécution.
        Améliorer l'Algorithme : Optimiser la manière dont les informations des tokens sont récupérées pour une meilleure efficacité.
