"""The Give section, in English and Ukrainian. Every entry states what was checked and links to it.
Each text is an (English, Ukrainian) pair.

US charities draw their IRS facts and ratings from data/irs.json and data/charity_navigator.json,
which refresh.py pulls and check.py compares against the live records. A charity with no record
stops the build.

A check may name a phrase its page must contain, as a fourth item: (English, Ukrainian, url, phrase).
check.py confirms each phrase is still there. "EIN on its own site matches" checks register the EIN."""
import html, json, pathlib

from i18n import both, plural_uk, slug

DATA = pathlib.Path(__file__).parent / 'data'
IRS = json.loads((DATA / 'irs.json').read_text(encoding='utf-8'))
CN = json.loads((DATA / 'charity_navigator.json').read_text(encoding='utf-8'))
# The day every entry below was last reviewed by hand. check.py fails once it is six months old.
REVIEWED = '2026-10-03'
EINS = []  # every US charity on the page, filled as the entries below are built
CLAIMS = []  # (url, phrase, what) for check.py, filled as the entries below are built
class Caveat(tuple):
    """A check that found something missing or worth knowing. The page marks it differently from a confirmation."""
def caveat(*check): return Caveat(check)

READ_VIA_SEARCH = caveat('its site blocks automated checks, so it was read through search', 'сайт блокує автоматичні перевірки, тому його читали через пошук', None)
EIN_MATCHES = ('EIN on its own site matches', 'EIN на сайті організації збігається')

def num_uk(x): return f'{x:.1f}'.replace('.', ',')

def us(ein):
    """Kind line and standard checks for a US 501(c)(3), built from the pulled records."""
    EINS.append(ein)
    r = IRS[ein]; c = CN[ein]; shown = f'{ein[:2]}-{ein[2:]}'; year = r['ruling'][:4]
    checks = [(f'IRS-recognized since {year}', f'визнана Податковою службою США (IRS) з {year} року', f'https://projects.propublica.org/nonprofits/organizations/{ein}')]
    if r['revenue']:
        m = r['revenue'] / 1e6
        checks.append((f'${m:.1f} million revenue on its {r["latest_year"]} tax filing', f'дохід за податковою декларацією {r["latest_year"]} року — {num_uk(m)} млн доларів', None))
    else:
        checks.append(caveat('no tax filing data published yet', 'даних податкової декларації ще не оприлюднено', None))
    cn_url = f'https://www.charitynavigator.org/ein/{ein}'
    if c['stars']:
        ratio = c['program_ratio']
        stars_uk = plural_uk(int(c['stars']), 'зірка', 'зірки', 'зірок')
        checks.append((f'Charity Navigator: {c["stars"]} of 4 stars, with {ratio:.1f}% of spending going to programs over three years',
                       f'Charity Navigator: {c["stars"]} {stars_uk} з 4; на програми йде {num_uk(ratio)} % витрат (середнє за три роки)', cn_url))
    else:
        checks.append(caveat('not yet rated by Charity Navigator', 'Charity Navigator ще не оцінював', cn_url))
    kind = (f'US 501(c)(3), EIN {shown}, {r["city"]}, {r["state"]}', f'Благодійна організація США 501(c)(3), EIN {shown}, {r["city"]}, {r["state"]}')
    return kind, checks

def org(name, kind, what, checks, action, url, ein=None): return dict(name=name, kind=kind, what=what, checks=checks, action=action, url=url, ein=ein)
def us_org(name, ein, what, extra_checks, action, url):
    kind, checks = us(ein)
    for check in extra_checks:
        if check[:2] == EIN_MATCHES: CLAIMS.append((check[2], f'{ein[:2]}-{ein[2:]}', f'{name[0]}: EIN on its own site'))
    return org(name, kind, what, checks + extra_checks, action, url, ein)
def give_at(domain): return (f'Give at {domain}', f'Пожертвувати на {domain}')
def same(name): return (name, name)

