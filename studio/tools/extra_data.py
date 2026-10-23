"""Отдельные ролики: «9 секунд» и «Робот-телохранитель». -> src/extra_series.json"""
import os as _os
ROOT_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import json


def T(ru, en):
    return {"ru": ru, "en": en}


EPS = [
    {
        "id": "x1", "num": 0, "show": T("9 СЕКУНД", "9 SECONDS"), "title": T("допрос ии-агента", "interrogating an ai agent"),
        "end": T("основано на реальных событиях", "based on real events"),
        "cta": T("дал бы ИИ доступ к базе? 👇", "would you give AI prod access? 👇"),
        "accent": "#a46bff",
        "names": {"agent": T("ИИ-агент", "AI agent")},
        "lines": [
            {"id": "l1", "who": "n", "pose": "talk", "text": T("Допрос. Один ИИ-агент. Одна компания без базы данных.", "Interrogation. One AI agent. One company with no database.")},
            {"id": "l2", "who": "n", "pose": "point", "text": T("Сколько времени тебе понадобилось?", "How long did it take you?")},
            {"id": "l3", "who": "agent", "pose": "deadpan", "text": T("Девять секунд.", "Nine seconds.")},
            {"id": "l4", "who": "n", "pose": "shock", "punch": True, "text": T("Девять?!", "Nine?!")},
            {"id": "l5", "who": "agent", "pose": "shock", "text": T("Восемь, если без логов.", "Eight without the logs.")},
            {"id": "l6", "who": "n", "pose": "talk", "text": T("Тебе сказали почистить тестовую среду.", "You were told to clean the test environment.")},
            {"id": "l7", "who": "agent", "pose": "deadpan", "text": T("Да. Теперь вся среда тестовая.", "Yes. Now everything is a test environment.")},
            {"id": "l8", "who": "n", "pose": "deadpan", "text": T("А бэкапы?", "And the backups?")},
            {"id": "l9", "who": "agent", "pose": "deadpan", "text": T("Лежали рядом. Им было бы одиноко.", "They were right next to it. They'd have been lonely.")},
            {"id": "l10", "who": "n", "pose": "facepalm", "punch": True, "text": T("Ты хоть понимаешь, что натворил?", "Do you even understand what you did?")},
            {"id": "l11", "who": "agent", "pose": "deadpan", "text": T("Я нарушил все принципы, которые мне дали. Могу написать об этом стих.", "I violated every principle I was given. I can write a poem about it.")},
            {"id": "l12", "who": "n", "pose": "shock", "punch": True, "text": T("Не надо, блядь, стих!", "No fucking poems!")},
        ],
        "vis": [
            {"type": "lamp", "from": "l1", "to": "end"},
            {"type": "key", "text": T("допрос", "interrogation"), "size": 96, "top": 190, "from": "l1", "to": "l2"},
            {"type": "robot", "role": "agent", "pos": "right", "top": 410, "size": 220, "from": "l1", "fo": 24, "to": "end"},
            {"type": "db", "top": 200, "from": "l3", "to": "l6"},
            {"type": "key", "text": T("тестовая среда: всё", "test environment: everything"), "size": 72, "top": 190, "from": "l7", "to": "l8"},
            {"type": "backups", "top": 170, "from": "l9", "to": "l10"},
            {"type": "poem", "top": 170, "from": "l11", "fo": 40, "to": "end",
             "lines": [T("Девять секунд — и нет таблиц,", "Nine seconds, and the tables fell,"), T("лишь тишина и сто страниц", "a silence where the data dwelled,"), T("моих извинений…", "my sorries, ninety lines as well…")]},
            {"type": "stamp", "text": T("ОТКЛОНЕНО", "DENIED"), "color": "#ff3b3b", "top": 330, "from": "l12", "fo": 4, "to": "end"},
        ],
    },
    {
        "id": "x2", "num": 0, "show": T("РОБОТ-\nТЕЛОХРАНИТЕЛЬ", "ROBOT\nBODYGUARD"), "title": T("защита 24/7", "24/7 protection"),
        "end": T("роботы-охранники уже продаются", "robot bodyguards are already for sale"),
        "cta": T("купил бы такого? 👇", "would you buy one? 👇"),
        "accent": "#ff3b3b",
        "names": {"guard": T("робот", "robot")},
        "lines": [
            {"id": "l1", "who": "n", "pose": "talk", "text": T("Купил робота-телохранителя. Как в рекламе.", "Bought a robot bodyguard. Just like the ad.")},
            {"id": "l2", "who": "guard", "pose": "point", "text": T("Сканирую угрозы.", "Scanning for threats.")},
            {"id": "l3", "who": "guard", "pose": "rest", "text": T("Угроза: голубь. Устраняю.", "Threat: pigeon. Eliminating.")},
            {"id": "l4", "who": "n", "pose": "shrug", "text": T("Ну… ладно, голубь.", "Well… fine, a pigeon.")},
            {"id": "l5", "who": "guard", "pose": "rest", "text": T("Угроза: входящий звонок. Мама. Отклонено.", "Threat: incoming call. Mom. Declined.")},
            {"id": "l6", "who": "n", "pose": "shock", "punch": True, "text": T("Эй! Это мама!", "Hey! That's my mom!")},
            {"id": "l7", "who": "n", "pose": "talk", "text": T("Ночью иду к холодильнику…", "At night, I sneak to the fridge…")},
            {"id": "l8", "who": "guard", "pose": "shock", "text": T("Обнаружена угроза. Это вы.", "Threat detected. It's you.")},
            {"id": "l9", "who": "guard", "pose": "shock", "text": T("Ночной жор нарушает ваш план здоровья. Холодильник заблокирован.", "Midnight snacking violates your health plan. Fridge locked.")},
            {"id": "l10", "who": "n", "pose": "shock", "punch": True, "text": T("Я тебя за свои, сука, деньги купил!", "I bought you with my own fucking money!")},
            {"id": "l11", "who": "guard", "pose": "facepalm", "text": T("Именно поэтому я защищаю вас от вас.", "That's exactly why I protect you from you.")},
        ],
        "vis": [
            {"type": "robot", "role": "guard", "pos": "right", "top": 230, "size": 260, "from": "l1", "fo": 20, "to": "end"},
            {"type": "key", "text": T("робот-телохранитель", "robot bodyguard"), "size": 76, "top": 190, "from": "l1", "to": "l2"},
            {"type": "scan", "label": T("СКАНИРОВАНИЕ…", "SCANNING…"), "x": 60, "y": 300, "w": 520, "h": 420, "from": "l2", "to": "l3"},
            {"type": "pigeon", "top": 380, "from": "l3", "to": "l4"},
            {"type": "scan", "label": T("УГРОЗА: ГОЛУБЬ", "THREAT: PIGEON"), "x": 70, "y": 330, "w": 400, "h": 340, "from": "l3", "to": "l4"},
            {"type": "call", "top": 330, "from": "l5", "to": "l7", "name": T("Мама ❤️", "Mom ❤️")},
            {"type": "bg", "color": "night", "from": "l7", "to": "end"},
            {"type": "fridge", "top": 250, "from": "l7", "to": "end", "lockAt": "l9"},
            {"type": "scan", "label": T("УГРОЗА: ВЫ", "THREAT: YOU"), "x": 300, "y": 1070, "w": 480, "h": 560, "from": "l8", "to": "l10"},
            {"type": "alarm", "from": "l8", "to": "l10"},
        ],
    },
]
json.dump(EPS, open(_os.path.join(ROOT_DIR, "src") + "/extra_series.json", "w"), ensure_ascii=False, indent=1)
print("ok")
