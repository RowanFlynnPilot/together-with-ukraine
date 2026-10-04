"""The history timeline. Every entry carries the sources its text was checked against.
Ukrainian text lives in history_uk.py, keyed by the English title; a missing translation stops the build.
check.py confirms the source links still load."""
import html

import photos
from i18n import both, slug
from photos import photo
import history_uk as UK

# The day the entries about the war as it stands were last brought up to date. check.py fails
# once this is more than four months old, as a reminder to revise them.
AS_OF = '2026-10-03'

IEU = 'https://www.encyclopediaofukraine.com/display.asp?linkpath=pages%5C'
def ieu(title, path): return (f'Encyclopedia of Ukraine, “{title}”', IEU + path)

AA = ('Anadolu Agency timeline, February 2026', 'https://www.aa.com.tr/en/asia-pacific/timeline-4-years-of-russia-ukraine-war-key-turning-points/3837840')
CFR = ('Council on Foreign Relations, Global Conflict Tracker', 'https://www.cfr.org/global-conflict-tracker/conflict/conflict-ukraine')

ERAS = [
 ('era-rus', 'Kyivan Rus’', '882 to 1253', [
  ('882', 'Oleh takes Kyiv',
   'According to the chronicles, Prince Oleh sails down the Dnipro, captures Kyiv and proclaims himself its prince. From there he extends his rule over neighboring tribes.',
   [ieu('Oleh, Prince', 'O%5CL%5COlehPrince.htm')]),
  ('988', 'Volodymyr the Great adopts Christianity',
   'Volodymyr allies with the Byzantine emperor, is baptized and orders the mass baptism of Kyiv. The rest of Rus’ is converted over time, sometimes by force.',
   [ieu('Volodymyr the Great', 'V%5CO%5CVolodymyrtheGreat.htm')]),
  ('1037', 'Saint Sophia rises in Kyiv',
   'Yaroslav the Wise founds the cathedral, and most of the original building survives at the core of the one standing today. He is traditionally credited with the first articles of Ruska Pravda, the most important collection of Rus’ laws.',
   [ieu('Saint Sophia Cathedral', 'S%5CA%5CSaintSophiaCathedral.htm'), ieu('Ruskaia Pravda', 'R%5CU%5CRuskaiaPravdaIT.htm')]),
  ('1240', 'Mongol armies sack Kyiv',
   'Batu Khan’s army sacks the city in December and its population is decimated. In the west, Prince Danylo of Galicia–Volhynia accepts a crown from the pope in 1253 and becomes king of Rus’.',
   [ieu('Kyiv', 'K%5CY%5CKyiv.htm'), ieu('Danylo Romanovych', 'D%5CA%5CDanyloRomanovych.htm')]),
 ]),
 ('era-cossacks', 'Cossacks and empires', '1569 to 1876', [
  ('1569', 'The Union of Lublin',
   'Poland and Lithuania merge into one commonwealth, and the Kyiv, Volhynia, Podilia and Bratslav regions pass to the Polish Crown. Out in the steppe, Cossacks live beyond any ruler’s authority.',
   [ieu('Lublin, Union of', 'L%5CU%5CLublinUnionof.htm'), ieu('Cossacks', 'C%5CO%5CCossacks.htm')]),
  ('1648', 'Khmelnytsky’s uprising',
   'Bohdan Khmelnytsky is elected hetman and leads a Cossack uprising that turns into a national revolution against Polish rule. Out of it comes the Hetman state, which lasts until 1782.',
   [ieu('Khmelnytsky, Bohdan', 'K%5CH%5CKhmelnytskyBohdan.htm'), ieu('Hetman state', 'H%5CE%5CHetmanstate.htm')]),
  ('1654', 'The Pereiaslav treaty',
   'In the middle of the war with Poland, Khmelnytsky allies with the tsar in Moscow. Ukrainian leaders see a temporary military alliance. Moscow uses the treaty to justify growing interference in Ukraine and to limit its sovereignty.',
   [ieu('Pereiaslav Treaty of 1654', 'P%5CE%5CPereiaslavTreatyof1654.htm')]),
  ('1709–10', 'Poltava and Orlyk’s constitution',
   'Hetman Ivan Mazepa joins Charles XII of Sweden against Moscow and is defeated at Poltava. In exile, the newly elected hetman Pylyp Orlyk signs a constitution that limits the hetman’s powers and sets up a Cossack parliament.',
   [ieu('Mazepa, Ivan', 'M%5CA%5CMazepaIvan.htm'), ieu('Bendery, Constitution of', 'B%5CE%5CBenderyConstitutionof.htm')]),
  ('1775', 'The Zaporozhian Sich is destroyed',
   'A Russian army destroys the last Cossack stronghold in June, during the reign of Catherine II.',
   [ieu('Zaporozhian Sich', 'Z%5CA%5CZaporozhianSich.htm')]),
  ('1840', 'Shevchenko publishes Kobzar',
   'Taras Shevchenko, born a serf, publishes his first collection of poems and becomes Ukraine’s national bard. In 1847 he is arrested, and his anti-tsarist verse earns him forced military service in a remote region.',
   [ieu('Shevchenko, Taras', 'S%5CH%5CShevchenkoTaras.htm')]),
  ('1876', 'The Ems decree',
   'A secret decree by Tsar Alexander II bans printing original works and translations in Ukrainian, importing Ukrainian books, and staging plays or public readings in the language. It continues a crackdown begun in 1863.',
   [ieu('Ems Ukase', 'E%5CM%5CEmsUkase.htm')]),
 ]),
 ('era-soviet', 'Revolution and Soviet rule', '1918 to 1991', [
  ('1918', 'The Ukrainian People’s Republic declares independence',
   'The declaration is dated January 22. A year later to the day, the republic proclaims its union with the Western Ukrainian republic. By 1921 Ukraine has been divided between the Soviet state and Poland.',
   [ieu('Struggle for Independence (1917–20)', 'S%5CT%5CStruggleforIndependence1917hD720.htm'), ieu('Riga, Peace Treaty of', 'R%5CI%5CRigaPeaceTreatyof.htm')]),
  ('1922', 'Soviet Ukraine joins the USSR',
   'The Soviet republics are bound into one union on December 30. A decade of Ukrainization follows: officials are required to learn Ukrainian, and Ukrainians are recruited into the state. Stalin then eliminates the policy and the Ukrainian elite it had raised.',
   [ieu('Union of Soviet Socialist Republics', 'U%5CN%5CUnionofSovietSocialistRepublics.htm'), ieu('Ukrainization', 'U%5CK%5CUkrainization.htm')]),
  ('1932–33', 'The Holodomor',
   'About four million people, mainly Ukrainian peasants, starve to death in a famine caused by the policies of Stalin and other Soviet leaders. Ukraine recognized it as a genocide in 2006, and both houses of the US Congress did so in 2018.',
   [ieu('Famine-Genocide of 1932–3', 'F%5CA%5CFamine6Genocideof1932hD73.htm'), ('UNIAN, on recognition by the US Congress', 'https://www.unian.info/world/holodomor-texas-state-legislature-recognizes-ukraine-famine-as-genocide-11437102.html')]),
  ('1941–44', 'Nazi occupation',
   'Millions of civilians are murdered. Between 1.4 and 1.5 million of Ukraine’s Jews are killed, two out of every three. At Babyn Yar in Kyiv, 33,771 Jews are shot over two days, September 29 and 30, 1941.',
   [ieu('Second World War', 'S%5CE%5CSecondWorldWar.htm'), ieu('Holocaust', 'H%5CO%5CHolocaust.htm'), ('US Holocaust Memorial Museum, on Babyn Yar', 'https://encyclopedia.ushmm.org/content/en/article/kiev-and-babi-yar')]),
  ('1944', 'The Crimean Tatars are deported',
   'The Soviet government accuses the Crimean Tatars of treason and deports them en masse to Central Asia and other distant regions. Between a fifth and a quarter die along the way.',
   [ieu('Crimean Tatars', 'C%5CR%5CCrimeanTatars.htm'), ieu('Crimea', 'C%5CR%5CCrimea.htm')]),
  ('1954', 'Crimea is transferred to Soviet Ukraine',
   'On February 19 the Soviet leadership moves Crimea from the Russian republic to the Ukrainian one, to help its economic development. After 1991 it remains part of independent Ukraine.',
   [ieu('Crimea', 'C%5CR%5CCrimea.htm')]),
  ('1986', 'Chornobyl',
   'An explosion at the nuclear plant in Kyiv oblast on April 26 becomes the worst disaster of its kind in the world. Soviet officials acknowledge an accident only after Swedish scientists detect the radiation two days later. Anger over the disaster feeds the movement for political reform in Ukraine.',
   [ieu('Chornobyl nuclear disaster', 'C%5CH%5CChornobylnucleardisaster.htm')]),
  ('1991', 'Independence',
   'Parliament declares independence on August 24. In a referendum on December 1, 90.3 percent of voters approve, on a turnout of 84.2 percent.',
   [ieu('Ukraine’s Declaration of Independence, 1991', 'U%5CK%5CUkrainehDAsDeclarationofIndependence1991.htm'), ieu('Referendum', 'R%5CE%5CReferendum.htm')]),
 ]),
 ('era-independent', 'Independent Ukraine', '1994 to 2014', [
  ('1994', 'The Budapest Memorandum',
   'Ukraine gives up the world’s third-largest nuclear arsenal. In return Russia, the United States and the United Kingdom commit to respect its sovereignty and existing borders and to refrain from using force against it.',
   [ieu('Budapest Memorandum', 'B%5CU%5CBudapestMemorandum.htm')]),
  ('2004', 'The Orange Revolution',
   'Mass protests follow a falsified presidential runoff. The Supreme Court finds the true result impossible to determine and orders a repeat vote on December 26, which Viktor Yushchenko wins.',
   [ieu('Orange Revolution', 'O%5CR%5COrangeRevolution.htm')]),
  ('2013–14', 'The Revolution of Dignity',
   'President Viktor Yanukovych postpones an association agreement with the European Union, then accepts a $15 billion loan from Russia. Protests on Kyiv’s Maidan grow into a popular uprising. More than 100 people are dead by the time Yanukovych flees to Russia in February 2014.',
   [ieu('Euromaidan Revolution', 'E%5CU%5CEuromaidanRevolution.htm')]),
  ('2014', 'Russia seizes Crimea and starts a war in Donbas',
   'Vladimir Putin orders the occupation and annexation of Crimea, then launches a war in the Donets Basin. The United Nations estimates that 14,200 to 14,400 people are killed there by the end of 2021.',
   [ieu('Euromaidan Revolution', 'E%5CU%5CEuromaidanRevolution.htm'), ('UN human rights office, conflict-related casualties 2014–2021', 'https://ukraine.un.org/en/168060-conflict-related-civilian-casualties-ukraine')]),
 ]),
 ('era-invasion', 'The full-scale invasion', '2022 to today', [
  ('Feb 2022', 'Russia launches a full-scale invasion',
   'The attack begins on February 24. The UN General Assembly demands that Russia withdraw, by 141 votes to 5. Russian forces leave the Kyiv, Chernihiv and Sumy regions by early April. UN investigators later document the killing of 441 civilians there, 73 of them in Bucha.',
   [('United Nations, General Assembly vote of March 2, 2022', 'https://press.un.org/en/2022/ga12407.doc.htm'), ('UN human rights chief, report to the Human Rights Council', 'https://www.unognewsroom.org/story/en/1413/un-high-commissioner-volker-tuerk-on-human-rights-situation-in-ukraine-at-hrc')]),
  ('Late 2022', 'Ukraine retakes ground in the east and south',
   'A surprise counteroffensive in September retakes Izium, Kupiansk and other towns in Kharkiv region, and Kherson city is liberated in November. Earlier, in June, the European Union makes Ukraine a candidate for membership.',
   [('NPR via MPR News, September 10, 2022', 'https://www.mprnews.org/story/2022/09/10/npr-ukraine-russia-troop-pullback-kharkiv'), ieu('Kherson', 'K%5CH%5CKherson.htm'), AA]),
  ('Mar 2023', 'An arrest warrant for Putin',
   'On March 17 the International Criminal Court issues a warrant for Vladimir Putin over the unlawful deportation and transfer of children from occupied areas of Ukraine to Russia.',
   [('International Criminal Court, press release', 'https://www.icc-cpi.int/news/situation-ukraine-icc-judges-issue-arrest-warrants-against-vladimir-vladimirovich-putin-and')]),
  ('June 2023', 'The Kakhovka dam is destroyed',
   'On the night of June 6 the dam, held by Russian forces, is blown up. Russia denies doing it. Floodwaters reach nearly 80 settlements and the reservoir drains.',
   [ieu('Kakhovka Hydroelectric Station', 'K%5CA%5CKakhovkaHydroelectricStation.htm'), ieu('Kakhovka Reservoir', 'K%5CA%5CKakhovkaReservoir.htm')]),
  ('2024', 'Membership talks, and a strike into Russia',
   'The European Union formally opens membership negotiations with Ukraine in June. In August Ukrainian forces cross into Russia’s Kursk region. Russia announces it has retaken the region in April 2025.',
   [AA]),
  ('2025–26', 'Talks without a ceasefire',
   'Russia and Ukraine meet in Istanbul in May 2025, their first talks in three years, and agree to exchange 1,000 prisoners each. Talks mediated by the United States continue into 2026 without producing a ceasefire.',
   [AA, CFR]),
  ('Oct 2026', 'The war continues',
   'The invasion is in its fifth year. Russia occupies about a fifth of Ukraine and continues to bombard its cities. Ukraine fights on.',
   [CFR, ('Ukrainska Pravda, DeepState figures, January 2026', 'https://www.pravda.com.ua/eng/news/2026/01/01/8014292/')]),
 ]),
]

