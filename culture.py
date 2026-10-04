"""The Culture tab: Ukraine's landscapes and landmarks, its food (with links to recipes), traditions,
holidays, Ukrainian festivals in the United States, and where to learn more.

Rule 8 in CLAUDE.md sets the standard: every sentence is supported by the sources the entry links to,
each Ukrainian claim rests on an authoritative source, recipes are linked, never copied, and events
come from their organizers' own pages. Each text is an (English, Ukrainian) pair. Each source is
(language, by, date or None, url, phrase); check.py confirms the phrase is still on the page."""
import datetime, html, re

import photos
from i18n import MONTHS_EN, both, dates
from photos import photo

# The day the events and resources below were last checked by hand. check.py fails once it is a year old.
REVIEWED = '2026-10-03'

HERO = photo('hero-lavra.jpg', ('The Kyiv Pechersk Lavra in morning mist', 'Києво-Печерська лавра в ранковому тумані'), 'KyivMax', 'CC BY-SA 4.0',
             'https://commons.wikimedia.org/wiki/File:%D0%9A%D0%B8%D1%94%D0%B2%D0%BE-%D0%9F%D0%B5%D1%87%D0%B5%D1%80%D1%81%D1%8C%D0%BA%D0%B0_%D0%9B%D0%B0%D0%B2%D1%80%D0%B0_%D0%B2_%D1%80%D0%B0%D0%BD%D0%BA%D0%BE%D0%B2%D0%BE%D0%BC%D1%83_%D1%82%D1%83%D0%BC%D0%B0%D0%BD%D1%96.jpg')

def view(p, related=None):
    """A gallery photo; its alt text doubles as the caption. related names a timeline entry."""
    return dict(photo=p, related=related)

GALLERY = [
 view(photo('kyiv-sophia.jpg', ('Saint Sophia Cathedral, Kyiv', 'Софійський собор, Київ'), 'Rbrechko', 'CC BY-SA 4.0',
            'https://commons.wikimedia.org/wiki/File:80-391-0151_Kyiv_St.Sophia%27s_Cathedral_RB_18.jpg'), ('history', 'Saint Sophia rises in Kyiv')),
 view(photo('kamianets.jpg', ('Kamianets-Podilskyi Castle at sunrise, Khmelnytskyi region', 'Кам’янець-Подільська фортеця на світанку, Хмельниччина'), 'Rbrechko', 'CC BY-SA 4.0',
            'https://commons.wikimedia.org/wiki/File:68-104-9007_Kamianets-Podilskyi_Fortress_RB_18_2.jpg')),
 view(photo('synevyr.jpg', ('Synevyr National Nature Park in autumn, Zakarpattia', 'Національний природний парк «Синевир» восени, Закарпаття'), 'Rbrechko', 'CC BY-SA 4.0',
            'https://commons.wikimedia.org/wiki/File:21-224-5054_NNP_Synevyr_RB_18.jpg')),
 view(photo('lviv.jpg', ('Market Square, Lviv', 'Площа Ринок, Львів'), 'Petar Milošević', 'CC BY-SA 3.0',
            'https://commons.wikimedia.org/wiki/File:%D0%9B%D0%B2%D0%BE%D0%B2_%D0%93%D0%B0%D0%BB%D0%B8%D1%86%D0%B8%D1%98%D0%B0.jpg')),
 view(photo('odesa-opera.jpg', ('The Odesa Opera and Ballet Theatre', 'Одеський театр опери та балету'), 'George Chernilevsky', 'Public domain',
            'https://commons.wikimedia.org/wiki/File:Odessa_Opera_Theatre_2016_G1.jpg')),
 view(photo('hoverla.jpg', ('Hoverla above the clouds, Carpathian National Nature Park', 'Говерла над хмарами, Карпатський національний природний парк'), 'Khoroshkov', 'CC BY-SA 4.0',
            'https://commons.wikimedia.org/wiki/File:%D0%93%D0%BE%D1%80%D0%B0_%D0%93%D0%BE%D0%B2%D0%B5%D1%80%D0%BB%D0%B0_%D0%BD%D0%B0%D0%B4_%D1%85%D0%BC%D0%B0%D1%80%D0%B0%D0%BC%D0%B8.jpg')),
 view(photo('khotyn.jpg', ('Khotyn Fortress on the Dnister under a full moon', 'Хотинська фортеця над Дністром у світлі повного місяця'), 'Ryzhkov Sergey', 'CC BY-SA 4.0',
            'https://commons.wikimedia.org/wiki/File:%D0%A5%D0%BE%D1%82%D0%B8%D0%BD%D1%81%D1%8C%D0%BA%D0%B0_%D1%84%D0%BE%D1%80%D1%82%D0%B5%D1%86%D1%8F_%D0%B2_%D0%BC%D1%96%D1%81%D1%8F%D1%87%D0%BD%D1%83_%D0%BD%D1%96%D1%87.jpg')),
 view(photo('bakota.jpg', ('Bakota Bay', 'Бакотська затока'), 'Стародубцев Олександр', 'CC BY-SA 4.0',
            'https://commons.wikimedia.org/wiki/File:%D0%91%D0%B0%D0%BA%D0%BE%D1%82%D0%B0_2.jpg')),
]

def entry(key, name, about, sources, **extra):
    """One entry: key, name and about (English, Ukrainian), sources, and the fields its section needs:
    recipes [(language, by, url, phrase)] and photo for dishes; date for holidays; where and when for
    events; where and url for resources."""
    return dict(key=key, name=name, about=about, sources=sources, **extra)

UNESCO_BORSHCH = 'https://ich.unesco.org/en/USL/culture-of-ukrainian-borscht-cooking-01852'
EOU_FOODS = ('en', 'Encyclopedia of Ukraine, “Traditional foods”', None, 'https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5CT%5CR%5CTraditionalfoods.htm')
UA_CUISINE = ('en', 'ukraine.ua', '2021-08-11', 'https://ukraine.ua/explore/ukrainian-cuisine/')
UA_CHRISTMAS = ('en', 'ukraine.ua', '2021-12-12', 'https://ukraine.ua/visit/christmas-dinner/')
KLOP, KLOP_UK = 'Yevhen Klopotenko', 'Євген Клопотенко'
KLOP_EN, KLOP_UA = 'https://klopotenko.com/en/', 'https://klopotenko.com/'
W = 'https://commons.wikimedia.org/wiki/File:'

