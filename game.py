from __future__ import annotations

from copy import deepcopy


ROOMS = {
    "hut": {
        "name": "Dark Hut",
        "title": "A dark hut with a weak ember",
        "description": "Wind pushes through the cracks. A cold ember waits in the stove.",
        "action_text": "You can keep the fire alive, search outside, or listen to the woods.",
    },
    "path": {
        "name": "Old Path",
        "title": "A narrow path cut into dead grass",
        "description": "A path runs between the hut and the deeper woods.",
        "action_text": "The path feels safe enough, but something has been moving out here.",
    },
    "forest": {
        "name": "Forest Edge",
        "title": "The treeline watches back",
        "description": "The forest edge is thick with brush and broken branches.",
        "action_text": "There may be wood, herbs, or worse things waiting in the dark.",
    },
    "well": {
        "name": "Dry Well",
        "title": "An old stone well stands open",
        "description": "The well is dry, but the stones around it hide useful scraps.",
        "action_text": "You can search the stones or rest for a moment.",
    },
    "gate": {
        "name": "Rust Gate",
        "title": "A rusted gate blocks the ruin road",
        "description": "Beyond the gate lies a collapsed ruin. The lock is weak but stubborn.",
        "action_text": "A little more preparation should get you through.",
    },
    "ruin": {
        "name": "Broken Hall",
        "title": "A ruin half-swallowed by roots",
        "description": "Inside the ruin, scraps of old banners cling to the walls.",
        "action_text": "This is far enough for a first expedition. Deeper halls can come later.",
    },
}


CONNECTIONS = {
    "hut": ["path"],
    "path": ["hut", "forest", "well"],
    "forest": ["path", "gate"],
    "well": ["path"],
    "gate": ["forest", "ruin"],
    "ruin": ["gate"],
}


MAP_LAYOUT = [
    "  -----------             -----------  ",
    "  |  Dark   |-------------|  Forest |  ",
    "  |   Hut   |             |   Edge  |  ",
    "  -----------             -----------  ",
    "        |                        |      ",
    "        |                        |      ",
    "  -----------             -----------  ",
    "  |   Old   |-------------|  Rust   |  ",
    "  |   Path  |             |  Gate   |  ",
    "  -----------             -----------  ",
    "        |                               ",
    "        |                               ",
    "  -----------             -----------  ",
    "  |   Dry   |             |  Broken |  ",
    "  |   Well  |             |   Hall  |  ",
    "  -----------             -----------  ",
]


ROOM_MARKERS = {
    "hut": (1, 5),
    "forest": (1, 33),
    "path": (7, 5),
    "gate": (7, 33),
    "well": (13, 5),
    "ruin": (13, 33),
}


DEFAULT_STATE = {
    "location": "hut",
    "fire": 1,
    "wood": 2,
    "scrap": 0,
    "herbs": 0,
    "health": 10,
    "max_health": 10,
    "day": 1,
    "visited": ["hut"],
    "gear": {
        "spear": False,
        "torch": False,
    },
    "flags": {
        "heard_whispers": False,
        "gate_open": False,
        "won": False,
        "game_over": False,
    },
    "encounter": None,
    "log": [
        "You wake in a dark hut. The ember is still barely alive.",
        "If the fire dies, courage goes with it.",
    ],
}


def new_game_state() -> dict:
    return deepcopy(DEFAULT_STATE)


def add_log(state: dict, message: str) -> None:
    state["log"].append(message)
    state["log"] = state["log"][-10:]


def visit_room(state: dict, room_id: str) -> None:
    if room_id not in state["visited"]:
        state["visited"].append(room_id)
        add_log(state, f"You discover {ROOMS[room_id]['name']}.")


def move_to(state: dict, destination: str) -> None:
    state["location"] = destination
    visit_room(state, destination)
    add_log(state, ROOMS[destination]["title"] + ".")


def start_encounter(state: dict, enemy_id: str) -> None:
    enemies = {
        "beast": {
            "name": "Starved Beast",
            "hp": 5,
            "damage": 2,
            "intro": "A starved beast slips out of the brush, ribs sharp against its hide.",
        },
        "warden": {
            "name": "Gate Warden",
            "hp": 7,
            "damage": 3,
            "intro": "A rusted watcher lurches awake behind the gate, iron joints shrieking.",
        },
    }
    state["encounter"] = deepcopy(enemies[enemy_id])
    add_log(state, state["encounter"]["intro"])