RAZOM_FAQ = 'https://www.razomforukraine.org/faq/'
GROUPS = [
 (('Defense', 'Оборона'),
  ('These fund Ukraine’s military directly. Gifts to them are generally not tax-deductible in the United States.',
   'Ці фонди напряму підтримують українське військо. У США пожертви на них зазвичай не зменшують оподатковуваний дохід.'), [
  org(same('UNITED24'), ('Government of Ukraine', 'Уряд України'),
      ('Ukraine’s official fundraising platform, started by President Zelenskyy in 2022. You choose where your money goes: defense, demining, medical aid, education or rebuilding.',
       'Офіційна фандрейзингова платформа України, яку 2022 року започаткував президент Зеленський. Ви самі обираєте напрям: оборона, розмінування, медична допомога, освіта чи відбудова.'),
      [('official .gov.ua site', 'офіційний сайт у домені .gov.ua', None),
       ('audited by Deloitte and BDO', 'аудит проводять Deloitte і BDO', 'https://u24.gov.ua/about', 'Deloitte and BDO'),
       ('publishes weekly spending reports', 'щотижня публікує звіти про витрати', 'https://u24.gov.ua/reports')],
      give_at('u24.gov.ua'), 'https://u24.gov.ua/'),
  org(('Come Back Alive', '«Повернись живим»'), ('Ukrainian foundation, since 2014', 'Український фонд, з 2014 року'),
      ('Equips Ukraine’s Defense Forces with drones, thermal optics, vehicles and weapons, and trains soldiers. In 2022 it became the first Ukrainian foundation allowed to import military goods.',
       'Забезпечує Сили оборони України дронами, тепловізорами, транспортом і зброєю та навчає військових. 2022 року першим з українських фондів отримав дозвіл на імпорт товарів військового призначення.'),
      [('management and anti-bribery systems certified by Bureau Veritas, an outside auditor, under ISO 9001 and ISO 37001', 'системи управління та протидії хабарництву сертифікував незалежний аудитор Bureau Veritas за стандартами ISO 9001 та ISO 37001', 'https://savelife.in.ua/en/materials/news-en/the-come-back-alive-foundation-has-passe-en/'),
       ('publishes every purchase and incoming donation', 'публікує всі закупівлі й надходження', 'https://savelife.in.ua/en/donate-en/'),
       READ_VIA_SEARCH],
      give_at('savelife.in.ua'), 'https://savelife.in.ua/en/'),
  org(('Serhiy Prytula Charity Foundation', 'Благодійний фонд Сергія Притули'), ('Ukrainian foundation, since 2020', 'Український фонд, з 2020 року'),
      ('Buys drones, vehicles, optics and medical supplies for the military, and runs humanitarian aid alongside.',
       'Купує для війська дрони, транспорт, оптику й медичні засоби, а також надає гуманітарну допомогу.'),
      [('in Ukraine’s state register as a nonprofit since July 2020, with reported income of about 2 billion hryvnias for 2025', 'у державному реєстрі України як неприбуткова організація з липня 2020 року; задекларований дохід за 2025 рік — близько 2 млрд гривень', 'https://opendatabot.ua/c/43720363', '43720363'),
       ('publishes an annual report and monthly reports on its military aid', 'публікує річний звіт і щомісячні звіти про допомогу війську', 'https://prytulafoundation.org/military-reports'),
       READ_VIA_SEARCH],
      give_at('prytulafoundation.org'), 'https://prytulafoundation.org/en/'),
 ]),
 (('Medical and humanitarian aid', 'Медична та гуманітарна допомога'),
  ('US-registered charities. Gifts are generally tax-deductible for US donors.',
   'Благодійні організації, зареєстровані у США. Американські жертводавці зазвичай можуть відняти такі пожертви від оподатковуваного доходу.'), [
  us_org(same('Razom for Ukraine'), '464604398',
      ('Founded in 2014; razom means “together.” Delivers medical and humanitarian aid in Ukraine and speaks up for Ukraine in the United States.',
       'Заснована 2014 року. Доставляє медичну й гуманітарну допомогу в Україну та обстоює інтереси України у Сполучених Штатах.'),
      [(*EIN_MATCHES, RAZOM_FAQ), ('publishes its financials', 'публікує фінансову звітність', 'https://www.razomforukraine.org/about-us/financials/', '990')],
      give_at('razomforukraine.org'), 'https://www.razomforukraine.org/donate/'),
  us_org(same('Nova Ukraine'), '465335435',
      ('Supplies hospitals, evacuates civilians and supports schools and communities across Ukraine.',
       'Забезпечує лікарні, евакуює цивільних і підтримує школи та громади по всій Україні.'),
      [('publishes impact and financial reports', 'публікує звіти про діяльність і фінанси', 'https://novaukraine.org/about-us/reports/')],
      give_at('novaukraine.org'), 'https://novaukraine.org/donate/'),
  us_org(same('United Help Ukraine'), '471837509',
      ('Sends medical equipment, from syringes to ventilators, to Ukrainian hospitals and medics, and humanitarian aid to civilians.',
       'Надсилає українським лікарням і медикам медичне обладнання, від шприців до апаратів ШВЛ, а цивільним — гуманітарну допомогу.'),
      [(*EIN_MATCHES, 'https://unitedhelpukraine.org/'), ('publishes financial reports', 'публікує фінансові звіти', 'https://unitedhelpukraine.org/financial-reports/')],
      give_at('unitedhelpukraine.org'), 'https://unitedhelpukraine.org/'),
  us_org(same('Sunflower of Peace'), '472620675',
      ('Funds tactical medical supplies and ambulances for Ukraine.', 'Фінансує засоби тактичної медицини та карети швидкої допомоги для України.'),
      [(*EIN_MATCHES, 'https://www.sunflowerofpeace.com/')],
      give_at('sunflowerofpeace.com'), 'https://www.sunflowerofpeace.com/'),
  us_org(same('Prytula Foundation USA'), '991441326',
      ('The US arm of the Prytula foundation, limited to civilian aid: medical supplies, evacuation vehicles, shelters and demining.',
       'Американське відділення фонду Притули, яке займається лише цивільною допомогою: медичні засоби, транспорт для евакуації, укриття та розмінування.'),
      [('announced by Serhiy Prytula himself', 'про створення оголосив сам Сергій Притула', 'https://x.com/serhiyprytula/status/1829871215206408239'),
       ('posts its Form 990 and auditor’s report', 'публікує податкову форму 990 і аудиторський звіт', 'https://prytulafoundation.us/transparency', '990')],
      give_at('prytulafoundation.us'), 'https://prytulafoundation.us/'),
 ]),
 (('Wounded and rehabilitation', 'Поранені та реабілітація'), None, [
  org(same('Superhumans Center'), ('Ukrainian medical center', 'Український медичний центр'),
      ('Provides prosthetics, reconstructive surgery and rehabilitation to soldiers and civilians injured in the war.',
       'Надає протезування, реконструктивну хірургію та реабілітацію військовим і цивільним, які постраждали від війни.'),
      [('publishes audited financial statements for 2023, 2024 and 2025', 'публікує фінансову звітність з аудиторськими висновками за 2023, 2024 і 2025 роки', 'https://superhumans.com/en/reports/')],
      give_at('superhumans.com'), 'https://superhumans.com/en/donate-en/'),
  us_org(same('Protez Foundation'), '882437069',
      ('Fits Ukrainians who lost limbs in the war with prosthetics at no charge. Based in Minnesota, with prosthetic centers in Ukraine.',
       'Безкоштовно протезує українців, які втратили кінцівки на війні. Працює в Міннесоті, має протезні центри в Україні.'),
      [(*EIN_MATCHES, 'https://www.protezfoundation.org/'), ('publishes an independent financial audit', 'публікує незалежний фінансовий аудит', 'https://www.protezfoundation.org/financial-audit')],
      give_at('protezfoundation.org'), 'https://www.protezfoundation.org/donate'),
 ]),
 (('Animals', 'Тварини'), None, [
  org(same('UAnimals'), ('Ukrainian nonprofit, since 2016', 'Українська неприбуткова організація, з 2016 року'),
      ('Evacuates animals from war zones and supplies food and medicine to shelters.', 'Евакуює тварин із зони бойових дій і забезпечує притулки кормом та ліками.'),
      [('publishes its registration documents', 'публікує реєстраційні документи', 'https://uanimals.org/en/documents/'),
       ('annual reports give income and spending, with 98.5 million hryvnias raised in 2025', 'у річних звітах наведено доходи й витрати; 2025 року зібрано 98,5 млн гривень', 'https://uanimals.org/en/yearly-reports/'),
       ('publishes monthly reports', 'публікує щомісячні звіти', 'https://uanimals.org/en/monthly-reports/'),
       caveat('no outside audit found', 'зовнішнього аудиту не знайдено', None)],
      give_at('uanimals.org'), 'https://uanimals.org/en/how-to-help/'),
 ]),
 (('Send supplies', 'Надіслати речі'),
  ('Check before you pack a box. Razom, for one, does not take clothing or general goods and suggests asking a local church or community center. Below are the goods the groups above accept, and two carriers that ship to Ukraine.',
   'Перш ніж пакувати коробку, з’ясуйте, чи її приймуть. Наприклад, Razom не бере одяг і речі загального вжитку та радить звернутися до місцевої церкви чи громадського центру. Нижче — речі, які приймають згадані вище організації, і два перевізники, що доставляють в Україну.'), [
  org(('Medical equipment and supplies, through Razom', 'Медичне обладнання та засоби — через Razom'),
      ('Also takes non-military aid for first responders and front-line personnel', 'Також приймає невійськову допомогу для рятувальників і тих, хто працює на передовій'),
      ('Razom accepts donated goods only in these categories. Its questions page gives the contact address.', 'Razom приймає речі лише цих категорій. Контактну адресу вказано на сторінці запитань і відповідей.'),
      [('stated on Razom’s own questions page', 'зазначено на сторінці запитань і відповідей Razom', RAZOM_FAQ)],
      ('Read Razom’s rules', 'Правила Razom'), RAZOM_FAQ),
  org(('Chromebooks, through Nova Ukraine', 'Ноутбуки Chromebook — через Nova Ukraine'), ('New or gently used', 'Нові або в доброму стані'),
      ('Nova Ukraine collects laptops for classrooms and community centers in Ukraine.', 'Nova Ukraine збирає ноутбуки для шкільних класів і громадських центрів в Україні.'),
      [('stated on Nova Ukraine’s own site', 'зазначено на сайті Nova Ukraine', 'https://novaukraine.org/donate-technology-and-equipment/')],
      ('Donate a Chromebook', 'Передати Chromebook'), 'https://novaukraine.org/donate-technology-and-equipment/'),
  org(('Bulk aid shipments, through Meest', 'Великі вантажі допомоги — через Meest'),
      ('Shipping company. For loads of 200 pounds or more', 'Транспортна компанія. Для вантажів від 200 фунтів (100 кг)'),
      ('Meest ships humanitarian cargo from the US by sea or air, free of duties. The recipient in Ukraine must be a registered organization, not an individual.',
       'Meest доставляє гуманітарні вантажі зі США морем або літаком без мита. Отримувачем в Україні має бути зареєстрована організація, а не приватна особа.'),
      [('terms and prices stated on Meest’s own site', 'умови й ціни зазначено на сайті Meest', 'https://us.meest.com/humanitarian-aid-packages-for-ukraine'), caveat('a commercial carrier, not a charity', 'це комерційний перевізник, а не благодійна організація', None)],
      ('See Meest’s terms', 'Умови Meest'), 'https://us.meest.com/humanitarian-aid-packages-for-ukraine'),
  org(('Parcels to people in Ukraine, through Nova Post', 'Посилки людям в Україні — через «Нову пошту»'),
      ('Shipping company with US branches', 'Транспортна компанія з відділеннями у США'),
      ('Nova Post ships parcels from the US to Ukraine and quotes humanitarian shipments on request.', '«Нова пошта» доставляє посилки зі США в Україну, а вартість гуманітарних відправлень розраховує на запит.'),
      [('stated on Nova Post’s own US site', 'зазначено на американському сайті «Нової пошти»', 'https://novapost.com/en-us/international/send-to-ukraine-parcel'), caveat('a commercial carrier, not a charity', 'це комерційний перевізник, а не благодійна організація', None)],
      ('Ship with Nova Post', 'Надіслати «Новою поштою»'), 'https://novapost.com/en-us/international/send-to-ukraine-parcel'),
 ]),
 (('Give your time', 'Допомогти часом'), None, [
  us_org(same('ENGin'), '883527494',
      ('Pairs you with someone in Ukraine for a weekly video chat in English. You help them practice and learn about each other’s countries.',
       'Знайде вам співрозмовника в Україні для щотижневих відеорозмов англійською. Ви допомагаєте практикувати мову, і обоє дізнаєтеся більше про країни одне одного.'),
      [('says on its own site that it is a registered 501(c)(3)', 'на власному сайті зазначає, що є зареєстрованою організацією 501(c)(3)', 'https://www.enginprogram.org/faqs-for-volunteers', '501(c)(3)')],
      ('Volunteer with ENGin', 'Стати волонтером ENGin'), 'https://www.enginprogram.org/volunteer'),
  org(('Razom volunteers', 'Волонтерство в Razom'), ('Run by Razom for Ukraine, listed above', 'Організація Razom for Ukraine, згадана вище'),
      ('Razom takes volunteer applications through a form on its questions page and places people as its teams need them.',
       'Razom приймає заявки волонтерів через форму на сторінці запитань і відповідей та залучає людей, коли вони потрібні командам.'),
      [('stated on Razom’s own questions page', 'зазначено на сторінці запитань і відповідей Razom', RAZOM_FAQ)],
      ('Volunteer with Razom', 'Стати волонтером Razom'), RAZOM_FAQ),
  org(('United Help Ukraine volunteers', 'Волонтерство в United Help Ukraine'), ('Run by United Help Ukraine, listed above', 'Організація United Help Ukraine, згадана вище'),
      ('Volunteers help at events and pack supplies and gifts that go straight to Ukraine.', 'Волонтери допомагають на заходах і пакують речі та подарунки, які відправляють прямо в Україну.'),
      [('stated on its own site', 'зазначено на сайті організації', 'https://unitedhelpukraine.org/how-you-can-help/')],
      ('Sign up to volunteer', 'Записатися у волонтери'), 'https://unitedhelpukraine.org/how-you-can-help/'),
 ]),
]

