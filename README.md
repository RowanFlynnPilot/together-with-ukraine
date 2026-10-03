# Together with Ukraine

A two-language (English and Ukrainian) page with three parts:

- **History**: 30 entries from Kyivan Rus' to today, each linked to the source it was checked against.
- **Eat and shop**: Ukrainian restaurants, bakeries and markets in the United States, on a map.
- **Give**: where to donate money, send supplies or volunteer, with what was verified about each group.

Live site: https://rowanflynnpilot.github.io/together-with-ukraine/

## Run it

```powershell
python build.py
start site\index.html
```

`build.py` needs nothing beyond Python. It writes `site/index.html` and uses no network.

## Check it

```powershell
python -m pip install -r requirements.txt
python check.py
```

`check.py` re-verifies the page against the live web and exits with an error if anything changed:

- each US charity's IRS record and Charity Navigator rating still match `data/`
- every link on the page, and every listed business's website, still loads

GitHub runs the same check every Monday (`.github/workflows/check.yml`) and emails you if it fails.

When it fails:

- **A record changed** (a new tax filing, a new rating): run `python refresh.py`, read `git diff data/`, and commit if the change is real. `refresh.py` also stamps today's date as the "checked" date shown on the page.
- **A link broke**: find where it is used (`history.py`, `give.py`, `data/places.json` or `template.html`) and replace the link or remove the entry.

Some sites turn automated requests away (they answer 403 or 429), and which ones do depends on the network the check runs from. Those links do not fail the check. Every report lists them so you can open them by hand.

## Change it

| To change | Edit |
|---|---|
| A history entry | `history.py`, and its Ukrainian text in `history_uk.py` |
| An organization | `give.py` (each text is an English and Ukrainian pair) |
| A place | `data/places.json`, and record why it qualifies in `data/places_review.json` |
| Page layout, interface text | `template.html` (`{{English||Українська}}` marks two-language text) |

Pushing to `main` rebuilds and publishes the site.

## Standards

- **History**: every sentence must be supported by the entry's listed sources.
- **Places**: a business is listed only if it calls itself Ukrainian on its own website or local press describes it that way.
- **Give**: US charities must appear in IRS records. Ukrainian groups must publish reports or audits, or be confirmed by an independent source. Every entry says what was checked.

The Ukrainian text is a machine translation that a native speaker has not yet reviewed. The page says so in its Ukrainian footer.

## Credits

Places were found through OpenStreetMap (© OpenStreetMap contributors, Open Database License). State shapes come from the `us-atlas` package. Most history entries draw on the Internet Encyclopedia of Ukraine, published by the Canadian Institute of Ukrainian Studies.
