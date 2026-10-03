# Together with Ukraine — handoff notes

Personal project of Rowan Flynn (GitHub: RowanFlynnPilot), started October 3, 2026 for his friend
Anastasiia, who is Ukrainian. It is not a Wausau Pilot & Review project and carries none of its branding.

Live: https://rowanflynnpilot.github.io/together-with-ukraine/ — the repo name must stay
`together-with-ukraine` to keep that address.

## What it is

One static page, English and Ukrainian, with four tabs: a sourced history timeline, stories of
Ukrainian people summarized from published reports, a map of Ukrainian places to eat and shop in the
US, and a list of vetted ways to give money, supplies or time. Stories link to the timeline entry,
place or organization they involve, and those link back. Every tab and entry has its own address
(`#give`, `#event-the-holodomor`, `#story-…`, `#place-…`, `#org-…`); `?lang=uk` forces Ukrainian.

## Commands (Windows, PowerShell 5.1)

```powershell
python build.py                                # writes site/index.html and site/preview.png, no network
python -m http.server 8765 --directory site    # view it at http://localhost:8765/
python -m pip install -r requirements.txt      # only check.py and refresh.py need it
python check.py                                # re-verify records, links, phrases, dates; exits 1 on any problem
python refresh.py; git diff data/              # pull fresh records after check.py reports a change
```

## Layout

| File | Role |
|---|---|
| `template.html` | The page: markup, CSS, and the script for tabs, links between sections, language, the state filter and the map. `{{English||Українська}}` becomes a two-language pair; `__NAME__` placeholders are filled by `build.py`. |
| `build.py` | Assembles the page and resolves the links between sections. No network. Stops on a missing translation, a link to an anchor that does not exist, or two elements with the same id. |
| `history.py` / `history_uk.py` | Timeline entries with their sources / the Ukrainian text, keyed by English title. `AS_OF` dates the entries about the war today. |
| `stories.py` | The People tab. Each story: person, context, title, text (all English/Ukrainian pairs), sources as `(language, outlet, date, url, phrase)`, and related entries elsewhere on the page. |
| `places.py` | Loads and validates `data/places.json`: checks each place's coordinates fall inside the state it names (point-in-polygon on the TopoJSON), and renders the list. |
| `give.py` | Organizations, each text an (English, Ukrainian) pair, each with a list of checks. US charities pull facts from `data/`. `REVIEWED` is the date of the last review by hand. A check can carry a fourth item, a phrase its page must contain. |
| `i18n.py` | `both()`, the `{{..||..}}` marker filler, dates in both languages, Ukrainian plurals, slugs. |
| `places_uk.py` | Ukrainian names for US states and kinds of place. |
| `records.py` | Pulls IRS records (ProPublica Nonprofit Explorer API) and Charity Navigator ratings. Uses `curl_cffi` with Chrome impersonation because several sites reject plain clients. Raises if a Charity Navigator page shows neither stars nor "Not Rated", so a layout change is never read as a lost rating. |
| `refresh.py` | Writes fresh records to `data/` and stamps `data/checked.json` (`records`). Does not touch the review dates. |
| `check.py` | Compares live records to `data/`, loads every link, confirms every recorded phrase is still on its page, checks the CDN integrity hashes, and fails on stale review dates. Run weekly by `.github/workflows/check.yml`. |
| `data/places.json` | The listed businesses, maintained by hand. Each has `state` (full name) and `basis`: a list of `{by, url, says}`, where `by` is `own website` or an outlet name and `says` is an exact phrase on that page. |
| `data/places_review.json` | `reviewed` (date of the last review by hand) and `held`: places held back, with the reason. |
| `data/states-10m.json` | US state shapes (us-atlas). |
| `.github/ISSUE_TEMPLATE/` | Forms for suggesting a place, story or group, or reporting a mistake. The footer links to them. |

Both languages are in the built page. CSS shows the one matching `<html data-lang>`; the script
switches it, remembers the choice in localStorage, and redraws what it writes itself (the state
menu, the order of the state groups, the map's labels). The place list is in the page, so it
works without the script; the map is drawn last, so a CDN failure takes out only the map.

## Rules for content

1. **History.** Every sentence must be supported by that entry's sources. The text was rewritten
   to match the sources, so do not "improve" a claim beyond what its source says. A new or changed
   entry needs its Ukrainian text in `history_uk.py`.
2. **Places.** List a business only if it calls itself Ukrainian on its own website or local press
   describes it that way. Serving Ukrainian food is not enough: one OpenStreetMap entry turned out
   to call itself a Russian restaurant. Yelp and other listings are not press. Record the evidence
   in the place's `basis` with an exact phrase; the page shows it and `check.py` re-reads it weekly.
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

## Known behavior

- `check.py` fails when a charity files a new tax return or its rating changes. That is the point.
  Run `refresh.py`, review the diff, commit.
- A link that answers 403 or 429 is reported as "refused", not as broken: the site turned the
  checker away, and which sites do that differs between a home connection and GitHub's servers
  (Nova Ukraine's site refused Rowan's machine but not the build machine). ukrainer.net leaves out
  an intermediate certificate, which browsers fetch for themselves and scripts cannot, so its pages
  are treated the same way. These links, with the phrase each should carry, are listed in every
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
- The places list has 31 places in 17 states and DC; Massachusetts still has none that qualify.
  Undecided: whether Multicook's frozen-food shops (now "a Ukrainian family business" on the brand
  site) belong; see `held`. Unverified leads: SLAVA Cafe (Asheville, NC), Nubo Café (Clearwater,
  FL), Sunflower Tastes (Port Angeles, WA), Banderyky (Vancouver, WA), Shchedryk grocery (Berlin, CT).
  New places must pass rule 2.
- Most pre-2022 history rests on one encyclopedia. A second independent source on the contested
  entries (Pereiaslav, the Holodomor, Crimea) would strengthen it.
