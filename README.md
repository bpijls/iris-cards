# Iris Deck

A printable card set for teaching **decision tree classifiers** by hand, using a
24-card subset of R.A. Fisher's Iris dataset (8 specimens per species, spread
across the sepal-length range).

Each card is styled like a Pokémon card:

- **Species** name on top (`setosa`, `versicolor`, `virginica`)
- **Flower artwork** (botanical watercolour, generated with the vonk `image` model)
- **Stats** below: sepal length/width, petal length/width (cm)
- Colour-coded border per species

## Files

| File | Purpose |
|---|---|
| `index.html` | The card-set webpage (filter by species, print to A4 — 3 cards/row) |
| `build.py` | Selects the subset, generates images via vonk, writes `data.js` / `data.json` |
| `iris_raw.csv` | Full source dataset (150 rows) |
| `images/` | Generated flower artwork, one PNG per card |
| `data.js` / `data.json` | The 24 selected specimens with their measurements |

## Regenerate

Requires `VONK_BASE_URL` and `VONK_API_KEY` in `.env` (see `.env.example`).

```bash
python3 build.py all          # all species (skips images that already exist)
python3 build.py setosa       # one species
rm images/*.png && python3 build.py all   # force fresh art
```

## Serve it

Runs as an nginx container behind the host's Caddy Docker Proxy:

```bash
cp .env.example .env      # adjust APP_DOMAIN / CADDY_NETWORK if needed
docker compose up -d
```

Caddy auto-routes `APP_DOMAIN` (set in `.env`) to the container via
the labels in `docker-compose.yml`. `nginx.conf` blocks `build.py`, `*.md`,
`.venv/` and dotfiles from being served. For local access without Caddy,
uncomment the `ports:` block and hit `http://localhost:${HOST_PORT}`.

## Use in class

1. Print `index.html` (browser → Print), cut out the 24 cards.
2. Students repeatedly pick a feature and a threshold, split the pile in two,
   and check class purity — building the tree physically.
3. Compare the hand-grown tree to `sklearn.tree.DecisionTreeClassifier`.
