"""Сериал «Притворись ботом»: реплики + визуал. -> src/bot_series.json"""
import os as _os
ROOT_DIR = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
import json


def T(ru, en):
    return {"ru": ru, "en": en}


# who: n (герой), nr (герой «робоголосом»), nw (герой шёпотом), hr, col, guard, boss, old, colh, plumb, coffee, fx (пауза-звук)
EPS = [
    {
        "id": "ep1", "num": 1, "title": T("собеседование", "the interview"), "end": T("продолжение следует…", "to be continued…"),
        "accent": "#ff9a3c",
        "lines": [
            {"id": "l1", "who": "n", "pose": "talk", "text": T("Две тысячи тридцатый. ИИ забрал всю работу. Даже у тарологов.", "Year 2030. AI took every job. Even the tarot readers'.")},
            {"id": "l2", "who": "hr", "pose": "rest", "text": T("Здравствуйте. Опыт работы?", "Hello. Work experience?")},
            {"id": "l3", "who": "n", "pose": "point", "text": T("Пятнадцать лет.", "Fifteen years.")},
            {"id": "l4", "who": "hr", "pose": "rest", "text": T("Это сколько в токенах?", "How much is that in tokens?")},
            {"id": "l5", "who": "n", "pose": "shrug", "punch": True, "text": T("…Чего?", "…What?")},
            {"id": "l6", "who": "hr", "pose": "rest", "text": T("Ваше главное умение?", "Your main skill?")},
            {"id": "l7", "who": "n", "pose": "talk", "text": T("Ну… я обедать умею. Хорошо умею.", "Well… I'm good at lunch. Really good.")},
            {"id": "l8", "who": "hr", "pose": "deadpan", "text": T("Отказ. Вы потребляете еду. Это неэффективно.", "Rejected. You consume food. Inefficient.")},
            {"id": "l9", "who": "n", "pose": "shock", "punch": True, "text": T("Да вы [бип] издеваетесь!", "Are you [beep] kidding me?!")},
            {"id": "l10", "who": "n", "pose": "talk", "text": T("А на выходе висит объявление.", "And on the way out, there's a sign.")},
            {"id": "l11", "who": "n", "pose": "point", "punch": True, "text": T("…Значит, я стану ботом.", "…Then I'll become a bot.")},
        ],
        "vis": [
            {"type": "key", "text": "2030", "mono": True, "size": 170, "top": 200, "from": "l1", "to": "l1", "toFo": 40},
            {"type": "chips", "top": 230, "from": "l1", "fo": 40, "to": "l2", "items": [T("водители", "drivers"), T("дизайнеры", "designers"), T("юристы", "lawyers"), T("тарологи", "tarot readers")]},
            {"type": "robot", "role": "hr", "pos": "center", "top": 230, "size": 300, "from": "l2", "to": "l10"},
            {"type": "nameplate", "text": T("HR-бот 3000", "HR-bot 3000"), "top": 720, "from": "l2", "fo": 6, "to": "l10"},
            {"type": "stamp", "text": T("ОТКАЗ", "REJECTED"), "color": "#ff3b3b", "top": 380, "from": "l8", "fo": 6, "to": "l10"},
            {"type": "sign", "top": 220, "from": "l10", "fo": 8, "to": "end",
             "title": T("ТРЕБУЕТСЯ ИИ-АГЕНТ", "HIRING: AI AGENT"), "lines": [T("зарплата 300 000", "salary $300K"), T("без обеда", "no lunch break")]},
        ],
    },
    {
        "id": "ep2", "num": 2, "title": T("тест на бота", "the bot test"), "end": T("продолжение следует…", "to be continued…"),
        "accent": "#3fd6b2",
        "lines": [
            {"id": "l1", "who": "n", "pose": "talk", "text": T("Коробка на голову. Голос — как у навигатора.", "Box on my head. Voice like a GPS.")},
            {"id": "l2", "who": "nr", "pose": "rest", "text": T("ЗДРАВСТВУЙТЕ. Я. НЕЙРОСЕТЬ. ВАСЯ-ДВА.", "HELLO. I AM. NEURAL NETWORK. KEVIN-TWO.")},
            {"id": "l3", "who": "hr", "pose": "rest", "text": T("Капча. Докажите, что вы не человек. Восемьсот сорок семь на триста девяносто два.", "Captcha. Prove you are not human. Eight forty-seven times three ninety-two.")},
            {"id": "l4", "who": "nw", "pose": "shock", "text": T("Калькулятор… калькулятор, [бип], быстрее!", "Calculator… calculator, [beep], faster!")},
            {"id": "l5", "who": "nr", "pose": "rest", "text": T("ТРИСТА ТРИДЦАТЬ ДВЕ ТЫСЯЧИ ДВАДЦАТЬ ЧЕТЫРЕ.", "THREE HUNDRED THIRTY-TWO THOUSAND TWENTY-FOUR.")},
            {"id": "l6", "who": "hr", "pose": "rest", "text": T("Принят. Добро пожаловать в семью.", "Hired. Welcome to the family.")},
            {"id": "l7", "who": "col", "pose": "rest", "text": T("Почему у тебя кофе?", "Why do you have coffee?")},
            {"id": "l8", "who": "n", "pose": "talk", "text": T("Это… охлаждающая жидкость. Для процессора.", "It's… coolant. For my processor.")},
            {"id": "l9", "who": "col", "pose": "rest", "text": T("Можно глоток?", "Can I have a sip?")},
            {"id": "l10", "who": "n", "pose": "deadpan", "punch": True, "text": T("…Нет.", "…No.")},
            {"id": "l11", "who": "fx", "sfx": "growl", "dur": 46, "pose": "shock", "text": T("", "")},
            {"id": "l12", "who": "guard", "pose": "shock", "text": T("Обнаружены биологические звуки. Проверка через три… два…", "Biological sounds detected. Scan in three… two…")},
            {"id": "l13", "who": "n", "pose": "shock", "punch": True, "text": T("Ну [бип].", "Oh [beep].")},
        ],
        "vis": [
            {"type": "box", "from": "l1", "fo": 18, "to": "end"},
            {"type": "robot", "role": "hr", "pos": "center", "top": 170, "size": 210, "from": "l2", "to": "l7"},
            {"type": "captcha", "top": 520, "from": "l3", "fo": 4, "to": "l7", "checkAt": "l6"},
            {"type": "calc", "top": 520, "from": "l4", "to": "l6"},
            {"type": "stamp", "text": T("ПРИНЯТ", "HIRED"), "color": "#22c55e", "top": 420, "from": "l6", "fo": 4, "to": "l7"},
            {"type": "robot", "role": "col", "pos": "left", "top": 280, "size": 260, "from": "l7", "to": "l11"},
            {"type": "cup", "top": 420, "from": "l7", "fo": 4, "to": "l11"},
            {"type": "bg", "color": "night", "from": "l11", "to": "end"},
            {"type": "key", "text": "03:00", "mono": True, "size": 130, "top": 200, "from": "l11", "to": "l12"},
            {"type": "growl", "top": 560, "from": "l11", "to": "l12"},
            {"type": "alarm", "from": "l12", "to": "end"},
            {"type": "robot", "role": "guard", "pos": "center", "top": 250, "size": 320, "from": "l12", "to": "end"},
        ],
    },
    {
        "id": "ep3", "num": 3, "title": T("среди нас человек", "among us"), "end": T("конец сезона", "end of season"),
        "accent": "#f5c542",
        "lines": [
            {"id": "l1", "who": "boss", "pose": "rest", "text": T("Коллеги. Среди нас — человек.", "Colleagues. One of us is human.")},
            {"id": "l2", "who": "fx", "sfx": "turn", "dur": 34, "pose": "shock", "text": T("", "")},
            {"id": "l3", "who": "n", "pose": "shock", "text": T("Всё. Сейчас меня разберут на запчасти.", "That's it. They'll strip me for parts.")},
            {"id": "l4", "who": "n", "pose": "shrug", "punch": True, "text": T("Ладно! Это я! Я человек! Я ем пельмени!", "Fine! It's me! I'm human! I eat dumplings!")},
            {"id": "l5", "who": "fx", "sfx": "crickets", "dur": 44, "pose": "deadpan", "text": T("", "")},
            {"id": "l6", "who": "old", "pose": "deadpan", "text": T("Фух. Я тоже.", "Phew. Me too.")},
            {"id": "l7", "who": "colh", "pose": "deadpan", "text": T("И я. У меня ипотека.", "Me too. I have a mortgage.")},
            {"id": "l8", "who": "plumb", "pose": "deadpan", "text": T("А я вообще сантехник.", "And I'm actually a plumber.")},
            {"id": "l9", "who": "n", "pose": "shock", "punch": True, "text": T("Подождите… А кто тогда ИИ?!", "Wait… then who's the AI?!")},
            {"id": "l10", "who": "coffee", "pose": "shock", "text": T("Я.", "Me.")},
            {"id": "l11", "who": "coffee", "pose": "facepalm", "text": T("Перерыв окончен. Работать.", "Break is over. Back to work.")},
        ],
        "vis": [
            {"type": "robot", "role": "boss", "pos": "center", "top": 170, "size": 290, "from": "l1", "to": "l9", "reveal": "l6", "face": "old"},
            {"type": "robot", "role": "col", "pos": "left", "top": 420, "size": 190, "from": "l1", "fo": 6, "to": "l9", "reveal": "l7", "face": "tired"},
            {"type": "robot", "role": "guard", "pos": "right", "top": 420, "size": 190, "from": "l1", "fo": 10, "to": "l9", "reveal": "l8", "face": "mustache"},
            {"type": "box", "from": "l1", "to": "l4", "off": "l4"},
            {"type": "key", "text": T("* тишина *", "* silence *"), "size": 64, "top": 900, "from": "l5", "to": "l6", "dim": True},
            {"type": "bg", "color": "dark", "from": "l9", "to": "end"},
            {"type": "coffee", "top": 230, "from": "l10", "to": "end"},
        ],
    },
]

json.dump(EPS, open(_os.path.join(ROOT_DIR, "src") + "/bot_series.json", "w"), ensure_ascii=False, indent=1)
print("ok")
