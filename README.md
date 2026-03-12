# ERP RAG System

Un système de gestion de documents avec découpage en chunks (RAG - Retrieval-Augmented Generation) intégrant une architecture modulaire, des patterns de conception et une base de données MongoDB. Ce projet permet l'upload de fichiers, leur découpage en segments textuels, et leur stockage structuré pour alimenter des applications de recherche sémantique ou de génération augmentée.

## Fonctionnalités

*   **Upload de fichiers (TXT, PDF)** avec validation (type, taille)
*   **Création automatique de projets** si inexistants
*   **Découpage intelligent des documents en chunks** (via LangChain `RecursiveCharacterTextSplitter`)
*   **Stockage des chunks et métadonnées** dans MongoDB
*   **Gestion des assets (fichiers)** avec suivi de leur état de traitement
*   **API REST documentée** avec FastAPI
*   **Logging structuré** (fichiers journaux quotidiens)
*   **Architecture faiblement couplée** basée sur des interfaces et des repositories

## Stack technique

*   **Langage :** Python 3.8+
*   **Gestionnaire d'environnement :** Miniconda (recommandé)
*   **Framework Web :** FastAPI
*   **Base de données :** MongoDB (via Docker)
*   **ORM/ODM :** Pymongo (asynchrone) + Pydantic pour la validation
*   **Découpage :** LangChain (`RecursiveCharacterTextSplitter`)
*   **Logging :** Module logging de Python avec fichiers rotatifs
*   **Conteneurisation :** Docker (pour MongoDB et Mongo-Express)

## Architecture

L'application suit une architecture en couches avec séparation claire des responsabilités :

```text
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│     Routes      │ ───▶ │   Controllers   │ ───▶ │    Services     │
│   (FastAPI)     │      │ (logique métier)│      │  (repositories) │
└─────────────────┘      └─────────────────┘      └─────────────────┘
         │                       │                         │
         ▼                       ▼                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Contexte applicatif                       │
│                   (AppContext, singleton DB)                     │
└─────────────────────────────────────────────────────────────────┐
                                    │
                                    ▼
                          ┌─────────────────────┐
                          │      MongoDB        │
                          │   (via Docker)      │
                          └─────────────────────┘
```

Les principaux composants :

*   **Modèles Pydantic :** Définissent la structure des données (projets, chunks, assets) et assurent la validation.
*   **Interfaces (ABC) :** `IDBClientContext` définit le contrat que tout client de base de données doit respecter.
*   **Client MongoDB :** Implémentation concrète de l'interface, utilise des repositories spécialisés pour chaque entité.
*   **Repositories :** `ProjectRepository`, `ChunkRepository`, `AssetRepository` encapsulent les opérations CRUD spécifiques.
*   **Factory :** `DBClientFactory` crée et met en cache une instance unique du client MongoDB (singleton).
*   **Contexte applicatif :** `AppContext` gère le cycle de vie (connexion/déconnexion) et fournit la dépendance `get_db` pour FastAPI.
*   **Contrôleurs :** `DataController`, `ProcessController`, `ProjectController` orchestrent la logique métier.
*   **Routes :** Endpoints FastAPI qui utilisent les contrôleurs et le client DB injecté.

## Structure du projet

```text
ERP_RagSyetem/
├── assets/                  # Stockage physique des fichiers uploadés
│   └── files/
│       └── {project_id}/
├── src/
│   ├── clients/             # Implémentations des clients de données
│   │   ├── MongoClient.py
│   │   └── repositories/
│   │       ├── AssetRepository.py
│   │       ├── ChunkRepository.py
│   │       └── ProjectRepository.py
│   ├── core/                # Cœur applicatif
│   │   └── AppContext.py
│   ├── factories/           # Fabrication d'instances
│   │   └── DbFactory.py
│   ├── helpers/             # Utilitaires transversaux
│   │   ├── config.py
│   │   ├── file_cleaner.py
│   │   └── logger.py
│   ├── interfaces/          # Contrats abstraits
│   │   └── IDBClientContext.py
│   ├── models/              # Modèles Pydantic
│   │   ├── db_schemes/
│   │   │   ├── Asset.py
│   │   │   ├── Chunk.py
│   │   │   ├── Project.py
│   │   │   └── base.py
│   │   └── enums/
│   │       ├── AssetTypes.py
│   │       ├── FileExtentionsEnums.py
│   │       └── ResponseEnums.py
│   ├── controllers/         # Logique métier
│   │   ├── BaseController.py
│   │   ├── DataController.py
│   │   ├── ProcessController.py
│   │   └── ProjectController.py
│   ├── routes/              # Points d'entrée API
│   │   ├── data.py
│   │   └── base.py
│   └── main.py              # Point d'entrée FastAPI
├── logs/                     # Fichiers de log
├── .env                      # Variables d'environnement
├── docker-compose.yml        # Configuration Docker pour MongoDB
├── mongo-init.js             # Script d'initialisation MongoDB
└── requirements.txt          # Dépendances Python
```

## Design patterns utilisés

| Pattern | Description | Emplacement |
| :--- | :--- | :--- |
| **Factory** | Création centralisée du client DB | `DbFactory.get_mongo_client()` |
| **Singleton** | Une seule instance du client MongoDB | Cache dans `DbFactory._clients` |
| **Repository** | Encapsulation des accès aux données par entité | `AssetRepository`, `ChunkRepository`, `ProjectRepository` |
| **Dependency Injection** | Injection du client DB dans les routes via `Depends` | `get_db()` dans `AppContext` |
| **Interface / Abstraction** | Contrat pour tous les clients DB | `IDBClientContext` |
| **Layered Architecture** | Séparation en couches (routes, contrôleurs, repositories) | Structure des dossiers |
| **DTO** | Objets de transfert de données pour la création/mise à jour | `ProjectCreate`, `AssetCreate`, etc. |
| **Lifespan Management** | Gestion du cycle de vie avec FastAPI | `lifespan` dans `main.py` |