DISHES = [
 entry('borshch', ('Borshch', 'Борщ'),
       ('Borshch is a soup of broth with beetroot, sugar beet or fermented beet juice, made in many versions and usually served with bread or garlic buns. The skill passes down within families, and in 2022 UNESCO put the culture of Ukrainian borscht cooking on its list of heritage in need of urgent safeguarding, because the war threatens it, not least by driving many of the people who cook it from their homes.',
        'Борщ — це суп на бульйоні з буряком, цукровим буряком або квашеним буряковим соком; він має багато різновидів і зазвичай подається з хлібом або часниковими пампушками. Уміння його готувати передається в родинах, і 2022 року ЮНЕСКО внесла культуру приготування українського борщу до списку нематеріальної спадщини, що потребує термінової охорони, бо їй загрожує війна, зокрема через те, що багато людей, які його готують, змушені були покинути свої домівки.'),
       [('en', 'UNESCO', '2022-07-01', UNESCO_BORSHCH, 'Culture of Ukrainian borscht cooking'),
        ('uk', 'Українська правда. Життя', '2022-07-01', 'https://life.pravda.com.ua/culture/2022/07/1/249372/', 'Культуру приготування українського борщу')],
       photo=photo('dish-borshch.jpg', ('Borshch with pampushky in Zaporizhzhia', 'Борщ із пампушками в Запоріжжі'), 'Brücke-Osteuropa', 'Public domain', W + 'Ukrainian_Borsch_with_Pampushky_in_Zaporizhia.JPG'),
       recipes=[('en', KLOP, KLOP_EN + 'ukrainian-borsch-with-pork-ribs/', 'traditional Ukrainian borsch with pork ribs'),
                ('uk', KLOP_UK, KLOP_UA + 'ukrainskij-borshh-na-svinaychuh-rebrah/', 'у цій страві живе українська душа')]),
 entry('varenyky', ('Varenyky', 'Вареники'),
       ('Varenyky are dumplings of dough wrapped around a filling: potato, cabbage, cottage cheese, mushrooms, meat or cherries. They are served with sour cream, fried onions or fried bacon, and the Encyclopedia of Ukraine calls them the favorite Ukrainian dish made of flour.',
        'Вареники — це вироби з тіста з начинкою: картоплею, капустою, сиром, грибами, м’ясом чи вишнями. Їх подають зі сметаною, смаженою цибулею або шкварками, а Енциклопедія України називає їх улюбленою українською стравою з борошна.'),
       [(*EOU_FOODS, 'favorite dish made of flour'), (*UA_CUISINE, 'Varenyky is made of dough')],
       photo=photo('dish-varenyky.jpg', ('Carpathian potato varenyky with sour cream', 'Карпатські вареники з картоплею та сметаною'), 'Марися Лебідь', 'CC BY-SA 4.0', W + '%D0%9A%D0%B0%D1%80%D0%BF%D0%B0%D1%82%D1%81%D1%8C%D0%BA%D1%96_%D0%B2%D0%B0%D1%80%D0%B5%D0%BD%D0%B8%D0%BA%D0%B8.jpg'),
       recipes=[('en', KLOP, KLOP_EN + 'sour-cherry-dumplings/', 'Sour cherry dumplings'),
                ('uk', KLOP_UK, KLOP_UA + 'vareniki-z-vishneu/', 'Простий рецепт вареників із вишнею')]),
 entry('holubtsi', ('Holubtsi', 'Голубці'),
       ('Holubtsi are fresh or pickled cabbage leaves rolled around buckwheat, millet, rice or meat. They are part of the Ukrainian Christmas Eve table, and in 2023 Lenten holubtsi with potato, a Lemko dish, were added to Ukraine’s national list of intangible cultural heritage.',
        'Голубці — це листя свіжої або квашеної капусти, загорнуте навколо начинки з гречки, пшона, рису чи м’яса. Вони — частина українського святвечірнього столу, а 2023 року пісні голубці з картоплею, страву лемківської кухні, внесли до Національного переліку нематеріальної культурної спадщини України.'),
       [(*EOU_FOODS, 'filled with buckwheat or millet grits'), (*UA_CHRISTMAS, 'integral element of Ukrainian Christmas food'),
        ('uk', 'Українська правда. Життя', '2026-08-24', 'https://life.pravda.com.ua/society/borshch-shpachki-chiberek-ta-inshi-stravi-nematerialnoji-spadshchini-ukrajini-317090/', 'традиційна страва лемківської кухні')],
       photo=photo('dish-holubtsi.jpg', ('Homemade holubtsi with sour cream', 'Домашні голубці зі сметаною'), 'Berser25', 'CC BY-SA 4.0', W + '%D0%93%D0%BE%D0%BB%D1%83%D0%B1%D1%86%D1%96_%D0%B7_%D1%81%D0%BC%D0%B5%D1%82%D0%B0%D0%BD%D0%BE%D1%8E.jpg'),
       recipes=[('en', KLOP, KLOP_EN + 'lent-friendly-authentic-ukrainian-stuffed-cabbage-rolls-with-potato-filling/', 'Stuffed cabbage rolls or holubtsi'),
                ('uk', KLOP_UK, KLOP_UA + 'idealno-do-postu-reczept-golubcziv-z-kartopli/', 'Рецепт голубців з картоплі')]),
 entry('deruny', ('Deruny', 'Деруни'),
       ('Deruny are potato pancakes, served with sour cream or cheese. Deruny made with onion were also among the dishes families put on the table for the Christmas Eve supper.',
        'Деруни — це картопляні оладки, які подають зі сметаною або сиром. Деруни з цибулею також були серед страв, які родини ставили на стіл на Святвечір.'),
       [(*UA_CHRISTMAS, 'Deruny (potato pancakes) prepared with onions'), (*EOU_FOODS, 'Potato pancakes are served with cheese or sour cream')],
       photo=photo('dish-deruny.jpg', ('Deruny filled with meat, with sour cream, in Zaporizhzhia', 'Деруни з м’ясом і сметаною в Запоріжжі'), 'Brücke-Osteuropa', 'Public domain', W + 'Deruny_Potato_Pancakes.JPG'),
       recipes=[('uk', KLOP_UK, KLOP_UA + 'kartoplyani-deruny-u-blenderi-reczept-vid-yevgena-klopotenka/', 'Картопляні деруни в блендері')]),
 entry('pampushky', ('Pampushky', 'Пампушки'),
       ('Pampushky are garlic buns, the usual companion of borshch: Ukraine’s official site says borshch is usually served with them, and UNESCO’s description of Ukrainian borshch says it is typically served with bread or garlic buns.',
        'Пампушки — це булочки з часником, звичний супутник борщу: офіційний сайт України пише, що борщ зазвичай подають із ними, а в описі ЮНЕСКО сказано, що український борщ зазвичай подають із хлібом або часниковими булочками.'),
       [(*UA_CUISINE, 'garlic fritters called pampushky'), ('en', 'UNESCO', '2022-07-01', UNESCO_BORSHCH, 'served with bread or garlic buns')],
       photo=photo('dish-pampushky.jpg', ('Pampushky with dill in Donetsk, 2012', 'Пампушки з кропом у Донецьку, 2012 рік'), 'MOs810', 'CC BY-SA 3.0', W + 'Pampuchy_Donetsk.JPG'),
       recipes=[('en', 'Anna Voloshyna', 'https://www.annavoloshyna.com/recipes/garlic-and-dill-pampushky', 'Ukrainian Garlic Pampushky'),
                ('uk', KLOP_UK, KLOP_UA + 'pampushky-z-chasnykom/', 'пампушки з часником та кропом')]),
 entry('kutia', ('Kutia', 'Кутя'),
       ('Kutia is boiled wheat seasoned with honey and poppy seeds, often with nuts and dried fruit. It is the most important of the twelve meatless dishes of the Christmas Eve supper and is usually eaten first; in old custom the head of the household invited the frost to eat kutia.',
        'Кутя — це варена пшениця з медом і маком, часто також із горіхами та сухофруктами. Це найважливіша з дванадцяти пісних страв святвечірньої вечері, і зазвичай її їдять першою; за давнім звичаєм господар запрошував мороз їсти кутю.'),
       [(*UA_CHRISTMAS, 'Kutia is the most important dish'), ('en', 'Encyclopedia of Ukraine, “Christmas”', None, 'https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5CC%5CH%5CChristmas.htm', 'frost to eat kutia')],
       photo=photo('dish-kutia.jpg', ('Kutia in a traditional Ukrainian bowl', 'Кутя в традиційній українській мисці'), 'Віщун', 'CC BY-SA 4.0', W + 'Kutia_in_traditional_ukrainian_bowl_2023.jpg'),
       recipes=[('en', 'NV (The New Voice of Ukraine)', 'https://english.nv.ua/life/recipes-for-traditional-ukraine-christmas-dish-kutia-50378933.html', 'Traditional Wheat Kutia'),
                ('uk', KLOP_UK, KLOP_UA + 'tradyczijna-kutya-z-pshenyczi-reczept-kuti-z-rodzynkamy-ta-makom/', 'Традиційно різдвяна кутя готується з пшениці')]),
 entry('uzvar', ('Uzvar', 'Узвар'),
       ('Uzvar is a drink of dried fruit, most often apples, pears, apricots and prunes, made into a fragrant decoction and sometimes sweetened with honey. It is an important part of the Christmas Eve supper.',
        'Узвар — це запашний відвар із сухофруктів, найчастіше яблук, груш, абрикосів і чорносливу, іноді з медом. Це важлива частина святвечірньої вечері.'),
       [(*UA_CUISINE, 'Uzvar is a healthy and refreshing beverage'), (*UA_CHRISTMAS, 'a rich and fragrant decoction of dried pears')],
       photo=photo('dish-uzvar.jpg', ('A glass of uzvar', 'Склянка узвару'), 'Ijon', 'CC BY-SA 4.0', W + 'Ukrainian_uzvar_2.jpg'),
       recipes=[('en', KLOP, KLOP_EN + 'mulled-uzvar-dried-fruit-drink/', 'Mulled uzvar (dried fruit drink)'),
                ('uk', KLOP_UK, KLOP_UA + 'uzvar-iz-suhofruktiv-reczept-tradyczijnogo-ukrayinskogo-napoyu/', 'рецепт традиційного українського напою')]),
 entry('paska', ('Paska', 'Паска'),
       ('Paska is the Easter bread that families take to church to be blessed, then share at the Easter meal with eggs and the other blessed foods. In western Ukraine it is low and cylindrical and decorated with dough ornaments; in the east it is baked tall.',
        'Паска — великодній хліб, який родини несуть до церкви освятити, а потім ділять за великодньою трапезою разом із яйцями та іншими освяченими стравами. На заході України паску печуть низькою циліндричною й прикрашають візерунками з тіста, на сході — високою.'),
       [(*EOU_FOODS, 'paska has a tall cylindrical form')],
       photo=photo('dish-paska.jpg', ('Easter paska with dyed eggs, Poltava region', 'Великодня паска з крашанками, Полтавщина'), 'Мандрівниця', 'CC BY-SA 4.0', W + '%D0%92%D0%B5%D0%BB%D0%B8%D0%BA%D0%BE%D0%B4%D0%BD%D1%8F_%D0%BF%D0%B0%D1%81%D0%BA%D0%B0_%D0%B7_%D0%BA%D1%80%D0%B0%D1%88%D0%B0%D0%BD%D0%BA%D0%B0%D0%BC%D0%B8._%D0%9F%D0%BE%D0%BB%D1%82%D0%B0%D0%B2%D1%89%D0%B8%D0%BD%D0%B0,_2021_%D1%80%D1%96%D0%BA.jpg'),
       recipes=[('uk', KLOP_UK, KLOP_UA + 'klassichna-paska/', 'Класичний рецепт дріжджової паски'),
                ('uk', KLOP_UK, KLOP_UA + 'medova-paska-z-sofijskogo-soboru-vid-yevgena-klopotenka/', 'Медова паска з Софійського собору')]),
 entry('banosh', ('Banosh', 'Банош'),
       ('Banosh is a Carpathian dish of corn grits served with fried pork fat, mushrooms and bryndza cheese. It is traditionally cooked over a fire to give it a smoky taste, and restaurants all across the Carpathians serve it.',
        'Банош — карпатська страва з кукурудзяної крупи, яку подають зі смаженим салом, грибами та бринзою. Традиційно його готують на вогні, щоб він мав димний присмак, і його подають у ресторанах по всіх Карпатах.'),
       [(*UA_CUISINE, 'Banosh is served in all the restaurants')],
       photo=photo('dish-banosh.jpg', ('Banosh with cracklings in Poliana, Zakarpattia', 'Банош зі шкварками в селі Поляна, Закарпаття'), 'Мандрівниця', 'CC BY-SA 4.0', W + '%D0%91%D0%B0%D0%BD%D0%BE%D1%88_%D0%B7%D1%96_%D1%88%D0%BA%D0%B2%D0%B0%D1%80%D0%BA%D0%B0%D0%BC%D0%B8_%D0%B2_%D1%81%D0%B5%D0%BB%D1%96_%D0%9F%D0%BE%D0%BB%D1%8F%D0%BD%D0%B0_%D0%97%D0%B0%D0%BA%D0%B0%D1%80%D0%BF%D0%B0%D1%82%D1%81%D1%8C%D0%BA%D0%BE%D1%97_%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%96._2019_%D1%80%D1%96%D0%BA.jpg'),
       recipes=[('en', KLOP, KLOP_EN + 'oyster-mushroom-banosh/', 'Oyster mushroom banosh'),
                ('uk', KLOP_UK, KLOP_UA + 'dusha-zakarpattya-banosh-z-brynzoyu-i-shkvarkamy-vid-yevgena-klopotenka/', 'банош з бринзою і шкварками')]),
 entry('halushky', ('Halushky', 'Галушки'),
       ('Halushky are pieces of dough made from wheat, buckwheat or corn flour, boiled in water and served with fried bacon, fried onions or sour cream. They are most at home in the Poltava region.',
        'Галушки — це шматочки тіста з пшеничного, гречаного чи кукурудзяного борошна, зварені у воді й подані зі шкварками, смаженою цибулею або сметаною. Найбільше їх шанують на Полтавщині.'),
       [('en', 'ukraine.ua', '2023-02-22', 'https://ukraine.ua/regions-of-ukraine/poltava-region/', 'one of the most famous dishes in Ukrainian cuisine'), (*EOU_FOODS, 'made of wheat, buckwheat, or corn flour')],
       photo=photo('dish-halushky.jpg', ('Steamed Poltava halushky in Poltava', 'Полтавські галушки на пару в Полтаві'), 'Мандрівниця', 'CC0', W + '%D0%A2%D1%80%D0%B0%D0%B4%D0%B8%D1%86%D1%96%D0%B9%D0%BD%D1%96_%D0%BF%D0%BE%D0%BB%D1%82%D0%B0%D0%B2%D1%81%D1%8C%D0%BA%D1%96_%D0%B3%D0%B0%D0%BB%D1%83%D1%88%D0%BA%D0%B8,_%D0%BF%D1%80%D0%B8%D0%B3%D0%BE%D1%82%D0%BE%D0%B2%D0%B0%D0%BD%D1%96_%D0%BD%D0%B0_%D0%BF%D0%B0%D1%80%D1%83,_%D1%83_%D1%80%D0%B5%D1%81%D1%82%D0%BE%D1%80%D0%B0%D0%BD%D1%96_%22%D0%93%D0%B0%D0%BB%D1%83%D1%88%D0%BA%D0%B0%22._%D0%9F%D0%BE%D0%BB%D1%82%D0%B0%D0%B2%D0%B0,_%D0%B2%D0%B5%D1%80%D0%B5%D1%81%D0%B5%D0%BD%D1%8C_2025_%D1%80%D0%BE%D0%BA%D1%83_01.jpg'),
       recipes=[('en', KLOP, KLOP_EN + 'poltava-halushky-with-sour-cherries-and-meat/', 'Poltava halushky with sour cherries and meat'),
                ('uk', KLOP_UK, KLOP_UA + 'galushki-z-myasom-i-vishnyamy/', 'Кулінарний скарб Полтавщини')]),
 entry('kapusniak', ('Kapusniak', 'Капусняк'),
       ('Kapusniak is a soup made with sauerkraut, which gives it its sour taste. In the Luhansk region, Pavlivskyi kapusniak, cooked with fish and served on holidays and when a whole village works together, is on the regional list of intangible cultural heritage.',
        'Капусняк — це суп із квашеною капустою, яка надає йому кислинки. На Луганщині павлівський капусняк, який варять із рибою й подають на свята та під час толоки, коли працює все село, внесено до регіонального переліку нематеріальної культурної спадщини.'),
       [(*EOU_FOODS, 'used to make cabbage soup'), ('en', 'ukraine.ua', '2023-02-23', 'https://ukraine.ua/regions-of-ukraine/luhansk-region/', 'Pavlivskyi kapusniak')],
       photo=photo('dish-kapusniak.jpg', ('Kapusniak in a clay bowl', 'Капусняк у глиняній мисці'), 'Lisenok111', 'CC BY-SA 4.0', W + '%D0%9A%D0%B0%D0%BF%D1%83%D1%81%D1%82%D0%BD%D1%8F%D0%BA.jpg'),
       recipes=[('uk', KLOP_UK, KLOP_UA + 'avtentychnyj-reczept-z-cherkashhyny-kapusnyak-zi-svynyachymy-rebramy-vid-yevgena-klopotenka/', 'Капусняк зі свинячими ребрами')]),
 entry('lviv-syrnyk', ('Lviv syrnyk', 'Львівський сирник'),
       ('Lviv syrnyk is a cheesecake made from fresh cottage cheese, the local specialty of Lviv and the most popular cheesecake in western Ukraine.',
        'Львівський сирник — це запечений десерт зі свіжого кисломолочного сиру, місцевий делікатес Львова і найпопулярніший сирник на заході України.'),
       [('en', 'ukraine.ua', '2021-06-24', 'https://ukraine.ua/visit/best-places-in-ukraine/', 'Lviv’s local speciality is ‘syrnyk’')],
       recipes=[('en', KLOP, KLOP_EN + 'lviv-cheesecake-2/', 'Lviv cheesecake'),
                ('uk', KLOP_UK, KLOP_UA + 'tradyczijnyj-lvivskyj-syrnyk-prostyj-reczept-smachnogo-desertu/', 'Традиційний львівський сирник')]),
]

