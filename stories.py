"""The People section: stories of Ukrainians, each summarized from one published report and linked to it.

Rule 6 in CLAUDE.md sets the standard. In short: the source is a news organization, a UN agency, a
museum or archive, or an established documentary project, and is free to read; the person is named
in it; the summary is in our own words, with no quotations, and every sentence is supported by the source.

Each text is an (English, Ukrainian) pair. Each source is (language, outlet, date, url, phrase): the
phrase, usually the person's surname as that page spells it, is what check.py looks for every week
to confirm the page still carries the story. Related entries elsewhere on the page are named by
their keys: ('history', English title), ('place', (name, city)), ('give', English organization name).

A story may have a photo, but only one that is openly licensed or in the public domain, credited as
its license requires (rule 6). Never a photo from the outlet's article: crediting it is not permission.
check.py confirms each photo's Wikimedia Commons page still carries the same license."""
import datetime, html

import photos
from i18n import both, dates, slug
from photos import photo

LANGUAGE_NAMES = {'en': ('in English', 'англійською'), 'uk': ('in Ukrainian', 'українською')}
RELATED_LABELS = {'history': ('In the timeline', 'В історії'), 'place': ('On the map', 'На мапі'), 'give': ('Give', 'Допомогти')}

def story(person, context, title, text, sources, related=(), photo=None):
    return dict(id='story-' + slug(person[0]), person=person, context=context, title=title, text=text, sources=sources, related=related, photo=photo)

INVASION = ('history', 'Russia launches a full-scale invasion')
UKRAINER = 'Ukraїner'

