# Portfolio Kevin Nguyen – kevin-nguyen.me

Site statique (HTML/CSS/JS, sans framework ni build). Hébergé sur Netlify, domaine `kevin-nguyen.me` (DNS chez Namecheap).

## Structure
- `site/` — **le site en ligne, source de vérité**. Déployer ce dossier tel quel.
  - `index.html` – accueil (hero, projets, à propos, méthode, planning d'alternance, FAQ, freelance)
  - `sushi-2-go.html`, `hem-8.html`, `cafe-koem.html`, `duckee.html`, `freelance.html` – études de cas
  - `img/` – images WebP · `og.jpg` – image de partage (Open Graph, 1200×627)
- `cv/` – CV une page : `cv.html` rendu en PDF avec Playwright (`node render.js`). Polices TTF dans `cv/fonts/`.
- `tools/` – scripts Python ayant généré la première version du site (`gen.py` + `content.py`) et les couvertures (`covers.py`), plus le gabarit de l'image de partage (`og.html`, `shot.js`).
  ⚠️ Les chemins y sont absolus et des modifications ont ensuite été faites directement dans `site/` (balises Open Graph, titre, portrait v2). **Modifier `site/` directement.**

## Déploiement
Recommandé : connecter ce dépôt à Netlify (Site configuration → Build & deploy → Link repository), *Publish directory* = `site`, pas de commande de build. Chaque push sur `main` redéploie.

## Notes
- Animations en JS natif (IntersectionObserver, scroll), pas de dépendance.
- Polices : Google Fonts (Anton, Instrument Serif, Manrope…) chargées dans le `<head>`.
- Après une modif de `og.jpg` ou des balises `og:*`, rafraîchir le cache LinkedIn via linkedin.com/post-inspector.