EOU = 'https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5C'
UNESCO = 'https://ich.unesco.org/en/'

TRADITIONS = [
 entry('petrykivka', ('Petrykivka painting', 'Петриківський розпис'),
       ('In the village of Petrykivka, people paint their homes, household objects and musical instruments with fantastic flowers and other motifs drawn from close observation of local plants and animals; the rooster stands for fire and spiritual awakening, and birds for light, harmony and happiness. Every family has at least one painter, local schools give every child the chance to learn it, and UNESCO added it to its Representative List of humanity’s intangible heritage in 2013.',
        'У селі Петриківка люди розписують житло, хатнє начиння й музичні інструменти фантастичними квітами та іншими мотивами, що постають з уважного спостереження за місцевими рослинами й тваринами; півень означає вогонь і духовне пробудження, а птахи — світло, гармонію та щастя. У кожній родині є щонайменше одна майстриня чи майстер, у місцевих школах кожна дитина має змогу навчитися розпису, а 2013 року ЮНЕСКО внесла його до Репрезентативного списку нематеріальної культурної спадщини людства.'),
       [('en', 'UNESCO', None, UNESCO + 'RL/petrykivka-decorative-painting-as-a-phenomenon-of-the-ukrainian-ornamental-folk-art-00893', 'Petrykivka decorative painting as a phenomenon')]),
 entry('kosiv-ceramics', ('Kosiv painted ceramics', 'Косівська мальована кераміка'),
       ('Kosiv painted ceramics, a tradition from the 18th century, include dishes, ceremonial items, toys and tiles of local clay. A contour drawing is scratched with a metal stick and painted in the traditional green and yellow, and in the kiln the green spreads into a watercolor effect called tears. The designs tell the history, folklore and customs of the Hutsuls, and UNESCO inscribed the tradition on its Representative List in 2019.',
        'Косівська мальована кераміка — традиція XVIII століття: посуд, обрядові вироби, іграшки й кахлі з місцевої глини. Контурний малюнок продряпують металевою паличкою й розписують традиційними зеленою та жовтою фарбами, а під час випалу зелена фарба розтікається, утворюючи ефект акварелі, який називають «сльозами». Сюжети розповідають про історію, фольклор і звичаї гуцулів, а 2019 року ЮНЕСКО внесла цю традицію до Репрезентативного списку.'),
       [('en', 'UNESCO', None, UNESCO + 'RL/tradition-of-kosiv-painted-ceramics-01456', 'Tradition of Kosiv painted ceramics')],
       photo=photo('tradition-kosiv.jpg', ('A Hutsul painted tile by Petro Koshak, Pystyn, 1911', 'Гуцульська мальована кахля Петра Кошака, Пистинь, 1911 рік'), 'Petro Koshak; photograph by the National Museum of Hutsulshchyna and Pokuttia Folk Art', 'Public domain', W + 'Koshak_Tile_Deer_1911.jpg')),
 entry('pysanka', ('Pysanka', 'Писанка'),
       ('Pysanky are eggs decorated by drawing patterns in wax and dipping them in dye, again and again, until the design is complete; the symbols carry personal wishes. The tradition predates Christianity but became part of Easter, and blessed pysanky are kept at home for protection. UNESCO inscribed it on its Representative List in 2024, on a joint nomination by Ukraine and Estonia, where Ukrainians also keep it.',
        'Писанка — це яйце, розписане воском і барвниками: візерунок наносять воском, а яйце занурюють у барвник, і так знову й знову, доки малюнок не буде завершено; у символах закладено особисті побажання. Традиція сягає дохристиянських часів, але стала великодньою, а освячені писанки зберігають удома як оберіг. 2024 року ЮНЕСКО внесла її до Репрезентативного списку за спільною номінацією України та Естонії, де її також підтримують українці.'),
       [('en', 'UNESCO', None, UNESCO + 'RL/pysanka-ukrainian-tradition-and-art-of-decorating-eggs-02134', 'a centuries-old Ukrainian tradition'),
        ('uk', 'Радіо Свобода', '2024-12-04', 'https://www.radiosvoboda.org/a/news-yunesko-pysanka-nematerialna-spadshchyna/33226065.html', 'заявку Україна подала спільно з Естонією')],
       photo=photo('tradition-pysanka.jpg', ('The pysanka Dolia by Tetiana Konoval, photographed in Kyiv in 2019', 'Писанка «Доля» Тетяни Коновал, сфотографована в Києві 2019 року'), 'Tetianakonoval', 'CC BY-SA 4.0', W + '%D0%9F%D0%B8%D1%81%D0%B0%D0%BD%D0%BA%D0%B0_%D0%A2._%D0%9A%D0%BE%D0%BD%D0%BE%D0%B2%D0%B0%D0%BB_%22%D0%94%D0%BE%D0%BB%D1%8F%22.jpg')),
 entry('vyshyvanka', ('Vyshyvanka', 'Вишиванка'),
       ('The vyshyvanka is a traditionally embroidered garment. Archaeological finds show that embroidery has existed in Ukraine since prehistoric times, first inspired by faith in the power of protective symbols. On Vyshyvanka Day, the third Thursday of May, Ukrainians wear embroidered clothing together.',
        'Вишиванка — традиційно вишитий одяг. Археологічні знахідки свідчать, що вишивка існує в Україні з доісторичних часів і спершу її надихала віра в силу символів-оберегів. У День вишиванки, третій четвер травня, українці разом вдягають вишитий одяг.'),
       [('en', 'Encyclopedia of Ukraine, “Embroidery”', None, EOU + 'E%5CM%5CEmbroidery.htm', 'embroidery has existed there since prehistoric times'),
        ('en', 'RFE/RL', '2022-05-20', 'https://www.rferl.org/a/ukraine-tradition-vyshyvanka-day-russia/31859790.html', 'takes place on the third Thursday of May')],
       photo=photo('tradition-vyshyvanka.jpg', ('A woman’s embroidered shirt from the Zhytomyr region, early 20th century, Ivan Honchar Museum, Kyiv', 'Жіноча вишита сорочка з Житомирщини, початок XX століття, Музей Івана Гончара, Київ'), 'Навка', 'CC BY-SA 3.0', W + 'Ukrainian_embroidered_womens_shirt_from_Zhytomyr_region.jpg')),
 entry('kobzars', ('Kobzars and the bandura', 'Кобзарство й бандура'),
       ('Kobzars were itinerant bards, usually blind, who sang epic, historical and religious songs to the kobza or bandura, a many-stringed Ukrainian instrument resembling a lute; others played the wheel lyre. Persecuted under the tsars and again in the 1920s and 1930s, their guilds were revived in the 1980s, and in 2024 UNESCO added the guilds’ program for passing the tradition on to its Register of Good Safeguarding Practices.',
        'Кобзарі — мандрівні співці, здебільшого незрячі, які виконували епічні, історичні та релігійні пісні під супровід кобзи або бандури, багатострунного українського інструмента, схожого на лютню; інші грали на колісній лірі. Їх переслідували за царської влади й знову в 1920–1930-х роках, у 1980-х їхні цехи відродилися, а 2024 року ЮНЕСКО внесла програму цехів із передавання традиції до Реєстру найкращих практик збереження.'),
       [('en', 'UNESCO', None, UNESCO + 'BSP/safeguarding-programme-of-kobza-and-wheel-lyre-tradition-02136', 'Ukrainian kobza and wheel lyre tradition'),
        ('en', 'Encyclopedia of Ukraine, “Bandura”', None, EOU + 'B%5CA%5CBandura.htm', 'A Ukrainian musical instrument similar'),
        ('en', 'Encyclopedia of Ukraine, “Kobzars”', None, EOU + 'K%5CO%5CKobzars.htm', 'these kobzars were usually blind')],
       photo=photo('tradition-bandura.jpg', ('Banduras from the late 18th to the early 20th century, Museum of Theatre, Music and Cinema Arts of Ukraine, Kyiv', 'Бандури кінця XVIII — початку XX століття, Музей театрального, музичного та кіномистецтва України, Київ'), 'Аимаина хикари', 'CC0', W + 'Banduras.jpg')),
 entry('shchedryk', ('Shchedryk, the song behind Carol of the Bells', '«Щедрик» — пісня, що стала Carol of the Bells'),
       ('The tune the world knows as Carol of the Bells is Shchedryk, Mykola Leontovych’s choral arrangement of a Ukrainian folk song. The Ukrainian National Chorus, formed to win recognition for Ukraine as it fought for independence, made its Carnegie Hall debut on October 5, 1922, and Peter Wilhousky later gave the song English lyrics and a new title. Leontovych did not live to see it: a Cheka agent shot him in 1921.',
        'Мелодія, відома світові як Carol of the Bells, — це «Щедрик» Миколи Леонтовича, хорова обробка української народної пісні. Український національний хор, створений, щоб здобути для України визнання в боротьбі за незалежність, уперше виступив у Карнегі-холі 5 жовтня 1922 року, а згодом Пітер Вільговський дав пісні англійський текст і нову назву. Леонтович цього не дочекався: 1921 року його застрелив агент ЧК.'),
       [('en', 'NPR', '2022-12-06', 'https://www.npr.org/2022/12/06/1140741769/ukraine-christmas-carol-carnegie-hall', 'Ukrainian composer Mykola Leontovych wrote Shchedryk'),
        ('en', 'Carnegie Hall', '2022-11-29', 'https://www.carnegiehall.org/Explore/Articles/2022/11/29/Carol-of-the-Bells', 'Carnegie Hall debut on October 5, 1922'),
        ('en', 'Encyclopedia of Ukraine, “Leontovych, Mykola”', None, EOU + 'L%5CE%5CLeontovychMykola.htm', 'shot by a Cheka agent')],
       related=('history', 'The Ukrainian People’s Republic declares independence'),
       photo=photo('tradition-shchedryk.jpg', ('The Ukrainian chorus in a Bain News Service photograph dated September 26, 1922', 'Український хор на світлині агентства Bain News Service, датованій 26 вересня 1922 року'), 'Bain News Service', 'Public domain', W + 'Ukraine_Chorus_LCCN2014715188.jpg')),
 entry('hopak', ('Hopak', 'Гопак'),
       ('The hopak is an original Ukrainian folk dance whose name comes from hopaty, to leap and stamp one’s feet. It arose as a men’s dance at the Zaporozhian Sich in the 16th century and later became a dance for couples, full of leaps, squats and turns. It is the culminating dance in the repertoire of almost every Ukrainian dance ensemble.',
        'Гопак — самобутній український народний танець, назва якого походить від слова «гопати», тобто стрибати й притупувати. Він виник у XVI столітті на Запорозькій Січі як чоловічий танець, а згодом став парним, сповненим стрибків, присядок і обертів. Він — кульмінація репертуару майже всіх українських танцювальних ансамблів.'),
       [('en', 'Encyclopedia of Ukraine, “Hopak”', None, EOU + 'H%5CO%5CHopakIT.htm', 'An original Ukrainian folk dance')],
       related=('history', 'The Zaporozhian Sich is destroyed'),
       photo=photo('tradition-hopak.jpg', ('Hopak, a folk painting from the late 18th century', '«Гопак», народна картина кінця XVIII століття'), 'Unknown artist', 'Public domain', W + 'Gopak.jpg')),
 entry('trembita', ('Trembita', 'Трембіта'),
       ('The trembita is a wooden horn of the Ukrainian Carpathians, one to three meters long, made from hollowed halves of spruce bound with birch bark. Its sound carries more than 10 kilometers, and herders in isolated mountain areas used set signals on it to announce a death, a funeral or a wedding.',
        'Трембіта — дерев’яний духовий інструмент українських Карпат завдовжки від одного до трьох метрів, зроблений із видовбаних половинок смереки й обмотаний березовою корою. Її звук чути за понад 10 кілометрів, і пастухи в ізольованих гірських місцевостях умовленими сигналами сповіщали нею про смерть, похорон чи весілля.'),
       [('en', 'Encyclopedia of Ukraine, “Trembita”', None, EOU + 'T%5CR%5CTrembitaIT.htm', 'found mainly in the Carpathian Mountains')],
       photo=photo('tradition-trembita.jpg', ('Hutsuls with a trembita, an engraving published around 1900', 'Гуцули з трембітою, гравюра, видана близько 1900 року'), 'Unknown author', 'Public domain', W + 'Huzulen_03.jpg')),
 entry('cossack-songs', ('Cossack songs of the Dnipropetrovsk region', 'Козацькі пісні Дніпропетровщини'),
       ('Communities in the Dnipropetrovsk region sing Cossack songs about the tragedy of war and the personal relationships of Cossack soldiers: one singer starts, a second comes in with an upper voice, and the rest follow in middle and lower voices. Many of the singers are in their 70s and 80s, and in 2016 UNESCO placed the tradition on its list of heritage in need of urgent safeguarding.',
        'Громади Дніпропетровщини співають козацькі пісні про трагедію війни та особисті стосунки козаків: один співак заводить, другий підхоплює верхнім голосом, а решта — середніми й нижніми. Багатьом виконавцям по 70–80 років, і 2016 року ЮНЕСКО внесла цю традицію до Списку нематеріальної культурної спадщини, що потребує термінової охорони.'),
       [('en', 'UNESCO', None, UNESCO + 'USL/cossack-s-songs-of-dnipropetrovsk-region-01194', 'Cossack songs are sung by communities')],
       photo=photo('tradition-cossack-songs.jpg', ('Kozak-banduryst (Cossack Mamai), a folk painting from the early 19th century, National Art Museum of Ukraine', 'Козак-бандурист (Козак Мамай), народна картина початку XIX століття, Національний художній музей України'), 'Unknown author', 'Public domain', W + 'Cossack_Mamay_1st_half_of_19th_c_(4).jpg')),
 entry('ornek', ('Örnek, the Crimean Tatar ornament', 'Орнек — кримськотатарський орнамент'),
       ('Örnek is the Crimean Tatar ornament, a system of about 35 symbols used in embroidery, weaving, pottery, jewelry and wood carving: a rose stands for a married woman, a tulip for a young man and an almond for an unmarried girl. UNESCO inscribed it on its Representative List in 2021 on Ukraine’s nomination, describing it as a Ukrainian system of symbols.',
        'Орнек — кримськотатарський орнамент, система з приблизно тридцяти п’яти символів, які використовують у вишивці, ткацтві, гончарстві, ювелірному мистецтві та різьбленні по дереву: троянда означає заміжню жінку, тюльпан — юнака, мигдаль — незаміжню дівчину. 2021 року ЮНЕСКО внесла орнек до Репрезентативного списку за номінацією України, назвавши його українською системою символів.'),
       [('en', 'UNESCO', None, UNESCO + 'RL/ornek-a-crimean-tatar-ornament-and-knowledge-about-it-01601', 'is a Ukrainian system of symbols')],
       related=('history', 'The Crimean Tatars are deported'),
       photo=photo('tradition-ornek.jpg', ('An ornament drawing by Adavie Efendiyeva, 1920', 'Орнаментальний малюнок Адавіє Ефендієвої, 1920 рік'), 'Adavie Efendiyeva', 'Public domain', W + 'Adaviye_Efendiyeva_01.JPG')),
]

