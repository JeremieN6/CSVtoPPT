# CSV ➜ PPT SaaS

Ce dépôt contient un pipeline complet pour transformer un dataset CSV/XLSX en présentation PowerPoint prête à être partagée.

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

- `GET /health` → vérifie que l’API répond.
- `POST /generate-report` → attend un fichier `file`, optionnellement `title`, `theme`, `use_ai`, `api_key`. Retourne un flux PPTX et la liste des warnings dans l’entête `X-Report-Warnings`.

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