
import itertools
from pprint import pprint
from typing import Iterable

import dlt
from dlt.sources.rest_api import rest_api_source
import requests


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
        r = requests.get(
            'https://api.weirdgloop.org/exchange/history/rs/all',
            params = {'id': parent_item['value']})
        r.raise_for_status()
        yield from itertools.chain.from_iterable(r.json().values())

    pipeline = dlt.pipeline(
        pipeline_name = 'rs_gemw',
        destination = dlt.destinations.duckdb(
            credentials = 'duckdb:///data/RS_GEMW/db.duckdb'),
        dataset_name = 'raw',
        progress = 'tqdm')
    
    load_info = pipeline.run(
        (source, exchange_history),
        write_disposition = 'replace'),
    pprint(load_info)


if __name__ == '__main__':
    main()