CORRECTIONS = [
 entry('national-gallery-degas', ('Degas’s Ukrainian Dancers, National Gallery, London', '«Українські танцівниці» Дега, Лондонська національна галерея'),
       ('In 2022, after an outcry from Ukrainians on social media, the National Gallery in London renamed an Edgar Degas pastel from Russian Dancers to Ukrainian Dancers. The gallery now says the dancers, drawn around 1899, are almost certainly Ukrainian rather than Russian. They wear blue and yellow ribbons in their hair.',
        '2022 року, після обурення українців у соцмережах, Лондонська національна галерея перейменувала пастель Едгара Дега з «Російських танцівниць» на «Українських танцівниць». Галерея тепер пише, що танцівниці, яких Дега намалював близько 1899 року, майже напевно українки, а не росіянки. У їхньому волоссі — сині й жовті стрічки.'),
       [('en', 'National Gallery, London', None, 'https://www.nationalgallery.org.uk/paintings/hilaire-germain-edgar-degas-ukrainian-dancers', 'almost certainly Ukrainian rather than Russian'),
        ('en', 'Smithsonian Magazine', '2022-04-11', 'https://www.smithsonianmag.com/smart-news/londons-national-gallery-renames-degas-russian-dancers-to-ukrainian-dancers-180979868/', 'Russian Dancers to Ukrainian Dancers')],
       photo=photo('fix-degas-ng.jpg', ('Edgar Degas, Ukrainian Dancers, about 1899, National Gallery, London', 'Едгар Дега, «Українські танцівниці», близько 1899 року, Лондонська національна галерея'), 'Edgar Degas', 'Public domain', W + 'Edgar_Degas_-_Ukrainian_Dancers_-_c._1899.png')),
 entry('met-degas', ('The Met’s Dancers in Ukrainian Dress', '«Танцівниці в українському вбранні» в Метрополітен-музеї'),
       ('In 2023 the Metropolitan Museum of Art in New York renamed its own Degas pastel from Russian Dancers to Dancers in Ukrainian Dress.',
        '2023 року нью-йоркський Метрополітен-музей перейменував свою пастель Дега з «Російських танцівниць» на «Танцівниць в українському вбранні».'),
       [('en', 'The Metropolitan Museum of Art', None, 'https://www.metmuseum.org/art/collection/search/459097', 'traditional Ukrainian folk dress undertaken by Degas'),
        ('en', 'Smithsonian Magazine', '2023-03-23', 'https://www.smithsonianmag.com/smart-news/new-yorks-metropolitan-museum-of-art-latest-to-rename-ukrainian-works-and-artists-180981859/', 'officially renamed the piece Dancers in Ukrainian Dress')],
       photo=photo('fix-degas-met.jpg', ('Edgar Degas, Dancers in Ukrainian Dress, 1899, The Metropolitan Museum of Art', 'Едгар Дега, «Танцівниці в українському вбранні», 1899 рік, Метрополітен-музей'), 'Edgar Degas', 'CC0', W + 'Russian_Dancers_MET_DT3112.jpg')),
 entry('met-kuindzhi-repin', ('Kuindzhi and Repin, Ukrainian at The Met', 'Куїнджі та Рєпін — українці в Метрополітен-музеї'),
       ('The Met also stopped listing the painters Arkhyp Kuindzhi and Illia Repin as Russian: both now appear as Ukrainian, Kuindzhi born in Mariupol and Repin in Chuhuiv. The Met’s entry for Kuindzhi’s Red Sunset notes that the Kuindzhi Art Museum in Mariupol was destroyed in a Russian airstrike in March 2022.',
        'Метрополітен-музей також перестав називати художників Архипа Куїнджі та Іллю Рєпіна росіянами: тепер обидва значаться українцями — Куїнджі народився в Маріуполі, а Рєпін у Чугуєві. В описі картини Куїнджі «Червоний захід сонця» зазначено, що в березні 2022 року Художній музей Куїнджі в Маріуполі зруйнував російський авіаудар.'),
       [('en', 'The Metropolitan Museum of Art', None, 'https://www.metmuseum.org/art/collection/search/436833', 'Kuindzhi Art Museum in Mariupol'),
        ('en', 'The Metropolitan Museum of Art', None, 'https://www.metmuseum.org/art/collection/search/437441', 'rural Ukrainian town of Chuhuiv'),
        ('en', 'The Guardian', '2023-03-19', 'https://www.theguardian.com/us-news/2023/mar/19/metropolitan-museum-art-reclassifies-russian-art-ukrainian', 'now categorized as Ukrainian')],
       photo=photo('fix-kuindzhi.jpg', ('Arkhyp Kuindzhi, Red Sunset, 1905–8, The Metropolitan Museum of Art', 'Архип Куїнджі, «Червоний захід сонця», 1905–1908, Метрополітен-музей'), 'Arkhyp Kuindzhi', 'Public domain', W + 'Red_Sunset_on_the_Dnieper_MET_DT2557.jpg')),
 entry('stedelijk-malevich', ('Malevich at the Stedelijk Museum, Amsterdam', 'Малевич у музеї Стеделейк, Амстердам'),
       ('By March 2023 the Stedelijk Museum in Amsterdam had stopped describing Kazimir Malevich, a leading figure of Suprematism, as Russian. It now says he was born in Ukraine to parents of Polish origin.',
        'Станом на березень 2023 року амстердамський музей Стеделейк уже не називав росіянином Казимира Малевича, одну з провідних постатей супрематизму. Тепер музей пише, що він народився в Україні в родині польського походження.'),
       [('en', 'The Art Newspaper', '2023-03-01', 'https://www.theartnewspaper.com/2023/03/01/russian-or-ukrainian-museums-update-kazimir-malevichs-nationality', 'born in Ukraine to parents of Polish origin')],
       photo=photo('fix-malevich.jpg', ('Kazimir Malevich, Hieratic Suprematist Cross, Stedelijk Museum Amsterdam', 'Казимир Малевич, «Ієратичний супрематичний хрест», музей Стеделейк, Амстердам'), 'Kazimir Malevich', 'Public domain', W + 'Malevitj.jpg')),
]