THEMES = [
 ('theme-home', ('At home in the war', 'Удома під час війни'),
  ('People in Ukraine who stayed, came back or started over, and keep their communities going.',
   'Люди в Україні, які залишилися, повернулися або почали все спочатку і тримають свої громади.'), [
  story(('Valentyna Hantseva', 'Валентина Ганцева'), ('Soldatske, Sumy region', 'Солдатське, Сумська область'),
        ('The librarian who took the books home', 'Бібліотекарка, яка забрала книжки додому'),
        ('The library in Soldatske, a village of about 400 people near Trostianets, had been open after a renovation for just two months when Russia’s full-scale invasion began. Russian forces first shelled the village on March 7, 2022, and within days an airstrike destroyed the library. The morning after the first shelling, librarian Valentyna Hantseva collected the books that survived and kept them at home, although Ukrainian books could bring reprisals if Russian troops found them. After Trostianets was liberated on March 28, 2022, residents and people displaced by the war fixed the roof themselves, and the library reopened that summer, the first building restored in the community.',
         'Бібліотека в Солдатському, селі неподалік Тростянця, де живе близько 400 людей, після ремонту пропрацювала лише два місяці, коли почалося повномасштабне вторгнення Росії. Уперше російські війська обстріляли село 7 березня 2022 року, а за кілька днів авіаудар зруйнував бібліотеку. Наступного ранку після першого обстрілу бібліотекарка Валентина Ганцева зібрала вцілілі книжки й зберігала їх удома, хоча за українські книжки російські військові могли покарати, якби їх знайшли. Після звільнення Тростянця 28 березня 2022 року мешканці села та внутрішньо переміщені люди самі полагодили дах, і того ж літа бібліотека знову відчинилася — це була перша відновлена будівля в громаді.'),
        [('en', UKRAINER, '2024-08-19', 'https://www.ukrainer.net/en/en-how-the-trostianets-community-is-being-restored/', 'Hantseva'),
         ('uk', UKRAINER, '2024-08-05', 'https://www.ukrainer.net/vidnovlennia-trostianets/', 'Ганцева')],
        [INVASION]),
  story(('Hennadii Pohorielov', 'Геннадій Погорєлов'), ('Makariv, Kyiv region', 'Макарів, Київська область'),
        ('Rebuilding Makariv', 'Відбудувати Макарів'),
        ('Makariv, about 50 kilometers from Kyiv, went through fighting and occupation from late February to April 2022, and almost 30 percent of its buildings were damaged or destroyed. Hennadii Pohorielov, an officer of the State Emergency Service, helped evacuate people during that time without wearing his uniform, for safety, and delivered aid once the village was liberated. In July 2022 he started the Rebuild Makariv Foundation, where officially only he and an accountant work; as a serving civil servant, he cannot be paid a salary under Ukraine’s anti-corruption law. With partners such as Oxfam it installed 700 windows and doors where funding had been set aside for 300, bought equipment for more than 20 small businesses, and helped build a new house in 44 days for a family whose home burned after shell fragments hit its roof.',
         'Макарів, приблизно за 50 кілометрів від Києва, пережив бої та окупацію з кінця лютого до квітня 2022 року; майже 30 відсотків його будівель було зруйновано або пошкоджено. Геннадій Погорєлов, офіцер Державної служби з надзвичайних ситуацій, у той час допомагав евакуювати людей, не вдягаючи форми задля безпеки, а після звільнення селища розвозив гуманітарну допомогу. У липні 2022 року він заснував фонд «Відбудуй Макарів», де офіційно працюють лише він і бухгалтер; зарплати він не отримує, бо як чинний державний службовець не має на неї права за антикорупційним законом. Разом із партнерами, зокрема Oxfam, фонд установив 700 вікон і дверей там, де гроші виділили на 300, закупив обладнання для понад 20 малих підприємств і допоміг за 44 дні збудувати новий дім для родини, чия хата згоріла після того, як уламки снаряда влучили в дах.'),
        [('en', UKRAINER, '2024-06-14', 'https://www.ukrainer.net/en/vidnovlennia-makariv-2/', 'Pohorielov'),
         ('uk', UKRAINER, '2024-04-25', 'https://www.ukrainer.net/vidnovlennia-makariv/', 'Погорєлов')],
        [INVASION]),
  story(('Viacheslav and Nadiia Bezprozvanyi', 'В’ячеслав і Надія Безпрозвані'), ('Kherson', 'Херсон'),
        ('Not ready to leave Kherson', 'Не готові покинути Херсон'),
        ('Starting in 1992, Viacheslav Bezprozvanyi spent about 20 years building a two-story house in Kherson, buying materials with what was left of his salary. After Russia destroyed the Kakhovka dam, the floodwater reached halfway up the second floor. He and his wife, Nadiia, had just finished repairing the inside when Russian tank fire hit the house. She was not hurt, but she became too afraid to sleep there. The couple, married almost 50 years, kept cleaning and repairing, and although their family urged them to move to a safer part of the city, in November 2023 they were not prepared to leave Kherson.',
         'Починаючи з 1992 року, В’ячеслав Безпрозваний близько 20 років будував двоповерховий будинок у Херсоні, купуючи матеріали за те, що лишалося від зарплати. Після того як Росія зруйнувала Каховську греблю, вода піднялася до половини другого поверху. Він і його дружина Надія щойно завершили ремонт усередині, коли будинок обстріляв російський танк. Вона не постраждала, але тепер боялася ночувати вдома. Подружжя, яке разом майже 50 років, і далі прибирало й лагодило будинок, і хоча рідні вмовляли їх перебратися в безпечніший район, у листопаді 2023 року залишати Херсон вони не були готові.'),
        [('en', 'The Kyiv Independent', '2023-11-11', 'https://kyivindependent.com/under-deadly-attacks-kherson-fights-to-keep-life-going-1-year-after-liberation/', 'Bezprozvanyi')],
        [('history', 'The Kakhovka dam is destroyed')]),
  story(('Tetiana Shpak', 'Тетяна Шпак'), ('Snihurivka, Mykolaiv region', 'Снігурівка, Миколаївська область'),
        ('A math teacher who finds mines', 'Учителька математики, яка шукає міни'),
        ('Tetiana Shpak, then 51 and a former math teacher, first helped build fortifications, and after she lost her father in a bombardment she said she wanted to be useful. By June 2024 she had spent a year with the HALO Trust clearing land around Snihurivka, which Russian forces mined while they held the area for much of 2022. Her job was to find the mines; other teams destroyed them. Her family was against the work at first, she said, but her daughter now says that when she grows up, she will try something similar too. Women made up 30 percent of the people clearing mines in Ukraine, according to official figures cited in the report.',
         'Тетяна Шпак, якій тоді був 51 рік, колишня вчителька математики, спершу допомагала будувати укріплення, а після того як утратила батька через бомбардування, сказала, що дуже хотіла бути корисною. У червні 2024 року вона вже рік працювала в організації HALO Trust, очищуючи землі довкола Снігурівки, які російські війська замінували, коли тримали цю територію більшу частину 2022 року. Її завданням було знаходити міни; знищували їх інші команди. За її словами, спершу родина була проти, а тепер донька каже, що, коли виросте, теж спробує щось подібне. Згідно з офіційними даними, які наводить джерело, жінки становили 30 відсотків тих, хто розміновує землі в Україні.'),
        [('en', 'Al Jazeera', '2024-06-12', 'https://www.aljazeera.com/gallery/2024/6/12/photos-female-deminers-step-in-to-clear-up-ukrainian-land', 'Shpak')]),
  story(('Kateryna Kolmykova', 'Катерина Колмикова'), ('From Mariupol to Kyiv', 'З Маріуполя до Києва'),
        ('Starting over, twice', 'Почати знову — двічі'),
        ('Before the full-scale invasion, Kateryna Kolmykova and her husband, Maksym, ran eight shops in Mariupol, where she sold handbags and he sold home appliances. The family left the city under fire in March 2022 and settled in Kyiv. Since leaving Mariupol they have lived in 15 rented apartments, and in Kyiv she earned money performing in a theater while he drove a truck. They went back into business with a new store, helped along by funny videos she posted online. When a Russian drone and missile attack hit the market where the store stood on June 16, the couple began selling the stock they still had at home, and Kolmykova said the thousands of messages of support they received meant she had no right to give up.',
         'До повномасштабного вторгнення Катерина Колмикова та її чоловік Максим мали вісім крамниць у Маріуполі: вона продавала сумки, а він — побутову техніку. У березні 2022 року родина виїхала з міста під обстрілами й оселилася в Києві. Відтоді подружжя змінило 15 орендованих квартир, а в Києві Катерина заробляла виступами в театрі, поки Максим працював водієм вантажівки. Згодом вони знову відкрили власну крамницю, якій допомагали кумедні відео, що їх Катерина викладала в мережі. Коли 16 червня російська атака дронами й ракетами влучила в ринок, де стояла крамниця, подружжя почало розпродувати товар, що лишився вдома, а Колмикова сказала, що тисячі повідомлень підтримки не дають їй права здатися.'),
        [('en', 'Radio Free Europe/Radio Liberty', '2026-07-21', 'https://www.rferl.org/a/mariupol-family-loses-business-twice-russia-ukraine-war-kolmykova/33808968.html', 'Kolmykova')],
        [('history', 'The war continues')]),
 ]),
 ('theme-us', ('A new home in the United States', 'Новий дім у Сполучених Штатах'),
  ('Ukrainians who came to the US after the full-scale invasion, and the people behind Ukrainian businesses that were here long before it.',
   'Українці, які приїхали до США після повномасштабного вторгнення, і люди, що стоять за українськими закладами, які працювали тут задовго до нього.'), [
  story(('The Kramarczuk family', 'Родина Крамарчуків'), ('Minneapolis, Minnesota', 'Міннеаполіс, Міннесота'),
        ('Seventy years of work for newcomers', 'Сімдесят років роботи для новоприбулих'),
        ('Wasyl and Anna Kramarczuk left Ukraine during World War II and started a butcher shop that has been part of northeast Minneapolis since 1954. For decades, people newly arrived from the former Soviet Union and its former satellite states have worked there, and the founders’ son Orest called it an incubator for immigrants and refugees from Eastern Europe. In April 2025, temporary workers from Ukraine made up about a third of the staff. One said the business had helped them with housing and documents; another had to stop working when her request to extend her work permit went unanswered. Grandson Nick Kramarczuk, the general manager, said they deserved the same opportunities his grandparents had.',
         'Василь та Анна Крамарчуки виїхали з України під час Другої світової війни й заснували м’ясну крамницю, яка з 1954 року є частиною північно-східного Міннеаполіса. Десятиліттями тут працювали люди, які щойно приїхали з колишнього Радянського Союзу та його колишніх країн-сателітів, і син засновників Орест назвав заклад інкубатором для іммігрантів і біженців зі Східної Європи. У квітні 2025 року приблизно третину персоналу становили тимчасові працівники з України. Одна з них розповіла, що заклад допоміг їм із житлом і документами; інша мусила припинити роботу, бо так і не отримала відповіді на запит про продовження дозволу на роботу. Онук засновників Нік Крамарчук, генеральний менеджер, сказав, що вони заслуговують на ті самі можливості, які мали його дідусь і бабуся.'),
        [('en', 'MPR News', '2025-04-25', 'https://www.mprnews.org/story/2025/04/25/ukrainian-workers-minneapolis-restaurant-trump-halts-work-permit-renewals', 'Kramarczuk')],
        [('place', ("Kramarczuk's Sausage Company", 'Minneapolis'))]),
  story(('Jason and Tom Birchard', 'Джейсон і Том Бірчарди'), ('New York', 'Нью-Йорк'),
        ('A line outside Veselka', 'Черга біля «Веселки»'),
        ('In March 2022, weeks into the full-scale invasion, customers lined up outside Veselka in Manhattan’s East Village throughout the day to show solidarity with Ukraine. About 40 percent of the staff came from Ukraine. Third-generation owner Jason Birchard, whose grandfather opened Veselka as a storefront in 1954, when the neighborhood was known as Little Ukraine, said they were in shock and that it was a miracle they came to work. Ukrainian cooks made 5,000 pierogies from scratch every day, and the Birchards said they were giving all of the restaurant’s borscht sales to humanitarian aid in Ukraine. Jason’s father, Tom Birchard, invited people to treat Veselka as their second dining room.',
         'У березні 2022 року, через кілька тижнів після початку повномасштабного вторгнення, біля «Веселки» в манхеттенському Іст-Вілліджі цілими днями стояли черги: так люди висловлювали солідарність з Україною. Близько 40 відсотків працівників були з України. Власник у третьому поколінні Джейсон Бірчард, чий дід відкрив «Веселку» як невелику крамницю 1954 року, коли район називали Малою Україною, сказав, що вони в шоці, і назвав дивом те, що вони приходять на роботу. Українські кухарі щодня ліпили 5 000 вареників, а Бірчарди заявили, що передають усі гроші від продажу борщу на гуманітарну допомогу Україні. Батько Джейсона, Том Бірчард, запросив людей вважати «Веселку» своєю другою їдальнею.'),
        [('en', 'CBS News', '2022-03-17', 'https://www.cbsnews.com/news/ukrainian-restaurant-veselka-new-york-east-village/', 'Birchard')],
        [('place', ('Veselka', 'New York'))]),
  story(('Vladimir Gapon', 'Володимир Гапон'), ('Fife, Washington', 'Файф, штат Вашингтон'),
        ('A Kharkiv native’s market in Fife', 'Крамниця харків’янина у Файфі'),
        ('Vladimir Gapon, a co-owner of Emish Market in Fife, emigrated from Ukraine more than 20 years ago. In May 2022 he was getting news from friends and family every morning, and he said his home city of Kharkiv had been destroyed. Many of his employees were Ukrainians who sent money home to their families. His 10-year-old daughter handed out candy and popcorn to people who donated and had raised thousands of dollars for Ukraine, and signs in the store pointed shoppers to organizations feeding people in Ukraine.',
         'Володимир Гапон, співвласник крамниці Emish Market у Файфі, емігрував з України понад 20 років тому. У травні 2022 року він щоранку отримував новини від друзів і рідних і розповів, що його рідне місто Харків зруйноване. Багато його працівників були українцями, які надсилали гроші своїм родинам. Його 10-річна донька роздавала цукерки й попкорн тим, хто жертвував, і вже зібрала для України тисячі доларів, а таблички в крамниці вели покупців на сайти організацій, що годують людей в Україні.'),
        [('en', 'KING 5', '2022-05-26', 'https://www.king5.com/article/entertainment/television/programs/evening/fighting-back-a-ukranian-specialty-market-in-fife-raises-money-and-hope-in-war-against-russia/281-b2f75b39-f5d9-49e1-a2f5-47535722b798', 'Gapon')],
        [('place', ('Emish Market', 'Fife'))]),
  story(('Peter and Ksenia Sokor', 'Петро і Ксенія Сокор'), ('Stoughton, Wisconsin', 'Стоутон, Вісконсин'),
        ('Two hours to pack, then Wisconsin', 'Дві години на збори, а потім Вісконсин'),
        ('When the full-scale invasion began, Russian forces bombed a military base about three miles from Peter and Ksenia Sokor’s home. With two hours to gather what they could, and forced to leave their dog behind, they left Ukraine with their three young daughters. After a long journey they were invited to stay with a family in Wisconsin, and they eventually rented their own apartment in Stoughton with help from a local volunteer group, which had assisted almost a dozen Ukrainian families that year. Peter took programming courses and began giving private piano lessons.',
         'Коли почалося повномасштабне вторгнення, російські війська бомбардували військову базу приблизно за п’ять кілометрів від дому Петра і Ксенії Сокорів. Маючи дві години на збори й мусивши залишити собаку, вони виїхали з України з трьома маленькими доньками. Після довгої дороги одна родина у Вісконсині запросила їх пожити в себе, а згодом вони винайняли власну квартиру в Стоутоні за допомогою місцевої волонтерської групи, яка того року допомогла майже десятку українських родин. Петро проходив курси програмування і почав давати приватні уроки гри на фортепіано.'),
        [('en', 'PBS Wisconsin', '2023-02-17', 'https://pbswisconsin.org/news-item/ukrainian-refugees-in-wisconsin-reflect-on-a-year-of-war/', 'Sokor')]),
  story(('Sergey and Christina Pokanevych', 'Сергій і Христина Поканевичі'), ('Midland, Michigan', 'Мідленд, Мічиган'),
        ('From five restaurants in Odesa to a bakery in Midland', 'Від п’яти ресторанів в Одесі до пекарні в Мідленді'),
        ('Sergey and Christina Pokanevych owned five restaurants in Odesa, and Sergey was a chef with more than a million followers on social media. Christina remembered waking to missile strikes that shook their house, and the family closed the restaurants and left. American sponsors hosted them for four months in Caro, Michigan, and once the couple could work they moved to Midland to work at the Great Hall. Christina said people across Midland donated anywhere from $5 to $50,000 toward Chef Sergey’s Bakery, which opened in January 2025; on opening day it sold out by 11 a.m. after selling more than 1,000 baked goods.',
         'Сергій і Христина Поканевичі мали п’ять ресторанів в Одесі, а в Сергія як кухаря було понад мільйон підписників у соцмережах. Христина згадувала, як вони прокинулися від ракетних ударів, від яких тремтів їхній дім; родина закрила ресторани й виїхала. Американські спонсори чотири місяці приймали їх у містечку Каро в Мічигані, а коли подружжя змогло працювати, вони переїхали до Мідленда й почали працювати в закладі Great Hall. За словами Христини, мешканці Мідленда жертвували від 5 до 50 000 доларів на пекарню Chef Sergey’s Bakery, яка відкрилася в січні 2025 року; у день відкриття до 11-ї ранку там продали понад тисячу виробів і розпродали все.'),
        [('en', 'WDET', '2025-01-22', 'https://wdet.org/2025/01/22/home-and-hope-ukrainian-refugees-open-bakery-in-midland/', 'Pokanevych')],
        [('place', ("Chef Sergey's Bakery", 'Midland'))]),
 ]),
 ('theme-culture', ('Keeping the culture', 'Зберегти культуру'),
  ('People who protect Ukrainian art, food, books and heritage while the war goes on.',
   'Люди, які бережуть українське мистецтво, кухню, книжки та спадщину, поки триває війна.'), [
  story(('Yevhen Klopotenko', 'Євген Клопотенко'), ('Kyiv', 'Київ'),
        ('The chef behind borsch’s UNESCO listing', 'Кухар, завдяки якому борщ потрапив до списку ЮНЕСКО'),
        ('Yevhen Klopotenko, a Kyiv chef and restaurateur who won MasterChef Ukraine in 2015, led the successful campaign to put borsch on UNESCO’s list of cultural heritage in urgent need of safeguarding. When Russian troops advanced on Kyiv in 2022, his restaurant became a bomb shelter, and he later opened a pop-up restaurant in Lviv and cooked borsch at the city’s railway station. For years he has worked with historians, searching Ukrainian literary manuscripts for dishes cooked centuries ago, and in 2024 he published an English-language cookbook. Recalling how the world stopped paying attention to the war in Syria, he told NPR his biggest motivation was not wanting Ukraine to disappear in the same way.',
         'Київський кухар і ресторатор Євген Клопотенко, переможець «МастерШефа» 2015 року, очолив успішну кампанію за внесення борщу до списку культурної спадщини ЮНЕСКО, що потребує термінової охорони. Коли 2022 року російські війська наступали на Київ, його ресторан став бомбосховищем, а згодом він відкрив тимчасовий ресторан у Львові й варив борщ на львівському вокзалі. Роками він разом з істориками шукав в українських літературних рукописах згадки про страви, які готували сотні років тому, а 2024 року видав англомовну кулінарну книжку. Згадуючи, як світ перестав зважати на війну в Сирії, він сказав NPR, що найбільше його мотивує бажання, щоб Україна не зникла так само.'),
        [('en', 'NPR', '2024-11-10', 'https://www.npr.org/2024/11/08/nx-s1-5168055/ukraine-chef-ukrainian-cuisine', 'Klopotenko')],
        photo=photo('klopotenko.jpg', ('Yevhen Klopotenko in a chef’s jacket', 'Євген Клопотенко в кухарському кітелі'), 'Владислав Нагорний',
                    'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:%D0%84%D0%B2%D0%B3%D0%B5%D0%BD_%D0%9A%D0%BB%D0%BE%D0%BF%D0%BE%D1%82%D0%B5%D0%BD%D0%BA%D0%BE_01.jpg')),
  story(('Victoria Amelina', 'Вікторія Амеліна'), ('Writer and war crimes researcher', 'Письменниця і дослідниця воєнних злочинів'),
        ('A book her friends brought to print', 'Книжка, яку друзі підготували до друку'),
        ('Victoria Amelina left a career in IT to write full time in 2015, and after Russia’s full-scale invasion she began working as a war crimes researcher. She died at 37 in July 2023 from injuries suffered when Russian missiles struck a restaurant in Kramatorsk, leaving the manuscript of her book Looking at Women, Looking at War unfinished. A group of her closest friends and colleagues prepared it for publication. In June 2025 it won Britain’s Orwell Prize for political writing, and Amelina became the first Ukrainian writer to receive it.',
         '2015 року Вікторія Амеліна залишила роботу в ІТ, щоб повністю присвятити себе літературі, а після початку повномасштабного вторгнення почала документувати воєнні злочини. Вона загинула в липні 2023 року у віці 37 років від поранень, яких зазнала, коли російські ракети влучили в ресторан у Краматорську; рукопис її книжки Looking at Women, Looking at War лишився незавершеним. Підготувати його до друку взялися її найближчі друзі й колеги. У червні 2025 року книжка отримала британську Орвеллівську премію за політичну літературу, і Амеліна стала першою серед українських письменників, хто її здобув.'),
        [('en', 'The Kyiv Independent', '2025-06-25', 'https://kyivindependent.com/ukrainian-author-killed-by-russia-awarded-uks-prestigious-orwell-prize-in-political-writing/', 'Amelina'),
         ('en', 'Al Jazeera', '2023-07-03', 'https://www.aljazeera.com/news/2023/7/3/victoria-amelina-tracked-russian-war-crimes-a-missile-killed-her', 'Amelina')],
        photo=photo('amelina.jpg', ('Victoria Amelina at a literary festival in Wrocław, 2018', 'Вікторія Амеліна на літературному фестивалі у Вроцлаві, 2018 рік'), 'Rafał Komorowski',
                    'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:Victoria_Amelina_1022.jpg')),
  story(('Hryhoriy Demyanov', 'Григорій Дем’янов'), ('From the Donetsk region to Dnipro', 'З Донеччини до Дніпра'),
        ('Medieval statues, rescued by hand', 'Середньовічні статуї, врятовані власноруч'),
        ('In 2024, volunteers moved stone statues carved centuries ago by the Cumans, or Polovtsy, a nomadic people of southern Ukraine, away from the front line in the Donetsk region. Volunteer Hryhoriy Demyanov said his team took out the first two with a car and trailer, using crowbars, a winch and their hands. On a later trip, he said, the shelling was heavy and drones were overhead, so they had to work very quickly. By June, nine sculptures had reached the relative safety of Dnipro on five trips paid for with donations from Ukrainians and foreigners. Demyanov said few such statues were left and that they were part of Ukraine’s history and identity, and Oleksandr Starik, acting director of the Dnipropetrovsk National Historical Museum, said removing them from the battlefield was essential.',
         '2024 року волонтери вивезли з прифронтових районів Донеччини кам’яні статуї, які багато століть тому створили половці (кумани) — кочовий народ, що жив на півдні України. Волонтер Григорій Дем’янов розповів, що перші дві статуї команда вивезла автомобілем із причепом, орудуючи ломами, лебідкою і власними руками. Під час наступної поїздки, за його словами, обстріли були серйозні й літали дрони, тож працювати доводилося дуже швидко. До червня дев’ять скульптур перевезли у відносно безпечний Дніпро за п’ять поїздок, оплачених пожертвами українців та іноземців. Дем’янов сказав, що таких статуй залишилося мало і що вони є частиною історії та ідентичності України, а в. о. директора Дніпропетровського національного історичного музею Олександр Старік наголосив, що вивезти їх з поля бою було необхідно.'),
        [('en', 'Radio Free Europe/Radio Liberty', '2024-06-24', 'https://www.rferl.org/a/ukraine-war-stone-statues-evacuated/33007046.html', 'Demyanov'),
         ('uk', 'Радіо Свобода', '2024-06-22', 'https://www.radiosvoboda.org/a/baby-z-frontovoyi-donechchyny/32996831.html', 'Дем’янов')]),
  story(('Ihor Nikolaienko and Anatolii Kharytonov', 'Ігор Ніколаєнко та Анатолій Харитонов'), ('Ivankiv, Kyiv region', 'Іванків, Київська область'),
        ('Twenty minutes to save Prymachenko', 'Двадцять хвилин, щоб урятувати Примаченко'),
        ('Ivankiv spent 35 days under Russian occupation in 2022. Residents had already gathered the paintings of the naïve artist Maria Prymachenko and hidden them together in the local museum when, on February 25, a projectile hit its roof. Two local men, Ihor Nikolaienko and Anatolii Kharytonov, saved exhibits for nearly 20 minutes, until the damaged ceiling began to bend. Prymachenko’s paintings were the first things they carried out, and some of them were saved; other works in the museum could not be saved in time. Prymachenko’s great-granddaughter Anastasiia said the museum, destroyed by the Russians, would be rebuilt.',
         '2022 року Іванків пробув 35 днів під російською окупацією. Місцеві мешканці вже встигли зібрати картини художниці наївного мистецтва Марії Примаченко й сховати їх разом в окремому місці музею, коли 25 лютого снаряд влучив у його дах. Двоє місцевих чоловіків, Ігор Ніколаєнко та Анатолій Харитонов, майже 20 хвилин рятували експонати, аж поки пошкоджена стеля не почала прогинатися. Першими вони винесли саме картини Примаченко, і частину з них урятували; інші роботи з музею врятувати не встигли. Правнучка Примаченко Анастасія сказала, що зруйнований росіянами музей відбудують.'),
        [('en', UKRAINER, '2022-04-26', 'https://www.ukrainer.net/en/prymachenko-3/', 'Nikolaienko'),
         ('uk', UKRAINER, '2022-04-20', 'https://www.ukrainer.net/prymachenko/', 'Ніколаєнко')],
        [INVASION]),
 ]),
 ('theme-recovery', ('Healing and helping', 'Одужання і допомога'),
  ('Wounded Ukrainians on the way back, and the people and groups helping them. Each of these groups is on the Give tab.',
   'Поранені українці на шляху до одужання, а також люди й організації, які їм допомагають. Усі ці організації є в розділі «Допомогти».'), [
  story(('Ivan Kovalyk', 'Іван Ковалик'), ('Lviv', 'Львів'),
        ('Walking in a month instead of a year', 'Пішов за місяць, а не за рік'),
        ('Ivan Kovalyk, a 22-year-old soldier, was hit in a Russian strike on the front line in eastern Ukraine, and by the time he was treated both his legs had to be amputated. In 2024 he received a rare place at the Superhumans Center in Lviv, which opened in April 2023 to give Ukrainians wounded in the war free prosthetics, rehabilitation and psychological care. He was told it would take a year to walk without crutches, and he did it in a month. He said he could walk, ride with his friends and study again, and that if allowed he wanted to return to the army to teach new soldiers about perseverance.',
         '22-річний військовий Іван Ковалик потрапив під російський удар на передовій на сході України, і на той час, коли він отримав лікування, обидві ноги довелося ампутувати. 2024 року він отримав рідкісне місце в центрі Superhumans у Львові, який з квітня 2023 року безоплатно надає пораненим на війні українцям протези, реабілітацію та психологічну допомогу. Йому казали, що ходити без милиць він зможе за рік, а він зробив це за місяць. Іван розповів, що знову може ходити, їздити з друзями і вчитися, а якщо дозволять, хоче повернутися до війська, щоб навчати новобранців не здаватися.'),
        [('en', 'PBS NewsHour', '2024-05-08', 'https://www.pbs.org/newshour/show/ukrainian-troops-who-lost-limbs-in-war-receive-prosthetics-and-hope-for-the-future', 'Kovalyk')],
        [('give', 'Superhumans Center')]),
  story(('Hryhorii Vorobiov and Dmytro Starikov', 'Григорій Воробйов і Дмитро Старіков'), ('Oakdale, Minnesota', 'Окдейл, Міннесота'),
        ('Three weeks in Minnesota', 'Три тижні в Міннесоті'),
        ('In 2023 the 12th group of wounded Ukrainian soldiers arrived at the Protez Foundation in Oakdale, Minnesota, for a three-week program of prosthetics and rehabilitation, greeted at the airport by dozens of local people. The group included Hryhorii Vorobiov, 30, who lost a leg in the battle for Bakhmut, and Dmytro Starikov, 35, who stepped on a Russian mine in the Donetsk region. The foundation, which runs on donations, paid for their travel, lodging and treatment; co-founder Yakov Gradinar had started it as a small operation in his kitchen. Since 2022 it had spent about $1.7 million fitting around 90 Ukrainians with prosthetics, and some of the soldiers walked comfortably on their new limbs for the first time in months.',
         '2023 року до Protez Foundation в Окдейлі (Міннесота) прибула 12-та група поранених українських військових на тритижневу програму протезування та реабілітації; в аеропорту їх зустрічали десятки місцевих жителів. Серед них були 30-річний Григорій Воробйов, який утратив ногу в боях за Бахмут, і 35-річний Дмитро Старіков, який підірвався на російській міні на Донеччині. Фонд, що існує на пожертви, оплатив їм дорогу, житло й лікування; співзасновник Яків Градинар починав його як невелику справу на власній кухні. Від 2022 року фонд витратив близько 1,7 млн доларів, щоб забезпечити протезами приблизно 90 українців, і деякі військові вперше за багато місяців змогли комфортно ходити на нових протезах.'),
        [('en', 'Scripps News', '2023-06-27', 'https://www.scrippsnews.com/world/europe/ukrainian-war-amputees-find-healing-and-support-at-minnesota-clinic', 'Vorobiov')],
        [('give', 'Protez Foundation')]),
  story(('Dariia Misko and Ian Foertsch', 'Дарія Місько та Ієн Фертш'), ('Kyiv and Golden Valley, Minnesota', 'Київ і Голден-Веллі, Міннесота'),
        ('Calls across an ocean', 'Розмови через океан'),
        ('Dariia Misko, a 26-year-old psychology master’s student in Kyiv, and Ian Foertsch, a 38-year-old software developer in Golden Valley, Minnesota, had been talking regularly since January through ENGin, a nonprofit that pairs Ukrainians with English speakers for weekly one-on-one conversations online. Misko said Foertsch had become a friend. Foertsch said he had expected to meet someone whose life was completely different from his, and instead met people much like him. ENGin began in 2020 as a small project for high school students and had drawn about 50,000 participants, roughly half of them Ukrainians, with most of the volunteers in the United States.',
         'Дарія Місько, 26-річна магістрантка, яка вивчає психологію в Києві, та Ієн Фертш, 38-річний розробник програмного забезпечення з Голден-Веллі в Міннесоті, з січня регулярно спілкувалися завдяки ENGin — неприбутковій організації, яка поєднує українців з англомовними волонтерами для щотижневих онлайн-розмов віч-на-віч. Дарія сказала, що Ієн став для неї другом. Ієн розповів, що очікував зустріти людину, чиє життя зовсім не схоже на його власне, а натомість познайомився з людьми, дуже схожими на нього. ENGin почався 2020 року як невеликий проєкт для старшокласників і залучив близько 50 000 учасників; приблизно половина з них — українці, а більшість волонтерів живуть у США.'),
        [('en', 'Minnesota Star Tribune', '2024-11-15', 'https://www.startribune.com/virtual-pen-pals-engin-pairs-ukrainians-and-americans-for-online-english-conversations/601181144', 'Misko')],
        [('give', 'ENGin')]),
  story(('Olena Bila', 'Олена Біла'), ('Kyiv region', 'Київщина'),
        ('A puppy named Baron', 'Цуценя на ім’я Барон'),
        ('Early in Russia’s full-scale invasion, Olena Bila and her husband closed their small business in the Kyiv region, and she joined UAnimals, an animal-rights nonprofit. On a mission near Kyiv on March 8, Ukrainian soldiers showed the couple a small wounded puppy, a Bernese mountain dog they named Baron. Later, in Izium, Ukrainian soldiers rescued ten dogs and decided to adopt all of them, and Bila said the dogs went to their new families, not to shelters. Bila said there had not been a second when she regretted becoming a volunteer.',
         'На початку повномасштабного вторгнення Олена Біла та її чоловік закрили свій невеликий бізнес на Київщині, і вона приєдналася до UAnimals — організації, що захищає права тварин. 8 березня під час однієї з поїздок поблизу Києва українські військові показали подружжю маленьке поранене цуценя — бернського зенненхунда, якого назвали Бароном. Згодом в Ізюмі українські військові врятували десятьох собак і вирішили взяти їх усіх до своїх родин, і, за словами Олени, собак відвезли до нових сімей, а не до притулків. Олена сказала, що жодної секунди не пошкодувала, що стала волонтеркою.'),
        [('en', 'The Kyiv Independent', '2022-12-29', 'https://kyivindependent.com/how-volunteers-risk-their-lives-to-rescue-abandoned-animals-amid-war/', 'Olena Bila')],
        [('give', 'UAnimals')]),
 ]),
 ('theme-history', ('History, lived', 'Історія, яку прожили'),
  ('People who lived through events in the timeline, several of them interviewed again during the full-scale war.',
   'Люди, які пережили події з розділу «Історія»; з кількома з них говорили вже під час повномасштабної війни.'), [
  story(('Liubov Yarosh', 'Любов Ярош'), ('Khodorkiv, Zhytomyr region', 'Ходорків, Житомирська область'),
        ('Three famines, and a war at 102', 'Три голоди і війна у 102 роки'),
        ('Liubov Yarosh was born in 1920 and lived through three famines. During the Holodomor her family lived in the village of Pustelnyki, later joined to Khodorkiv, and baked flatbreads from linden and nettle leaves, dried and ground into powder, with a little flour; the famine took two of her parents’ children, and she grew so swollen and weak that she could hardly walk. After the German occupation ended she was sent by force to Donbas, where she worked at a sawmill, and in 1948 she married and moved to Khodorkiv. In 2022, at 102, she was helping her relatives make camouflage suits for the army while three of her grandchildren served, and she said her biggest dream was for the war to end.',
         'Любов Ярош народилася 1920 року і пережила три голоди. Під час Голодомору її родина жила в селі Пустельники, яке згодом приєднали до Ходоркова, і пекла коржики з висушеного й розтертого на порошок листя липи та кропиви з дрібкою борошна; голод забрав двох дітей у родині, а сама вона так опухла й ослабла, що ледве ходила. Після звільнення від німецької окупації її фактично силоміць відправили на Донбас, де вона працювала на лісопильні, а 1948 року вона вийшла заміж і переїхала до Ходоркова. 2022 року, у 102 роки, вона разом із рідними допомагала плести маскувальні костюми для війська, де служили троє її онуків, і казала, що найбільше мріє, аби війна закінчилася.'),
        [('en', 'National Museum of the Holodomor-Genocide', '2022-09-09', 'https://holodomormuseum.org.ua/en/novyny/102-year-old-holodomor-witness-liubov-yarosh-the-biggest-dream-is-for-the-war-to-end/', 'Yarosh'),
         ('uk', 'Національний музей Голодомору-геноциду', '2022-09-09', 'https://holodomormuseum.org.ua/novyny/102-richna-svidok-holodomoru-liubov-iarosh-najbilsha-mriia-aby-vijna-zakinchylasia/', 'Ярош')],
        [('history', 'The Holodomor')]),
  story(('Rahyl Entina, Tatyana Zhuravliova and Larisa Dzuenko', 'Рахіль Ентіна, Тетяна Журавльова і Лариса Дзуенко'), ('Kyiv and Frankfurt', 'Київ і Франкфурт'),
        ('Refugees in 1941, and again in 2022', 'Біженки 1941 року — і знову 2022-го'),
        ('Rahyl Entina, Tatyana Zhuravliova and Larisa Dzuenko had escaped the Nazis once already. In 1941 Entina’s family fled the Nazi army, leaving on a train with no one telling them where they were going, and Dzuenko’s father, a journalist whose wife was Jewish, sent his family to Uzbekistan; Zhuravliova was 2 when the war started. In 2022, Russia’s invasion made them refugees again. Entina, 92, left Ukraine on an evacuation bus to Moldova and reached Germany with her daughter, and died of COVID-19 a week after they arrived. Zhuravliova and Dzuenko were evacuated from Kyiv and, after 26 hours on the road, arrived in Frankfurt, where they shared a room in a nursing home and memories of escaping the Nazis. Dzuenko said she wanted to go home as soon as things improved.',
         'Рахіль Ентіна, Тетяна Журавльова і Лариса Дзуенко вже одного разу рятувалися від нацистів. 1941 року родина Ентіни тікала від нацистської армії потягом, і ніхто не казав їм, куди вони їдуть, а батько Дзуенко, журналіст, чия дружина була єврейкою, відправив родину до Узбекистану; Журавльовій було два роки, коли почалася війна. 2022 року російське вторгнення знову зробило їх біженками. 92-річна Ентіна виїхала з України евакуаційним автобусом до Молдови й дісталася з донькою Німеччини, де за тиждень після приїзду померла від COVID-19. Журавльову і Дзуенко евакуювали з Києва, і після 26 годин дороги вони прибули до Франкфурта, де жили в одній кімнаті в будинку для літніх людей і ділилися спогадами про втечу від нацистів. Дзуенко сказала, що хоче повернутися додому, щойно ситуація покращиться.'),
        [('en', 'PBS NewsHour', '2022-09-07', 'https://www.pbs.org/newshour/show/holocaust-survivors-fleeing-russias-invasion-of-ukraine-find-safety-in-unexpected-place', 'Entina')],
        [('history', 'Nazi occupation')]),
  story(('Mustafa Dzhemilev', 'Мустафа Джемілєв'), ('Crimean Tatar leader', 'Лідер кримських татар'),
        ('A life that began with deportation', 'Життя, що почалося з депортації'),
        ('Mustafa Dzhemilev was born in Crimea in 1943, survived the deportation of the Crimean Tatars the next year, and grew up in exile in Soviet Uzbekistan, where, he said, everything they knew about Crimea came from their parents. As a teenager he co-founded the Union of Young Crimean Tatars, and the Soviet authorities arrested him six times and held him in prisons and labor camps for 15 years. He led the Mejlis, the Crimean Tatars’ highest executive body, until 2013. Shortly after Russia occupied Crimea in 2014 he was banned from entering the peninsula, and in November 2023, for his 80th birthday, Ukraine made him a Hero of Ukraine.',
         'Мустафа Джемілєв народився в Криму 1943 року, наступного року пережив депортацію кримських татар і виріс на засланні в радянському Узбекистані, де, за його словами, все про Крим вони дізнавалися від батьків. Підлітком він став одним із засновників Союзу кримськотатарської молоді, а радянська влада шість разів його заарештовувала й загалом 15 років тримала у в’язницях і таборах. До 2013 року він очолював Меджліс — найвищий виконавчий орган кримських татар. Невдовзі після окупації Криму Росією 2014 року йому заборонили в’їзд на півострів, а в листопаді 2023 року, до 80-річчя, йому присвоїли звання Героя України.'),
        [('en', 'Radio Free Europe/Radio Liberty', '2024-05-17', 'https://www.rferl.org/a/crimea-tatars-dzhemilev-genocide/32951623.html', 'Dzhemilev')],
        [('history', 'The Crimean Tatars are deported')],
        photo=photo('dzhemilev.jpg', ('Mustafa Dzhemilev at the Senate of Poland', 'Мустафа Джемілєв у Сенаті Польщі'), 'Katarzyna Czerwińska',
                    'CC BY-SA 3.0 pl', 'https://commons.wikimedia.org/wiki/File:Mustafa_Dzhemilev_Senate_of_Poland_02.JPG')),
  story(('Hanna Zavorotna', 'Ганна Заворотна'), ('Kupovate, Chornobyl exclusion zone', 'Куповате, Чорнобильська зона відчуження'),
        ('Home again, inside the zone', 'Знову вдома, у зоні'),
        ('Hanna Zavorotna, born in 1933, stayed in her village of Kupovate for almost six days after the Chornobyl explosion, because no one told her about the explosion or the radiation. She learned of the evacuation while working in a collective-farm field, when the head of the village came to tell them. Her family spent that summer in the village of Kopyliv, then moved to a house in nearby Hruzke that had no stove, and after the winter they decided to go home. When Ukraїner told her story in 2018, she was 84 and one of 18 people living in a village that had about a thousand residents before the accident.',
         'Ганна Заворотна, яка народилася 1933 року, після вибуху на Чорнобильській АЕС майже шість днів залишалася у своєму селі Куповатому, бо ніхто не сказав їй ні про вибух, ні про радіацію. Про евакуацію вона дізналася, коли працювала на колгоспному полі й туди прийшов голова сільради. Літо її родина провела в селі Копилів, потім переїхала до будинку в сусідньому Грузькому, де не було печі, і після зими вирішила повернутися додому. Коли 2018 року Ukraїner розповів її історію, їй було 84 роки, і вона була однією з 18 мешканців села, де до аварії жило близько тисячі людей.'),
        [('en', UKRAINER, '2018-10-01', 'https://www.ukrainer.net/en/self-settlers-of-chornobyl-returning-home/', 'Zavorotna'),
         ('uk', UKRAINER, '2018-04-26', 'https://www.ukrainer.net/samosely-chornobylya/', 'Заворотній')],
        [('history', 'Chornobyl')]),
  story(('Artem Chekh', 'Артем Чех'), ('Writer and soldier', 'Письменник і військовий'),
        ('From the Maidan to the front', 'Від Майдану до фронту'),
        ('The writer Artem Chekh said he was not politically active before the EuroMaidan protests. That changed on November 30, 2013, when he watched Berkut riot police beat peaceful protesters, most of them students, and force them out of Independence Square, and he stayed with the revolution until Viktor Yanukovych left office and fled to Russia in February 2014. In 2015 he joined the army and fought for almost a year in the Luhansk region, which he wrote about in his 2017 book Absolute Zero. When Russia launched its full-scale invasion in 2022 he went back to fight, and in November 2023 he was still serving.',
         'Письменник Артем Чех розповів, що до Євромайдану не був політично активним. Усе змінилося 30 листопада 2013 року, коли він побачив, як «Беркут» побив мирних протестувальників, здебільшого студентів, і витіснив їх з майдану Незалежності. Він залишався з революцією, доки в лютому 2014 року Віктор Янукович не покинув посаду й не втік до Росії. 2015 року він пішов до війська й майже рік воював на Луганщині, про що написав у книжці «Точка нуль» (2017). Коли 2022 року Росія розпочала повномасштабне вторгнення, він знову пішов воювати і в листопаді 2023 року досі служив.'),
        [('en', 'The Kyiv Independent', '2023-11-21', 'https://kyivindependent.com/a-nations-blossoming-euromaidan-activists-and-their-further-battles-against-russia/', 'Chekh')],
        [('history', 'The Revolution of Dignity')],
        photo=photo('chekh.jpg', ('Artem Chekh at the Meridian Czernowitz festival in Chernivtsi, 2021', 'Артем Чех на фестивалі «Меридіан Черновіц» у Чернівцях, 2021 рік'), 'Germany2019',
                    'CC BY-SA 4.0', 'https://commons.wikimedia.org/wiki/File:Artem_Tschech_am_Meridian_Czernowitz,_2021.png')),
 ]),
]

