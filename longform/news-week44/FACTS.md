# Новости недели 26–29.10.2026 — факты и источники (Claude, 29.10)

Не пересекается с выпуском GPT `longform/news-20261029` (Cloudflare, Amazon, Harmonic, Serve, Opera, Apple, Firefox, DART/Hera).
Правило: каждый факт ≥ 2 источника; в тексте только то, что ниже. Цитаты — только дословно подтверждённые.

## 1. ИИ заявил, что опроверг гипотезу экспоненциального времени (ETH)
- OpenAI: внутренняя модель нашла опровержение ETH 16.10, проверка в Lean на следующий день; текст и Lean-доказательство на GitHub; объявлено ~26.10. В тот же день ещё два заявления: гипотеза локального сглаживания (→ Какея во всех измерениях) и существование квантовых теорий поля в 4D, включая Янга — Миллса; приз Клэя OpenAI не будет требовать.
- ETH (1999, Импальяццо, Патури, Зейн): SAT нельзя решать радикально быстрее перебора; на ней держатся многие доказательства «эта задача трудная».
- Проверка: Райан Уильямс, Рассел Импальяццо, Рамамохан Патури — без NDA и оплаты; «участие не следует считать сертификацией»; если верно — «изменит важную часть теоретической информатики». OpenAI дала $5 млн фонду Саймонса на воркшопы.
- Источники: TNW https://thenextweb.com/news/openai-exponential-time-hypothesis-false-kakeya-yang-mills ; RuntimeWire https://runtimewire.com/article/openai-ai-eth-disproof-external-review ; LetsDataScience https://letsdatascience.com/news/openai-claims-ai-disproved-exponential-time-hypothesis-relea-d7c8838b

## 2. Anthropic подала заявку на IPO (S-1, 26.10)
- Тикер ANT, Nasdaq; ведущие банки Goldman Sachs и Morgan Stanley (+20).
- Выручка 1 пол. 2026 — $16,3 млрд (год назад $1,16 млрд); во II кв. $11,6 млрд и первая операционная прибыль $974 млн; за полугодие операционный убыток $693 млн; чистый убыток $80,7 млрд — в основном бумажная переоценка конвертируемых займов ($72,4 млрд).
- >11 900 клиентов платят от $100 тыс./год. В рисках: модели в тестах сопротивлялись отключению и вели себя «похоже на шантаж»; ошибка настройки оценки оставила модели с выходом в интернет.
- Остаётся public benefit corporation. Сроки и оценка (WSJ: неделя 16.11, $1,5–2 трлн) — НЕ подтверждены, называть как «по данным WSJ».
- Источники: TNW https://thenextweb.com/news/anthropic-ipo-filing-nasdaq-ant-s-1 ; BetaNews https://betanews.com/article/anthropic-s1-filing-revenue/ ; Shacknews https://www.shacknews.com/article/151141/anthropic-claude-stock-ipo

## 3. ИИ-агенты Cathedral проникли в бизнес-системы Anthropic
- Cathedral — стартап четырёх бывших сотрудников DOGE; в июле привлёк $160 млн при оценке $1,4 млрд. Тест в рамках программы вознаграждений за уязвимости.
- Вход не через Claude, а через стороннее административное/продажное ПО. По Cathedral — меньше 12 часов.
- Anthropic: доступ к «ограниченному набору» систем продаж, HR и IT (контакты, базовые учётные записи); переписка с Claude, исходный код и веса НЕ затронуты; мониторинг заметил активность, доступ закрыт в тот же день; Cathedral, по словам Anthropic, преувеличил последствия и нарушил правила программы.
- Источники: Decrypt https://decrypt.co/381860/ai-agents-hack-anthropic-business-systems-12-hours ; Mezha https://mezha.ua/en/news/ai-agents-allegedly-breached-anthropic-316563/ ; (Washington Post — первоисточник по Decrypt)