HOLIDAYS = [
 entry('vyshyvanka-day', ('Vyshyvanka Day', 'День вишиванки'),
       ('On Vyshyvanka Day Ukrainians wear traditional embroidered clothing. Lesia Voronyuk, a student at Chernivtsi National University, started it in 2006 to preserve Ukrainian folk traditions.',
        'У День вишиванки українці вдягають традиційний вишитий одяг. Свято започаткувала 2006 року Леся Воронюк, студентка Чернівецького національного університету, щоб зберегти українські народні традиції.'),
       [('en', 'RFE/RL', '2022-05-20', 'https://www.rferl.org/a/ukraine-tradition-vyshyvanka-day-russia/31859790.html', 'takes place on the third Thursday of May')],
       date=('Third Thursday of May', 'Третій четвер травня')),
 entry('kupala', ('Ivan Kupala', 'Івана Купала'),
       ('Ivan Kupala, one of the oldest festivals in Ukrainian culture, began as a pagan midsummer festival; the church tried to replace it with the feast of the Nativity of Saint John the Baptist, but it survived and took John’s name, Ivan. It is celebrated on the night of June 23–24.',
        'Івана Купала — одне з найдавніших свят в українській культурі — постало як язичницьке свято літнього сонцестояння; церква намагалася замінити його Різдвом Івана Хрестителя, але свято збереглося й отримало ім’я Івана. Його відзначають у ніч з 23 на 24 червня.'),
       [('uk', 'Суспільне Запоріжжя', '2026-06-23', 'https://suspilne.media/zaporizhzhia/1337930-ivana-kupala-2026-tradicii-magia-istoria-ta-ak-svatkuvali-na-hortici-v-zaporizzi/', 'у ніч проти 24 червня'),
        ('en', 'Encyclopedia of Ukraine, “Kupalo festival”', None, EOU + 'K%5CU%5CKupaloFestival.htm', 'Nativity of Saint John the Baptist')],
       date=('Night of June 23–24', 'Ніч з 23 на 24 червня')),
 entry('statehood-day', ('Day of Ukrainian Statehood', 'День Української Державності'),
       ('The Day of Ukrainian Statehood falls on July 15; the same 2023 law that moved Christmas moved it from July 28.',
        'День Української Державності відзначають 15 липня; той самий закон 2023 року, що переніс Різдво, переніс і це свято з 28 липня.'),
       [('en', 'The Kyiv Independent', '2023-07-28', 'https://kyivindependent.com/zelensky-signs-law/', 'moved from July 28 to July 15')],
       date=('July 15', '15 липня')),
 entry('flag-day', ('National Flag Day', 'День Державного Прапора'),
       ('Ukraine marks National Flag Day on August 23, the day before Independence Day, raising the blue and yellow flag.',
        'Україна відзначає День Державного Прапора 23 серпня, напередодні Дня Незалежності, піднімаючи синьо-жовтий прапор.'),
       [('en', 'Al Jazeera', '2026-08-23', 'https://www.aljazeera.com/gallery/2026/8/23/photos-ukraine-observes-national-flag-day', 'one day before its Independence Day')],
       date=('August 23', '23 серпня')),
 entry('independence-day', ('Independence Day', 'День Незалежності'),
       ('On August 24, 1991, the parliament of Soviet Ukraine declared Ukraine an independent state, and Ukraine celebrates Independence Day every August 24.',
        '24 серпня 1991 року Верховна Рада Української РСР проголосила Україну незалежною державою, і Україна святкує День Незалежності щороку 24 серпня.'),
       [('en', 'Encyclopedia of Ukraine, “Ukraine’s Declaration of Independence, 1991”', None, EOU + 'U%5CK%5CUkrainehDAsDeclarationofIndependence1991.htm', 'passed on 24 August 1991'),
        ('en', 'Al Jazeera', '2026-08-23', 'https://www.aljazeera.com/gallery/2026/8/23/photos-ukraine-observes-national-flag-day', 'one day before its Independence Day')],
       date=('August 24', '24 серпня'), related=('history', 'Independence')),
 entry('language-day', ('Day of Ukrainian Writing and Language', 'День української писемності та мови'),
       ('A presidential decree of July 28, 2023, moved the Day of Ukrainian Writing and Language from November 9 to October 27. Every year Ukrainians at home and abroad mark it by writing the nationwide Radio Dictation of National Unity.',
        'Указ Президента від 28 липня 2023 року переніс День української писемності та мови з 9 листопада на 27 жовтня. Щороку до цього дня українці в Україні й за кордоном пишуть Всеукраїнський радіодиктант національної єдності.'),
       [('uk', 'Уповноважений із захисту державної мови', '2023-09-27', 'https://mova-ombudsman.gov.ua/news/nahaduvannia-za-misiats-27-zhovtnia-den-ukrainskoi-pysemnosti-ta-movy', 'перенесена з 9 листопада на 27 жовтня'),
        ('uk', 'Радіо Свобода', '2023-10-27', 'https://www.radiosvoboda.org/a/news-radiodyktant-natsionalnoyi-yednosti/32656041.html', 'з 9 листопада на 27 жовтня')],
       date=('October 27', '27 жовтня')),
 entry('holodomor-remembrance', ('Holodomor Remembrance Day', 'День пам’яті жертв Голодомору'),
       ('On the fourth Saturday of November, Ukraine and the world honor the victims of the Holodomor. At 4 p.m. people light candles in their windows or at memorials.',
        'У четверту суботу листопада Україна та світ вшановують жертв Голодомору. О 16:00 люди запалюють свічки у вікнах або біля меморіалів.'),
       [('en', 'National Museum of the Holodomor-Genocide', '2020-11-20', 'https://holodomormuseum.org.ua/en/novyny/holodomor-remembrance-day-2020/', 'The fourth Saturday in November'),
        ('uk', 'Національний музей Голодомору-геноциду', '2020-11-20', 'https://holodomormuseum.org.ua/novyny/den-pam-iati-zhertv-holodomoru-2020/', 'Четверта субота листопада')],
       date=('Fourth Saturday of November', 'Четверта субота листопада'), related=('history', 'The Holodomor')),
 entry('christmas', ('Christmas', 'Різдво Христове'),
       ('Since 2023 Ukraine’s Christmas state holiday has fallen on December 25 instead of January 7, the day Russia keeps. President Zelenskyy signed the law on July 28, 2023, as part, he said, of renouncing Russian heritage.',
        'З 2023 року державне свято Різдва в Україні припадає на 25 грудня, а не на 7 січня, коли його відзначає Росія. Президент Зеленський підписав закон 28 липня 2023 року, назвавши це частиною відмови від російської спадщини.'),
       [('en', 'The Kyiv Independent', '2023-07-28', 'https://kyivindependent.com/zelensky-signs-law/', 'changing the date of the Christmas state holiday')],
       date=('December 25', '25 грудня')),
 entry('malanka', ('Malanka, or Shchedryi Vechir', 'Маланка, або Щедрий вечір'),
       ('Malanka, also called Shchedryi Vechir or Generous Eve, is a Ukrainian folk feast on New Year’s Eve, when carolers go from house to house singing shchedrivky to honor the household. Since 2023 it has fallen on the evening of December 31.',
        'Маланка, або Щедрий вечір, — українське народне свято напередодні Нового року, коли щедрувальники ходять від хати до хати й співають щедрівки, величаючи господарів. З 2023 року його відзначають увечері 31 грудня.'),
       [('en', 'Encyclopedia of Ukraine, “Malanka”', None, EOU + 'M%5CA%5CMalankaIT.htm', 'A Ukrainian folk feast on New Year'),
        ('uk', 'Суспільне Культура', '2023-12-29', 'https://suspilne.media/culture/648406-sedrij-vecir-abo-malanka-vidnini-31-grudna-pro-ukrainski-tradicii-svata/', 'увечері 31 грудня, в переддень календарного нового року')],
       date=('December 31', '31 грудня')),
]
UCU_FESTIVALS = 'https://ucufoundation.org/get-involved-event/upcoming-ukrainian-festivals/'

EVENTS = [
 entry('east-village-festival', ('Ukrainian Festival on East Seventh Street', 'Український фестиваль на Східній Сьомій вулиці'),
       ('A three-day street festival on East Seventh Street hosted by St. George Ukrainian Catholic Church, with Ukrainian food, live music, dance and vendors. In 2026 it marked its 50th anniversary.',
        'Триденний вуличний фестиваль на Східній Сьомій вулиці, який влаштовує українська католицька церква Святого Юра: українські страви, жива музика, танці та ярмарок. У 2026 році фестиваль відзначив 50-річчя.'),
       [('en', 'EV Grieve', '2026-05-13', 'https://evgrieve.com/2026/05/the-50th-anniversary-edition-of.html', 'Hosted by St. George Ukrainian Catholic Church'),
        ('en', 'Our Town', '2025-05-13', 'https://www.ourtownny.com/news/festival-in-east-village-aims-to-to-keep-ukrainian-culture-alive-ED4577521', 'from Friday, May 16 to Sunday, May 18')],
       where=('New York, NY', 'Нью-Йорк'), when=('Mid-May (May 15–17 in 2026)', 'Середина травня (15–17 травня 2026 року)')),
 entry('soyuzivka-ukraine-fest', ('Ukraine Fest at Soyuzivka', 'Український фестиваль на Союзівці'),
       ('A summer festival at Soyuzivka, a Ukrainian heritage center the Ukrainian National Association bought as a cultural center, with performers from the United States, Canada and Ukraine.',
        'Літній фестиваль на Союзівці — українському осередку, який Український народний союз придбав як культурний центр; виступають артисти зі США, Канади та України.'),
       [('en', 'Soyuzivka', None, 'https://soyuzivka.com/calendar-of-events/ukrainian-festival/', 'promoting Ukrainian entertainers'),
        ('en', 'Soyuzivka', None, 'https://soyuzivka.com/festival/', 'from the United States, Canada, and Ukraine'),
        ('en', 'Soyuzivka', None, 'https://soyuzivka.com/', 'purchased Soyuzivka to serve as a cultural center')],
       where=('Kerhonkson, NY', 'Кергонксон, штат Нью-Йорк'), when=('July (July 10–12 in 2026)', 'Липень (10–12 липня 2026 року)')),
 entry('rochester-ukrainian-festival', ('St. Josaphat’s Ukrainian Festival', 'Український фестиваль парафії святого Йосафата'),
       ('Founded in 1973 to share Ukrainian crafts, food, music and dance with the Rochester area.',
        'Фестиваль, заснований 1973 року, знайомить жителів Рочестера з українськими ремеслами, кухнею, музикою й танцем.'),
       [('en', 'St. Josaphat’s Ukrainian Festival', None, 'https://www.rochesterukrainianfestival.com/about.php', 'was established in 1973'),
        ('en', 'St. Josaphat’s Ukrainian Festival', None, 'https://www.rochesterukrainianfestival.com/', 'August 13-16, 2026')],
       where=('Rochester, NY', 'Рочестер, штат Нью-Йорк'), when=('August (August 13–16 in 2026)', 'Серпень (13–16 серпня 2026 року)')),
 entry('ukrainian-village-fest-chicago', ('Ukrainian Village Fest', 'Фестиваль «Українське село»'),
       ('A two-day street festival run by Sts. Volodymyr and Olha Ukrainian Catholic Parish in Chicago, with Ukrainian vendors, performers and food.',
        'Дводенний вуличний фестиваль української католицької парафії святих Володимира і Ольги в Чикаго: українські продавці, виконавці та страви.'),
       [('en', 'Ukrainian Congress Committee of America, Illinois', None, 'https://uccaillinois.org/event/ukrainian-village-fest-2/', 'Two-day street festival showcasing Ukrainian vendors'),
        ('en', 'Ukrainian Catholic University Foundation', None, UCU_FESTIVALS, 'August 15–16, 2026')],
       where=('Chicago, IL', 'Чикаго, штат Іллінойс'), when=('Mid-August (August 15–16 in 2026)', 'Середина серпня (15–16 серпня 2026 року)')),
 entry('tryzub-independence-festival', ('Ukrainian Independence Day Folk Festival at Tryzub', 'Фольклорний фестиваль до Дня незалежності України в центрі «Тризуб»'),
       ('Held every year at the Ukrainian American Sport Center Tryzub to mark Ukraine’s Independence Day, with Ukrainian music, song and dance, food and a crafts market. Of each paid admission, $2 goes to humanitarian aid for victims of the war in Ukraine.',
        'Щорічний фестиваль в Українсько-американському спортивному центрі «Тризуб» до Дня незалежності України: українська музика, пісні й танці, кухня та ярмарок ремесел. З кожного платного квитка 2 долари передають на гуманітарну допомогу постраждалим від війни в Україні.'),
       [('en', 'Ukrainian American Sport Center Tryzub', None, 'https://www.tryzub.org/', 'Annual Ukrainian Independence Day Folk Festival'),
        ('en', 'Ukrainian American Sport Center Tryzub', None, 'https://www.tryzub.org/Ukraine-Festival-2026', 'donated to Humanitarian Aid for Victims of War in Ukraine')],
       where=('Horsham, PA', 'Горшем, штат Пенсільванія'), when=('Late August (August 23 in 2026)', 'Кінець серпня (23 серпня 2026 року)')),
 entry('colorado-ukrainian-festival', ('Colorado Ukrainian Festival', 'Український фестиваль Колорадо'),
       ('A one-day festival run by Ukrainians of Colorado with Ukrainian music, dance, food and art. All proceeds go to humanitarian aid in Ukraine.',
        'Одноденний фестиваль, який влаштовує організація Ukrainians of Colorado: українська музика, танці, кухня й мистецтво. Усі кошти, зібрані на фестивалі, йдуть на гуманітарну допомогу в Україні.'),
       [('en', 'Ukrainians of Colorado', None, 'https://www.ukrainiansofcolorado.org/events', 'All proceeds from the Colorado Ukrainian Festival'),
        ('en', 'Ukrainians of Colorado', None, 'https://www.ukrainiansofcolorado.org/events', 'Saturday, August 22, 2026')],
       where=('Lakewood, CO', 'Лейквуд, штат Колорадо'), when=('Late August (August 22 in 2026)', 'Кінець серпня (22 серпня 2026 року)')),
 entry('house-of-ukraine-festival', ('Ukrainian Festival at the House of Ukraine', 'Український фестиваль у Домі України'),
       ('A one-day festival at the House of Ukraine, one of the international cottages in Balboa Park, with a free program of Ukrainian music and dance on the lawn. Proceeds support humanitarian aid to Ukraine.',
        'Одноденний фестиваль у Домі України — одному з міжнародних котеджів у парку Бальбоа — з безкоштовною програмою української музики й танцю на газоні просто неба. Виторг іде на гуманітарну допомогу Україні.'),
       [('en', 'House of Ukraine', None, 'https://houseofukraine.org/event/lawn-program-2026/', 'House of Ukraine @ Balboa Park'),
        ('en', 'KPBS', None, 'https://www.kpbs.org/events/2026/09/05/ukrainian-festival-free-lawn-program', 'Proceeds support humanitarian aid to Ukraine.')],
       where=('San Diego, CA', 'Сан-Дієго, штат Каліфорнія'), when=('September (September 5 in 2026)', 'Вересень (5 вересня 2026 року)')),
 entry('washington-ukrainian-festival', ('Washington Ukrainian Festival', 'Вашингтонський український фестиваль'),
       ('A weekend festival on the grounds of St. Andrew’s Ukrainian Orthodox Cathedral, with a full Ukrainian kitchen run by parishioners and visiting chefs.',
        'Фестиваль на вихідних на території українського православного собору Святого Андрія з українською кухнею, яку готують парафіяни та запрошені кухарі.'),
       [('en', 'Washington Ukrainian Festival', None, 'https://www.ukrainefestdc.com/', 'A full Ukrainian kitchen run by parishioners'),
        ('en', 'Washington Ukrainian Festival', None, 'https://www.ukrainefestdc.com/', 'St. Andrew\'s Ukrainian Orthodox Cathedral')],
       where=('Silver Spring, MD', 'Сілвер-Спрінг, штат Меріленд'), when=('September (September 18–20 in 2026)', 'Вересень (18–20 вересня 2026 року)')),
 entry('uaccnj-ukrainian-festival', ('Ukrainian Festival at the UACCNJ', 'Український фестиваль Українсько-американського культурного центру Нью-Джерсі'),
       ('The annual festival of the Ukrainian American Cultural Center of New Jersey, with food, entertainment and vendors.',
        'Щорічний фестиваль Українсько-американського культурного центру Нью-Джерсі: страви, розваги та ярмарок.'),
       [('en', 'Ukrainian American Cultural Center of New Jersey', None, 'https://uaccnj.org/event/17th-annual-ukrainian-festival/', 'Annual Ukrainian Festival'),
        ('en', 'Ukrainian Catholic University Foundation', None, UCU_FESTIVALS, 'September, 26, 2026')],
       where=('Whippany, NJ', 'Віппані, штат Нью-Джерсі'), when=('Late September (September 26 in 2026)', 'Кінець вересня (26 вересня 2026 року)')),
 entry('ukrainian-festival-minnesota', ('Ukrainian Festival of Minnesota', 'Український фестиваль Міннесоти'),
       ('Held at the Ukrainian American Community Center since 2006, with Ukrainian dance, music, food and drinks. The 2026 festival was postponed for the center’s renovation.',
        'З 2006 року фестиваль відбувається в Українсько-американському громадському центрі: український танець, музика, страви й напої. У 2026 році його перенесли через ремонт центру.'),
       [('en', 'Ukrainian Festival of Minnesota', None, 'https://ukrainianfestivalmn.com/', 'In 2026 the Ukrainian Festival has been postponed'),
        ('en', 'Ukrainian American Community Center', None, 'https://uaccmn.org/arts-and-culture/ukrainian-festival-of-minnesota/', 'Since 2006 the UACCMN has been the site'),
        ('en', 'Ukrainian American Community Center', None, 'https://uaccmn.org/arts-and-culture/ukrainian-festival-of-minnesota/', 'on the third weekend of September')],
       where=('Minneapolis, MN', 'Міннеаполіс, штат Міннесота'), when=('Third weekend of September; postponed in 2026', 'Третій вікенд вересня; у 2026 році перенесено')),
 entry('holodomor-commemoration-nyc', ('Holodomor commemoration at St. Patrick’s Cathedral', 'Вшанування пам’яті жертв Голодомору в соборі Святого Патрика'),
       ('A memorial service for the victims of the Holodomor, organized by the Ukrainian Congress Committee of America and held at the cathedral every year since 1987.',
        'Панахида за жертвами Голодомору, яку організовує Український конгресовий комітет Америки; у соборі її проводять щороку з 1987 року.'),
       [('en', 'The Ukrainian Weekly', '2025-11-27', 'https://subscription.ukrweekly.com/thousands-gather-in-st-patricks-cathedral-to-commemorate-holodomor-victims/', 'Organized by the Ukrainian Congress Committee of America'),
        ('en', 'The Ukrainian Weekly', '2025-11-27', 'https://subscription.ukrweekly.com/thousands-gather-in-st-patricks-cathedral-to-commemorate-holodomor-victims/', 'every year since 1987')],
       where=('New York, NY', 'Нью-Йорк'), when=('November (November 22 in 2025)', 'Листопад (22 листопада 2025 року)'), related=('history', 'The Holodomor')),
 entry('parma-ukrainian-village-parade', ('Ukrainian Village Parade & Festival', 'Парад і фестиваль «Українське село»'),
       ('A parade and festival in Parma’s Ukrainian Village. Since 2011 the parade has been a symbol of the community’s celebration of Ukraine’s independence.',
        'Парад і фестиваль в Українському селі в Пармі. Від 2011 року парад став для громади символом святкування незалежності України.'),
       [('en', 'Ukrainian Village in Parma', None, 'https://ukrainianvillageparma.org/', 'Since 2011, the parade has become a symbol'),
        ('en', 'City of Parma', None, 'https://cityofparma-oh.gov/Calendar.aspx?EID=826', 'Saturday, August 22, 2026')],
       where=('Parma, OH', 'Парма, штат Огайо'), when=('Late August (August 22 in 2026)', 'Кінець серпня (22 серпня 2026 року)')),
]