STORIES = [s for _, _, _, stories in THEMES for s in stories]

def _validate():
    ids = set()
    for s in STORIES:
        for field in ('person', 'context', 'title', 'text'):
            if len(s[field]) != 2 or not all(x.strip() for x in s[field]): raise ValueError(f'{s["id"]}: {field} needs English and Ukrainian text')
        # Ukrainian sets organization names in «», so only the English text can be checked for quotations.
        if '“' in s['text'][0] or '"' in s['text'][0]: raise ValueError(f'{s["id"]}: summaries are in our own words, without quotations')
        if not s['sources']: raise ValueError(f'{s["id"]}: no source')
        for lang, outlet, date, url, phrase in s['sources']:
            if lang not in LANGUAGE_NAMES or not outlet or not url.startswith('https://') or not phrase.strip(): raise ValueError(f'{s["id"]}: bad source {url}')
            datetime.date.fromisoformat(date)
        if s['id'] in ids: raise ValueError(f'two stories have the id {s["id"]}')
        ids.add(s['id'])
        if s['photo']: photos.validate(s['photo'], s['id'])
_validate()

def photo_files():
    """The image files the stories use, for build.py to copy."""
    return [photos.IMAGES / s['photo']['file'] for s in STORIES if s['photo']]

def claims():
    """(url, phrase, what) for check.py: each source page must still carry the story, and each photo's page its license."""
    return ([(url, phrase, f'story of {s["person"][0]}: {outlet}') for s in STORIES for _, outlet, _, url, phrase in s['sources']]
            + [photos.claim(s['photo'], f'photo of {s["person"][0]}: license') for s in STORIES if s['photo']])

