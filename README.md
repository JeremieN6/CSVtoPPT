# CSV ➜ PPT SaaS — v2.0.0

Ce dépôt contient un pipeline complet pour transformer un dataset CSV/XLSX en présentation PowerPoint prête à être partagée.

**Phase 1 (v1.0.0)** : Modules A–G développés et fonctionnels  
**Phase 2 (v2.0.0)** : Fonctionnalités avancées en cours de développement

- Modules A–E : ingestion, analyse, visualisations et génération de slides en Python.
- Module F : API FastAPI orchestrant le pipeline et retournant le PPTX.
- Module G : frontend Vue 3 + Tailwind + Flowbite pour déclencher la génération depuis le navigateur.

---

## ✨ Fonctionnalités principales

- Upload/drag & drop de fichiers CSV ou XLSX.
- Formulaire minimal pour nommer le rapport et choisir une palette.
- Appel `POST /generate-report` (FastAPI) en multipart/form-data.
- Loader, bannière d’erreur et affichage des avertissements retournés par l’API.
- Téléchargement direct du fichier PPTX généré.
- Section Module G intégrée dans la landing BabyDose (`LP_ReportGenerator`) pour garder le style historique.

---

## 🧱 Stack

- **Frontend** : Vite + Vue 3 (Composition API), Tailwind CSS 3.4, Flowbite UI.
- **Backend** : FastAPI, pandas, matplotlib, python-pptx (voir `backend/`).
- **Build** : `vite build` pour le frontend, `uvicorn backend.main:app` pour l’API.

---

## 🚀 Démarrage rapide

```bash
git clone https://github.com/<votre-utilisateur>/csvtoppt.git
cd csvtoppt

# Frontend
npm install
npm run dev

# Backend (dans un autre terminal)
uvicorn backend.main:app --reload
```

Par défaut, le frontend cible `http://localhost:8000`. Vous pouvez adapter via `VITE_API_BASE_URL` dans un fichier `.env` à la racine.

---

## 🧪 Endpoints utiles

- `GET /health` → vérifie que l'API répond.
- `POST /generate-report` → attend un fichier `file`, optionnellement `title`, `theme`, `use_ai`, `api_key`. Retourne un flux PPTX et la liste des warnings dans l'entête `X-Report-Warnings`.

---

## 🗺️ Roadmap Phase 2

### Phase 2.A — IA Avancée
- **Module H (v2.1.0)** : Génération IA de textes intelligents pour chaque slide
- **Module I (v2.2.0)** : Création de thèmes PPT gérés en Python (Corporate, Minimal, Creative…)
- **Module J (v2.3.0)** : Orchestration complète dans un fichier pipeline propre

### Phase 2.B — Production-ready
- **Module K (v2.4.0)** : Système de logs centralisé (backend + Python + pipeline)
- **Module N (v2.5.0)** : Observabilité & erreurs proprement gérées (retours JSON + logs)

### Phase 2.C — Expérience utilisateur
- **Module L (v2.6.0)** : Dashboard utilisateur (historique, derniers fichiers générés)
- **Module M (v2.7.0)** : Ajout d'options avant génération (sélection de colonnes, choix du style IA, choix du thème PPT)

### Phase 2.D — Industrialisation
- **Module O (v2.8.0)** : Architecture multi-worker (génération PPT dans un job séparé)

---

## 📂 Arborescence condensée

```
frontend/
 ├─ index.html
 ├─ public/
 └─ src/
	 ├─ App.vue
	 ├─ components/FileUploader.vue
	 ├─ main.js
	 └─ style.css
backend/
 ├─ main.py
 ├─ modules/
 └─ services/
```

---

## 🤝 Contribution

1. Forkez le dépôt.
2. Créez une branche `feature/ma-feature`.
3. Ajoutez vos tests et gardez le frontend isolé (aucune logique métier côté Vue).
4. Ouvrez une Pull Request détaillant le scope et les vérifications effectuées.

---

## � Licence

MIT © 2025 — Utilisation libre pour vos propres expérimentations SaaS.