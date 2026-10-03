"""The history timeline. Every entry carries the sources its text was checked against.
Ukrainian text lives in history_uk.py, keyed by the English title; a missing translation stops the build.
check.py confirms the source links still load."""
import html

from i18n import both
import history_uk as UK

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

def render():
    """Returns the timeline HTML in both languages, the entry count, and the era list for the jump links."""
    e = html.escape; out = []; n = 0; eras = []
    for era_id, name, span, events in ERAS:
        name_uk, span_uk = UK.ERAS[name]; eras.append((era_id, name, name_uk))
        out.append(f'    <div class="era" id="{era_id}">\n      <h3>{both(name, name_uk)} {both(span, span_uk, cls="era-range")}</h3>\n      <ol class="events">')
        for year, title, text, sources in events:
            title_uk, text_uk = UK.EVENTS[title]
            links = '; '.join(f'<a href="{e(url)}" target="_blank" rel="noopener">{e(label)}</a>' for label, url in sources)
            label = both('Sources', 'Джерела') if len(sources) > 1 else both('Source', 'Джерело')
            out.append(f'        <li class="event"><span class="year">{both(year, UK.YEARS.get(year, year))}</span><div><h4>{both(title, title_uk)}</h4><p>{both(text, text_uk)}</p><p class="src">{label}: {links}</p></div></li>')
            n += 1
        out.append('      </ol>\n    </div>')
    return '\n'.join(out), n, eras