# Line icons, 24 by 24, drawn with the stroke. A story without a photo shows its theme's icon in place of a face.
ICONS = {
    'theme-home': 'M3 11 12 4l9 7M5.5 9.5V20h13V9.5M10 20v-5.5h4V20',
    'theme-us': 'M4 8h16v11H4ZM9 8V5.5h6V8M4 13h16',
    'theme-culture': 'M12 6.5C10 5 7 4.5 3.5 5v13c3.5-.5 6.5 0 8.5 1.5 2-1.5 5-2 8.5-1.5V5C17 4.5 14 5 12 6.5ZM12 6.5v13',
    'theme-recovery': 'M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10Z',
    'theme-history': 'M6.5 3.5h11M6.5 20.5h11M8 3.5c0 4.5 4 5.5 4 8.5s-4 4-4 8.5M16 3.5c0 4.5-4 5.5-4 8.5s4 4 4 8.5',
    'history': 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18ZM12 7.5V12l3 2',
    'place': 'M12 21s-6.5-5.6-6.5-11a6.5 6.5 0 0 1 13 0c0 5.4-6.5 11-6.5 11ZM12 12.5a2.5 2.5 0 1 0 0-5 2.5 2.5 0 0 0 0 5Z',
    'give': 'M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10Z',
}
if missing := {theme_id for theme_id, _, _, _ in THEMES} - set(ICONS): raise ValueError(f'themes without an icon: {sorted(missing)}')