RESOURCES = [
 entry('ukrainian-museum-nyc', ('The Ukrainian Museum', 'Український музей'),
       ('Founded by the Ukrainian National Women’s League of America, the museum has been in Manhattan’s East Village, also called Little Ukraine, since 1976. Its collection holds more than 8,000 folk art objects, along with fine art and archives.',
        'Музей заснував Союз українок Америки; з 1976 року він працює в манхеттенському Іст-Віллиджі, який ще називають Маленькою Україною. Його колекція налічує понад 8000 предметів народного мистецтва, а також твори образотворчого мистецтва й архівні матеріали.'),
       [('en', 'own website', None, 'https://www.theukrainianmuseum.org/about-the-museum/', 'Since 1976, The Ukrainian Museum has been'),
        ('en', 'own website', None, 'https://www.theukrainianmuseum.org/about-the-museum/', 'more than 8,000 folk art objects'),
        ('en', 'own website', None, 'https://www.theukrainianmuseum.org/', 'also known as Little Ukraine')],
       where=('New York, NY', 'Нью-Йорк'), url='https://www.theukrainianmuseum.org/'),
 entry('ukrainian-national-museum-chicago', ('Ukrainian National Museum of Chicago', 'Український національний музей у Чикаго'),
       ('Founded in 1952 by displaced scholars, the museum holds folk art, fine art and an archive, with embroidery from across Ukraine on permanent display.',
        'Музей заснували 1952 року вчені-переселенці; тут зберігаються народне та образотворче мистецтво й архів, а вишивка з усієї України представлена в постійній експозиції.'),
       [('en', 'own website', None, 'https://ukrainiannationalmuseum.org/history-2/', 'founded in 1952 by displaced scholars'),
        ('en', 'own website', None, 'https://ukrainiannationalmuseum.org/', 'Ukrainian Embroidery from across Ukraine on Permanent Display')],
       where=('Chicago, IL', 'Чикаго, штат Іллінойс'), url='https://ukrainiannationalmuseum.org/'),
 entry('uima-chicago', ('Ukrainian Institute of Modern Art', 'Український інститут модерного мистецтва'),
       ('Founded in 1971 in Chicago’s Ukrainian Village, the institute shows contemporary art and hosts concerts, readings, lectures and films. Its permanent collection includes works by Alexander Archipenko.',
        'Інститут заснували 1971 року в чиказькому Українському селі; тут показують сучасне мистецтво, влаштовують концерти, читання, лекції та кінопокази. У постійній колекції є твори Олександра Архипенка.'),
       [('en', 'own website', None, 'https://uima-chicago.org/about-2-1', 'The Institute was founded in 1971'),
        ('en', 'own website', None, 'https://uima-chicago.org/about-2-1', 'Located in the heart of Ukrainian Village'),
        ('en', 'own website', None, 'https://uima-chicago.org/about-2-1', 'Alexander Archipenko')],
       where=('Chicago, IL', 'Чикаго, штат Іллінойс'), url='https://uima-chicago.org/'),
 entry('ukrainian-museum-archives-cleveland', ('Ukrainian Museum-Archives', 'Український музей-архів'),
       ('Displaced scholars founded it in 1952 to preserve Ukrainian history and culture while such material was being deliberately destroyed in Soviet Ukraine. It holds Ukrainian sacred art and a library of more than 45,000 books.',
        'Музей-архів заснували 1952 року вчені-переселенці, щоб зберегти пам’ятки української історії та культури, які в Радянській Україні тоді навмисно знищували. Тут є українське сакральне мистецтво та бібліотека з понад 45 000 книжок.'),
       [('en', 'own website', None, 'https://umacleveland.org/', 'deliberately destroyed in Soviet Ukraine'),
        ('en', 'own website', None, 'https://umacleveland.org/', 'world-class assembly of Ukrainian sacred art'),
        ('en', 'own website', None, 'https://umacleveland.org/', 'over 45,000 books')],
       where=('Cleveland, OH', 'Клівленд, штат Огайо'), url='https://umacleveland.org/'),
 entry('uhec-somerset', ('Ukrainian History and Education Center', 'Український історично-освітній центр'),
       ('The center tells the story of Ukraine and of Ukrainian Americans through exhibitions, archives and educational programs. Its museum holds more than 15,000 objects, and its genealogy group helps people search for Ukrainian ancestors.',
        'Центр розповідає про Україну та українських американців через виставки, архіви й освітні програми. Музейна колекція налічує понад 15 000 предметів, а генеалогічна група допомагає шукати українських предків.'),
       [('en', 'own website', None, 'https://www.ukrhec.org/', 'of Ukraine and the Ukrainian American experience'),
        ('en', 'own website', None, 'https://www.ukrhec.org/', 'over 15,000 objects of folk art'),
        ('en', 'own website', None, 'https://www.ukrhec.org/', 'Ukrainian Genealogy Group')],
       where=('Somerset, NJ', 'Сомерсет, штат Нью-Джерсі'), url='https://www.ukrhec.org/'),
 entry('ukrainian-institute-of-america', ('Ukrainian Institute of America', 'Український інститут Америки'),
       ('Founded in 1948 by the inventor William Dzus, the institute is housed in a landmark mansion at Fifth Avenue and East 79th Street. It hosts exhibits, concerts, films, readings and lectures, all open to the public.',
        'Інститут, який 1948 року заснував винахідник Вільям Дзус, міститься в історичному особняку на розі П’ятої авеню та Східної 79-ї вулиці. Тут відбуваються виставки, концерти, кінопокази, читання й лекції, відкриті для всіх.'),
       [('en', 'own website', None, 'https://ukrainianinstitute.org/', 'Founded in 1948 by William Dzus'),
        ('en', 'own website', None, 'https://ukrainianinstitute.org/', '2 East 79th Street and Fifth Avenue'),
        ('en', 'own website', None, 'https://ukrainianinstitute.org/', 'all open to the public')],
       where=('New York, NY', 'Нью-Йорк'), url='https://ukrainianinstitute.org/'),
 entry('ukrainian-lessons', ('Ukrainian Lessons with Anna Ohoiko', 'Ukrainian Lessons з Анною Огойко'),
       ('Anna Ohoiko, a Ukrainian teacher, runs podcast courses from beginner to advanced level and a free blog that works as a digital textbook.',
        'Анна Огойко, викладачка української мови, веде подкасти для рівнів від початкового до просунутого та безкоштовний блог, що працює як цифровий підручник.'),
       [('en', 'own website', None, 'https://www.ukrainianlessons.com/', 'a Ukrainian teacher and founder of Ukrainian Lessons'),
        ('en', 'own website', None, 'https://www.ukrainianlessons.com/', 'Ukrainian digital textbook'),
        ('en', 'own website', None, 'https://www.ukrainianlessons.com/thepodcast/', 'weekly Ukrainian Lessons Podcast episodes')],
       where=('Online', 'Онлайн'), url='https://www.ukrainianlessons.com/'),
 entry('duolingo-ukrainian', ('Ukrainian on Duolingo', 'Українська на Duolingo'),
       ('Duolingo’s Ukrainian course was developed in 2015 with the Peace Corps. After Russia’s full-scale invasion in 2022, more than 1.3 million people around the world began studying Ukrainian on it.',
        'Курс української на Duolingo створили 2015 року разом із Корпусом миру. Після повномасштабного вторгнення Росії 2022 року понад 1,3 мільйона людей у світі почали вчити на ньому українську.'),
       [('en', '90.5 WESA', '2022-03-24', 'https://www.wesanews.org/arts-sports-culture/2022-03-24/as-war-in-ukraine-continues-people-around-the-world-are-signing-up-to-learn-the-ukrainian-language', 'in 2015 in partnership with the Peace Corps'),
        ('en', 'Duolingo', None, 'https://blog.duolingo.com/2022-duolingo-language-report/', 'began studying Ukrainian in a show of solidarity')],
       where=('Online', 'Онлайн'), url='https://www.duolingo.com/course/uk/en/Learn-Ukrainian'),
 entry('harvard-ukrainian-summer-institute', ('Harvard Ukrainian Summer Institute', 'Гарвардський український літній інститут'),
       ('Held every summer since 1971, the institute offers seven weeks of Harvard Summer School courses in Ukrainian studies; in 2026 they included Ukrainian for Reading Knowledge. Competitive need-based scholarships are available.',
        'Інститут працює щоліта з 1971 року й пропонує семитижневі курси з українознавства в Гарвардській літній школі; 2026 року серед них був курс читання українською. Можна отримати конкурсну стипендію з урахуванням фінансових потреб.'),
       [('en', 'Harvard Ukrainian Research Institute', None, 'https://www.huri.harvard.edu/harvard-ukrainian-summer-institute', 'Every summer since 1971'),
        ('en', 'Harvard Ukrainian Research Institute', None, 'https://www.huri.harvard.edu/harvard-ukrainian-summer-institute', 'Ukrainian for Reading Knowledge'),
        ('en', 'Harvard Ukrainian Research Institute', None, 'https://www.huri.harvard.edu/harvard-ukrainian-summer-institute', 'Scholarships are highly competitive and need-based')],
       where=('Cambridge, MA', 'Кембридж, штат Массачусетс'), url='https://www.huri.harvard.edu/harvard-ukrainian-summer-institute'),
 entry('ui-speaking-club', ('Ukrainian Language Speaking Club', 'Розмовний клуб української мови'),
       ('A free online speaking club from the Ukrainian Institute in Kyiv for international learners of Ukrainian at level B1 or above, meeting weekly on Zoom.',
        'Безкоштовний онлайн-розмовний клуб Українського інституту в Києві для іноземців, які вивчають українську на рівні B1 і вище; заняття щотижня в Zoom.'),
       [('en', 'Ukrainian Institute', '2026-07-14', 'https://ui.org.ua/en/news-en/the-ukrainian-institute-is-launching-a-ukrainian-language-speaking-club-for-international-learners/', 'B1 level or above'),
        ('en', 'Ukrainian Institute', '2026-07-14', 'https://ui.org.ua/en/news-en/the-ukrainian-institute-is-launching-a-ukrainian-language-speaking-club-for-international-learners/', 'Sessions will be held online via Zoom')],
       where=('Online', 'Онлайн'), url='https://ui.org.ua/en/news-en/the-ukrainian-institute-is-launching-a-ukrainian-language-speaking-club-for-international-learners/'),
 entry('harvard-library-ukrainian-literature', ('Harvard Library of Ukrainian Literature', 'Гарвардська бібліотека української літератури'),
       ('A book series from Harvard’s Ukrainian Research Institute, launched in 2021, that publishes Ukrainian literature in English translation and is distributed by Harvard University Press.',
        'Книжкова серія Українського наукового інституту Гарвардського університету, яка видає українську літературу в англійських перекладах; її започаткували 2021 року, а поширює Harvard University Press.'),
       [('en', 'Harvard Ukrainian Research Institute', '2021-08-06', 'https://www.huri.harvard.edu/news/huri-launches-new-publications-series-harvard-library-ukrainian-literature', 'outstanding Ukrainian literature in English translation'),
        ('en', 'Harvard Ukrainian Research Institute', '2021-08-06', 'https://www.huri.harvard.edu/news/huri-launches-new-publications-series-harvard-library-ukrainian-literature', 'distributed by Harvard University Press')],
       where=('Online and in print', 'Онлайн і друком'), url='https://books.huri.harvard.edu/'),
 entry('ukraine-history-culture-course', ('Ukraine: History, Culture and Identities', '«Україна: історія, культура та ідентичності»'),
       ('A free English-language online course on Ukraine’s history, culture and society from the Middle Ages to the present day, made by the Ukrainian Institute with the EdEra online education studio and the National University of Kyiv-Mohyla Academy, and offered on Coursera.',
        'Безкоштовний англомовний онлайн-курс про історію, культуру та суспільство України від Середньовіччя до сьогодення, створений Українським інститутом разом зі студією онлайн-освіти EdEra та Національним університетом «Києво-Могилянська академія»; доступний на Coursera.'),
       [('en', 'Ukrainian Institute', None, 'https://ui.org.ua/en/news-en/the-course-about-history-and-culture-of-ukraine-is-now-available-on-coursera/', 'The course is free of charge.'),
        ('en', 'Ukrainian Institute', None, 'https://ui.org.ua/en/news-en/the-course-about-history-and-culture-of-ukraine-is-now-available-on-coursera/', 'from the Middle Ages to the present day'),
        ('uk', 'Український інститут', None, 'https://ui.org.ua/news/news-academic-programmes/kurs-pro-istoriyu-ta-kulturu-ukrayiny-teper-na-coursera/', 'Києво-Могилянська академія')],
       where=('Online', 'Онлайн'), url='https://www.coursera.org/learn/ukraine-history-culture-and-identities'),
 entry('ukrainer', ('Ukraїner', 'Ukraїner'),
       ('A multilingual nonprofit media outlet with stories about Ukraine’s regions, people and culture. Several of the stories on the People tab come from it.',
        'Багатомовне некомерційне медіа з історіями про регіони, людей і культуру України. Кілька історій у розділі «Люди» взято саме звідти.'),
       [('en', 'own website', None, 'https://www.ukrainer.net/en/', 'multilingual non-profit media organisation'),
        ('uk', 'own website', None, 'https://www.ukrainer.net/', 'Досліджуємо Україну')],
       where=('Online', 'Онлайн'), url='https://www.ukrainer.net/en/'),
 entry('encyclopedia-of-ukraine', ('Internet Encyclopedia of Ukraine', 'Інтернет-енциклопедія України'),
       ('Run by the Canadian Institute of Ukrainian Studies, it calls itself the most comprehensive English-language source of authoritative information on Ukraine. Most of the history on this page draws on it.',
        'Енциклопедію веде Канадський інститут українських студій; вона називає себе найповнішим англомовним джерелом авторитетної інформації про Україну. Більшість історичного розділу цієї сторінки спирається саме на неї.'),
       [('en', 'Canadian Institute of Ukrainian Studies', None, 'https://www.encyclopediaofukraine.com/', 'most comprehensive source of authoritative information in English')],
       where=('Online', 'Онлайн'), url='https://www.encyclopediaofukraine.com/'),
]

