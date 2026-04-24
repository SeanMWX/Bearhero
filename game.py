from __future__ import annotations

from copy import deepcopy
from html import escape
import random


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
        "map_pos": (2, 2),
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
        "map_pos": (2, 8),
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
        "map_pos": (28, 2),
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
        "map_pos": (2, 14),
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
        "map_pos": (28, 8),
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
        "map_pos": (28, 14),
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


MAP_STYLE = {
    "room_width": 11,
    "room_height": 4,
    "padding_x": 2,
    "padding_y": 2,
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
    "craft_coat": {"en": "Sew a padded coat", "zh": "缝制护身棉衣"},
    "craft_charm": {"en": "Thread a scavenger charm", "zh": "串起拾荒护符"},
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
    "descend_left": {"en": "Take the left passage", "zh": "走左侧通道"},
    "descend_right": {"en": "Take the right passage", "zh": "走右侧通道"},
    "loot_ruin": {"en": "Search the chamber", "zh": "搜索房间"},
    "camp_ruin": {"en": "Catch your breath", "zh": "停下喘息"},
    "fight_ruin": {"en": "Challenge the shadow", "zh": "迎战阴影"},
    "claim_banner": {"en": "Claim the fallen banner", "zh": "拾起倒下的旗帜"},
    "move:gate:return": {"en": "Leave the ruin", "zh": "离开废墟"},
    "move:forest:return": {"en": "Step back into the woods", "zh": "退回树林"},
    "rest:well": {"en": "Sit and recover", "zh": "坐下恢复"},
    "move:path:return": {"en": "Retreat to the path", "zh": "退回旧径"},
}


EQUIPMENT_DEFS = {
    "spear": {
        "label": {"en": "Spear", "zh": "长矛"},
        "craft_action": "craft_spear",
        "craft_room": "hut",
        "cost": {"scrap": 2},
        "message_key": "craft_spear",
        "bonuses": {"attack": 1},
    },
    "torch": {
        "label": {"en": "Torch", "zh": "火把"},
        "craft_action": "craft_torch",
        "craft_room": "hut",
        "cost": {"scrap": 1, "wood": 1},
        "message_key": "craft_torch",
        "bonuses": {"fire_cap": 1},
    },
    "coat": {
        "label": {"en": "Padded Coat", "zh": "护身棉衣"},
        "craft_action": "craft_coat",
        "craft_room": "hut",
        "cost": {"scrap": 1, "wood": 2},
        "message_key": "craft_coat",
        "bonuses": {"defense": 1},
    },
    "charm": {
        "label": {"en": "Scavenger Charm", "zh": "拾荒护符"},
        "craft_action": "craft_charm",
        "craft_room": "well",
        "cost": {"scrap": 1, "herbs": 1},
        "message_key": "craft_charm",
        "bonuses": {"loot": 1},
    },
}


ROGUELIKE_RUN_CONFIG = {
    "mode": "surface-expedition",
    "seed_min": 1000,
    "seed_max": 9999,
    "starting_depth": 1,
    "threat_per_day": 1,
    "depth_goal": 3,
}