def _icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{ICONS[name]}"/></svg>'

def related():
    """(story id, English name, Ukrainian name, kind, key) for every link from a story to another section."""
    return [(s['id'], *s['person'], kind, key) for s in STORIES for kind, key in s['related']]

def _read(s):
    """Buttons to the published story, one per source: sources in the reader's language first, others marked."""
    e = html.escape; out = []
    for i, lang in enumerate(('en', 'uk')):
        attrs = 'data-l="en"' if lang == 'en' else 'data-l="uk" lang="uk"'
        buttons = []
        for src_lang, outlet, date, url, _ in sorted(s['sources'], key=lambda src: src[0] != lang):
            note = '' if src_lang == lang else f' · {LANGUAGE_NAMES[src_lang][i]}'
            buttons.append(f'<a class="read-btn" href="{e(url)}" target="_blank" rel="noopener"><span class="read-outlet">{e(outlet)}</span><span class="read-date">{dates(date)[i]}{note}</span></a>')
        out.append(f'<div class="story-read" {attrs}><span class="story-read-label">{("Read the full story", "Повна історія")[i]}</span>{"".join(buttons)}</div>')
    return ''.join(out)

def _card(s, theme_id, targets):
    p = s['photo']
    avatar = photos.img(p) if p else _icon(theme_id)
    credit = f'\n          <p class="credit story-credit">{photos.credit(p)}</p>' if p else ''
    chips = []
    for kind, key in s['related']:
        target_id, en, uk = targets[kind, key]
        label_en, label_uk = RELATED_LABELS[kind]
        chips.append(f'<a class="rel-chip" href="#{target_id}">{_icon(kind)}<span><span class="rel-kind">{both(label_en, label_uk)}</span> {both(en, uk)}</span></a>')
    related_html = f'\n          <p class="story-related">{"".join(chips)}</p>' if chips else ''
    return f'''        <article class="story" id="{s['id']}" tabindex="-1">
          <header class="story-head">
            <div class="story-avatar{' has-photo' if p else ''}">{avatar}</div>
            <div>
              <p class="story-who">{both(*s['person'])}</p>
              <p class="story-where">{both(*s['context'])}</p>
            </div>
          </header>{credit}
          <h4 class="story-title">{both(*s['title'])}</h4>
          <p class="story-text" id="{s['id']}-text">{both(*s['text'])}</p>
          <button type="button" class="story-more" aria-expanded="false" aria-controls="{s['id']}-text" hidden><span class="more">{both('Read more', 'Читати далі')}</span><span class="less">{both('Show less', 'Згорнути')}</span></button>
          {_read(s)}{related_html}
        </article>'''

def render(targets):
    """The tab's HTML and its jump links. targets maps (kind, key) to (element id, English label, Ukrainian label)."""
    out = []
    for number, (theme_id, title, intro, stories) in enumerate(THEMES, 1):
        out.append(f'''    <section class="theme" id="{theme_id}" aria-labelledby="{theme_id}-title">
      <header class="section-head">
        <p class="section-num" aria-hidden="true">{number:02d}</p>
        <h3 id="{theme_id}-title">{both(*title)}</h3>
        <p class="section-intro">{both(*intro)}</p>
      </header>
      <div class="stories">
''' + '\n'.join(_card(s, theme_id, targets) for s in stories) + '''
      </div>
    </section>''')
    return '\n'.join(out), [(theme_id, *title) for theme_id, title, _, _ in THEMES]