## Installation et configuration

### Prérequis

*   Miniconda (ou Anaconda) installé
*   Docker et Docker Compose
*   Git

### Étapes

1.  **Cloner le dépôt**
    ```bash
    git clone <url-du-repo>
    cd ERP_RagSyetem
    ```

2.  **Créer un environnement Conda**
    ```bash
    conda create -n erp-rag-env python=3.8
    conda activate erp-rag-env
    ```

3.  **Installer les dépendances**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Lancer MongoDB avec Docker**
    ```bash
    docker-compose up -d
    ```
    Le fichier `docker-compose.yml` fourni lance MongoDB et Mongo-Express (interface web disponible sur [http://localhost:8081](http://localhost:8081)).
    Les identifiants par défaut sont :
    *   **Utilisateur admin :** `admin` / `admin_password`
    *   **Utilisateur application :** `erp_app` / `erp_app_password`

5.  **Configurer les variables d'environnement**
    Créez un fichier `.env` à la racine du projet (au même niveau que `src/`) avec le contenu suivant :
    ```env
    APP_NAME=ERP_RagSystem
    APP_VERSION=1.0.0
    OPENAI_API_KEY=your-key-here

    # MongoDB
    MONGO_APP_USER=erp_app
    MONGO_APP_PASSWORD=erp_app_password
    MONGO_DATABASE=erp_rag_db

    # Paramètres fichiers
    FILE_MAX_SIZE=10
    FILE_CHUNK_SIZE=1048576
    FILE_EXTENTIONS_ALLOWED=["jpg","jpeg","png","pdf","txt"]
    ```
    > **Important :** Remplacez les valeurs par défaut par vos propres identifiants, surtout le mot de passe MongoDB.

6.  **Initialiser la base de données (optionnel)**
    Si vous utilisez le script `mongo-init.js` fourni, les collections et utilisateurs seront créés automatiquement au premier démarrage de MongoDB. Sinon, vous pouvez créer manuellement l'utilisateur `erp_app` via Mongo-Express.

7.  **Lancer l'application**
    ```bash
    cd src
    uvicorn main:app --reload --port 5000
    ```
    L'API sera accessible sur [http://localhost:5000](http://localhost:5000). La documentation interactive Swagger est disponible sur [http://localhost:5000/docs](http://localhost:5000/docs).

## API Endpoints

### Base
| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/` | Message de bienvenue |
| GET | `/health` | Vérification de l'état de l'application et de la connexion MongoDB |

### Projets
| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/data/v1/projects` | Crée un projet (body JSON avec `project_id`, `name`, etc.). |
| GET | `/data/v1/projects/{project_id}` | Détails d'un projet. |
| GET | `/data/v1/projects` | Liste tous les projets (pagination via `skip` et `limit`). |
| PUT | `/data/v1/projects/{project_id}` | Met à jour un projet. |
| DELETE | `/data/v1/projects/{project_id}` | Supprime un projet et ses données associées. |

### Upload et traitement
| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| POST | `/data/v1/upload/{project_id}` | Upload d'un fichier (TXT ou PDF). Crée le projet s'il n'existe pas et incrémente le compteur de fichiers du projet. |
| POST | `/data/v1/process/{project_id}` | Traite un fichier : découpage en chunks via LangChain et stockage dans MongoDB. Retourne le nombre de chunks générés. |
| GET | `/data/v1/projects/{project_id}/assets` | Liste tous les assets (fichiers) d'un projet. Option `?asset_type=file` (ou `stream`) pour filtrer par type. |

### Assets (détail)
| Méthode | Endpoint | Description |
| :--- | :--- | :--- |
| GET | `/data/v1/assets/{asset_id}` | Récupère les métadonnées d'un asset spécifique. |
| DELETE | `/data/v1/assets/{asset_id}` | Supprime un asset et ses chunks associés. |

## Utilisation avec Conda

Pour travailler sur le projet, activez l'environnement Conda à chaque fois :
```bash
conda activate erp-rag-env
```
Pour mettre à jour les dépendances après modification de `requirements.txt` :
```bash
pip install -r requirements.txt
```

## Logging

Les logs sont enregistrés dans le dossier `logs/` à la racine du projet. Deux fichiers sont générés quotidiennement :
*   `app_YYYYMMDD.log` : logs généraux (INFO, DEBUG, WARNING)
*   `errors_YYYYMMDD.log` : logs d'erreur (ERROR)

La configuration se trouve dans `src/helpers/logger.py`.

## Tests

Des tests unitaires peuvent être ajoutés dans un dossier `tests/`. Pour l'instant, vous pouvez tester manuellement les endpoints via Swagger UI à l'adresse [http://localhost:5000/docs](http://localhost:5000/docs).

## Contribution

Les contributions sont les bienvenues. Veuillez suivre les bonnes pratiques :
1.  Créez une branche pour chaque fonctionnalité
2.  Commentez votre code si nécessaire
3.  Assurez-vous que les tests passent
4.  Mettez à jour la documentation si besoin

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---
*Remarque : Ce README est évolutif. N'hésitez pas à l'enrichir au fur et à mesure de l'avancement du projet.*