def org_id(o): return 'org-' + slug(o['name'][0])
def group_id(title): return 'give-' + slug(title[0])

# Line icons, 24 by 24, drawn with the stroke, one per group: a shield, a medical cross, a heart, a paw, a box, a clock.
ICONS = {
    'Defense': 'M12 3 4.5 6v5.5c0 4.6 3.2 8.4 7.5 9.5 4.3-1.1 7.5-4.9 7.5-9.5V6Z',
    'Medical and humanitarian aid': 'M9.5 3.5h5v6h6v5h-6v6h-5v-6h-6v-5h6Z',
    'Wounded and rehabilitation': 'M12 20s-7.5-4.6-7.5-10A4.3 4.3 0 0 1 12 7.4 4.3 4.3 0 0 1 19.5 10c0 5.4-7.5 10-7.5 10Z',
    'Animals': 'M8 8a1.6 2 0 1 1-3.2 0 1.6 2 0 1 1 3.2 0ZM11.6 6a1.6 2 0 1 1-3.2 0 1.6 2 0 1 1 3.2 0ZM15.6 6a1.6 2 0 1 1-3.2 0 1.6 2 0 1 1 3.2 0ZM19.2 8a1.6 2 0 1 1-3.2 0 1.6 2 0 1 1 3.2 0ZM12 11.5c-3 0-6 4.5-6 6.5 0 1.6 1.3 2.5 3 2.2 1.2-.2 2-.7 3-.7s1.8.5 3 .7c1.7.3 3-.6 3-2.2 0-2-3-6.5-6-6.5Z',
    'Send supplies': 'M3.5 7.5 12 3l8.5 4.5v9L12 21l-8.5-4.5ZM3.5 7.5 12 12l8.5-4.5M12 12v9',
    'Give your time': 'M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18ZM12 7.5V12l3 2',
}
if {title[0] for title, _, _ in GROUPS} != set(ICONS): raise ValueError('every group of organizations needs exactly one icon')


def targets():
    """English name -> (element id, English label, Ukrainian label), for links from other sections."""
    return {o['name'][0]: (org_id(o), *o['name']) for _, _, orgs in GROUPS for o in orgs}

def claims():
    """(url, phrase, what) for check.py: phrases each check's page must still contain."""
    return CLAIMS + [(check[2], check[3], f'{o["name"][0]}: {check[0]}') for _, _, orgs in GROUPS for o in orgs for check in o['checks'] if len(check) == 4]

def _icon(title):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="{ICONS[title]}"/></svg>'

def _stars(o):
    """A US charity's Charity Navigator stars, drawn, when it has a rating."""
    stars = o['ein'] and CN[o['ein']]['stars']
    if not stars: return ''
    n = int(stars)
    return (f'<p class="org-stars"><span class="stars" aria-hidden="true">{"★" * n}{"☆" * (4 - n)}</span>'
            f'{both(f"Charity Navigator: {n} of 4 stars", f"Charity Navigator: {n} з 4 зірок")}</p>')

def _checks(o):
    """What was checked, one line each: a check mark for what was confirmed, an exclamation mark for what was missing or worth knowing."""
    e = html.escape; items = []
    for check in o['checks']:
        en, uk, url = check[:3]
        text = f'<a href="{e(url)}" target="_blank" rel="noopener">{both(en, uk)}</a>' if url else both(en, uk)
        items.append(f'<li class="{"caveat" if isinstance(check, Caveat) else "ok"}">{text}</li>')
    return f'<div class="org-checks"><p class="org-checks-label">{both("What we checked", "Що ми перевірили")}</p><ul>{"".join(items)}</ul></div>'

def render(story_links):
    """The tab's HTML and its jump links. story_links maps an org id to [(story id, English label, Ukrainian label)]."""
    e = html.escape; out = []
    for number, (title, intro, orgs) in enumerate(GROUPS, 1):
        intro_html = f'\n        <p class="section-intro">{both(*intro)}</p>' if intro else ''
        cards = []
        for o in orgs:
            stories = ''.join(f'<a class="rel-chip" href="#{sid}"><span><span class="rel-kind">{both("Story", "Історія")}</span> {both(en, uk)}</span></a>'
                              for sid, en, uk in story_links.get(org_id(o), []))
            cards.append(f'''        <article class="org" id="{org_id(o)}" tabindex="-1">
          <header class="org-head">
            <span class="org-icon">{_icon(title[0])}</span>
            <div>
              <h4 class="org-name">{both(*o["name"])}</h4>
              <p class="org-kind">{both(*o["kind"])}</p>
            </div>
          </header>{_stars(o)}
          <p class="org-what">{both(*o["what"])}</p>
          {_checks(o)}{f'{chr(10)}          <p class="story-related">{stories}</p>' if stories else ''}
          <a class="give-link" href="{e(o["url"])}" target="_blank" rel="noopener">{both(*o["action"])}</a>
        </article>''')
        out.append(f'''    <section class="cause" id="{group_id(title)}" aria-labelledby="{group_id(title)}-title">
      <header class="section-head">
        <p class="section-num" aria-hidden="true">{number:02d}</p>
        <h3 id="{group_id(title)}-title">{both(*title)}</h3>{intro_html}
      </header>
      <div class="orgs">
''' + '\n'.join(cards) + '''
      </div>
    </section>''')
    return '\n'.join(out), [(group_id(title), *title) for title, _, _ in GROUPS]
