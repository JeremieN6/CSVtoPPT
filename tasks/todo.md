# tasks/todo.md — Task Tracker

> Utilisé par Claude Code pour planifier et suivre les tâches en cours.
> Créer une nouvelle section par tâche. Ne pas supprimer les sections terminées.

---

## Format

```
### [DATE] — Titre de la tâche

**Objectif** : Description courte.

**Plan** :
- [ ] Étape 1
- [ ] Étape 2
- [ ] Vérification

**Résultat** :
*(Rempli une fois la tâche terminée)*
```

---

## Tâches

### [2026-05-15] — Créer un skill modern frontend design

**Objectif** : Ajouter un skill réutilisable pour guider la conception d'interfaces frontend modernes dans ce workspace.

**Plan** :
- [x] Définir le scope et la structure du skill à partir des consignes Copilot et du format `SKILL.md`
- [x] Créer le skill workspace dans `.github/skills/modern-frontend-design/SKILL.md`
- [x] Vérifier la structure, le frontmatter et la clarté des déclencheurs d'usage

**Résultat** :
Draft validé dans `.github/skills/modern-frontend-design/SKILL.md` avec frontmatter correct, workflow réutilisable, critères de qualité, logique de décision et exemples de prompts. Une confirmation utilisateur peut encore préciser si le skill doit être davantage orienté Vue/Tailwind ou rester framework-agnostic.
