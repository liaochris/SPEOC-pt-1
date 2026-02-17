### Ancestry Person-County Scraper

Scrapes individual person records from Ancestry Library Edition to find their residential county. Uses Selenium to authenticate via a university library proxy, search the 1790 census collection, and parse county information from results.

### Usage

```bash
python main.py CT --year 1790
```

Requires Ancestry Library Edition access via a university proxy. See `ancestry_scraper/auth.py` for proxy configuration.

### Pipeline

1. `create_names_lookup.py` — Reads cleaned loan office certificates, deduplicates by name+state, writes `names_to_lookup_{state}.csv`
2. `main.py` — CLI entrypoint. Reads lookup CSVs, calls `worker.process_name()` for each row
3. `analyze_results.py` — Loads scraper results, parses county strings, generates choropleth maps

### Tests

```bash
pytest source/scrape/ancestry_person_county_scraper/
```

Unit tests in `tests/`. Integration tests (marked `integration`) require live Ancestry access.
