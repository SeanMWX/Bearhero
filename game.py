from __future__ import annotations

from copy import deepcopy
from html import escape


LANGUAGES = ("en", "zh")


def pick_lang(lang: str | None) -> str:
    return lang if lang in LANGUAGES else "en"


def text(value: str | dict[str, str], lang: str) -> str:
    if isinstance(value, dict):
        selected = pick_lang(lang)
        return value.get(selected) or value["en"]
    return value


ROOMS = {
    "hut": {
        "name": {"en": "Dark Hut", "zh": "黑屋"},
        "title": {"en": "A dark hut with a weak ember", "zh": "一间黑暗的小屋，炉中余烬微弱"},
        "description": {
            "en": "Wind pushes through the cracks. A cold ember waits in the stove.",
            "zh": "冷风从裂缝里灌进来，炉膛里还有一点将熄未熄的余烬。",
        },
        "action_text": {
            "en": "You can keep the fire alive, search outside, or listen to the woods.",
            "zh": "你可以添火、外出搜寻，或静听林中的动静。",
        },
    },
    "path": {
        "name": {"en": "Old Path", "zh": "旧径"},
        "title": {"en": "A narrow path cut into dead grass", "zh": "一条压入枯草中的狭窄小径"},
        "description": {
            "en": "A path runs between the hut and the deeper woods.",
            "zh": "这条小径连接着木屋和更深的树林。",
        },
        "action_text": {
            "en": "The path feels safe enough, but something has been moving out here.",
            "zh": "这条路看起来还算安全，但附近显然有什么东西在活动。",
        },
    },
    "forest": {
        "name": {"en": "Forest Edge", "zh": "林缘"},
        "title": {"en": "The treeline watches back", "zh": "树线之外，仿佛有什么正回望着你"},
        "description": {
            "en": "The forest edge is thick with brush and broken branches.",
            "zh": "林缘灌木丛生，折断的树枝散落一地。",
        },
        "action_text": {
            "en": "There may be wood, herbs, or worse things waiting in the dark.",
            "zh": "黑暗里也许有木材、草药，或者更糟的东西在等着你。",
        },
    },
    "well": {
        "name": {"en": "Dry Well", "zh": "枯井"},
        "title": {"en": "An old stone well stands open", "zh": "一口古老的石井敞开着"},
        "description": {
            "en": "The well is dry, but the stones around it hide useful scraps.",
            "zh": "井早已干涸，但井沿石缝间藏着一些有用的零碎。",
        },
        "action_text": {
            "en": "You can search the stones or rest for a moment.",
            "zh": "你可以翻找石缝，或者在这里稍作休息。",
        },
    },
    "gate": {
        "name": {"en": "Rust Gate", "zh": "锈门"},
        "title": {"en": "A rusted gate blocks the ruin road", "zh": "一扇锈蚀的大门挡住了通往废墟的路"},
        "description": {
            "en": "Beyond the gate lies a collapsed ruin. The lock is weak but stubborn.",
            "zh": "门后是一片坍塌的遗迹。锁头已经老旧，却还顽固地撑着。",
        },
        "action_text": {
            "en": "A little more preparation should get you through.",
            "zh": "再多做一点准备，你也许就能闯过去。",
        },
    },
    "ruin": {
        "name": {"en": "Broken Hall", "zh": "破厅"},
        "title": {"en": "A ruin half-swallowed by roots", "zh": "一座被树根吞没大半的残破大厅"},
        "description": {
            "en": "Inside the ruin, scraps of old banners cling to the walls.",
            "zh": "废墟深处，残破的旧旗帜还挂在墙边。",
        },
        "action_text": {
            "en": "This is far enough for a first expedition. Deeper halls can come later.",
            "zh": "第一次探索到这里已经足够，更多深处的秘密可以留待以后。",
        },
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


MAP_LAYOUTS = {
    "en": [
        "  -----------             -----------  ",
        "  | Dark Hut|-------------|Forest Edg|  ",
        "  |         |             |         |  ",
        "  -----------             -----------  ",
        "        |                        |      ",
        "        |                        |      ",
        "  -----------             -----------  ",
        "  | Old Path|-------------|Rust Gate|  ",
        "  |         |             |         |  ",
        "  -----------             -----------  ",
        "        |                               ",
        "        |                               ",
        "  -----------             -----------  ",
        "  | Dry Well|             |BrokenHal|  ",
        "  |         |             |         |  ",
        "  -----------             -----------  ",
    ],
    "zh": [
        "  -----------             -----------  ",
        "  |  黑屋   |-------------|  林缘   |  ",
        "  |         |             |         |  ",
        "  -----------             -----------  ",
        "        |                        |      ",
        "        |                        |      ",
        "  -----------             -----------  ",
        "  |  旧径   |-------------|  锈门   |  ",
        "  |         |             |         |  ",
        "  -----------             -----------  ",
        "        |                               ",
        "        |                               ",
        "  -----------             -----------  ",
        "  |  枯井   |             |  破厅   |  ",
        "  |         |             |         |  ",
        "  -----------             -----------  ",
    ],
}


ROOM_MARKERS = {
    "hut": (2, 7),
    "forest": (2, 35),
    "path": (8, 7),
    "gate": (8, 35),
    "well": (14, 7),
    "ruin": (14, 35),
}


ACTION_LABELS = {
    "restart": {"en": "Begin again", "zh": "重新开始"},
    "attack": {"en": "Attack", "zh": "攻击"},
    "brace": {"en": "Brace", "zh": "招架"},
    "flee": {"en": "Flee", "zh": "撤退"},
    "use_herb": {"en": "Use herb", "zh": "使用草药"},
    "stoke_fire": {"en": "Stoke the fire", "zh": "添火"},
    "rest": {"en": "Rest until morning", "zh": "休息到天亮"},
    "move:path": {"en": "Walk to the old path", "zh": "前往旧径"},
    "listen": {"en": "Listen to the wind", "zh": "倾听风声"},
    "craft_spear": {"en": "Forge a crude spear", "zh": "制作粗制长矛"},
    "craft_torch": {"en": "Bind a torch", "zh": "捆扎火把"},
    "scavenge_path": {"en": "Search the roadside", "zh": "搜索路边"},
    "investigate_path": {"en": "Investigate the tracks", "zh": "调查痕迹"},
    "move:hut": {"en": "Return to the hut", "zh": "回到黑屋"},
    "move:forest": {"en": "Head to the forest edge", "zh": "前往林缘"},
    "move:well": {"en": "Check the dry well", "zh": "查看枯井"},
    "gather_wood": {"en": "Gather wood", "zh": "收集木材"},
    "forage": {"en": "Forage for herbs", "zh": "采集草药"},
    "hunt_noise": {"en": "Follow the movement in the brush", "zh": "追踪灌木中的动静"},
    "move:gate": {"en": "Push toward the rust gate", "zh": "前往锈门"},
    "search_well": {"en": "Search the well stones", "zh": "翻找井沿石缝"},
    "open_gate": {"en": "Force the rusted gate", "zh": "强闯锈门"},
    "move:ruin": {"en": "Enter the broken hall", "zh": "进入破厅"},
    "claim_banner": {"en": "Claim the fallen banner", "zh": "拾起倒下的旗帜"},
    "move:gate:return": {"en": "Leave the ruin", "zh": "离开废墟"},
    "move:forest:return": {"en": "Step back into the woods", "zh": "退回树林"},
    "rest:well": {"en": "Sit and recover", "zh": "坐下恢复"},
    "move:path:return": {"en": "Retreat to the path", "zh": "退回旧径"},
}


GEAR_LABELS = {
    "spear": {"en": "Spear", "zh": "长矛"},
    "torch": {"en": "Torch", "zh": "火把"},
}


ENEMIES = {
    "beast": {
        "name": {"en": "Starved Beast", "zh": "饥饿野兽"},
        "hp": 5,
        "damage": 2,
        "intro": {
            "en": "A starved beast slips out of the brush, ribs sharp against its hide.",
            "zh": "一头饥饿野兽从灌木中钻出，肋骨在皮下清晰可见。",
        },
    },
    "warden": {
        "name": {"en": "Gate Warden", "zh": "守门者"},
        "hp": 7,
        "damage": 3,
        "intro": {
            "en": "A rusted watcher lurches awake behind the gate, iron joints shrieking.",
            "zh": "锈门后，一个锈蚀的守望者猛然苏醒，铁关节发出刺耳尖鸣。",
        },
    },
}


MESSAGES = {
    "wake_intro": {
        "en": "You wake in a dark hut. The ember is still barely alive.",
        "zh": "你在一间黑屋中醒来，炉火余烬还勉强留着一口气。",
    },
    "wake_hint": {
        "en": "If the fire dies, courage goes with it.",
        "zh": "如果火熄了，勇气也会一起熄灭。",
    },
    "discover_room": {
        "en": "You discover {room_name}.",
        "zh": "你发现了{room_name}。",
    },
    "room_title_entry": {
        "en": "{room_title}.",
        "zh": "{room_title}。",
    },
    "enemy_intro": {
        "en": "{intro}",
        "zh": "{intro}",
    },
    "enemy_hits": {
        "en": "The {enemy_name} hits you for {damage}.",
        "zh": "{enemy_name}对你造成了 {damage} 点伤害。",
    },
    "collapse_dark": {
        "en": "You collapse into the dark. The run ends here.",
        "zh": "你倒在黑暗中。这一趟到此为止。",
    },
    "attack_hit": {
        "en": "You strike the {enemy_name} for {damage}.",
        "zh": "你击中了{enemy_name}，造成 {damage} 点伤害。",
    },
    "beast_falls": {
        "en": "The beast falls. You salvage a metal charm from its collar.",
        "zh": "野兽倒下了。你从它的项圈上拆下一枚金属饰片。",
    },
    "warden_falls": {
        "en": "The warden crashes apart. The gate hangs open behind it.",
        "zh": "守门者轰然散架，身后的大门也随之敞开。",
    },
    "brace_wait": {
        "en": "You tighten your stance and wait for the impact.",
        "zh": "你稳住身形，准备硬接这一击。",
    },
    "use_herb": {
        "en": "You crush bitter herbs into the wound and keep breathing.",
        "zh": "你把苦草揉进伤口，勉强稳住呼吸。",
    },
    "flee_enemy": {
        "en": "You break away from the {enemy_name} and run.",
        "zh": "你甩开{enemy_name}，转身逃离。",
    },
    "escape_unclean": {
        "en": "You escape, but not cleanly.",
        "zh": "你逃掉了，但并不轻松。",
    },
    "bled_out": {
        "en": "You made it out, then bled out on the road.",
        "zh": "你勉强逃了出来，却倒在路上失血而亡。",
    },
    "dark_too_deep": {
        "en": "You turn back. The dark feels too deep without a stronger fire behind you.",
        "zh": "你还是退了回来。没有更旺的炉火做后盾，前方的黑暗太深了。",
    },
    "gate_holds": {
        "en": "The gate still holds.",
        "zh": "大门依然紧闭。",
    },
    "stoke_fire": {
        "en": "You feed the stove. Warmth returns to your hands.",
        "zh": "你给炉子添了柴，暖意重新回到手里。",
    },
    "no_wood": {
        "en": "No wood left. The ember shrinks instead.",
        "zh": "木柴已经没有了，余烬反而更暗了一些。",
    },
    "rest_cold": {
        "en": "You rest through the cold and wake to another grey day.",
        "zh": "你在寒意中休息，醒来时又是灰蒙蒙的一天。",
    },
    "rest_tea": {
        "en": "You brew a bitter herb tea and recover some nerve.",
        "zh": "你煮了一壶苦草茶，稍微恢复了些精神。",
    },
    "listen": {
        "en": "Somewhere beyond the hut, metal scraped stone. You are not alone out there.",
        "zh": "木屋外的某处，金属刮擦石头的声音一闪而过。你并不孤单。",
    },
    "craft_spear": {
        "en": "You lash a knife of scrap to a pole. It should keep the dark at arm's length.",
        "zh": "你把一片废铁绑到木杆上，做成一柄长矛。它至少能让黑暗离你远一点。",
    },
    "craft_torch": {
        "en": "You bind a torch and catch it from the stove. The flame steadies your nerve.",
        "zh": "你扎好火把并从炉火中引燃，跳动的火焰让你镇定下来。",
    },
    "gather_wood": {
        "en": "You drag back a bundle of wet branches. It will do.",
        "zh": "你拖回一捆潮湿树枝，勉强还能用。",
    },
    "forage": {
        "en": "You find a bitter herb growing under the brush.",
        "zh": "你在灌木下找到了一株苦草。",
    },
    "scavenge_path": {
        "en": "You dig a bent strip of metal out of the mud.",
        "zh": "你从泥里挖出一截弯曲的金属片。",
    },
    "search_well": {
        "en": "Between the stones you find old nails and a short iron hook.",
        "zh": "你在石缝之间翻出几枚旧钉子和一只短铁钩。",
    },
    "claim_banner": {
        "en": "You lift the fallen banner from the dust. Bearhero has a beginning.",
        "zh": "你从尘土中举起倒下的旗帜。Bearhero 的故事开始了。",
    },
}


UI_TEXT = {
    "page_title": {"en": "Bearhero", "zh": "Bearhero"},
    "eyebrow": {"en": "Bearhero", "zh": "Bearhero"},
    "restart": {"en": "Restart", "zh": "重新开始"},
    "map_heading": {"en": "Map", "zh": "地图"},
    "map_legend": {
        "en": "`X` is your current location. `O` marks places you have visited.",
        "zh": "`X` 表示你当前所在位置，`O` 表示你已到访过的地点。",
    },
    "status_heading": {"en": "Status", "zh": "状态"},
    "actions_heading": {"en": "Actions", "zh": "行动"},
    "aftermath_heading": {"en": "Aftermath", "zh": "后续"},
    "log_heading": {"en": "Log", "zh": "日志"},
    "win_note": {
        "en": "You brought something back from the dark. That is enough for day one.",
        "zh": "你从黑暗中带回了一样东西。第一天，这样就足够了。",
    },
    "noscript": {
        "en": "JavaScript is required for the no-reload interface.",
        "zh": "无刷新交互模式需要启用 JavaScript。",
    },
    "status_updating": {"en": "Updating...", "zh": "更新中..."},
    "status_failed": {"en": "Request failed. Try again.", "zh": "请求失败，请重试。"},
    "lang_en": {"en": "EN", "zh": "EN"},
    "lang_zh": {"en": "中文", "zh": "中文"},
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
        {"key": "wake_intro", "params": {}},
        {"key": "wake_hint", "params": {}},
    ],
}


def new_game_state() -> dict:
    return deepcopy(DEFAULT_STATE)


def room_name(room_id: str, lang: str) -> str:
    return text(ROOMS[room_id]["name"], lang)


def room_title(room_id: str, lang: str) -> str:
    return text(ROOMS[room_id]["title"], lang)


def enemy_name(enemy: dict, lang: str) -> str:
    return text(enemy["name"], lang)


def localized_param(kind: str, value: object) -> dict[str, object]:
    return {"kind": kind, "value": value}


def resolve_params(lang: str, params: dict) -> dict:
    resolved = {}
    for key, value in params.items():
        if isinstance(value, dict):
            kind = value.get("kind")
            if kind == "room_name":
                resolved[key] = room_name(value["value"], lang)
            elif kind == "room_title":
                resolved[key] = room_title(value["value"], lang)
            elif kind == "enemy_name":
                resolved[key] = enemy_name(value["value"], lang)
            elif kind == "localized_text":
                resolved[key] = text(value["value"], lang)
            else:
                resolved[key] = text(value, lang)
        else:
            resolved[key] = value
    return resolved


def render_message(entry: dict | str, lang: str) -> str:
    if isinstance(entry, str):
        return entry
    template = text(MESSAGES[entry["key"]], lang)
    return template.format(**resolve_params(lang, entry.get("params", {})))


def add_log(state: dict, key: str, **params: object) -> None:
    state["log"].append({"key": key, "params": params})
    state["log"] = state["log"][-10:]


def visit_room(state: dict, room_id: str) -> None:
    if room_id not in state["visited"]:
        state["visited"].append(room_id)
        add_log(state, "discover_room", room_name=localized_param("room_name", room_id))


def move_to(state: dict, destination: str) -> None:
    state["location"] = destination
    visit_room(state, destination)
    add_log(state, "room_title_entry", room_title=localized_param("room_title", destination))


def start_encounter(state: dict, enemy_id: str) -> None:
    state["encounter"] = deepcopy(ENEMIES[enemy_id])
    add_log(state, "enemy_intro", intro=localized_param("localized_text", state["encounter"]["intro"]))


def enemy_strikes(state: dict, reduced: bool = False) -> None:
    if not state["encounter"]:
        return
    damage = state["encounter"]["damage"] - (1 if reduced else 0)
    damage = max(damage, 0)
    state["health"] = max(state["health"] - damage, 0)
    add_log(
        state,
        "enemy_hits",
        enemy_name=localized_param("enemy_name", state["encounter"]),
        damage=damage,
    )
    if state["health"] == 0:
        state["flags"]["game_over"] = True
        add_log(state, "collapse_dark")


def end_encounter(state: dict, victory_key: str) -> None:
    add_log(state, victory_key)
    state["encounter"] = None


def localize_action(key: str, label_key: str, lang: str) -> dict:
    return {"key": key, "label": text(ACTION_LABELS[label_key], lang)}


def available_actions(state: dict, lang: str = "en") -> list[dict]:
    lang = pick_lang(lang)

    if state["flags"]["game_over"]:
        return [localize_action("restart", "restart", lang)]

    if state["encounter"]:
        actions = [
            localize_action("attack", "attack", lang),
            localize_action("brace", "brace", lang),
            localize_action("flee", "flee", lang),
        ]
        if state["herbs"] > 0 and state["health"] < state["max_health"]:
            actions.append(localize_action("use_herb", "use_herb", lang))
        return actions

    location = state["location"]
    actions: list[dict] = []

    if location == "hut":
        actions.append(localize_action("stoke_fire", "stoke_fire", lang))
        actions.append(localize_action("rest", "rest", lang))
        actions.append(localize_action("move:path", "move:path", lang))
        if not state["flags"]["heard_whispers"]:
            actions.append(localize_action("listen", "listen", lang))
        if state["scrap"] >= 2 and not state["gear"]["spear"]:
            actions.append(localize_action("craft_spear", "craft_spear", lang))
        if state["scrap"] >= 1 and state["wood"] >= 1 and not state["gear"]["torch"]:
            actions.append(localize_action("craft_torch", "craft_torch", lang))

    if location == "path":
        actions.append(localize_action("scavenge_path", "scavenge_path", lang))
        actions.append(localize_action("investigate_path", "investigate_path", lang))
        actions.append(localize_action("move:hut", "move:hut", lang))
        actions.append(localize_action("move:forest", "move:forest", lang))
        actions.append(localize_action("move:well", "move:well", lang))

    if location == "forest":
        actions.append(localize_action("gather_wood", "gather_wood", lang))
        actions.append(localize_action("forage", "forage", lang))
        actions.append(localize_action("hunt_noise", "hunt_noise", lang))
        actions.append(localize_action("move:path", "move:path:return", lang))
        if state["fire"] >= 2:
            actions.append(localize_action("move:gate", "move:gate", lang))

    if location == "well":
        actions.append(localize_action("search_well", "search_well", lang))
        actions.append(localize_action("rest", "rest:well", lang))
        actions.append(localize_action("move:path", "move:path", lang))

    if location == "gate":
        actions.append(localize_action("move:forest", "move:forest:return", lang))
        if state["scrap"] >= 2 and not state["flags"]["gate_open"]:
            actions.append(localize_action("open_gate", "open_gate", lang))
        if state["flags"]["gate_open"]:
            actions.append(localize_action("move:ruin", "move:ruin", lang))

    if location == "ruin":
        if not state["flags"]["won"]:
            actions.append(localize_action("claim_banner", "claim_banner", lang))
        actions.append(localize_action("move:gate", "move:gate:return", lang))

    return actions


def apply_action(state: dict, action: str) -> dict:
    if action == "restart":
        return new_game_state()

    if action not in {item["key"] for item in available_actions(state)}:
        return state

    if state["flags"]["game_over"]:
        return state

    if state["encounter"]:
        enemy = state["encounter"]

        if action == "attack":
            damage = 3 if state["gear"]["spear"] else 2
            enemy["hp"] -= damage
            add_log(
                state,
                "attack_hit",
                enemy_name=localized_param("enemy_name", enemy),
                damage=damage,
            )
            if enemy["hp"] <= 0:
                if enemy_name(enemy, "en") == "Starved Beast":
                    state["scrap"] += 1
                    end_encounter(state, "beast_falls")
                else:
                    state["flags"]["gate_open"] = True
                    end_encounter(state, "warden_falls")
            else:
                enemy_strikes(state)
            return state

        if action == "brace":
            add_log(state, "brace_wait")
            enemy_strikes(state, reduced=True)
            return state

        if action == "use_herb":
            if state["herbs"] > 0:
                state["herbs"] -= 1
                state["health"] = min(state["health"] + 3, state["max_health"])
                add_log(state, "use_herb")
                enemy_strikes(state, reduced=True)
            return state

        if action == "flee":
            fallback = "path" if state["location"] != "hut" else "hut"
            add_log(state, "flee_enemy", enemy_name=localized_param("enemy_name", enemy))
            state["encounter"] = None
            move_to(state, fallback)
            state["health"] = max(state["health"] - 1, 0)
            add_log(state, "escape_unclean")
            if state["health"] == 0:
                state["flags"]["game_over"] = True
                add_log(state, "bled_out")
            return state

    if action.startswith("move:"):
        destination = action.split(":", 1)[1]
        if destination in CONNECTIONS[state["location"]]:
            if destination == "gate" and state["fire"] < 2:
                add_log(state, "dark_too_deep")
            elif destination == "ruin" and not state["flags"]["gate_open"]:
                add_log(state, "gate_holds")
            else:
                move_to(state, destination)
        return state

    if action == "stoke_fire":
        if state["wood"] > 0:
            state["wood"] -= 1
            state["fire"] = min(state["fire"] + 1, 4)
            add_log(state, "stoke_fire")
        else:
            add_log(state, "no_wood")
            state["fire"] = max(state["fire"] - 1, 0)

    elif action == "rest":
        state["day"] += 1
        state["fire"] = max(state["fire"] - 1, 0)
        if state["location"] == "well" and state["herbs"] > 0:
            state["herbs"] -= 1
            add_log(state, "rest_tea")
            state["fire"] = min(state["fire"] + 1, 4)
        else:
            add_log(state, "rest_cold")

    elif action == "listen":
        state["flags"]["heard_whispers"] = True
        add_log(state, "listen")

    elif action == "craft_spear":
        state["scrap"] -= 2
        state["gear"]["spear"] = True
        add_log(state, "craft_spear")

    elif action == "craft_torch":
        state["scrap"] -= 1
        state["wood"] -= 1
        state["gear"]["torch"] = True
        state["fire"] = min(state["fire"] + 1, 4)
        add_log(state, "craft_torch")

    elif action == "gather_wood":
        state["wood"] += 2
        add_log(state, "gather_wood")

    elif action == "forage":
        state["herbs"] += 1
        add_log(state, "forage")

    elif action == "scavenge_path":
        state["scrap"] += 1
        add_log(state, "scavenge_path")

    elif action == "investigate_path":
        start_encounter(state, "beast")

    elif action == "hunt_noise":
        start_encounter(state, "beast")

    elif action == "search_well":
        state["scrap"] += 1
        add_log(state, "search_well")

    elif action == "open_gate":
        state["scrap"] -= 2
        start_encounter(state, "warden")

    elif action == "claim_banner":
        state["flags"]["won"] = True
        add_log(state, "claim_banner")

    return state


def render_map(state: dict, lang: str = "en") -> str:
    lines = [list(row) for row in MAP_LAYOUTS[pick_lang(lang)]]
    for room_id in state["visited"]:
        row, col = ROOM_MARKERS[room_id]
        marker = "X" if room_id == state["location"] else "O"
        lines[row][col] = marker
    return "\n".join("".join(row) for row in lines)


def render_map_html(state: dict, lang: str = "en") -> str:
    lines = [list(row) for row in MAP_LAYOUTS[pick_lang(lang)]]
    markers = {}
    for room_id in state["visited"]:
        row, col = ROOM_MARKERS[room_id]
        marker = "X" if room_id == state["location"] else "O"
        lines[row][col] = marker
        markers[(row, col)] = marker

    html_lines = []
    for row_index, row in enumerate(lines):
        parts = []
        for col_index, char in enumerate(row):
            if (row_index, col_index) in markers:
                css_class = "map-marker-x" if markers[(row_index, col_index)] == "X" else "map-marker-o"
                parts.append(f'<span class="{css_class}">{escape(char)}</span>')
            else:
                parts.append(escape(char))
        html_lines.append("".join(parts))
    return "\n".join(html_lines)


def current_room(state: dict, lang: str = "en") -> dict:
    room = ROOMS[state["location"]]
    return {
        "name": text(room["name"], lang),
        "title": text(room["title"], lang),
        "description": text(room["description"], lang),
        "action_text": text(room["action_text"], lang),
    }


def stats(state: dict, lang: str = "en") -> list[tuple[str, int | str]]:
    goal_key = "goal_claimed" if state["flags"]["won"] else "goal_active"
    goal_value = {
        "goal_claimed": {"en": "Banner claimed", "zh": "已取得旗帜"},
        "goal_active": {"en": "Claim the banner", "zh": "取得旗帜"},
    }
    gear_names = [text(GEAR_LABELS[name], lang) for name, owned in state["gear"].items() if owned]
    return [
        (text({"en": "Day", "zh": "天数"}, lang), state["day"]),
        (text({"en": "Health", "zh": "生命"}, lang), f"{state['health']}/{state['max_health']}"),
        (text({"en": "Fire", "zh": "火势"}, lang), state["fire"]),
        (text({"en": "Wood", "zh": "木材"}, lang), state["wood"]),
        (text({"en": "Scrap", "zh": "废料"}, lang), state["scrap"]),
        (text({"en": "Herbs", "zh": "草药"}, lang), state["herbs"]),
        (text({"en": "Gear", "zh": "装备"}, lang), ", ".join(gear_names) or text({"en": "None", "zh": "无"}, lang)),
        (text({"en": "Goal", "zh": "目标"}, lang), text(goal_value[goal_key], lang)),
    ]


def ui_text(lang: str) -> dict[str, str]:
    lang = pick_lang(lang)
    return {
        "lang": lang,
        "page_title": text(UI_TEXT["page_title"], lang),
        "eyebrow": text(UI_TEXT["eyebrow"], lang),
        "restart": text(UI_TEXT["restart"], lang),
        "map_heading": text(UI_TEXT["map_heading"], lang),
        "map_legend": text(UI_TEXT["map_legend"], lang),
        "status_heading": text(UI_TEXT["status_heading"], lang),
        "actions_heading": text(UI_TEXT["actions_heading"], lang),
        "aftermath_heading": text(UI_TEXT["aftermath_heading"], lang),
        "log_heading": text(UI_TEXT["log_heading"], lang),
        "win_note": text(UI_TEXT["win_note"], lang),
        "noscript": text(UI_TEXT["noscript"], lang),
        "status_updating": text(UI_TEXT["status_updating"], lang),
        "status_failed": text(UI_TEXT["status_failed"], lang),
        "lang_en": text(UI_TEXT["lang_en"], lang),
        "lang_zh": text(UI_TEXT["lang_zh"], lang),
    }


def present_log(state: dict, lang: str) -> list[str]:
    entries: list[dict | str] = state["log"]
    return [render_message(entry, lang) for entry in reversed(entries)]