SECTIONS = [  # id, title, introduction, entries
 ('culture-food', ('Food and recipes', 'Кухня та рецепти'),
  ('Dishes that are Ukrainian by origin, each with a recipe from a Ukrainian source. The recipes stay on their authors’ sites.',
   'Страви українського походження, до кожної — рецепт з українського джерела. Рецепти залишаються на сайтах їхніх авторів.'), DISHES),
 ('culture-traditions', ('Traditions, crafts and music', 'Традиції, ремесла та музика'),
  ('Several are on UNESCO’s lists of intangible cultural heritage.', 'Деякі з них внесено до списків нематеріальної культурної спадщини ЮНЕСКО.'), TRADITIONS),
 ('culture-corrections', ('Ukrainian, not Russian', 'Українське, а не російське'),
  ('Museums and institutions that have corrected how they label Ukrainian art and artists.', 'Музеї та установи, які виправили підписи до українського мистецтва й митців.'), CORRECTIONS),
 ('culture-holidays', ('Holidays and dates', 'Свята та пам’ятні дати'), None, HOLIDAYS),
 ('culture-events', ('Ukrainian festivals in the United States', 'Українські фестивалі у Сполучених Штатах'),
  ('Recurring events open to the public. Dates change from year to year, so check the organizer’s page.', 'Регулярні події, відкриті для всіх. Дати щороку змінюються, тож перевіряйте сторінку організатора.'), EVENTS),
 ('culture-resources', ('Museums and ways to learn more', 'Музеї та де дізнатися більше'), None, RESOURCES),
]

