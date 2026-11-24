# Mise à jour portefeuille — ordre à suivre

Structure du zip = structure du repo GitHub (copie les fichiers aux mêmes chemins).

| # | Fichier | Où | Action |
|---|---------|----|--------|
| 1 | Exportation_de_transactions.csv | racine | déjà fait ✅ |
| 2 | parse_csv.py | racine | Créer |
| 3 | fetch.py | racine | Remplacer |
| 4 | .github/workflows/update.yml | .github/workflows/ | Remplacer |
| 5 | Actions → Mise à jour → Run workflow | GitHub | Lancer, vérifier les logs |
| 6 | index_patch/bloc1_parser_csv_xirr_dragdrop.js | index.html | Remplacer le bloc `function pcsv(t){` … `rd.readAsText(fl)};` |
| 7 | index_patch/bloc2_kpi_xirr.js | index.html | Remplacer la ligne `document.getElementById("kp").innerHTML=` (celle avec « Gain / perte ») |
| 8 | index_patch/bloc3_fetch_portfolio.js | index.html | Remplacer la ligne `fetch("data/portfolio.json` |

Logs attendus à l'étape 5 :
- Job portfolio : `OK 17 positions, 128 tx, 42 flux cash`
- Job prices : `OK 20/23, manquants: ['SPCX']` (ou similaire)

Commits conseillés : un par fichier / par bloc (retour arrière facile via History → Revert).
Fais les étapes 1-5 d'abord, valide, PUIS 6-8 (de préférence sur ordinateur).
Assure-toi que le dossier `data/` existe dans le repo.
