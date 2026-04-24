# Beahero

Beahero is a minimal Python web game inspired by the slow-burn pacing of A Dark Room.

This first prototype focuses on:

- a compact text adventure loop
- an ASCII map built from `-` and `|`
- session-based progress
- a small set of story choices and resources
- combat, damage, and game-over flow
- basic crafting for early gear

## Run

```bash
python3 -m pip install --break-system-packages -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:8888`.

## Run With Docker

```bash
docker compose up --build
```

Then open `http://127.0.0.1:8888`.

## Test With Docker

```bash
docker compose run --rm test
```

## Structure

- `app.py` - Flask entry point
- `game.py` - state, actions, map rendering, story data
- `templates/index.html` - game UI
- `static/style.css` - presentation

## Next Ideas

- equipment and upgrades
- deeper map layers
- branching story arcs