def enemy_strikes(state: dict, reduced: bool = False) -> None:
    if not state["encounter"]:
        return
    damage = state["encounter"]["damage"] - (1 if reduced else 0)
    damage = max(damage, 0)
    state["health"] = max(state["health"] - damage, 0)
    add_log(state, f"The {state['encounter']['name']} hits you for {damage}.")
    if state["health"] == 0:
        state["flags"]["game_over"] = True
        add_log(state, "You collapse into the dark. The run ends here.")


def end_encounter(state: dict, victory_text: str) -> None:
    add_log(state, victory_text)
    state["encounter"] = None


def available_actions(state: dict) -> list[dict]:
    if state["flags"]["game_over"]:
        return [{"key": "restart", "label": "Begin again"}]

    if state["encounter"]:
        actions = [
            {"key": "attack", "label": "Attack"},
            {"key": "brace", "label": "Brace"},
            {"key": "flee", "label": "Flee"},
        ]
        if state["herbs"] > 0 and state["health"] < state["max_health"]:
            actions.append({"key": "use_herb", "label": "Use herb"})
        return actions

    location = state["location"]
    actions: list[dict] = []

    if location == "hut":
        actions.append({"key": "stoke_fire", "label": "Stoke the fire"})
        actions.append({"key": "rest", "label": "Rest until morning"})
        actions.append({"key": "move:path", "label": "Walk to the old path"})
        if not state["flags"]["heard_whispers"]:
            actions.append({"key": "listen", "label": "Listen to the wind"})
        if state["scrap"] >= 2 and not state["gear"]["spear"]:
            actions.append({"key": "craft_spear", "label": "Forge a crude spear"})
        if state["scrap"] >= 1 and state["wood"] >= 1 and not state["gear"]["torch"]:
            actions.append({"key": "craft_torch", "label": "Bind a torch"})

    if location == "path":
        actions.append({"key": "scavenge_path", "label": "Search the roadside"})
        actions.append({"key": "investigate_path", "label": "Investigate the tracks"})
        actions.append({"key": "move:hut", "label": "Return to the hut"})
        actions.append({"key": "move:forest", "label": "Head to the forest edge"})
        actions.append({"key": "move:well", "label": "Check the dry well"})

    if location == "forest":
        actions.append({"key": "gather_wood", "label": "Gather wood"})
        actions.append({"key": "forage", "label": "Forage for herbs"})
        actions.append({"key": "hunt_noise", "label": "Follow the movement in the brush"})
        actions.append({"key": "move:path", "label": "Retreat to the path"})
        if state["fire"] >= 2:
            actions.append({"key": "move:gate", "label": "Push toward the rust gate"})

    if location == "well":
        actions.append({"key": "search_well", "label": "Search the well stones"})
        actions.append({"key": "rest", "label": "Sit and recover"})
        actions.append({"key": "move:path", "label": "Return to the path"})

    if location == "gate":
        actions.append({"key": "move:forest", "label": "Step back into the woods"})
        if state["scrap"] >= 2 and not state["flags"]["gate_open"]:
            actions.append({"key": "open_gate", "label": "Force the rusted gate"})
        if state["flags"]["gate_open"]:
            actions.append({"key": "move:ruin", "label": "Enter the broken hall"})

    if location == "ruin":
        if not state["flags"]["won"]:
            actions.append({"key": "claim_banner", "label": "Claim the fallen banner"})
        actions.append({"key": "move:gate", "label": "Leave the ruin"})

    return actions


