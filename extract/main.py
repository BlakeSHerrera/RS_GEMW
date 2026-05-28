
import functools
import itertools
import pathlib
from pprint import pprint
import time
from typing import Iterable

import dlt
from dlt.sources.rest_api import rest_api_source
import polars as pl
import requests


@functools.wraps(requests.request)
def request(*args, **kwargs) -> dict:
    r = requests.request(*args, **kwargs)
    r.raise_for_status()
    if not r.content:
        # Too many requests returns as 200 with empty content
        time.sleep(1)
        return request(*args, **kwargs)
    return r.json()


def wide_to_long(record: dict[str, str]) -> Iterable[dict]:
    u, f = '%LAST_UPDATE%', '%LAST_UPDATE_F%'
    for k, v in record.items():
        if k not in (u, f):
            yield {
                'name': k,
                'value': v,
                'last_update': record[u],
                'last_update_f': record[f]
            }


@dlt.resource
def item_details() -> Iterable[dict]:
    # There are more categories than listed in the tsv?
    for category in range(44):
        j = request(
            'GET',
            'https://secure.runescape.com/m=itemdb_rs/api/catalogue/category.json',
            params = {'category': category})
        for d in j['alpha']:
            # item count doesn't seem to match what the API returns.
            yield from get_items_from_pages(category, d['letter'], d['items'])


def get_items_from_pages(category: int, alpha: str, count: int) -> Iterable[dict]:
    if count == 0:
        return
    for page in itertools.count(1):
        j = request(
            'GET',
            'https://secure.runescape.com/m=itemdb_rs/api/catalogue/items.json',
            params = {
                'category': category,
                'alpha': alpha,
                'page': page
            })
        data = j['items']
        yield from data
        if len(data) < 12:
            break


def main():
    modules = ['GEIDs', 'GELimits', 'GEValues', 'GEHighAlchs', 'GELowAlchs', 'GEVolumes']
    source = rest_api_source({
        'client': {
            'base_url': ''
        },
        'resource_defaults': {
            'endpoint': {
                'paginator': 'single_page'
            }
        },
        'resources': [
            {
                'name': m.lower(),
                'endpoint': {
                    'path': 'https://runescape.wiki/',
                    'params': {
                        'title': f'Module:{m}/data.json',
                        'action': 'raw',
                        'ctype': 'application/json'
                    },
                },
            } 
            for m in modules
        ]
    })
    for m in modules:
        source.resources[m.lower()].add_yield_map(wide_to_long, insert_at = 1)

    @dlt.transformer(
        data_from = source.resources['geids'], 
        name = "exchange_history")
    def exchange_history(parent_item):
        j = request(
            'GET'
            'https://api.weirdgloop.org/exchange/history/rs/all',
            params = {'id': parent_item['value']})
        yield from itertools.chain.from_iterable(j.values())

    csvs = [dlt.resource(pl.read_csv(f), name = f.stem) for f in pathlib.Path('extract').glob('*.csv')]

    pipeline = dlt.pipeline(
        pipeline_name = 'rs_gemw',
        destination = dlt.destinations.duckdb(
            credentials = 'duckdb://data/RS_GEMW/raw.duckdb'),
        dataset_name = 'rs',
        progress = 'tqdm')
    
    load_info = pipeline.run(
        [
            source, 
            # exchange_history,
            item_details,
            *csvs
        ],
        write_disposition = 'replace'),
    pprint(load_info)


if __name__ == '__main__':
    main()