def event_id(title): return 'event-' + slug(title)

def targets():
    """English title -> (element id, English label, Ukrainian label), for links from other sections."""
    return {title: (event_id(title), f'{year}: {title}', f'{UK.YEARS.get(year, year)}: {UK.EVENTS[title][0]}')
            for _, _, _, events in ERAS for year, title, _, _ in events}

# Pictures from Wikimedia Commons (rule 7): one banner per era, keyed by era id, and one for some entries,
# keyed by English title. An era without one opens on the cross-stitch pattern; an entry without one has none.
ERA_PHOTOS = {
 'era-rus': photo('era-rus.jpg', ('Inside Saint Sophia Cathedral, Kyiv, with its 11th-century mosaics', 'Інтер’єр Софійського собору в Києві з мозаїками XI століття'), 'Galvm', 'CC BY-SA 4.0',
       'https://commons.wikimedia.org/wiki/File:Kyiv-Saint_Sophia_Cathedral-interior-11.jpg'),
 'era-cossacks': photo('era-cossacks.jpg', ('Mykola Ivasiuk, Bohdan Khmelnytsky’s Entry into Kyiv, National Art Museum of Ukraine', 'Микола Івасюк, «В’їзд Богдана Хмельницького до Києва», Національний художній музей України'), 'Mykola Ivasiuk', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:Pic_I_V_Ivasiuk_Mykola_Bohdan_Khmelnytskys_Entry_to_Kyiv.jpg'),
 'era-soviet': photo('era-soviet.jpg', ('A 100-hryvnia note of the Ukrainian People’s Republic, 1918, designed by Heorhii Narbut', 'Банкнота 100 гривень Української Народної Республіки, 1918 рік, автор — Георгій Нарбут'), 'Heorhii Narbut', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:Ukrainian_100_hryvnia%27s_note_of_the_People%27s_repub.jlic_of_Ukraine_%281918%29_front_side.jpg'),
 'era-independent': photo('era-independent.jpg', ('Wheat fields under a blue sky in Lviv region', 'Пшеничні поля під синім небом на Львівщині'), 'Raimond Spekking', 'CC BY-SA 4.0',
       'https://commons.wikimedia.org/wiki/File:Wheat_fields_in_Ukraine-5966-98.jpg'),
 'era-invasion': photo('era-invasion.jpg', ('The wrecked An-225 Mriya in its hangar at Hostomel, April 2022', 'Зруйнована «Мрія» Ан-225 в ангарі в Гостомелі, квітень 2022 року'), 'Oleksandr Ratushniak', 'CC BY-SA 4.0',
       'https://commons.wikimedia.org/wiki/File:Antonov_Airport_after_Russian_invasion_of_Ukraine_and_Mriya_%28cropped%29.jpg'),
}
EVENT_PHOTOS = {
 'Oleh takes Kyiv': photo('event-882.jpg', ('Oleh receives tribute, a miniature from the 15th-century Radziwiłł Chronicle', 'Олег отримує данину, мініатюра з Радзивіллівського літопису XV століття'), 'Unknown author', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:Oleg_in_Radzivill.jpg'),
 'Volodymyr the Great adopts Christianity': photo('event-988.jpg', ('The monument to Volodymyr the Great in Kyiv, unveiled in 1853', 'Пам’ятник Володимирові Великому в Києві, відкритий 1853 року'), 'Алексей Косенко', 'CC BY-SA 4.0',
       'https://commons.wikimedia.org/wiki/File:%D0%9F%D0%B0%D0%BC%D1%8F%D1%82%D0%BD%D0%B8%D0%BA_%D0%BA%D0%BD%D1%8F%D0%B7%D1%8E_%D0%92%D0%BB%D0%B0%D0%B4%D0%B8%D0%BC%D0%B8%D1%80%D1%83_%D0%B7%D0%B8%D0%BC%D0%BE%D0%B9.jpg'),
 'Saint Sophia rises in Kyiv': photo('event-1037.jpg', ('The Virgin Orans, the 11th-century mosaic in the apse of Saint Sophia', 'Оранта, мозаїка XI століття в апсиді Софійського собору'), 'Unknown artist', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:Oranta-Kyiv.jpg'),
 'Mongol armies sack Kyiv': photo('event-1240.jpg', ('Batu’s army before Kyiv, an illustration from Mykola Arkas’s History of Ukraine-Rus’, 1912', 'Військо Батия під Києвом, ілюстрація з «Історії України-Русі» Миколи Аркаса, 1912 рік'), 'From Mykola Arkas, History of Ukraine-Rus’ (1912)', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:%D0%86%D1%81%D1%82%D0%BE%D1%80%D1%96%D1%8F_%D0%A3%D0%BA%D1%80%D0%B0%D1%97%D0%BD%D0%B8-%D0%A0%D1%83%D1%81%D1%96._1912._%D0%91%D0%B0%D1%82%D0%B8%D0%B9_%D0%BF%D1%96%D0%B4_%D0%9A%D0%B8%D1%97%D0%B2%D0%BE%D0%BC.jpg'),
 'The Union of Lublin': photo('event-1569.jpg', ('Jan Matejko, The Union of Lublin, 1869, Lublin Museum', 'Ян Матейко, «Люблінська унія», 1869 рік, Люблінський музей'), 'Jan Matejko', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:Lublin_Museum_2018_P12_Jan_Matejko_Union_of_Lublin.jpg'),
 'Khmelnytsky’s uprising': photo('event-1648.jpg', ('Bohdan Khmelnytsky, an engraving by Willem Hondius, 1651, Rijksmuseum', 'Богдан Хмельницький, гравюра Віллема Гондіуса, 1651 рік, Рейксмузеум'), 'Willem Hondius (Rijksmuseum)', 'CC0',
       'https://commons.wikimedia.org/wiki/File:Portrait_of_Hetman_Bohdan_Khmelnytsky_%28Willem_Hondius%2C_engraving%29.jpeg'),
 'Poltava and Orlyk’s constitution': photo('event-1710.jpg', ('The first page of Pylyp Orlyk’s constitution, 1710, National Archives of Sweden', 'Перша сторінка Конституції Пилипа Орлика, 1710 рік, Національний архів Швеції'), 'National Archives of Sweden', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:Filip_Orliks_konstitution_front_1-crop.tif'),
 'Shevchenko publishes Kobzar': photo('event-1840.jpg', ('The title page of Shevchenko’s Kobzar, 1840', 'Титульна сторінка «Кобзаря» Шевченка, 1840 рік'), 'Taras Shevchenko', 'CC BY-SA 4.0',
       'https://commons.wikimedia.org/wiki/File:1840_-_Kobzar_-_page_3_-_page_1_%28Title%29_-.jpg'),
 'The Ems decree': photo('event-1876.jpg', ('A plaque in Bad Ems, Germany, on the house where the decree was signed', 'Пам’ятна дошка в Бад-Емсі, Німеччина, на будинку, де підписали указ'), 'Silin2005', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:Ems_Ukaz_plaque_in_Bad_Ems.JPG'),
 'The Ukrainian People’s Republic declares independence': photo('event-1918.jpg', ('The Fourth Universal of the Central Rada, January 22, 1918', 'IV Універсал Української Центральної Ради, 22 січня 1918 року'), 'Ukrainian Central Rada', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:IV_%D0%A3%D0%BD%D1%96%D0%B2%D0%B5%D1%80%D1%81%D0%B0%D0%BB_%D0%A3%D0%A6%D0%A0.jpg'),
 'The Holodomor': photo('event-1932.jpg', ('Candles and ears of wheat on Holodomor Remembrance Day in Lviv, 2013', 'Свічки та колоски на День пам’яті жертв Голодомору у Львові, 2013 рік'), 'DixonD', 'CC BY-SA 3.0',
       'https://commons.wikimedia.org/wiki/File:Holodomor_Remembrance_Day_2013_in_Lviv_18.JPG'),
 'Nazi occupation': photo('event-1941.jpg', ('The Babyn Yar ravine in Kyiv, 2020', 'Урочище Бабин Яр у Києві, 2020 рік'), 'Педагог Світлана', 'CC BY-SA 4.0',
       'https://commons.wikimedia.org/wiki/File:%D0%91%D0%B0%D0%B1%D0%B8%D0%BD_%D0%AF%D1%80%2C_%D1%83%D1%80%D0%BE%D1%87%D0%B8%D1%89%D0%B5%2C_%D0%A8%D0%B5%D0%B2%D1%87%D0%B5%D0%BD%D0%BA%D1%96%D0%B2%D1%81%D1%8C%D0%BA%D0%B8%D0%B9_%D1%82%D0%B0_%D0%9F%D0%BE%D0%B4%D1%96%D0%BB%D1%8C%D1%81%D1%8C%D0%BA%D0%B8%D0%B9_%D1%80%D0%B0%D0%B9%D0%BE%D0%BD%D0%B8%2C_%D0%BC.%D0%9A%D0%B8%D1%97%D0%B2.jpg'),
 'The Crimean Tatars are deported': photo('event-1944.jpg', ('The Khan’s Palace in Bakhchysarai, Crimea, 2013', 'Ханський палац у Бахчисараї, Крим, 2013 рік'), 'Fluid70', 'CC BY-SA 3.0',
       'https://commons.wikimedia.org/wiki/File:Bakhchisaray_Palace%2C_Panorama%2C_2013.jpg'),
 'Crimea is transferred to Soviet Ukraine': photo('event-1954.jpg', ('The transfer decree as printed in the Soviet Vedomosti, March 1954', 'Указ про передачу, надрукований у радянських «Відомостях», березень 1954 року'), 'Presidium of the Supreme Soviet of the USSR', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:The_transfer_of_Crimea.jpg'),
 'Chornobyl': photo('event-1986.jpg', ('The Chornobyl plant and the Prypiat River from the International Space Station, 2018', 'Чорнобильська АЕС і річка Прип’ять з Міжнародної космічної станції, 2018 рік'), 'NASA', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:ISS-57_Chernobyl_Nuclear_Power_Plant%2C_Ukraine.jpg'),
 'Independence': photo('event-1991.jpg', ('The Act of Declaration of Independence of Ukraine, August 24, 1991', 'Акт проголошення незалежності України, 24 серпня 1991 року'), 'Verkhovna Rada of the Ukrainian SSR', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:Declaration_of_Independence_of_Ukraine%2C_1991.jpg'),
 'The Budapest Memorandum': photo('event-1994.jpg', ('An empty missile silo at the Museum of the Strategic Missile Forces in Ukraine', 'Порожня ракетна шахта в Музеї ракетних військ стратегічного призначення'), 'Vladimir Zinin', 'CC BY-SA 3.0',
       'https://commons.wikimedia.org/wiki/File:Missile_silo_at_the_Strategic_Missile_Forces_Museum.JPG'),
 'The Revolution of Dignity': photo('event-2014-maidan.jpg', ('A barricade on Hrushevskoho Street, Kyiv, February 2014', 'Барикада на вулиці Грушевського в Києві, лютий 2014 року'), 'Аимаина хикари', 'CC0',
       'https://commons.wikimedia.org/wiki/File:%D0%91%D0%B0%D1%80%D1%80%D0%B8%D0%BA%D0%B0%D0%B4%D0%B0_%D0%BD%D0%B0_%D0%B3%D1%80%D1%83%D1%88%D0%B5.jpg'),
 'Russia seizes Crimea and starts a war in Donbas': photo('event-2014-map.jpg', ('Map of the war in Ukraine as of September 2014', 'Мапа війни в Україні станом на вересень 2014 року'), 'Niele', 'CC BY-SA 4.0',
       'https://commons.wikimedia.org/wiki/File:2014_Russo-ukrainian-conflict_map.svg'),
 'Ukraine retakes ground in the east and south': photo('event-2022.jpg', ('Map of the Kherson counteroffensive, 2022', 'Мапа Херсонського контрнаступу, 2022 рік'), 'Rr016', 'CC BY-SA 4.0',
       'https://commons.wikimedia.org/wiki/File:2022_Kherson_Counteroffensive.png'),
 'An arrest warrant for Putin': photo('event-2023-icc.jpg', ('The International Criminal Court in The Hague', 'Міжнародний кримінальний суд у Гаазі'), 'Choinowski', 'CC BY-SA 4.0',
       'https://commons.wikimedia.org/wiki/File:International_Criminal_Court_2022.jpg'),
 'The Kakhovka dam is destroyed': photo('event-2023-kakhovka.jpg', ('The Kakhovka Reservoir from space, full in June 2022 and drained on June 18, 2023', 'Каховське водосховище з космосу: повне в червні 2022 року і спорожніле 18 червня 2023 року'), 'NASA Earth Observatory (Lauren Dauphin), Landsat data from the US Geological Survey', 'Public domain',
       'https://commons.wikimedia.org/wiki/File:Ukrainereservoir_oli2_2023169_lrg.jpg'),
 'Membership talks, and a strike into Russia': photo('event-2024.jpg', ('Map of the Ukrainian incursion into Russia’s Kursk region, August 2024', 'Мапа операції ЗСУ в Курській області Росії, серпень 2024 року'), 'Ecrusized', 'CC0',
       'https://commons.wikimedia.org/wiki/File:August_2024_Kursk_Oblast_incursion.svg'),
 'The war continues': photo('event-2026.jpg', ('Storm clouds over a sunflower field in Volyn region', 'Грозові хмари над соняшниковим полем на Волині'), 'Domalchuk', 'CC BY 4.0',
       'https://commons.wikimedia.org/wiki/File:Cumulonimbus_storm_clouds_over_sunflower_field_Ukraine.jpg'),
}

def _check_photos():
    era_ids = {era_id for era_id, _, _, _ in ERAS}
    titles = {title for _, _, _, events in ERAS for _, title, _, _ in events}
    for key, p in ERA_PHOTOS.items():
        if key not in era_ids: raise ValueError(f'ERA_PHOTOS: no era {key!r}')
        photos.validate(p, key)
    for key, p in EVENT_PHOTOS.items():
        if key not in titles: raise ValueError(f'EVENT_PHOTOS: no entry {key!r}')
        photos.validate(p, key)
_check_photos()

def photo_files():
    return [photos.IMAGES / p['file'] for p in [*ERA_PHOTOS.values(), *EVENT_PHOTOS.values()]]

def claims():
    """(url, phrase, what) for check.py: each picture's Commons page must still show its license."""
    return [photos.claim(p, f"history picture {p['file']}: license") for p in [*ERA_PHOTOS.values(), *EVENT_PHOTOS.values()]]

def era_nav():
    """The eras as a ribbon of links, oldest first."""
    links = []
    for era_id, name, span, _ in ERAS:
        name_uk, span_uk = UK.ERAS[name]
        links.append(f'      <a class="era-link" href="#{era_id}"><span class="era-link-span">{both(span, span_uk)}</span><span class="era-link-name">{both(name, name_uk)}</span></a>')
    return '\n'.join(links)

def _sources(sources):
    """The sources on one line, opening to the links. Each label is 'Outlet, article'; the line names the outlets."""
    e = html.escape
    outlets = ', '.join(dict.fromkeys(label.split(',')[0] for label, _ in sources))
    summary = both(('Sources: ' if len(sources) > 1 else 'Source: ') + outlets, ('Джерела: ' if len(sources) > 1 else 'Джерело: ') + outlets)
    links = ''.join(f'<li><a href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a></li>' for label, url in sources)
    return f'<details class="why"><summary>{summary}</summary><ul>{links}</ul></details>'

def render(story_links):
    """The timeline HTML in both languages. story_links maps an event id to [(story id, English label, Ukrainian label)]."""
    out = []
    for number, (era_id, name, span, events) in enumerate(ERAS, 1):
        name_uk, span_uk = UK.ERAS[name]
        p = ERA_PHOTOS.get(era_id)
        picture = f'{photos.img(p)}<p class="credit">{photos.credit(p)}</p>' if p else ''
        out.append(f'''    <div class="era" id="{era_id}">
      <header class="era-head{'' if p else ' c-ornament'}">{picture}
        <div class="era-title">
          <p class="era-num">{both(f"Chapter {number}", f"Розділ {number}")}</p>
          <h3>{both(name, name_uk)}</h3>
          <p class="era-range">{both(span, span_uk)}</p>
        </div>
      </header>
      <ol class="events">''')
        for year, title, text, sources in events:
            title_uk, text_uk = UK.EVENTS[title]
            p = EVENT_PHOTOS.get(title)
            # A panorama runs across the card; a tall picture, such as a document page, sits narrower beside the text.
            shape = '' if not p else ' wide' if p['size'][0] > 1.9 * p['size'][1] else ' tall' if p['size'][1] > 1.15 * p['size'][0] else ''
            figure = f'<figure class="event-fig{shape}">{photos.img(p)}<figcaption class="credit">{photos.credit(p)}</figcaption></figure>' if p else ''
            stories = ''.join(f'<p class="event-story"><a href="#{sid}">{both("A story from this time: " + en, "Історія з цього часу: " + uk)}</a></p>'
                              for sid, en, uk in story_links.get(event_id(title), []))
            out.append(f'''        <li class="event" id="{event_id(title)}" tabindex="-1">
          <p class="event-year">{both(year, UK.YEARS.get(year, year))}</p>
          <div class="event-card">{figure}
            <h4>{both(title, title_uk)}</h4>
            <p>{both(text, text_uk)}</p>{stories}
            {_sources(sources)}
          </div>
        </li>''')
        out.append('      </ol>\n    </div>')
    return '\n'.join(out)