# How entries are shown. The build checks each against the entry's own text, so nothing here says more than its sources.
# The year UNESCO listed an entry, shown as a badge; the entry's text must name UNESCO and the year.
UNESCO_YEAR = {'borshch': '2022', 'petrykivka': '2013', 'kosiv-ceramics': '2019', 'pysanka': '2024', 'kobzars': '2024', 'cossack-songs': '2016', 'ornek': '2021'}
# The label each museum dropped and the one it uses now, each (English, Ukrainian); the English must be in the entry's text.
RELABELS = {
    'national-gallery-degas': (('Russian Dancers', 'Російські танцівниці'), ('Ukrainian Dancers', 'Українські танцівниці')),
    'met-degas': (('Russian Dancers', 'Російські танцівниці'), ('Dancers in Ukrainian Dress', 'Танцівниці в українському вбранні')),
    'met-kuindzhi-repin': (('Russian', 'Росіяни'), ('Ukrainian', 'Українці')),
    'stedelijk-malevich': (('Russian', 'Росіянин'), ('Born in Ukraine to parents of Polish origin', 'Народився в Україні в родині польського походження')),
}
# What each resource is for, with its label and icon.
RESOURCE_KINDS = {
    'visit': (('Visit', 'Відвідати'), ['ukrainian-museum-nyc', 'ukrainian-national-museum-chicago', 'uima-chicago', 'ukrainian-museum-archives-cleveland', 'uhec-somerset', 'ukrainian-institute-of-america']),
    'learn': (('Learn', 'Навчатися'), ['ukrainian-lessons', 'duolingo-ukrainian', 'harvard-ukrainian-summer-institute', 'ui-speaking-club', 'ukraine-history-culture-course']),
    'read': (('Read', 'Читати'), ['harvard-library-ukrainian-literature', 'ukrainer', 'encyclopedia-of-ukraine']),
}
KIND_OF_RESOURCE = {key: kind for kind, (_, keys) in RESOURCE_KINDS.items() for key in keys}
# Line icons, 24 by 24, drawn with the stroke: a building with columns, a speech bubble, an open book, a map pin.
ICONS = {
    'visit': 'M3 21h18M4 9.5h16M12 3 4 7.5h16ZM6.5 9.5v8.5M10 9.5v8.5M14 9.5v8.5M17.5 9.5v8.5M3.5 18h17',
    'learn': 'M4 5h16v10H9l-5 4ZM8 9h8M8 12h5',
    'read': 'M12 6.5C10 5 7 4.5 3.5 5v13c3.5-.5 6.5 0 8.5 1.5 2-1.5 5-2 8.5-1.5V5C17 4.5 14 5 12 6.5ZM12 6.5v13',
    'pin': 'M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11ZM12 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z',
}
MONTHS_SHORT = (['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                ['Січ', 'Лют', 'Бер', 'Квіт', 'Трав', 'Черв', 'Лип', 'Серп', 'Вер', 'Жовт', 'Лист', 'Груд'])

def leaf(text):
    """(month index, day or days or None) from an English date such as 'Night of June 23–24' or 'Mid-May (May 15–17 in 2026)'."""
    month = re.search('|'.join(MONTHS_EN), text)
    if not month: raise ValueError(f'no month in the date {text!r}')
    day = re.search(r'\b(\d{1,2}(?:–\d{1,2})?)\b(?!\d)', text[month.start():])
    return MONTHS_EN.index(month.group()), day.group(1) if day else None

def _validate():
    keys = set()
    photos.validate(HERO, 'header photo')
    for v in GALLERY: photos.validate(v['photo'], v['photo']['file'])
    for section_id, _, _, entries in SECTIONS:
        for x in entries:
            where = f"{section_id}: {x['key']}"
            for field in ('name', 'about') + tuple(f for f in ('date', 'where', 'when') if f in x):
                if len(x[field]) != 2 or not all(t.strip() for t in x[field]): raise ValueError(f'{where}: {field} needs English and Ukrainian text')
            if '“' in x['about'][0] or '"' in x['about'][0]: raise ValueError(f'{where}: write the text in our own words, without quotations')
            if not x['sources']: raise ValueError(f'{where}: no source')
            for lang, by, date, url, says in x['sources'] + [(lang, by, None, url, says) for lang, by, url, says in x.get('recipes', [])]:
                if lang not in ('en', 'uk') or not by or not url.startswith('https://') or not says.strip(): raise ValueError(f'{where}: bad source {url}')
                if date: datetime.date.fromisoformat(date)
            if x.get('photo'): photos.validate(x['photo'], where)
            if x['key'] in keys: raise ValueError(f'two Culture entries have the key {x["key"]}')
            keys.add(x['key'])
    for key, year in UNESCO_YEAR.items():
        x = next((x for _, _, _, entries in SECTIONS for x in entries if x['key'] == key), None)
        if not x or 'UNESCO' not in x['about'][0] or year not in x['about'][0]: raise ValueError(f'UNESCO_YEAR: {key} does not say UNESCO listed it in {year}')
    if set(RELABELS) != {x['key'] for x in CORRECTIONS}: raise ValueError('RELABELS needs exactly one entry per correction')
    for x in CORRECTIONS:
        for en, _ in RELABELS[x['key']]:
            if en.casefold() not in x['about'][0].casefold(): raise ValueError(f"RELABELS: {x['key']} does not say {en!r}")
    if set(KIND_OF_RESOURCE) != {x['key'] for x in RESOURCES} or len(KIND_OF_RESOURCE) != len(RESOURCES): raise ValueError('RESOURCE_KINDS needs every resource exactly once')
    for x in HOLIDAYS: leaf(x['date'][0])
    for x in EVENTS: leaf(x['when'][0])
_validate()

def photo_files():
    """The image files the tab and the header use, for build.py to copy."""
    entries = [x for _, _, _, items in SECTIONS for x in items]
    return [photos.IMAGES / p['file'] for p in [HERO] + [v['photo'] for v in GALLERY] + [x['photo'] for x in entries if x.get('photo')]]

def claims():
    """(url, phrase, what) for check.py: every source and recipe, and every photo's license."""
    out = [photos.claim(HERO, 'header photo: license')] + [photos.claim(v['photo'], f"photo {v['photo']['file']}: license") for v in GALLERY]
    for _, _, _, entries in SECTIONS:
        for x in entries:
            out += [(url, says, f"culture {x['key']}: {by}") for _, by, _, url, says in x['sources']]
            out += [(url, says, f"culture {x['key']}: recipe from {by}") for _, by, url, says in x.get('recipes', [])]
            if x.get('photo'): out.append(photos.claim(x['photo'], f"culture {x['key']}: photo license"))
    return out

def hero_credit():
    return photos.credit(HERO)

def _icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{ICONS[name]}"/></svg>'

def _sources(x):
    """The sources on one line, opening to the links with their dates; sources in the reader's language come first."""
    e = html.escape
    own = lambda by, label: label if by == 'own website' else by
    items = [(lang, by, date, url) for lang, by, date, url, _ in x['sources']]
    names = lambda i: list(dict.fromkeys(own(by, ('its own website', 'власний сайт')[i]) for _, by, _, _ in items))
    other = {'en': ('in English', 'англійською'), 'uk': ('in Ukrainian', 'українською')}
    summary, lists = [], []
    for i, lang in enumerate(('en', 'uk')):
        n = names(i)
        label = (('Source', 'Sources'), ('Джерело', 'Джерела'))[i][len(n) > 1]
        attrs = 'data-l="en"' if lang == 'en' else 'data-l="uk" lang="uk"'
        summary.append(f'<span {attrs}>{label}: {e(", ".join(n))}</span>')
        links = []
        for item_lang, by, date, url in sorted(items, key=lambda x: x[0] != lang):
            when = f', {dates(date)[i]}' if date else ''
            note = '' if item_lang == lang else f' <span class="src-lang">({other[item_lang][i]})</span>'
            links.append(f'<li><a href="{e(url)}" target="_blank" rel="noopener">{e(own(by, ("its website", "сайт")[i]))}{when}</a>{note}</li>')
        lists.append(f'<ul {attrs}>{"".join(links)}</ul>')
    return f'<details class="why"><summary>{"".join(summary)}</summary>{"".join(lists)}</details>'

def _recipes(x):
    """Recipe buttons, each naming its author and language; recipes in the reader's language come first."""
    e = html.escape; out = []
    names = {'en': ('English', 'англійською'), 'uk': ('Ukrainian', 'українською')}
    for i, lang in enumerate(('en', 'uk')):
        attrs = 'data-l="en"' if lang == 'en' else 'data-l="uk" lang="uk"'
        label = (('Recipe', 'Recipes'), ('Рецепт', 'Рецепти'))[i][len(x['recipes']) > 1]
        buttons = ''.join(f'<a class="recipe-btn" href="{e(url)}" target="_blank" rel="noopener">{e(by)} <span class="recipe-lang">{names[item_lang][i]}</span><span class="visually-hidden">: {e(x["name"][i])}</span></a>'
                          for item_lang, by, url, _ in sorted(x['recipes'], key=lambda r: r[0] != lang))
        out.append(f'<div class="recipes" {attrs}><span class="recipes-label">{label}</span>{buttons}</div>')
    return ''.join(out)

def _timeline(x, targets):
    if not x.get('related'): return ''
    target_id, en, uk = targets[x['related']]
    return f'<p class="c-link"><a href="#{target_id}">{both("In the timeline: " + en, "В історії: " + uk)}</a></p>'

def _media(x):
    """The entry's photo with its credit, or, without one, its Ukrainian name on an embroidery pattern."""
    badge = f'<span class="badge">{both("UNESCO " + UNESCO_YEAR[x["key"]], "ЮНЕСКО " + UNESCO_YEAR[x["key"]])}</span>' if x['key'] in UNESCO_YEAR else ''
    if x.get('photo'):
        return f'<figure class="c-media">{badge}{photos.img(x["photo"])}<figcaption class="credit">{photos.credit(x["photo"])}</figcaption></figure>'
    return f'<div class="c-media c-ornament" aria-hidden="true">{badge}<span class="c-ornament-name" lang="uk">{html.escape(x["name"][1])}</span></div>'

def _head(x):
    """The entry's name, with its Ukrainian name under it on the English page."""
    native = f'<p class="c-native" data-l="en" lang="uk">{html.escape(x["name"][1])}</p>' if x['name'][1] != x['name'][0] else ''
    return f'<h4 class="c-name">{both(*x["name"])}</h4>{native}'

def _card(x, section_id, targets):
    """A dish or a tradition: picture, name, text, recipes, sources."""
    return f"""        <article class="culture-item c-card" id="{section_id}-{x['key']}" tabindex="-1">
          {_media(x)}
          <div class="c-body">
            {_head(x)}
            <p class="c-about">{both(*x['about'])}</p>
            {_recipes(x) if 'recipes' in x else ''}{_timeline(x, targets)}
            {_sources(x)}
          </div>
        </article>"""

def _correction(x, section_id, targets):
    """A museum's correction: the work, the label it dropped and the one it uses now."""
    (old_en, old_uk), (new_en, new_uk) = RELABELS[x['key']]
    figure = f'<figure class="fix-art">{photos.img(x["photo"])}<figcaption class="credit">{photos.credit(x["photo"])}</figcaption></figure>' if x.get('photo') else ''
    return f"""        <article class="culture-item fix" id="{section_id}-{x['key']}" tabindex="-1">
          {figure}
          <div class="fix-body">
            <h4 class="c-name">{both(*x['name'])}</h4>
            <p class="relabel"><span class="visually-hidden">{both('Was:', 'Було:')}</span><s>{both(old_en, old_uk)}</s><span class="relabel-arrow" aria-hidden="true">→</span><span class="visually-hidden">{both('now:', 'тепер:')}</span><strong>{both(new_en, new_uk)}</strong></p>
            <p class="c-about">{both(*x['about'])}</p>
            {_sources(x)}
          </div>
        </article>"""

def _dated(x, section_id, targets, field):
    """A holiday or a festival, under a calendar leaf."""
    month, day = leaf(x[field][0])
    where = f'<p class="c-where">{_icon("pin")}{both(*x["where"])}</p>' if 'where' in x else ''
    return f"""        <article class="culture-item c-dated" id="{section_id}-{x['key']}" tabindex="-1">
          <div class="leaf" aria-hidden="true"><span class="leaf-month">{both(MONTHS_SHORT[0][month], MONTHS_SHORT[1][month])}</span>{f'<span class="leaf-day">{day}</span>' if day else '<span class="leaf-day c-ornament"></span>'}</div>
          <div class="c-body">
            <h4 class="c-name">{both(*x['name'])}</h4>
            <p class="c-when">{both(*x[field])}</p>{where}
            <p class="c-about">{both(*x['about'])}</p>{_timeline(x, targets)}
            {_sources(x)}
          </div>
        </article>"""

def _resource(x, section_id, targets):
    kind = KIND_OF_RESOURCE[x['key']]
    label = RESOURCE_KINDS[kind][0]
    return f"""        <article class="culture-item c-resource" id="{section_id}-{x['key']}" tabindex="-1">
          <p class="c-kind"><span class="c-kind-icon">{_icon(kind)}</span>{both(*label)} · {both(*x['where'])}</p>
          <h4 class="c-name">{both(*x['name'])}</h4>
          <p class="c-about">{both(*x['about'])}</p>
          <p class="c-actions"><a class="place-btn" href="{html.escape(x['url'])}" target="_blank" rel="noopener">{both('Website', 'Сайт')}<span class="visually-hidden">: {both(*x['name'])}</span></a></p>
          {_sources(x)}
        </article>"""

# How each section lays out its entries: the renderer, the grid's class, and the order of the entries.
LAYOUTS = {
    'culture-food': (_card, 'c-grid', None),
    'culture-traditions': (_card, 'c-grid', None),
    'culture-corrections': (_correction, 'fix-list', None),
    'culture-holidays': (lambda x, s, t: _dated(x, s, t, 'date'), 'c-grid dated-grid', lambda x: leaf(x['date'][0])[0]),
    'culture-events': (lambda x, s, t: _dated(x, s, t, 'when'), 'c-grid dated-grid', lambda x: leaf(x['when'][0])[0]),
    'culture-resources': (_resource, 'c-grid', lambda x: list(RESOURCE_KINDS).index(KIND_OF_RESOURCE[x['key']])),
}

def _section(number, section_id, title, intro, body, cls=''):
    intro_html = f'\n        <p class="section-intro">{both(*intro)}</p>' if intro else ''
    return f'''    <section class="culture-section{cls}" id="{section_id}" aria-labelledby="{section_id}-title">
      <header class="section-head">
        <p class="section-num" aria-hidden="true">{number:02d}</p>
        <h3 id="{section_id}-title">{both(*title)}</h3>{intro_html}
      </header>
{body}
    </section>'''

def render(targets):
    """The tab's HTML and its jump links. targets maps (kind, key) to (element id, English label, Ukrainian label)."""
    tiles = []
    for i, v in enumerate(GALLERY):
        p = v['photo']; link = ''
        if v['related']:
            target_id, en, uk = targets[v['related']]
            link = f'<a class="tile-link" href="#{target_id}">{both("In the timeline: " + en, "В історії: " + uk)}</a>'
        tiles.append(f'''        <figure class="tile{' tile-wide' if i == 5 else ''}">{photos.img(p, 'eager' if i == 0 else 'lazy')}
          <figcaption><span class="tile-caption">{both(*p['alt'])}</span>{link}<span class="credit">{photos.credit(p)}</span></figcaption>
        </figure>''')
    out = [_section(1, 'culture-gallery', ("Ukraine’s beauty", 'Краса України'), None, f'      <div class="bento">\n{chr(10).join(tiles)}\n      </div>')]
    nav = [('culture-gallery', "Ukraine’s beauty", 'Краса України')]
    for section_id, title, intro, entries in SECTIONS:
        render_one, grid, order = LAYOUTS[section_id]
        items = sorted(entries, key=order) if order else entries
        body = f'      <div class="{grid}">\n' + '\n'.join(render_one(x, section_id, targets) for x in items) + '\n      </div>'
        out.append(_section(len(nav) + 1, section_id, title, intro, body, ' culture-fixes' if section_id == 'culture-corrections' else ''))
        nav.append((section_id, *title))
    return '\n'.join(out), nav