RUIN_CHAMBERS = {
    "storehouse": {
        "name": {"en": "Storehouse", "zh": "储藏间"},
        "title": {"en": "A cracked storehouse full of splinters and old crates", "zh": "一间堆满裂木箱和碎屑的储藏间"},
        "description": {
            "en": "Dusty shelves lean against the wall. Something useful may still be buried here.",
            "zh": "落灰的木架斜靠在墙边，废墟里也许还埋着能用的东西。",
        },
        "action_text": {
            "en": "You can search the room, push deeper, or turn back while the route is still clear.",
            "zh": "你可以搜索房间、继续深入，或者趁退路还清楚时折返。",
        },
        "action": "loot_ruin",
        "reward_table": {"scrap": (1, 2), "herbs": (0, 1)},
        "message_key": "loot_ruin",
    },
    "camp": {
        "name": {"en": "Ash Camp", "zh": "灰烬营地"},
        "title": {"en": "An abandoned camp ringed with cold ash", "zh": "一处被冷灰围住的废弃营地"},
        "description": {
            "en": "Someone stopped here before you. The fire is dead, but the ground is momentarily safe.",
            "zh": "有人比你更早在这里停留过。火堆早已熄灭，但这里暂时还算安全。",
        },
        "action_text": {
            "en": "You can steady yourself here before the next descent.",
            "zh": "你可以在这里先稳住呼吸，再继续往下。",
        },
        "action": "camp_ruin",
        "message_key": "camp_ruin",
    },
    "forge": {
        "name": {"en": "Old Forge", "zh": "旧熔炉"},
        "title": {"en": "A forge chamber still smelling faintly of hot iron", "zh": "一间还残留着铁腥味的旧熔炉室"},
        "description": {
            "en": "Collapsed racks and shattered molds litter the floor, but good scrap still hides in the slag.",
            "zh": "坍塌的支架和碎模具铺了一地，但渣堆里仍旧埋着不错的废料。",
        },
        "action_text": {
            "en": "This room favors anyone willing to dig with dirty hands.",
            "zh": "这里只偏爱那些肯把手伸进灰里的拾荒者。",
        },
        "action": "loot_ruin",
        "reward_table": {"scrap": (2, 3)},
        "message_key": "loot_ruin",
    },
    "lair": {
        "name": {"en": "Shadow Lair", "zh": "阴影巢穴"},
        "title": {"en": "The dark here feels occupied", "zh": "这里的黑暗像是被什么东西占住了"},
        "description": {
            "en": "Fresh scratches bite across the stone. Something living waits in the chamber ahead.",
            "zh": "新鲜的抓痕划过石面，前面的房间里显然还藏着活物。",
        },
        "action_text": {
            "en": "If you mean to keep descending, something has to give first.",
            "zh": "如果你想继续深入，得先把这里的东西解决掉。",
        },
        "action": "fight_ruin",
        "enemy": "beast",
        "message_key": "fight_ruin",
    },
    "sanctuary": {
        "name": {"en": "Quiet Shrine", "zh": "寂静祠堂"},
        "title": {"en": "A shrine chamber where the dust lies strangely still", "zh": "一间连灰尘都显得过于安静的祠堂"},
        "description": {
            "en": "The walls here keep the noise down. Even fear settles differently in this chamber.",
            "zh": "这里的墙壁压低了一切声音，就连恐惧都像被放慢了一拍。",
        },
        "action_text": {
            "en": "If you need one calm breath before the next floor, this is the place for it.",
            "zh": "如果你想在下层之前换一口稳气，这里正适合停一下。",
        },
        "action": "camp_ruin",
        "message_key": "camp_ruin",
    },
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
    "craft_coat": {
        "en": "You stitch together a padded coat from scrap cloth and old cord.",
        "zh": "你用旧布和绳线缝出一件护身棉衣，至少能替你挡下一些擦伤。",
    },
    "craft_charm": {
        "en": "You string wire, nails, and herb stems into a scavenger charm for luck.",
        "zh": "你把铁丝、旧钉和草茎串成一枚拾荒护符，给自己添一点运气。",
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
    "loot_ruin": {
        "en": "You pry useful fragments out of the ruin and stash them for the climb.",
        "zh": "你从废墟里撬出一些还能用的碎件，塞进包里留着继续下探。",
    },
    "camp_ruin": {
        "en": "You slow your breathing and let the chamber settle around you for a moment.",
        "zh": "你放慢呼吸，让四周的黑暗暂时沉下去，给自己争出片刻喘息。",
    },
    "fight_ruin": {
        "en": "You step forward and let the chamber's owner come to you.",
        "zh": "你主动向前一步，等着房间里的东西自己扑过来。",
    },
    "descend_ruin": {
        "en": "You descend another layer into the ruin. The route behind you feels thinner.",
        "zh": "你又向废墟深处下降了一层，身后的退路也跟着变得更细了。",
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
    "gear": {},
    "run": {},
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
    state = deepcopy(DEFAULT_STATE)
    seed = random.randint(ROGUELIKE_RUN_CONFIG["seed_min"], ROGUELIKE_RUN_CONFIG["seed_max"])
    state["gear"] = {gear_id: False for gear_id in EQUIPMENT_DEFS}
    state["run"] = {
        "mode": ROGUELIKE_RUN_CONFIG["mode"],
        "seed": seed,
        "depth": ROGUELIKE_RUN_CONFIG["starting_depth"],
        "threat": 1,
        "ruin_path": [],
        "ruin_branches": [],
        "cleared_depths": [],
    }
    branches = build_ruin_branches(seed)
    state["run"]["ruin_path"] = [branches["start"]]
    state["run"]["ruin_branches"] = branches["choices"]
    return state


def room_name(room_id: str, lang: str) -> str:
    return text(ROOMS[room_id]["name"], lang)


def room_title(room_id: str, lang: str) -> str:
    return text(ROOMS[room_id]["title"], lang)


def enemy_name(enemy: dict, lang: str) -> str:
    return text(enemy["name"], lang)


def gear_bonus(state: dict, bonus_key: str) -> int:
    total = 0
    for gear_id, owned in state["gear"].items():
        if owned:
            total += EQUIPMENT_DEFS[gear_id]["bonuses"].get(bonus_key, 0)
    return total


def can_craft_equipment(state: dict, gear_id: str) -> bool:
    equipment = EQUIPMENT_DEFS[gear_id]
    if state["gear"][gear_id]:
        return False
    if state["location"] != equipment["craft_room"]:
        return False
    return all(state[resource] >= cost for resource, cost in equipment["cost"].items())


def crafted_equipment_actions(state: dict, lang: str) -> list[dict]:
    actions = []
    for gear_id, equipment in EQUIPMENT_DEFS.items():
        if can_craft_equipment(state, gear_id):
            actions.append(localize_action(equipment["craft_action"], equipment["craft_action"], lang))
    return actions


def build_ruin_route(seed: int) -> list[str]:
    branches = build_ruin_branches(seed)
    return [branches["start"], *[pair[0] for pair in branches["choices"]]]


def build_ruin_branches(seed: int) -> dict[str, object]:
    chamber_ids = sorted(RUIN_CHAMBERS)
    rng = random.Random(seed)
    start = rng.choice(chamber_ids)
    choices: list[tuple[str, str]] = []
    previous = start
    for _ in range(ROGUELIKE_RUN_CONFIG["depth_goal"] - 1):
        pool = [chamber_id for chamber_id in chamber_ids if chamber_id != previous]
        left = rng.choice(pool)
        right_pool = [chamber_id for chamber_id in pool if chamber_id != left] or pool
        right = rng.choice(right_pool)
        choices.append((left, right))
        previous = left
    return {"start": start, "choices": choices}


def current_ruin_chamber(state: dict) -> dict:
    chamber_id = state["run"]["ruin_path"][state["run"]["depth"] - 1]
    return RUIN_CHAMBERS[chamber_id]


def resolve_chamber_reward(state: dict, chamber: dict) -> dict[str, int]:
    reward_table = chamber.get("reward_table", {})
    if not reward_table:
        return {}
    rng = random.Random(f"{state['run']['seed']}:{state['run']['depth']}:{chamber['name']['en']}")
    resolved = {}
    for resource, bounds in reward_table.items():
        low, high = bounds
        resolved[resource] = rng.randint(low, high)
    return resolved


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
    state["encounter"]["id"] = enemy_id
    threat_bonus = max(state["run"]["threat"] - 1, 0)
    state["encounter"]["hp"] += threat_bonus
    state["encounter"]["damage"] += threat_bonus // 2
    add_log(state, "enemy_intro", intro=localized_param("localized_text", state["encounter"]["intro"]))


def enemy_strikes(state: dict, reduced: bool = False) -> None:
    if not state["encounter"]:
        return
    damage = state["encounter"]["damage"] - gear_bonus(state, "defense") - (1 if reduced else 0)
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


def ruin_branch_label(state: dict, branch_index: int, lang: str) -> str:
    next_depth = state["run"]["depth"]
    chamber_id = state["run"]["ruin_branches"][next_depth - 1][branch_index]
    chamber = RUIN_CHAMBERS[chamber_id]
    tendency = {
        "loot_ruin": {"en": "loot", "zh": "搜刮"},
        "camp_ruin": {"en": "rest", "zh": "休整"},
        "fight_ruin": {"en": "fight", "zh": "战斗"},
    }[chamber["action"]]
    if lang == "zh":
        return f"{text(ACTION_LABELS['descend_left' if branch_index == 0 else 'descend_right'], lang)}：{text(chamber['name'], lang)}（{text(tendency, lang)}）"
    return f"{text(ACTION_LABELS['descend_left' if branch_index == 0 else 'descend_right'], lang)}: {text(chamber['name'], lang)} ({text(tendency, lang)})"


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
        actions.extend(crafted_equipment_actions(state, lang))

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
        actions.extend(crafted_equipment_actions(state, lang))

    if location == "gate":
        actions.append(localize_action("move:forest", "move:forest:return", lang))
        if state["scrap"] >= 2 and not state["flags"]["gate_open"]:
            actions.append(localize_action("open_gate", "open_gate", lang))
        if state["flags"]["gate_open"]:
            actions.append(localize_action("move:ruin", "move:ruin", lang))

    if location == "ruin":
        chamber = current_ruin_chamber(state)
        current_depth = state["run"]["depth"]
        cleared = current_depth in state["run"]["cleared_depths"]
        if not cleared:
            actions.append(localize_action(chamber["action"], chamber["action"], lang))
        if cleared and current_depth < ROGUELIKE_RUN_CONFIG["depth_goal"]:
            actions.append({"key": "descend_left", "label": ruin_branch_label(state, 0, lang)})
            actions.append({"key": "descend_right", "label": ruin_branch_label(state, 1, lang)})
        elif not state["flags"]["won"]:
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
            damage = 2 + gear_bonus(state, "attack")
            enemy["hp"] -= damage
            add_log(
                state,
                "attack_hit",
                enemy_name=localized_param("enemy_name", enemy),
                damage=damage,
            )
            if enemy["hp"] <= 0:
                if enemy.get("id") == "beast":
                    state["scrap"] += 1 + gear_bonus(state, "loot")
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

    elif action in {equipment["craft_action"] for equipment in EQUIPMENT_DEFS.values()}:
        for gear_id, equipment in EQUIPMENT_DEFS.items():
            if equipment["craft_action"] != action:
                continue
            for resource, cost in equipment["cost"].items():
                state[resource] -= cost
            state["gear"][gear_id] = True
            if gear_id == "torch":
                state["fire"] = min(state["fire"] + 1, 4 + gear_bonus(state, "fire_cap"))
            add_log(state, equipment["message_key"])
            break

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

    elif action in {"descend_left", "descend_right"}:
        branch_pair = state["run"]["ruin_branches"][state["run"]["depth"] - 1]
        branch_index = 0 if action == "descend_left" else 1
        state["run"]["depth"] = min(state["run"]["depth"] + 1, ROGUELIKE_RUN_CONFIG["depth_goal"])
        next_chamber = branch_pair[branch_index]
        if len(state["run"]["ruin_path"]) < state["run"]["depth"]:
            state["run"]["ruin_path"].append(next_chamber)
        else:
            state["run"]["ruin_path"][state["run"]["depth"] - 1] = next_chamber
        state["run"]["threat"] += ROGUELIKE_RUN_CONFIG["threat_per_day"]
        add_log(state, "descend_ruin")

    elif action in {"loot_ruin", "camp_ruin", "fight_ruin"}:
        chamber = current_ruin_chamber(state)
        current_depth = state["run"]["depth"]
        if action == "loot_ruin":
            reward = resolve_chamber_reward(state, chamber)
            state["scrap"] += reward.get("scrap", 0) + gear_bonus(state, "loot")
            state["herbs"] += reward.get("herbs", 0)
            add_log(state, chamber["message_key"])
        elif action == "camp_ruin":
            state["health"] = min(state["health"] + 2, state["max_health"])
            state["run"]["threat"] = max(state["run"]["threat"] - 1, 1)
            add_log(state, chamber["message_key"])
        elif action == "fight_ruin":
            add_log(state, chamber["message_key"])
            start_encounter(state, chamber["enemy"])
        if current_depth not in state["run"]["cleared_depths"]:
            state["run"]["cleared_depths"].append(current_depth)

    return state


def render_map(state: dict, lang: str = "en") -> str:
    room_width = MAP_STYLE["room_width"]
    room_height = MAP_STYLE["room_height"]
    max_x = max(room["map_pos"][0] for room in ROOMS.values()) + room_width + MAP_STYLE["padding_x"]
    max_y = max(room["map_pos"][1] for room in ROOMS.values()) + room_height + MAP_STYLE["padding_y"]
    lines = [[" " for _ in range(max_x)] for _ in range(max_y)]

    def draw_char(x: int, y: int, char: str) -> None:
        if 0 <= y < len(lines) and 0 <= x < len(lines[y]):
            lines[y][x] = char

    def draw_room(room_id: str) -> None:
        room = ROOMS[room_id]
        x, y = room["map_pos"]
        top = "-" * room_width
        for offset, char in enumerate(top):
            draw_char(x + offset, y, char)
            draw_char(x + offset, y + room_height - 1, char)
        for inner_row in range(1, room_height - 1):
            draw_char(x, y + inner_row, "|")
            draw_char(x + room_width - 1, y + inner_row, "|")
        label = room_name(room_id, lang)[: room_width - 2].center(room_width - 2)
        marker = "X" if room_id == state["location"] else "O"
        marker_line = marker.center(room_width - 2) if room_id in state["visited"] else " " * (room_width - 2)
        for offset, char in enumerate(label):
            draw_char(x + 1 + offset, y + 1, char)
        if room_id in state["visited"]:
            for offset, char in enumerate(marker_line):
                draw_char(x + 1 + offset, y + 2, char)

    def draw_connection(start_room: str, end_room: str) -> None:
        start_x, start_y = ROOMS[start_room]["map_pos"]
        end_x, end_y = ROOMS[end_room]["map_pos"]
        start_center_x = start_x + room_width // 2
        start_center_y = start_y + 1
        end_center_x = end_x + room_width // 2
        end_center_y = end_y + 1
        if start_center_y == end_center_y:
            for col in range(min(start_center_x, end_center_x) + room_width // 2 - 1, max(start_center_x, end_center_x) - room_width // 2 + 2):
                draw_char(col, start_center_y, "-")
        elif start_center_x == end_center_x:
            for row in range(min(start_center_y, end_center_y) + 1, max(start_center_y, end_center_y)):
                draw_char(start_center_x, row, "|")

    for room_id, neighbors in CONNECTIONS.items():
        for neighbor in neighbors:
            if room_id < neighbor:
                draw_connection(room_id, neighbor)
    for room_id in ROOMS:
        draw_room(room_id)

    return "\n".join("".join(row).rstrip() for row in lines)


def render_map_html(state: dict, lang: str = "en") -> str:
    raw_map = render_map(state, lang)
    lines = [list(row) for row in raw_map.splitlines()]

    html_lines = []
    for row_index, row in enumerate(lines):
        parts = []
        for col_index, char in enumerate(row):
            if char in {"X", "O"}:
                css_class = "map-marker-x" if char == "X" else "map-marker-o"
                parts.append(f'<span class="{css_class}">{escape(char)}</span>')
            else:
                parts.append(escape(char))
        html_lines.append("".join(parts))
    return "\n".join(html_lines)


def current_room(state: dict, lang: str = "en") -> dict:
    if state["location"] == "ruin":
        chamber = current_ruin_chamber(state)
        depth = state["run"]["depth"]
        return {
            "name": f"{text(chamber['name'], lang)} {depth}",
            "title": text(chamber["title"], lang),
            "description": text(chamber["description"], lang),
            "action_text": text(chamber["action_text"], lang),
        }
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
    gear_names = [text(EQUIPMENT_DEFS[name]["label"], lang) for name, owned in state["gear"].items() if owned]
    return [
        (text({"en": "Day", "zh": "天数"}, lang), state["day"]),
        (text({"en": "Run", "zh": "本局"}, lang), f"#{state['run']['seed']}"),
        (text({"en": "Depth", "zh": "层数"}, lang), state["run"]["depth"]),
        (text({"en": "Health", "zh": "生命"}, lang), f"{state['health']}/{state['max_health']}"),
        (text({"en": "Fire", "zh": "火势"}, lang), state["fire"]),
        (text({"en": "Wood", "zh": "木材"}, lang), state["wood"]),
        (text({"en": "Scrap", "zh": "废料"}, lang), state["scrap"]),
        (text({"en": "Herbs", "zh": "草药"}, lang), state["herbs"]),
        (text({"en": "Threat", "zh": "威胁"}, lang), state["run"]["threat"]),
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
