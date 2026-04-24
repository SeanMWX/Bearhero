from __future__ import annotations

import os

from flask import Flask, redirect, render_template, request, session, url_for

from game import apply_action, available_actions, current_room, new_game_state, render_map, stats


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "beahero-dev-secret")


def get_state() -> dict:
    state = session.get("game_state")
    if not state:
        state = new_game_state()
        session["game_state"] = state
    return state


@app.get("/")
def index():
    state = get_state()
    return render_template(
        "index.html",
        room=current_room(state),
        actions=available_actions(state),
        map_text=render_map(state),
        log=state["log"],
        stats=stats(state),
        won=state["flags"]["won"],
    )


@app.post("/action")
def action():
    state = get_state()
    session["game_state"] = apply_action(state, request.form["action"])
    return redirect(url_for("index"))


@app.post("/restart")
def restart():
    session["game_state"] = new_game_state()
    return redirect(url_for("index"))


if __name__ == "__main__":
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", "8888"))
    app.run(host=host, port=port, debug=True)
