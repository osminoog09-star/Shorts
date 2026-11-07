#!/usr/bin/env python3
"""Source of chapters c2..c8 for «Оумуамуа» (Claude, 07.11.2026) → levels/cN.json.
Shot tuple: (suffix, seed, prompt, kind) kind: 'space' = floating in black outer space (ground/landscape banned), 'scene' = normal.
Beat tuple: (shot_suffix, text, extra-dict)."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPACE_NEG = "landscape, ground, horizon, mountains, desert, planet surface, terrain, boat, sea, water"


def chapter(cid, card, shots, beats):
    out = {"id": cid, "card": card, "shots": [], "beats": []}
    for suf, seed, prompt, kind in shots:
        s = {"id": f"{cid}_{suf}", "seed": seed, "prompt": prompt, "layers": ["dust"]}
        if kind == "space": s["neg"] = SPACE_NEG
        out["shots"].append(s)
    for n, (suf, text, *extra) in enumerate(beats, 1):
        b = {"id": f"{cid}b{n:02d}", "shot": f"{cid}_{suf}", "text": text}
        if extra: b.update(extra[0])
        out["beats"].append(b)
    (HERE / "levels" / f"{cid}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return sum(len(b["text"].split()) for b in out["beats"])


OU = "Оумуамуа"
def al(*xs): return {"alias": list(xs)}


W = {}
W["c2"] = chapter("c2", ["ГЛАВА ВТОРАЯ", "Откуда приходят гости"], [
    ("a", 1201, "the whole solar system seen from far above, planets on thin glowing elliptical orbits around the bright sun, one dark object crossing on an open curved path, majestic", "space"),
    ("b", 1202, "a vast spherical cloud of billions of icy comets surrounding a tiny distant sun, faint blue glow, enormous scale, deep space", "space"),
    ("c", 1203, "two distant star systems separated by an immense black void, a tiny icy fragment drifting between them, loneliness, deep space", "space"),
    ("d", 1204, "a young star surrounded by a dusty protoplanetary disk with forming planets, a giant planet flinging small icy bodies out into space, dramatic", "space"),
    ("e", 1205, "the bright blue white star Vega shining in a dense star field of the constellation Lyra, deep space, sparkling", "space"),
    ("f", 1206, "astronomers in a 1980s observatory office at night with printed star charts and a large telescope visible through a doorway, warm lamp", "scene"),
    ("g", 1207, "a huge modern survey telescope inside an open observatory dome at night pointing at the milky way, red interior lights", "scene"),
    ("h", 1208, "a small dark object moving fast past the earth and the moon, distant sun, sense of speed, motion streak, deep space", "space"),
    ("i", 1209, "an object leaving the solar system toward a cluster of stars in Pegasus, the sun small behind, long glowing trajectory line, deep space", "space"),
    ("j", 1291, "a dark elongated asteroid floating in pitch black interstellar space, faint cold starlight on its edge, no star nearby, melancholic", "space"),
], [
    ("a", "Чтобы понять, почему эта находка так взволновала учёных, нужно вспомнить, как устроена наша Солнечная система."),
    ("a", "Планеты, астероиды и кометы движутся вокруг Солнца по замкнутым орбитам. Они вечно возвращаются. Солнце держит их всех."),
    ("b", "Даже самые далёкие кометы прилетают из облака Оорта. Это огромная ледяная оболочка на краю нашей системы. Но и она принадлежит Солнцу."),
    ("h", f"Орбита {OU} не была замкнутой. Она была открытой кривой — гиперболой. Объект не падал к Солнцу. Он пролетал мимо.", al("Орбита Умуамуа не была замкнутой. Она была открытой кривой — гиперболой. Объект не падал к Солнцу. Он пролетал мимо.")),
    ("h", "Его скорость была слишком велика. Никакая планета не могла так разогнать камень. Он пришёл извне."),
    ("f", "Астрономы ждали таких гостей десятилетиями. Расчёты давно говорили: межзвёздные тела должны существовать. И их должно быть много."),
    ("d", "Когда рождаются планеты, гиганты вроде Юпитера выбрасывают из молодых систем миллиарды ледяных обломков."),
    ("c", "Эти обломки уходят в межзвёздную пустоту. И летят. Миллионы лет. Сотни миллионов лет. Пока случайно не встретят другую звезду."),
    ("f", "Но ни одного такого гостя никто не видел. Они слишком маленькие и слишком тёмные. Их невозможно заметить, пока они не подлетят совсем близко."),
    ("g", "Всё изменилось, когда появились телескопы, которые каждую ночь фотографируют всё небо. Их строили, чтобы защищать Землю от астероидов."),
    ("g", f"Один из них и поймал {OU}. Через сорок дней после того, как гость прошёл ближе всего к Солнцу.", al("Один из них и поймал Умуамуа. Через сорок дней после того, как гость прошёл ближе всего к Солнцу.", "Один из них и поймал Оумуамуа. Через 40 дней после того, как гость прошёл ближе всего к Солнцу.")),
    ("h", "К тому моменту он уже пролетел внутри орбиты Меркурия. Обогнул Солнце. И теперь уходил прочь."),
    ("e", "Он прилетел со стороны созвездия Лиры. Почти оттуда, где на нашем небе сияет яркая Вега."),
    ("e", "Но это совпадение. Сотни тысяч лет назад, когда гость был в тех краях, Веги там ещё не было. Звёзды тоже движутся."),
    ("c", "Откуда он на самом деле, не знает никто. Его родная звезда могла давно погаснуть. Или уйти на другой край галактики."),
    ("f", "Сначала ему дали обозначение кометы. Потом астероида. А потом пришлось придумать новую категорию.", {"quote": "1I/2017 U1"}),
    ("f", "Буква I. Межзвёздный. Номер один. Первый в истории человечества.", al("Буква И. Межзвёздный. Номер один. Первый в истории человечества.")),
    ("i", "Теперь он летит в сторону созвездия Пегаса. В две тысячи двадцать втором году он пересёк орбиту Нептуна.", al("Теперь он летит в сторону созвездия Пегаса. В 2022 году он пересёк орбиту Нептуна.")),
    ("j", "И больше никогда не вернётся. Ни к нам, ни к одному из своих прежних солнц. У него нет дома. Только дорога."),
])

W["c3"] = chapter("c3", ["ГЛАВА ТРЕТЬЯ", "Тень неправильной формы"], [
    ("a", 1301, "a large professional telescope at night under a starry sky on a mountain, laser guide beam, cinematic", "scene"),
    ("b", 1302, "a single tiny point of light among stars seen through a telescope, flickering brightness, dark, minimal, deep space", "space"),
    ("c", 1303, "an extremely elongated dark red cigar shaped asteroid tumbling end over end in black outer space, sunlight on its edge, stars", "space"),
    ("d", 1396, "a flat oval reddish asteroid shaped like a thin smooth pebble, seen from above at an angle, floating alone in black outer space with stars all around it, nothing below it", "space"),
    ("e", 1305, "close-up of a dark reddish rocky surface covered in cosmic dust, irradiated crust, harsh sunlight, black space behind", "space"),
    ("f", 1306, "two asteroids colliding in black outer space, fragments flying apart, bright flash, dramatic", "space"),
    ("g", 1307, "a small infrared space telescope with a gold sunshield orbiting far from earth, stars, deep space", "space"),
    ("h", 1308, "a scientist at night comparing many photographs of a star field on a light table, magnifying glass, warm lamp", "scene"),
    ("i", 1309, "a reddish icy dwarf world in the distant cold outer solar system, faint sun, deep space", "space"),
    ("j", 1390, "a dark elongated asteroid floating in pitch black outer space, tumbling slowly, faint sunlight on its tip, stars, mysterious, lonely", "space"),
], [
    ("a", f"Весь мир бросился смотреть на гостя. Но увидеть {OU} по-настоящему не смог ни один телескоп.", al("Весь мир бросился смотреть на гостя. Но увидеть Умуамуа по-настоящему не смог ни один телескоп.")),
    ("b", "Он был слишком мал и слишком далёк. Даже в самые мощные инструменты он выглядел как одна-единственная точка."),
    ("b", "Всё, что у астрономов было, — это свет. Как ярко точка светится. И как этот блеск меняется со временем."),
    ("h", "И блеск менялся очень странно. За несколько часов точка становилась ярче почти в десять раз. А потом снова тускнела."),
    ("c", "Так бывает, когда вращается тело очень вытянутой формы. Когда оно повёрнуто к нам боком, оно отражает много света. Когда торцом — почти ничего."),
    ("c", "По расчётам выходило, что гость в несколько раз длиннее, чем шире. Возможно, в шесть раз. А может, и больше."),
    ("e", "Ни один известный астероид или комета в Солнечной системе не бывает настолько вытянутым. Это было за пределами всего, что мы знали."),
    ("d", "Позже появилась другая модель. Что, если он не сигара, а плоский блин? Тонкий диск, который вращается и вспыхивает краем."),
    ("d", "Обе формы объясняли блеск. Обе были невероятными. Художники рисовали сигару. Учёные спорили."),
    ("f", "Ещё одна деталь: он не просто вращался, а кувыркался. Беспорядочно, сразу вокруг нескольких осей."),
    ("f", "Такое случается после сильного удара. Возможно, когда-то давно, в своей родной системе, он пережил столкновение."),
    ("e", "Его цвет оказался красноватым. Как у ледяных тел на окраине нашей системы, которые миллиарды лет облучают космические лучи."),
    ("i", "Похоже, он долго странствовал в холоде, и излучение испекло его поверхность в тёмную корку."),
    ("g", "Космический телескоп Спитцер попытался поймать его тепло. И не увидел ничего. Гость оказался слишком мал даже для него."),
    ("g", "Это позволило оценить размер. Примерно от ста до четырёхсот с лишним метров. Как небоскрёб, летящий через пустоту.", al("Это позволило оценить размер. Примерно от 100 до 400 с лишним метров. Как небоскрёб, летящий через пустоту.")),
    ("b", "Маленький. Тёмный. Неправильной формы. Кувыркающийся. Уже этого хватило бы, чтобы назвать его самым странным объектом года."),
    ("j", "Но всё это было только началом. Главная загадка пряталась не в его форме. А в том, как он двигался."),
])

W["c4"] = chapter("c4", ["ГЛАВА ЧЕТВЁРТАЯ", "Ускорение"], [
    ("a", 1401, "a dark elongated asteroid moving away from the bright sun along a glowing trajectory line, a second faint predicted line diverging from it, deep space", "space"),
    ("b", 1402, "the sun shining fiercely in black outer space, solar wind and light rays streaming outward, majestic", "space"),
    ("c", 1403, "an ordinary icy comet near the sun with bright jets of gas shooting from its surface and a glowing coma, deep space", "space"),
    ("d", 1404, "a dark asteroid in sunlight with absolutely no gas and no dust around it, clean sharp silhouette, black space", "space"),
    ("e", 1405, "a scientist's desk at night covered with orbit calculations, curved lines, a laptop with a graph, coffee, lamp, no readable text", "scene"),
    ("f", 1406, "the hubble space telescope floating above the blue earth, stars, deep space", "space"),
    ("g", 1407, "a large professional telescope observatory on a high mountain at dusk, several domes open, purple sky", "scene"),
    ("h", 1408, "a spinning asteroid with small jets of gas pushing it, rotating faster, motion blur, deep space", "space"),
    ("i", 1409, "a giant question mark shape formed by stars and dust in a dark nebula, deep space, mysterious", "space"),
    ("j", 1410, "a tiny dark object disappearing into the black, the sun far behind, stars, melancholic", "space"),
], [
    ("j", "Пока гость уходил, астрономы продолжали следить за ним. Каждую ночь. Хаббл, огромные телескопы в Чили и на Гавайях."),
    ("g", "Они хотели точно рассчитать его путь. Это обычная работа. Законы Ньютона известны больше трёхсот лет.", al("Они хотели точно рассчитать его путь. Это обычная работа. Законы Ньютона известны больше 300 лет.")),
    ("a", "Но точки на снимках не ложились на расчётную кривую. Гость каждый день оказывался чуть дальше, чем должен был."),
    ("e", "Сначала подумали на ошибки измерений. Проверили. Пересчитали. Ошибки не было."),
    ("a", f"{OU} ускорялся. Совсем слабо — примерно на тысячную долю от силы солнечного притяжения. Но ускорялся.", al("Умуамуа ускорялся. Совсем слабо — примерно на тысячную долю от силы солнечного притяжения. Но ускорялся.")),
    ("b", "И это ускорение было направлено от Солнца. Чем ближе к Солнцу, тем сильнее. Как будто Солнце мягко толкало его в спину."),
    ("e", "Летом две тысячи восемнадцатого года статью об этом опубликовал журнал Nature. Один из главных научных журналов мира.", {"say": "Летом две тысячи восемнадцатого года статью об этом опубликовал журнал Нейчер. Один из главных научных журналов мира.", "alias": ["Летом 2018 года статью об этом опубликовал журнал Nature. Один из главных научных журналов мира.", "Летом 2018 года статью об этом опубликовал журнал Нейчер. Один из главных научных журналов мира."]}),
    ("c", "У комет такое бывает. Солнце нагревает лёд, из трещин бьют струи газа. И работают как маленькие реактивные двигатели."),
    ("c", "Самое простое объяснение: гость — это комета. Просто необычная."),
    ("d", "Но у кометы, которую толкают струи, должна быть кома. Облако пыли и газа вокруг ядра. И хвост."),
    ("d", "У гостя не было ни того, ни другого. Самые чувствительные приборы не нашли ни пыли, ни углекислого газа, ни угарного."),
    ("h", "И ещё одна нестыковка. Струи газа почти никогда не бьют ровно. Они закручивают комету. Её вращение меняется."),
    ("h", "Вращение гостя почти не изменилось. Его что-то толкало. Сильно и ровно. Но ничего не было видно."),
    ("f", "Для науки это неприятная ситуация. Есть сила. Есть её след. И нет источника."),
    ("i", "Учёные начали предлагать версии. Одни — осторожные. Другие — настолько смелые, что о них заговорили в новостях по всему миру."),
    ("b", "И самая громкая версия утверждала: этого гостя толкает не газ. А сам солнечный свет."),
])

W["c5"] = chapter("c5", ["ГЛАВА ПЯТАЯ", "Парус"], [
    ("a", 1501, "an old university campus building at night in winter, warm lit windows, snow, quiet, mysterious", "scene"),
    ("b", 1502, "a gigantic ultra thin square solar sail of shimmering silver foil floating in black outer space, sunlight reflecting off it, distant sun", "space"),
    ("c", 1593, "a gigantic ultra thin square solar sail membrane of shimmering silver foil tumbling in black outer space, sunlight flashing off it, science fiction spacecraft, stars", "space"),
    ("d", 1504, "an alien derelict object of unknown technology drifting in black outer space, dark metallic, faint glow, mysterious, stars", "space"),
    ("e", 1505, "a huge radio telescope dish at night under the milky way, green valley, listening to the sky", "scene"),
    ("f", 1506, "many small light sails propelled by powerful laser beams from earth toward distant stars, science fiction concept, deep space", "space"),
    ("g", 1507, "a crowded scientific conference hall with a speaker on stage in front of a large screen showing a starry sky, audience silhouettes", "scene"),
    ("h", 1508, "a stack of newspapers and magazines on a desk with dramatic space covers, morning light, no readable text", "scene"),
    ("i", 1509, "a lone man in a coat standing on a hill at night looking up at the stars, city lights far below, contemplative", "scene"),
    ("j", 1590, "a small broken square solar sail membrane of silver foil with torn edges drifting in black interstellar space, tiny distant sun, science fiction spacecraft wreck, stars", "space"),
], [
    ("a", "Осенью две тысячи восемнадцатого года в Гарварде вышла короткая статья. Её авторы — астрофизик Ави Лёб и его коллега Шмуэль Бялый.", al("Осенью 2018 года в Гарварде вышла короткая статья. Её авторы — астрофизик Ави Лёб и его коллега Шмуэль Бялый.")),
    ("b", "Их идея была простой и пугающей. Свет имеет давление. Слабое, но настоящее. Если предмет очень лёгкий и очень большой, свет может его толкать."),
    ("b", "Так работают солнечные паруса. Люди уже запускали такие аппараты в космос. Тонкая плёнка, которую разгоняет Солнце."),
    ("c", f"Чтобы свет разогнал {OU} так, как это видели телескопы, он должен быть невероятно тонким. Меньше миллиметра в толщину.", al("Чтобы свет разогнал Умуамуа так, как это видели телескопы, он должен быть невероятно тонким. Меньше миллиметра в толщину.")),
    ("c", "Такую вещь природа сделать не умеет. А цивилизация — может."),
    ("d", "Авторы осторожно написали: возможно, это обломок чужой технологии. Сломанный парус, который миллионы лет дрейфует между звёздами."),
    ("d", "Или даже зонд, который прислали к нам специально."),
    ("h", "Через несколько дней об этом писали все. Пришельцы. Инопланетный корабль. Гарвардский профессор считает, что нас посетили."),
    ("e", "Проверить хотели сразу. Ещё в декабре две тысячи семнадцатого года на гостя направили огромный радиотелескоп. Искали сигналы.", al("Проверить хотели сразу. Ещё в декабре 2017 года на гостя направили огромный радиотелескоп. Искали сигналы.")),
    ("e", "Тишина. Ни передачи, ни шума двигателей. Ничего, что можно было бы назвать голосом."),
    ("g", "Большинство учёных отнеслись к идее паруса скептически. Необычные утверждения требуют необычных доказательств. А доказательств не было."),
    ("g", "Лёб не отступал. Он написал книгу. Выступал. Повторял: наука должна допускать и такую возможность, а не отбрасывать её заранее."),
    ("i", "Ирония в том, что он во многом был прав. Само по себе ускорение никто не мог объяснить. Просто большинство не хотело объяснять его пришельцами."),
    ("f", "И в этом же споре родилась другая мысль. Если парус — это так удобно, может, его стоит сделать нам самим?"),
    ("f", "Люди уже обсуждают проекты: крошечные зонды на световых парусах, которые мощные лазеры разгонят к соседним звёздам."),
    ("j", "Если когда-нибудь такой зонд улетит от нас и сломается, где-то в другой системе его тоже назовут загадкой."),
    ("c", "А пока у учёных был выбор. Поверить в парус. Или найти природное тело, которое могло бы вести себя так же."),
])

W["c6"] = chapter("c6", ["ГЛАВА ШЕСТАЯ", "Ледяные версии"], [
    ("a", 1601, "a translucent iceberg of frozen hydrogen floating in black outer space, faint blue glow, starlight, deep space", "space"),
    ("b", 1602, "a giant molecular cloud in deep space, dark dense regions of gas and dust with young stars glowing inside", "space"),
    ("c", 1603, "an icy dwarf planet like Pluto with nitrogen glaciers and a heart shaped plain, distant sun, deep space", "space"),
    ("d", 1604, "a large asteroid impact on an icy dwarf planet, chunks of white ice flying into space, dramatic", "space"),
    ("e", 1605, "a bright white flat slab of nitrogen ice drifting in black outer space, reflecting sunlight, stars", "space"),
    ("f", 1606, "a fluffy porous cloud-like clump of cosmic dust, extremely delicate, floating in black outer space, stars", "space"),
    ("g", 1607, "an icy rock in black outer space with an invisible gentle glow of escaping gas, sunlight, subtle shimmer, stars", "space"),
    ("h", 1608, "cosmic rays striking an icy surface in deep space, tiny bright streaks hitting ice, scientific concept art", "space"),
    ("i", 1609, "a scientist laboratory with a cryogenic chamber, frost on metal, blue light, no readable text", "scene"),
    ("j", 1610, "a reddish elongated rock with a faint icy shimmer floating away into black outer space, stars, calm", "space"),
], [
    ("a", "Первая природная версия звучала почти как фантастика. Что, если гость — это айсберг из замёрзшего водорода?"),
    ("a", "Водородный лёд испаряется, не оставляя видимого следа. Нет пыли. Нет яркого газа. Только невидимая струя, которая мягко толкает тело."),
    ("b", "Такие айсберги могли бы рождаться в самых холодных уголках галактики. В плотных облаках газа, где появляются новые звёзды."),
    ("b", "Но у версии нашёлся слабый пункт. Водородный лёд слишком нежный. В межзвёздной пустоте его быстро испарил бы свет звёзд. Он просто не дожил бы до нас."),
    ("c", "Вторая версия пришла с окраин нашей собственной системы. Посмотрите на Плутон. Его поверхность покрыта ледниками из замёрзшего азота."),
    ("d", "Когда в молодой системе рождаются планеты, такие ледяные миры часто сталкиваются. От них откалываются куски."),
    ("e", "Что, если гость — осколок азотной коры чужого Плутона? Плоский, как плита. Светлый. И очень холодный."),
    ("e", "Азот при испарении тоже почти не виден. А плоская форма объясняет и блеск, и сильный толчок от слабой струи."),
    ("e", "Модель была красивой. Но для неё нужно слишком много азотных обломков в галактике. Хватит ли их — неизвестно."),
    ("f", "Третья версия совсем странная. Гость — это пушистый комок пыли, в сотню раз менее плотный, чем воздух. Почти облако."),
    ("f", "Такую хрупкую вещь солнечный свет и правда может толкать. Но выжила бы она в долгом путешествии — большой вопрос."),
    ("i", "А в две тысячи двадцать третьем году в журнале Nature появилось объяснение, которое многим показалось самым простым.", {"say": "А в две тысячи двадцать третьем году в журнале Нейчер появилось объяснение, которое многим показалось самым простым.", "alias": ["А в 2023 году в журнале Nature появилось объяснение, которое многим показалось самым простым.", "А в 2023 году в журнале Нейчер появилось объяснение, которое многим показалось самым простым."]}),
    ("h", "Гость — обычная ледяная комета. Только за миллионы лет пути космические лучи превратили часть его льда в водород. И водород остался запертым внутри."),
    ("g", "Когда гость подлетел к Солнцу, лёд прогрелся, и запертый водород начал выходить наружу. Тихо. Невидимо. Без пыли."),
    ("g", "Этого хватает, чтобы дать то самое крошечное ускорение. И при этом не оставить следа, который увидели бы телескопы."),
    ("j", "Многие учёные сегодня считают это объяснение самым вероятным. Но проверить его уже нельзя. Гость ушёл слишком далеко."),
    ("j", "Мы так и не узнаем наверняка. И поэтому все взгляды обратились к одному вопросу. Когда прилетит следующий?"),
])

W["c7"] = chapter("c7", ["ГЛАВА СЕДЬМАЯ", "Второй и третий"], [
    ("a", 1701, "a small amateur observatory with a homemade dome on a hill in Crimea at night, starry sky, one lit window", "scene"),
    ("b", 1702, "a fuzzy interstellar comet with a bright coma and a long tail crossing the stars, deep space, cinematic", "space"),
    ("c", 1703, "a telescope in the chilean desert at night under the milky way, clear sky, red dome lights", "scene"),
    ("d", 1704, "an ancient very fast comet with a glowing green coma speeding past the sun, motion streak, deep space", "space"),
    ("e", 1705, "the red planet mars in black space with a bright comet passing near it, a small orbiter spacecraft in the foreground", "space"),
    ("f", 1706, "a huge modern observatory building on a chilean mountain top at sunset, a large telescope, dramatic sky", "scene"),
    ("g", 1707, "a spacecraft waiting in deep space far from earth, solar panels deployed, ready to intercept a comet, stars", "space"),
    ("h", 1708, "the milky way galaxy seen from above with countless stars, an ancient object drifting from the old galactic disk, majestic", "space"),
    ("i", 1709, "a fast probe spacecraft chasing a tiny dark object into interstellar space, long exhaust glow, stars", "space"),
    ("j", 1710, "a new mysterious object approaching the solar system from interstellar darkness, the sun bright ahead, stars", "space"),
], [
    ("a", "Ответ пришёл быстрее, чем ожидали. Летом две тысячи девятнадцатого года. И нашёл гостя не большой институт, а один человек.", al("Ответ пришёл быстрее, чем ожидали. Летом 2019 года. И нашёл гостя не большой институт, а один человек.")),
    ("a", "Астроном-любитель Геннадий Борисов в Крыму. На телескоп, который он собрал сам."),
    ("b", "Второй межзвёздный гость получил имя Борисов. И оказался совсем не похожим на первого."),
    ("b", "У него была кома. Был хвост. Он выглядел как самая обычная комета. Только прилетевшая из другой звёздной системы."),
    ("b", f"Это стало важным выводом. Значит, такие тела бывают разными. И {OU} — не правило, а исключение.", al("Это стало важным выводом. Значит, такие тела бывают разными. И Умуамуа — не правило, а исключение.")),
    ("c", "А первого июля две тысячи двадцать пятого года телескоп системы ATLAS в Чили заметил третьего гостя.", {"say": "А первого июля две тысячи двадцать пятого года телескоп системы Атлас в Чили заметил третьего гостя.", "alias": ["А 1 июля 2025 года телескоп системы ATLAS в Чили заметил третьего гостя.", "А 1 июля 2025 года телескоп системы Атлас в Чили заметил третьего гостя."]}),
    ("d", "Он летел очень быстро. Почти шестьдесят километров в секунду. Быстрее обоих предшественников.", al("Он летел очень быстро. Почти 60 километров в секунду. Быстрее обоих предшественников.")),
    ("h", "Его путь подсказывает, что он мог прийти из древней части галактики. Возможно, он старше нашего Солнца."),
    ("e", "На этот раз за гостем следили не только с Земли. Его снимали аппараты у Марса, мимо которого он пролетал осенью."),
    ("d", "Он вёл себя как комета. Кома, хвост, газ. И всё-таки нашлись те, кто снова спросил: а вдруг?"),
    ("f", "Но главное событие тех лет — не сам гость. В Чили заработала новая обсерватория имени Веры Рубин."),
    ("f", "Она будет снимать всё южное небо каждые несколько ночей. Учёные надеются, что межзвёздных гостей станут находить регулярно."),
    ("g", "А Европейское космическое агентство готовит аппарат, который будет ждать в космосе. Когда появится подходящая цель, он полетит навстречу."),
    ("i", f"Есть даже проекты погони за самим {OU}. Догнать его можно. Но полёт займёт десятилетия.", al("Есть даже проекты погони за самим Умуамуа. Догнать его можно. Но полёт займёт десятилетия.")),
    ("j", "Первый гость застал нас врасплох. Мы увидели его, когда он уже уходил. Следующего мы надеемся встретить заранее."),
    ("j", "И тогда, может быть, мы впервые подлетим к осколку чужой звёздной системы и посмотрим на него вблизи."),
])

W["c8"] = chapter("c8", ["ГЛАВА ВОСЬМАЯ", "Посланник"], [
    ("a", 1801, "white observatory telescope dome on top of a dormant volcano summit at dawn above a sea of clouds, first light, peaceful, wide shot", "scene"),
    ("b", 1802, "the milky way galaxy spanning the whole sky above a quiet mountain, a lone observer silhouette, awe", "scene"),
    ("c", 1803, "a lonely elongated reddish rock drifting through a glowing colorful nebula in deep space, majestic, slow", "space"),
    ("d", 1804, "an alien star system with a red sun and ringed planets seen from far away, ancient, mysterious, deep space", "space"),
    ("e", 1805, "a child looking through a small telescope at night on a balcony, city lights, stars, wonder", "scene"),
    ("f", 1806, "the earth seen from deep space as a tiny pale blue dot in a beam of sunlight, vast darkness", "space"),
    ("g", 1807, "an empty observatory control room at dawn, monitors glowing with star fields, coffee cup, quiet", "scene"),
    ("h", 1808, "countless tiny dark objects drifting between stars of the galaxy, invisible travelers, deep space, poetic", "space"),
    ("i", 1809, "a tiny dark object fading into the black depths of interstellar space, the sun a small bright star far behind, loneliness", "space"),
    ("j", 1810, "a sky full of stars over the ocean at night seen from a volcano summit, one star slightly moving, quiet ending", "scene"),
], [
    ("i", f"Сегодня {OU} уже за орбитой Нептуна. Его не видит ни один телескоп. Он снова стал тем, кем был до встречи с нами. Тёмной точкой в пустоте.", al("Сегодня Умуамуа уже за орбитой Нептуна. Его не видит ни один телескоп. Он снова стал тем, кем был до встречи с нами. Тёмной точкой в пустоте.")),
    ("c", "Через десятки тысяч лет он уйдёт из облака Оорта. Через миллионы — встретит другую звезду. Может быть, там тоже кто-то посмотрит в небо."),
    ("d", "Он пришёл из системы, которую мы никогда не увидим. Может быть, её солнце давно погасло. А может быть, там до сих пор кружатся планеты."),
    ("d", "И этот камень — единственное, что мы когда-либо держали в руках из того мира. Пусть только в виде точки на снимке."),
    ("h", "Мы до сих пор не знаем, чем он был. Ледяным осколком. Плитой азота. Пушистым облаком пыли. Или чем-то, что сделали чьи-то руки."),
    ("h", "Но он научил нас главному. Между звёздами не пусто. Там постоянно летят гости. Просто раньше мы их не замечали."),
    ("g", "Ещё десять лет назад о межзвёздных объектах писали только теоретики. Теперь у них есть номера. Первый. Второй. Третий."),
    ("e", "Где-то сейчас подрастает ребёнок, который станет астрономом. Возможно, именно он увидит четвёртого. Или сотого."),
    ("b", "И однажды кто-то из них поймает гостя, который будет вести себя совсем не как камень."),
    ("f", "Что мы тогда сделаем? Узнаем ли мы послание, если оно прилетит? Или примем его за ещё одну странную комету?"),
    ("a", f"Гавайцы назвали его {OU}. Посланник издалека, прибывший первым.", al("Гавайцы назвали его Умуамуа. Посланник издалека, прибывший первым.")),
    ("a", "Первым — значит, не последним."),
    ("j", "А значит, где-то там, в темноте, уже летит следующий. И он тоже не знает, что мы его ждём."),
    ("j", "Кто мы для таких гостей? Случайная остановка на долгом пути? Или те, кто наконец научился смотреть?"),
])

if __name__ == "__main__":
    for k, v in W.items(): print(k, v)
    print("total c2..c8 words", sum(W.values()))