def apply_action(state: dict, action: str) -> dict:
    if action == "restart":
        return new_game_state()

    if state["flags"]["game_over"]:
        return state

    if state["encounter"]:
        enemy = state["encounter"]

        if action == "attack":
            damage = 3 if state["gear"]["spear"] else 2
            enemy["hp"] -= damage
            add_log(state, f"You strike the {enemy['name']} for {damage}.")
            if enemy["hp"] <= 0:
                if enemy["name"] == "Starved Beast":
                    state["scrap"] += 1
                    end_encounter(state, "The beast falls. You salvage a metal charm from its collar.")
                else:
                    state["flags"]["gate_open"] = True
                    end_encounter(state, "The warden crashes apart. The gate hangs open behind it.")
            else:
                enemy_strikes(state)
            return state

        if action == "brace":
            add_log(state, "You tighten your stance and wait for the impact.")
            enemy_strikes(state, reduced=True)
            return state

        if action == "use_herb":
            if state["herbs"] > 0:
                state["herbs"] -= 1
                state["health"] = min(state["health"] + 3, state["max_health"])
                add_log(state, "You crush bitter herbs into the wound and keep breathing.")
                enemy_strikes(state, reduced=True)
            return state

        if action == "flee":
            fallback = "path" if state["location"] != "hut" else "hut"
            add_log(state, f"You break away from the {enemy['name']} and run.")
            state["encounter"] = None
            move_to(state, fallback)
            state["health"] = max(state["health"] - 1, 0)
            add_log(state, "You escape, but not cleanly.")
            if state["health"] == 0:
                state["flags"]["game_over"] = True
                add_log(state, "You made it out, then bled out on the road.")
            return state

    if action.startswith("move:"):
        destination = action.split(":", 1)[1]
        if destination in CONNECTIONS[state["location"]]:
            if destination == "gate" and state["fire"] < 2:
                add_log(state, "You turn back. The dark feels too deep without a stronger fire behind you.")
            elif destination == "ruin" and not state["flags"]["gate_open"]:
                add_log(state, "The gate still holds.")
            else:
                move_to(state, destination)
        return state

    if action == "stoke_fire":
        if state["wood"] > 0:
            state["wood"] -= 1
            state["fire"] = min(state["fire"] + 1, 4)
            add_log(state, "You feed the stove. Warmth returns to your hands.")
        else:
            add_log(state, "No wood left. The ember shrinks instead.")
            state["fire"] = max(state["fire"] - 1, 0)

    elif action == "rest":
        state["day"] += 1
        state["fire"] = max(state["fire"] - 1, 0)
        if state["location"] == "well" and state["herbs"] > 0:
            state["herbs"] -= 1
            add_log(state, "You brew a bitter herb tea and recover some nerve.")
            state["fire"] = min(state["fire"] + 1, 4)
        else:
            add_log(state, "You rest through the cold and wake to another grey day.")

    elif action == "listen":
        state["flags"]["heard_whispers"] = True
        add_log(state, "Somewhere beyond the hut, metal scraped stone. You are not alone out there.")

    elif action == "craft_spear":
        state["scrap"] -= 2
        state["gear"]["spear"] = True
        add_log(state, "You lash a knife of scrap to a pole. It should keep the dark at arm's length.")

    elif action == "craft_torch":
        state["scrap"] -= 1
        state["wood"] -= 1
        state["gear"]["torch"] = True
        state["fire"] = min(state["fire"] + 1, 4)
        add_log(state, "You bind a torch and catch it from the stove. The flame steadies your nerve.")

    elif action == "gather_wood":
        state["wood"] += 2
        add_log(state, "You drag back a bundle of wet branches. It will do.")

    elif action == "forage":
        state["herbs"] += 1
        add_log(state, "You find a bitter herb growing under the brush.")

    elif action == "scavenge_path":
        state["scrap"] += 1
        add_log(state, "You dig a bent strip of metal out of the mud.")

    elif action == "investigate_path":
        start_encounter(state, "beast")

    elif action == "hunt_noise":
        start_encounter(state, "beast")

    elif action == "search_well":
        state["scrap"] += 1
        add_log(state, "Between the stones you find old nails and a short iron hook.")

    elif action == "open_gate":
        state["scrap"] -= 2
        start_encounter(state, "warden")

    elif action == "claim_banner":
        state["flags"]["won"] = True
        add_log(state, "You lift the fallen banner from the dust. Beahero has a beginning.")

    return state


def render_map(state: dict) -> str:
    lines = [list(row) for row in MAP_LAYOUT]
    for room_id in state["visited"]:
        row, col = ROOM_MARKERS[room_id]
        marker = "X" if room_id == state["location"] else "O"
        lines[row][col] = marker
    return "\n".join("".join(row) for row in lines)


def current_room(state: dict) -> dict:
    return ROOMS[state["location"]]


def stats(state: dict) -> list[tuple[str, int | str]]:
    return [
        ("Day", state["day"]),
        ("Health", f"{state['health']}/{state['max_health']}"),
        ("Fire", state["fire"]),
        ("Wood", state["wood"]),
        ("Scrap", state["scrap"]),
        ("Herbs", state["herbs"]),
        ("Gear", ", ".join(name for name, owned in state["gear"].items() if owned) or "None"),
        ("Goal", "Claim the banner" if not state["flags"]["won"] else "Banner claimed"),
    ]
