from __future__ import annotations

import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from game import apply_action, available_actions, current_room, new_game_state, render_map, stats


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "beahero-dev-secret")


def get_state() -> dict:
    state = session.get("game_state")
    if not state:
        state = new_game_state()
        session["game_state"] = state
    return state


def present_state(state: dict) -> dict:
    return {
        "room": current_room(state),
        "actions": available_actions(state),
        "map_text": render_map(state),
        "log": list(reversed(state["log"])),
        "stats": [{"label": label, "value": str(value)} for label, value in stats(state)],
        "won": state["flags"]["won"],
        "game_over": state["flags"]["game_over"],
    }


@app.get("/")
def index():
    return render_template("index.html", initial_state=present_state(get_state()))


@app.get("/api/state")
def api_state():
    return jsonify(present_state(get_state()))


@app.post("/api/action")
def api_action():
    payload = request.get_json(silent=True) or request.form
    state = get_state()
    session["game_state"] = apply_action(state, payload["action"])
    return jsonify(present_state(session["game_state"]))


@app.post("/api/restart")
def api_restart():
    session["game_state"] = new_game_state()
    return jsonify(present_state(session["game_state"]))


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
