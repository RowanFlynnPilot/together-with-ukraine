# Together with Ukraine

A two-language (English and Ukrainian) page with six parts:

- **Culture** (the page opens here): Ukraine's landscapes and landmarks in photos, its food with links to recipes, traditions, holidays, Ukrainian festivals in the US, books, films and music with where to find them, and where to learn more. A Coming up panel shows the holidays and festivals of this month and next.
- **History**: 30 entries from Kyivan Rus' to today, each linked to the source it was checked against.
- **People**: stories of Ukrainians, in Ukraine and in the United States, each summarized from one published report and linked to it.
- **In the US**: how many people of Ukrainian ancestry live in the United States and where, from the Census Bureau's American Community Survey: a map by state, every state's figures with their margins of error, the largest metro areas, and the rise in people born in Ukraine since 2021.
- **Eat and shop**: Ukrainian restaurants, cafés, bakeries and markets in the United States, filtered by state and kind, on a map that zooms to each state, each with the evidence it was listed on.
- **Give**: where to donate money, send supplies or volunteer, with what was verified about each group.

The parts link to each other: a story about the Holodomor links to that timeline entry and back, a story about Veselka links to Veselka on the map. Every section and entry has its own address (`#give`, `#story-liubov-yarosh`), and `?lang=uk` opens the page in Ukrainian.

Live site: https://rowanflynnpilot.github.io/together-with-ukraine/

## Run it

```powershell
python build.py
python -m http.server 8765 --directory site
```

Then open http://localhost:8765/. `build.py` needs nothing beyond Python. It writes `site/index.html`, `site/review.html` (every text beside its Ukrainian, for a native speaker to check) and `site/apple-touch-icon.png` (the icon a phone shows for the page on its home screen), copies the pictures, and uses no network.

The build refuses to produce a page that is wrong in ways it can detect: a missing translation, a place whose coordinates fall outside the state it names, a place with no evidence, a story that links to an entry that does not exist, or two entries with the same address.

## Check it

```powershell
python -m pip install -r requirements.txt
python check.py
```

`check.py` re-verifies the page against the live web and exits with an error if anything changed, broke or went stale:

- each US charity's IRS record and Charity Navigator rating still match `data/`
- every link on the page still loads
- every recorded phrase is still on its page: the words each business is listed on, the EIN on each charity's own site, the person each story is about
- the map scripts still match their integrity hashes
- the entries about the war today, the places review and the Give review are not too old (4, 12 and 6 months)
- the Census figures are the latest year the Census Bureau has published

GitHub runs the same check every Monday (`.github/workflows/check.yml`) and emails you if it fails.

When it fails:

- **A record changed** (a new tax filing, a new rating): run `python refresh.py`, read `git diff data/`, and commit if the change is real.
- **A link broke**: find where it is used (`history.py`, `stories.py`, `give.py`, `data/places.json` or `template.html`) and replace the link or remove the entry.
- **A phrase is gone**: open the page. If the business closed or no longer calls itself Ukrainian, remove it and record why under `held` in `data/places_review.json`. If the site was only redesigned, update the phrase. If a story was taken down, remove it.
- **Something went stale**: review that part of the page, then update its date (`AS_OF` in `history.py`, `reviewed` in `data/places_review.json`, `REVIEWED` in `give.py`).
- **New Census figures are out** (usually each September): run `python census.py`, read `git diff data/census.json`, rebuild, and commit.

Some sites turn automated requests away (they answer 403 or 429), and which ones do depends on the network the check runs from. A site whose certificate chain leads to a root scripts no longer trust also cannot be checked; Ukraїner's is, because `data/ukrainer-chain.pem` holds the chain browsers find for it. Those links do not fail the check. Every report lists them, with the phrase to look for, so you can open them by hand.

## Change it

| To change | Edit |
|---|---|
| A history entry | `history.py`, and its Ukrainian text in `history_uk.py` |
| A story | `stories.py` (each text is an English and Ukrainian pair) |
| A dish, tradition, holiday, event or resource, or a gallery photo | `culture.py` |
| An organization | `give.py` (each text is an English and Ukrainian pair) |
| A place | `data/places.json`, with its state and the evidence it is listed on |
| A place held back | `data/places_review.json`, with the reason |
| The Census figures | `python census.py` rewrites `data/census.json`; `diaspora.py` renders the tab |
| Page layout, interface text | `template.html` (`{{English||Українська}}` marks two-language text) |

Every pull request is built first (`.github/workflows/build.yml`), so a change that breaks the build shows a red check before it can be merged. Pushing to `main` rebuilds and publishes the site. People can suggest places, stories and groups, or report mistakes, through the forms under the repository's Issues tab.

## Standards

- **History**: every sentence must be supported by the entry's listed sources.
- **People**: a story comes from a news organization, a UN agency, a museum or archive, or an established documentary project, and is free to read. The person is named in it. The summary is in our own words, without quotations, and every sentence is supported by the report. No graphic detail, no minors by full name, no one in Russian-occupied territory, and nothing that adds to the risk a named person faces. Photos are used only when openly licensed (from Wikimedia Commons, credited as the license requires), never taken from the outlet's article.
- **Places**: a business is listed if its own website or the press says it serves Ukrainian food, sells Ukrainian goods, or is owned by Ukrainians. Each listing shows which, with the evidence. `python scout.py` lists leads from OpenStreetMap, and a monthly GitHub job opens an issue with any new ones.
- **In the US**: every figure is the Census Bureau's own estimate, shown with its margin of error; a figure the Bureau did not publish is marked as such, never filled in. A claim of change must clear the margins of error, or the build stops.
- **Give**: US charities must appear in IRS records. Ukrainian groups must publish reports or audits, or be confirmed by an independent source. Every entry says what was checked.

The Ukrainian text is a machine translation that a native speaker has not yet reviewed. The page says so in its Ukrainian footer.

## Credits

Places were found through OpenStreetMap (© OpenStreetMap contributors, Open Database License). Population figures are from the US Census Bureau's American Community Survey. State shapes come from the `us-atlas` package. Most history entries draw on the Internet Encyclopedia of Ukraine, published by the Canadian Institute of Ukrainian Studies. The stories are summaries; the reports they come from belong to their publishers.
