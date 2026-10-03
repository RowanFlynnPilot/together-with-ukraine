# Together with Ukraine — handoff notes

Personal project of Rowan Flynn (GitHub: RowanFlynnPilot), started October 3, 2026 for his friend
Anastasiia, who is Ukrainian. It is not a Wausau Pilot & Review project and carries none of its branding.

Live: https://rowanflynnpilot.github.io/together-with-ukraine/ — the repo name must stay
`together-with-ukraine` to keep that address.

## What it is

One static page, English and Ukrainian, with three tabs: a sourced history timeline, a map of
Ukrainian places to eat and shop in the US, and a list of vetted ways to give money, supplies or time.

## Commands (Windows, PowerShell 5.1)

```powershell
python build.py                                # writes site/index.html, no network
python -m pip install -r requirements.txt      # only check.py and refresh.py need it
python check.py                                # re-verify records and links; exits 1 on any change
python refresh.py; git diff data/              # pull fresh records after check.py reports a change
```

## Layout

| File | Role |
|---|---|
| `template.html` | The page: markup, CSS, and the script for tabs, language and the map. `{{English||Українська}}` becomes a two-language pair; `__NAME__` placeholders are filled by `build.py`. |
| `build.py` | Assembles `site/index.html`. No network. Stops on a missing translation, unknown state or kind of place, or a charity with no record. |
| `history.py` / `history_uk.py` | Timeline entries with their sources / the Ukrainian text, keyed by English title. |
| `give.py` | Organizations, each text an (English, Ukrainian) pair, each with a list of checks. US charities pull facts from `data/`. |
| `i18n.py` | `both()` and the `{{..||..}}` marker filler. |
| `places_uk.py` | Ukrainian names for US states and kinds of place. |
| `records.py` | Pulls IRS records (ProPublica Nonprofit Explorer API) and Charity Navigator ratings. Uses `curl_cffi` with Chrome impersonation because several sites reject plain clients. |
| `refresh.py` | Writes fresh records to `data/` and stamps `data/checked.json`. |
| `check.py` | Compares live records to `data/` and loads every link. Run weekly by `.github/workflows/check.yml`. |
| `data/places.json` | The listed businesses. Hand-maintained. |
| `data/places_review.json` | Why each business is listed, and which were held back and why. |
| `data/states-10m.json` | US state shapes (us-atlas). |

Both languages are in the built page. CSS shows the one matching `<html data-lang>`; the script
switches it, remembers the choice in localStorage, and redraws the places section's labels.

## Rules for content

1. **History.** Every sentence must be supported by that entry's sources. The text was rewritten
   to match the sources, so do not "improve" a claim beyond what its source says. A new or changed
   entry needs its Ukrainian text in `history_uk.py`.
2. **Places.** List a business only if it calls itself Ukrainian on its own website or local press
   describes it that way. Serving Ukrainian food is not enough: one OpenStreetMap entry turned out
   to call itself a Russian restaurant. Record the basis in `data/places_review.json`.
3. **Give.** A US charity must be in IRS records (add its EIN with `us_org`, then run `refresh.py`).
   A Ukrainian group must publish reports or audits, or be confirmed by an independent source.
   Every entry gets a "Checked" line that says exactly what was verified, including what was not
   found (UAnimals has no outside audit, and the page says so).
4. **US arms of Ukrainian groups.** List one only when the parent organization or its founder
   confirms it. Prytula Foundation USA qualified because Serhiy Prytula announced it himself.
5. **Commercial carriers** (Meest, Nova Post) are labeled as carriers, not charities.

## Deliberately not listed

- **Come Back Alive, Inc.** (US, EIN 92-2081235): its site names Taras Chmut as founder, but the
  site was down on October 3, 2026 and no tax filing data is published.
- **Superhumans Ukraine Inc.** (EIN 88-4049977): IRS-registered, but not tied to the center's own site.
- **Ukraine House DC Foundation** (EIN 87-2080907): reported as UNITED24's US partner, not confirmed
  on UNITED24's site, 2 of 4 stars on Charity Navigator.
- **Revived Soldiers Ukraine**: 3 of 4 stars, but its site could not be read.
- Eight businesses held back from the places list; see `data/places_review.json`.

## Engineering rules

One correct path, no fallbacks, fail fast. The build never touches the network; the check never
writes files. Read and write every file with `encoding='utf-8'`: the content is Ukrainian and
Windows defaults to another encoding.

## Known behavior

- `check.py` fails when a charity files a new tax return or its rating changes. That is the point.
  Run `refresh.py`, review the diff, commit.
- A link that answers 403 or 429 is reported as "refused", not as broken: the site turned the
  checker away, and which sites do that differs between a home connection and GitHub's servers
  (Nova Ukraine's site refused Rowan's machine but not the build machine). Refused links are
  listed in every report for a manual look. Only other failures (404, 5xx, timeouts) fail the run.
  The charity records are different: if ProPublica or Charity Navigator refuses, the run fails,
  because then the ratings cannot be verified.
- GitHub turns off scheduled workflows after 60 days without a commit and emails first.

## Open items

- A native speaker has not reviewed the Ukrainian text. When that is done, delete the last
  paragraph of the footer in `template.html`.
- The places list is thin: 24 places in 12 states and DC, with nothing in Ohio, Michigan,
  New Jersey, Massachusetts or Texas. New places must pass rule 2.
- Most pre-2022 history rests on one encyclopedia. A second independent source on the contested
  entries (Pereiaslav, the Holodomor, Crimea) would strengthen it.
