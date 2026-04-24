from __future__ import annotations

import os

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from game import (
    apply_action,
    available_actions,
    current_room,
    new_game_state,
    pick_lang,
    present_log,
    render_map_html,
    stats,
    ui_text,
)


app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "beahero-dev-secret")


def get_state() -> dict:
    state = session.get("game_state")
    if not state:
        state = new_game_state()
        session["game_state"] = state
    return state


def get_lang() -> str:
    lang = pick_lang(session.get("lang"))
    session["lang"] = lang
    return lang


def present_state(state: dict, lang: str | None = None) -> dict:
    lang = pick_lang(lang or get_lang())
    return {
        "room": current_room(state, lang),
        "actions": available_actions(state, lang),
        "map_html": render_map_html(state),
        "log": present_log(state, lang),
        "stats": [{"label": label, "value": str(value)} for label, value in stats(state, lang)],
        "won": state["flags"]["won"],
        "game_over": state["flags"]["game_over"],
        "ui": ui_text(lang),
    }


@app.get("/")
def index():
    initial_state = present_state(get_state())
    return render_template("index.html", initial_state=initial_state)


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


@app.post("/api/lang")
def api_lang():
    payload = request.get_json(silent=True) or request.form
    lang = pick_lang(payload.get("lang"))
    session["lang"] = lang
    return jsonify(present_state(get_state(), lang))


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
