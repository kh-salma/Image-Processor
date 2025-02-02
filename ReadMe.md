# 🖼️ Projet de Recherche d'Images par Similarité

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-5.0%2B-green)](https://www.mongodb.com/)

## 📚 Table des Matières
- [Interface de Recherche](#-interface-de-recherche)
- [Interface d'Analyse](#-interface-danalyse)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Architecture Technique](#-architecture-technique)
- [Synthèse](#-synthèse)
- [Contributeurs](#-contributeurs)
- [Annexe](#-annexe)

## 🔍 Interface de Recherche (Home)
**Fonctionnalités** :
- Sélection d'une image depuis la base `BD_images` via un panneau latéral.
- Configuration des paramètres :
  - Combinaison de descripteurs (Couleur/Forme/Texture/CNN):
    - **Descripteurs de Couleur** : Histogramme, Histogramme H de Saturation, Histogramme de Blob
    - **Descripteurs de Forme [Filtres : Sobel, Prewitt, Scharr]** : Histogramme d'Orientation, Histogramme d'Orientation Pondéré par la Norme, Histogramme d'Orientation de Blob, Histogramme Directionnel de Blob 
    - **Descripteurs de Texture** : Histogramme Statistique, Histogramme LBP (Local Binary Pattern), Histogramme LBP de Blob, Histogramme Haralick
    -  **Descripteurs CNN** : Modèle MobileNet entrainé avec *ImageNet*
  - Espace colorimétrique (13 options disponibles):
    - RGB, Grayscale Uniform, Grayscale - Norme 601, Grayscale - Norme 907, YUV, YIQ, I1I2I3, Normalized RGB, HSV, HSL, CMYK, Indexed Image 2.2.2, Indexed Image 4.4.4,  Indexed Image 8.8.8
  - Méthode de distance (7 métriques):
    - Distance Euclidienne, Distance Manhattan, Distance Tchebychev, Intersection d'Histogrammes X, Intersection d'Histogrammes Y, Chi-2, Minkowski
  - Méthode de normalization possible pour les descripteurs traditionnels (5 méthodes):
    - Probabilité, Norme, MinMax, Standardisation, Rang
  - Nombre d'images à afficher (1-18).
- Résultats triés par similarité croissante avec scores de distance.

**NB :** Pour réduire le temps de réponse, un prétraitement a été effectué pour conserver l'ensemble des histogrammes de chaque espace colorimétrique sous forme de fichiers JSON.

![Interface de Recherche](./Interface%20Graphique/InterfaceGraphique/Assets/Screenshoots/Interface%20de%20Recherche.png)

## 📈 Interface d'Analyse (Évaluations)
**Fonctionnalités** :
- Tableau avec des combinaisons et leur MAP pré-évaluées et triées par ordre décroissant 
- Données stockées dans MongoDB :
    ```javascript
    {
        _id: ObjectId("6792544cb1a7f07e50c067ea"),
        combination: {
        color_space: 'gray_601',
        color_desc: 'Blob Histogram',
        shape_desc: 'Orientation Histogram',
        shape_filter: 'scharr',
        texture_desc: 'Haralick Histogram',
        cnn_desc: 'MobileNet Model',
        normalization_method: 'Probability',
        distance: 'chi_2'
        },
        map: 0.6817226473922905
    }
    ```

**NB :** Pour réduire le temps de réponse, une pré-évaluation a été effectué pour stocker certaines combinaions et leur MAP dans une collection MongoDB.
**Note supplémentaire :** Vu le nombre élevé de combinaisons possibles, si vous souhaitez en traiter davantage, exécutez le script *Python `Evaluation/Evaluator.py`*.

![Interface d'Évaluation'](./Interface%20Graphique/InterfaceGraphique/Assets/Screenshoots/Interface%20d'Evaluation.png)

## 🛠 Installation
1. Cloner le dépôt :
    ```sh
    git clone [https://github.com/kh-salma/Image-Processor.git](https://github.com/kh-salma/Image-Processor.git)
    cd "./Image-Processor/Interface Graphique"
    ```
2. Créer un environnement virtuel :
    ```sh
    python -m venv .venv
    .\.venv\Scripts\activate
    ```
3. Installer les dépendances :
    ```sh
    pip install -r "./InterfaceGraphique/Assets/requirements.txt"
    ```
4. Démarrer le serveur MongoDB dans un terminal à part (local par défaut sur mongodb://localhost:27017). [Devra rester ouvert lors du lancement de l'application]
    ```sh
    mongod  # Sous Windows
    ```
5. Puis dans un autre terminal, importer la base de données MongoDB :
    ```sh
    mongorestore --db image_retrieval --dir "<chemin-vers-le-projet>/Interface Graphique/InterfaceGraphique/Assets/Json Files/mongodb_dump/image_retrieval"
    ```
*Remplacez <chemin-vers-le-projet> par le chemin vers votre dossier du projet Image-Processor*

**NB :** Assuez-vous d'avoir MongoDB installé

## 🚀 Utilisation
1. Lancer l'application :
    ```sh
    python "./InterfaceGraphique/App.py"  
    ```
2. Recherche d'images :
  - Sélectionnez une image dans le panneau latéral.
  - Configurez les paramètres dans la sidebar.
  - Cliquez sur "Scan".
3. Analyse des performances :
  - Accédez au tableau des évaluations via le bouton "Évaluations".
  - Explorez les combinaisons et leur MAP via le tableau.

## 🧠 Architecture Technique
- [InterfaceGraphique/](Interface Graphique/InterfaceGraphique/ )
    - [Interface Graphique/InterfaceGraphique/App.py](Interface App.py ) : Point d'entrée de l'application.
    - [Describors/](Interface Graphique/InterfaceGraphique/Describors/ ) : Contient les classes pour les descripteurs de couleur, forme, texture et CNN ainsi que la classe de normalization.
    - [Filters/](Interface Graphique/InterfaceGraphique/Filters/ ) : Contient la classe avec les méthodes de calcul de distances considérées.
    - [Evaluation/](Interface Graphique/InterfaceGraphique/Evaluation/) : Contient la classe pour l'évaluation des combinaisons.
    - [Preprocessor/](Interface Graphique/InterfaceGraphique/Preprocessor/ ) : Contient les classes pour la conversion des couleurs et le prétraitement des images.
    - [Assets/](Interface Graphique/InterfaceGraphique/Assets/ ) : Contient les fichiers de configuration, les fichiers JSON des histogrammes et les fichiers BSON & JSON des collections MongoDB.

## 🧠 Synthèse
- Sur les 130 combinaisons évaluées, la meilleure MAP obtenue est *0.6817*, correspondant à :
    ```javascript
    combination: {
        color_space: 'gray_601',
        color_desc: 'Blob Histogram',
        shape_desc: 'Orientation Histogram',
        shape_filter: 'scharr',
        texture_desc: 'Haralick Histogram',
        cnn_desc: 'MobileNet Model',
        normalization_method: 'Probability',
        distance: 'chi_2'
    }
    ```
- Les meilleures performances sont obtenues avec CNN, mais certaines combinaisons avec CNN affichent une MAP < 0.01. Cela peut être dû à :
    - **Mauvaise complémentarité des features :** Certains descripteurs ajoutent du bruit plutôt qu'une information discriminante.
    - **Ignorance des poids :** Tous les descripteurs sont pondérés de manière égale, alors que CNN pourrait avoir une importance plus grande.
- La meilleure MAP obtenue sans CNN est *0.21*, avec la combinaison :
    ```javascript
    combination: {
        color_space: 'indexed_8,8,8',
        color_desc: 'Blob Histogram',
        shape_desc: 'Blob Orientation Histogram',
        shape_filter: 'sobel',
        texture_desc: '',
        cnn_desc: '',
        normalization_method: '',
        distance: 'minkowski'
    }
    ```
- La soutenance réalisée a permis d'avoir une vision plus critique des résultats et d'explorer les raisons des écarts observés. Ce projet met en évidence la valeur ajoutée des descripteurs traditionnels et des descripteurs basés sur CNN en analysant leurs complémentarités et leurs limites. Il contribue à une meilleure compréhension des caractéristiques discriminantes utilisées en recherche d'images et à l'optimisation des méthodes d'extraction pour améliorer la pertinence des résultats.

## 👩‍💻 Contributeurs
- Salma KHALLAD 

## 📝 Annexe
- Lien vers la présentation réalisée pour ce projet : [Conva Presentation](https://www.canva.com/design/DAGdAoh1yog/GNS-RNluPjwyLH0-yL_kyw/edit?utm_content=DAGdAoh1yog&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton)