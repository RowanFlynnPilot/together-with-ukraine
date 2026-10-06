# Together with Ukraine — handoff notes

Personal project of Rowan Flynn (GitHub: RowanFlynnPilot), started October 3, 2026 for his friend
Anastasiia, who is Ukrainian. It is not a Wausau Pilot & Review project and carries none of its branding.

Live: https://rowanflynnpilot.github.io/together-with-ukraine/ — the repo name must stay
`together-with-ukraine` to keep that address.

## What it is

One static page, English and Ukrainian, with five tabs: Ukrainian culture (a photo gallery, food with
recipes, traditions, holidays, US festivals and resources), a sourced history timeline, stories of
Ukrainian people summarized from published reports, a map of Ukrainian places to eat and shop in
the US, and a list of vetted ways to give money, supplies or time. The page opens on Culture. The header carries the flag,
a photo of the Kyiv Pechersk Lavra under a blue wash, and a row of links to the tabs with their
counts, which `build.py` counts from the content. The footer says how each part is checked, with
the review dates. Stories link to the timeline entry,
place or organization they involve, and those link back. Every tab and entry has its own address
(`#give`, `#event-the-holodomor`, `#story-…`, `#place-…`, `#org-…`); `?lang=uk` forces Ukrainian.

## Commands (Windows, PowerShell 5.1)

```powershell
python build.py                                # writes site/index.html and the home-screen icon, no network
python -m http.server 8765 --directory site    # view it at http://localhost:8765/
python -m pip install -r requirements.txt      # only check.py and refresh.py need it
python check.py                                # re-verify records, links, phrases, dates; exits 1 on any problem
python refresh.py; git diff data/              # pull fresh records after check.py reports a change
python scout.py                                # leads for new places from OpenStreetMap (slow; needs the public Overpass server)
```

## Layout

| File | Role |
|---|---|
| `template.html` | The page: markup, CSS, and the script for tabs, links between sections, language, the state filter, Near me (the list sorted by distance from the reader, worked out in the browser) and the map. `{{English||Українська}}` becomes a two-language pair; `__NAME__` placeholders are filled by `build.py`. |
| `build.py` | Assembles the page and resolves the links between sections. No network. Stops on a missing translation, a link to an anchor that does not exist, or two elements with the same id. |
| `history.py` / `history_uk.py` | Timeline entries with their sources / the Ukrainian text, keyed by English title. `AS_OF` dates the entries about the war today. `ERA_PHOTOS` (a banner per era) and `EVENT_PHOTOS` (a picture beside some entries) hold the timeline's pictures. |
| `culture.py` | The Culture tab: the header photo, the gallery, and the food, traditions, "Ukrainian, not Russian", holidays, events and resources sections. `REVIEWED` dates the events and resources. `UNESCO_YEAR` (the badge), `RELABELS` (the label each museum dropped and the one it uses now) and `RESOURCE_KINDS` shape how entries look; the build checks each against the entry's own text. An entry without a photo shows its Ukrainian name on a cross-stitch pattern. |
| `photos.py` | Photo rules shared by stories and culture: accepted licenses, image sizes, the credit line, the license claim `check.py` looks for. |
| `stories.py` | The People tab. Each story: person, context, title, text (all English/Ukrainian pairs), sources as `(language, outlet, date, url, phrase)`, related entries elsewhere on the page, and optionally a `photo(...)`; without one, the card shows its theme's icon (`ICONS`). Long stories show their first lines and open with Read more. |
| `places.py` | Loads and validates `data/places.json`: checks each place's coordinates fall inside the state it names (point-in-polygon on the TopoJSON), and renders the listings as cards. Also holds the groups of kinds of place behind the filter buttons and icons, and `PHOTOS`, the openly licensed photos taken at listed places that run above the list. |
| `give.py` | Organizations, each text an (English, Ukrainian) pair, each with a list of checks. US charities pull facts from `data/`. `REVIEWED` is the date of the last review by hand. A check can carry a fourth item, a phrase its page must contain. A check that found something missing or worth knowing (no outside audit, not yet rated, a commercial carrier) is written `caveat(...)`, and the page marks it with an exclamation mark instead of a check mark. |
| `i18n.py` | `both()`, the `{{..||..}}` marker filler, dates in both languages, Ukrainian plurals, slugs. |
| `places_uk.py` | Ukrainian names for US states and kinds of place. |
| `records.py` | Pulls IRS records (ProPublica Nonprofit Explorer API) and Charity Navigator ratings. Uses `curl_cffi` with Chrome impersonation because several sites reject plain clients. Raises if a Charity Navigator page shows neither stars nor "Not Rated", so a layout change is never read as a lost rating. |
| `refresh.py` | Writes fresh records to `data/` and stamps `data/checked.json` (`records`). Does not touch the review dates. |
| `check.py` | Compares live records to `data/`, loads every link, confirms every recorded phrase is still on its page, checks the CDN integrity hashes, and fails on stale review dates. Run weekly by `.github/workflows/check.yml`. |
| `data/places.json` | The listed businesses, maintained by hand. Each has `state` (full name), `ukrainian` (one or more of `food`, `goods`, `owner`) and `basis`: a list of `{by, url, says}`, where `by` is `own website` or an outlet name and `says` is an exact phrase on that page. |
| `scout.py` | Prints OpenStreetMap leads for new places (tagged Ukrainian cuisine, a Ukrainian name, or a Ukrainian word in the name) that are not listed or held. Leads still need rule 2. Writes nothing. `.github/workflows/scout.yml` runs it on the first of each month and opens an issue listing any leads. |
| `data/places_review.json` | `reviewed` (date of the last review by hand) and `held`: places held back, with the reason. |
| `data/states-10m.json` | US state shapes (us-atlas). |
| `images/` | Pictures for the stories, the header, the Culture and History tabs and the places, openly licensed or public domain (rule 7), saved at display size. Copied to `site/images/` by the build. `share.jpg` is the picture a shared link shows: the header photo with the title, made once and kept here, carrying the photographer's credit as its CC BY-SA license requires. |
| `.github/ISSUE_TEMPLATE/` | Forms for suggesting a place, story or group, or reporting a mistake. The footer links to them. |

Both languages are in the built page. CSS shows the one matching `<html data-lang>`; the script
switches it, remembers the choice in localStorage, and redraws what it writes itself (the state
menu, the order of the state groups, the map's labels). The place list is in the page, so it
works without the script; the map is drawn last, so a CDN failure takes out only the map.
The theme follows the system until the reader picks light or dark with the switch beside the
language switch; the choice is kept in localStorage and applied by a one-line script in the head,
before the page draws, so it never flashes the other theme.

## Rules for content

1. **History.** Every sentence must be supported by that entry's sources. The text was rewritten
   to match the sources, so do not "improve" a claim beyond what its source says. A new or changed
   entry needs its Ukrainian text in `history_uk.py`.
2. **Places.** List a business if its own website or the press says it serves Ukrainian food,
   sells Ukrainian goods, or is owned by Ukrainians or Ukrainian Americans (Rowan widened the rule
   to owners on October 3, 2026). Record which in `ukrainian` (`food`, `goods`, `owner`); the page
   shows it. "Eastern European", "Slavic" or "Russian" wording alone does not count, and a business
   that calls itself Russian is out even with a Ukrainian owner: one OpenStreetMap entry turned out
   to be a Russian restaurant. Restaurants, cafés, bakeries, delis, groceries, gift and craft shops
   and bookstores count; food trucks, market stalls, frozen-food shops (Multicook), event halls,
   home bakers and chain franchises do not. Yelp, Google and social media are not evidence. Record
   the evidence in `basis` with an exact phrase; the page shows it and `check.py` re-reads it weekly.
3. **Give.** A US charity must be in IRS records (add its EIN with `us_org`, then run `refresh.py`).
   A Ukrainian group must publish reports or audits, or be confirmed by an independent source.
   Every entry gets a "Checked" line that says exactly what was verified, including what was not
   found (UAnimals has no outside audit, and the page says so).
4. **US arms of Ukrainian groups.** List one only when the parent organization or its founder
   confirms it. Prytula Foundation USA qualified because Serhiy Prytula announced it himself.
5. **Commercial carriers** (Meest, Nova Post) are labeled as carriers, not charities.
6. **Stories.** The source is a news organization, a UN agency, a museum or archive, or an
   established documentary project (Ukraїner), and is free to read (the Star Tribune's metered
   wall was accepted for the ENGin story). The person is named in it. The summary is in our own
   words, past tense, with no quotations (the build rejects quotation marks in the English), and
   every sentence is supported by the source; dates the source does not state are left out. No
   graphic detail. Minors by first name only, or better, unnamed. Nobody in Russian-occupied
   territory. Nothing that adds to the risk a named person faces: the Kramarczuk's story names the
   family but not the Ukrainian workers whose work permits lapsed. Link the Ukrainian version of
   the report when the outlet published one. Each source's phrase (usually the surname as that
   page spells it) is what `check.py` looks for.
7. **Photos.** Only openly licensed or public-domain photos, from Wikimedia Commons, credited with
   author, license and a link, as the license requires. Never a photo from the outlet's article,
   even credited: credit is not permission, and agency photos (AFP, AP, Getty) bring demand
   letters. No photos of private people, which would add to what identifies them. Check a
   "public domain" claim before trusting it: a VOA photo was rejected because VOA also runs wire
   photos, and a Ukrainian stamp of Prymachenko's art because her paintings are still under
   copyright. Save the Commons thumbnail in `images/` at about twice the largest size the page shows it, never
   cropped (photos on cards about 720 px wide, History entries 480, tall documents beside the text 360,
   panoramas 1000, era banners 1280); `check.py` confirms the
   Commons page still shows the license. Licenses accepted are listed in `photos.py`.
8. **Culture.** Every sentence is supported by the sources it links to, and each Ukrainian claim
   rests on an authoritative source (UNESCO, the Encyclopedia of Ukraine, ukraine.ua, the Ukrainian
   Institute, museums, major outlets). Leave out dishes and customs shared across the former USSR
   unless a source calls them Ukrainian. Recipes are linked, never copied, and come from Ukrainian
   sources first (ukraine.ua, Yevhen Klopotenko, the Ukrainian Institute). Events come from their
   organizers' own pages; give the usual month rather than a date unless the page states one.

## Deliberately not listed

- **Come Back Alive, Inc.** (US, EIN 92-2081235): its site names Taras Chmut as founder, but the
  site was down on October 3, 2026 and no tax filing data is published.
- **Superhumans Ukraine Inc.** (EIN 88-4049977): IRS-registered, but not tied to the center's own site.
- **Ukraine House DC Foundation** (EIN 87-2080907): reported as UNITED24's US partner, not confirmed
  on UNITED24's site, 2 of 4 stars on Charity Navigator.
- **Revived Soldiers Ukraine**: 3 of 4 stars, but its site could not be read.
- Eight businesses held back from the places list; see `data/places_review.json`.
- **Stories left out on purpose:** Tamara Islyamova's testimony of the 1944 deportation (Krym.Realii,
  Ukrainian only), because she lives in Crimea, now occupied; Mustafa Dzhemilev's story covers the
  deportation instead. Kateryna Temchenko (Cap Times, Madison, February 2025), because the story turns
  on her immigration status. A WBEZ story about a Chicago-area family whose father was detained by
  ICE, because the family asked not to be named.

## Engineering rules

One correct path, no fallbacks, fail fast. The build never touches the network; the check never
writes files. Read and write every file with `encoding='utf-8'`: the content is Ukrainian and
Windows defaults to another encoding.

Accessibility: every label a screen reader reads comes in both languages, written as a
visually hidden `{{English||Українська}}` pair that `aria-labelledby` points to, never an
English-only `aria-label`. A link that repeats on many cards (Website, Map, Read more, a recipe)
carries the name of its place, person or dish in a visually hidden span. The site's yellow focus
ring disappears on yellow, so anything on a yellow background draws its own focus style, as the
tabs do. Run axe-core on each tab in both languages after a layout change; it should find nothing.

## Known behavior

- `check.py` fails when a charity files a new tax return or its rating changes. That is the point.
  Run `refresh.py`, review the diff, commit.
- A link that answers 403 or 429 is reported as "refused", not as broken: the site turned the
  checker away, and which sites do that differs between a home connection and GitHub's servers
  (Nova Ukraine's site refused Rowan's machine but not the build machine). ukrainer.net leaves out
  an intermediate certificate, which browsers fetch for themselves and scripts cannot, so its pages
  are treated the same way. So are 202 answers (a bot challenge), and the TEGNA stations (KING 5, ABC10,
  13News Now, `WALLED` in check.py), which answer GitHub's servers with a stand-in page that has no article. These links, with the phrase each should carry, are listed in every
  report for a manual look. Only other failures (404, 5xx, timeouts, other certificate errors) fail
  the run.
- A page that loads but no longer carries its phrase fails the run: a business renamed or closed,
  a story taken down (news sites often redirect a removed article to their home page, which still
  answers 200), or a redesign that changed the wording. Look, then fix the entry or the phrase.
- The run also fails when a review date is too old: `AS_OF` in `history.py` after 4 months,
  `REVIEWED` in `give.py` after 6, `reviewed` in `data/places_review.json` after 12. Review that
  part of the page, then move the date.
  The charity records are different: if ProPublica or Charity Navigator refuses, the run fails,
  because then the ratings cannot be verified.
- GitHub turns off scheduled workflows after 60 days without a commit and emails first.

## Open items

- A native speaker has not reviewed the Ukrainian text, including the story summaries and the
  Ukrainian spellings of names taken from English-only reports, which follow the official
  transliteration backwards and are unconfirmed (for example Безпрозваний, Поканевич, Сокор, Гапон,
  Бірчард, Фертш, Градинар, Ентіна, Дзуенко). When that is done, delete the footer paragraph in `template.html` that says the
  Ukrainian is a machine translation.
- The places list has 101 places in 29 states and DC, from three passes of state-by-state research
  (October 3, 2026) in local press and the businesses' own sites. Every state was searched at least
  once; the 21 without a listing turned up nothing that passes rule 2 (the near-misses are in `held`).
  Worth rechecking: Hatta Ukrainian Cuisine (Wood Village, OR), whose own site failed to load; Just
  Right Cake (Wausau, WI), Ukrainian-owned but closed as of October 2026; Mriya Bakery (Vancouver, WA). Undecided: Multicook-style prepared and frozen-food shops (held).
  `python scout.py` gives OpenStreetMap leads. New places must pass rule 2.
- Most pre-2022 history rests on one encyclopedia. A second independent source on the contested
  entries (Pereiaslav, the Holodomor, Crimea) would strengthen it.