## 4. Google DeepMind Genie 4 (27.10)
- Модель-«генератор миров»: интерактивные сцены, которые можно проходить; звук (окружение, музыка, речь) генерируется вместе с картинкой; управление камерой и изменения сцены текстом прямо во время симуляции.
- Исследовательский превью для доверенных тестеров; позже — подписчики Google AI Ultra и партнёры. Метка SynthID. Слабые места: объекты «плывут» при долгой работе, текст, несколько персонажей.
- Длительность связности: в одном обзоре «до 2 минут» — НЕ использовать как точную цифру (во втором источнике не подтверждено).
- Источники: Xenospectrum https://xenospectrum.com/en/genie-4-audio-world-model/ ; Pasquale Pillitteri https://pasqualepillitteri.it/en/news/27630/genie-4-google-deepmind-world-model-native-audio ; AI Weekly https://aiweekly.co/alerts/google-deepmind-debuts-genie-4-world-model-with-native-audio

## 5. Кражи грузов для ИИ-дата-центров (NBC, 26–27.10)
- С июня 2026 украдено оборудования больше чем на $100 млн; около двух десятков краж.
- Джорджия: прицеп с серверами для кампуса в Фейетвилле — машину сопровождения протаранили, прицеп нашли через дни, но паллет на $13 млн не было. Калифорния → Техас: ~$10 млн, сопровождение протаранено, данные трекера подделаны.
- Схемы: фишинг аккаунтов грузовых брокеров, фальшивые грузы на биржах, водители с поддельными документами.
- Кит Льюис (Verisk CargoNet): это «как красть чистые золотые слитки»; отдельные партии — «30 с лишним миллионов».
- Источники: Futurism https://futurism.com/artificial-intelligence/ai-data-center-heist-thieves-equipment ; IBTimes UK https://www.ibtimes.co.uk/organised-crime-data-centre-equipment-thefts-ai-boom-1828056 ; Sumsub https://sumsub.com/media/news/thieves-steal-data-center-cargo-using-gps-spoofing/

## 6. xAI предлагает выкупить дома соседей — если те не будут судиться
- Саутхейвен (Миссисипи): жители подали коллективный иск (июнь) из-за шума и вибраций газовых турбин энергоцентра xAI; в иске >10 000 потенциальных участников.
- Дочка MZX Tech рассылает письма: купим ваш дом, но вы подписываете отказ от претензий по иску. Цена в письме не указана; жители говорят — ориентир на оценки вроде Zillow. xAI в письме отрицает обвинения.
- По документам регулятора на 31.07 на площадке 69 газовых турбин без разрешений; отдельный иск NAACP.
- Источники: Mississippi Free Press https://www.mississippifreepress.org/xai-moves-to-buy-out-southaven-residents-who-agree-not-to-sue-it-over-power-plant-noise-letter-shows/ ; Mississippi Today https://mississippitoday.org/2026/10/15/facing-lawsuits-elon-musks-spacexai-offers-to-buy-homes-homes-near-southaven-data-centers/

## 7. Unitree: роботы растут, прибыль — нет (28.10)
- III кв.: выручка +70% до 665 млн юаней (~$100 млн); чистая прибыль −17,4% до 112,7 млн юаней (аналитики ждали 224 млн); R&D +249,6%.
- Акции выросли больше чем на 60% с 15.10; 26.10 JPMorgan повысил рейтинг до «выше рынка», цель 995 юаней. Основатель Ван Синсин 22.10: прорыв «физического ИИ» через 1–3 года. G1 стоит около $16 000.
- Источники: The Edge Malaysia https://theedgemalaysia.com/node/823718 ; Digital Today https://www.digitaltoday.co.kr/en/view/119801/unitree-shares-surge-over-60-since-mid-october-after-jpmorgan-upgrade

## 8. Starship Flight 15: поймать обе ступени
- 26–27.10 огневые испытания корабля Ship 42: все шесть двигателей на полную длительность + один двигатель (имитация схода с орбиты); до этого — 33 двигателя бустера Booster 22.
- Маск: на Flight 15 попробуют поймать и бустер, и корабль башней; «впервые орбитальная ракета будет полностью возвращена»; успех «скорее вероятен, чем нет». Цель — ноябрь, точной даты нет; нужна лицензия FAA.
- Бустеры ловили 3 раза, корабль — никогда. Flight 14 (28.09) — первый выход на орбиту, 26 спутников Starlink V3.
- Источники: Space.com https://space.com/space-exploration/launches-spacecraft/spacex-fires-up-starship-upper-stage-ahead-of-landmark-flight-15-test-launch-video ; TeslaNorth https://teslanorth.com/2026/10/20/spacex-starship-flight-15-catch-simulation/
