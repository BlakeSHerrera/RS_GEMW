'''
This module connects to various RuneScape APIs to pull item and exchange history
before loading it into duckdb via dlt.
'''

import functools
import itertools
from pprint import pprint
import time
from typing import Iterable

import dlt
from dlt.sources.rest_api import rest_api_source
import requests


@functools.wraps(requests.request)
def request(*args, **kwargs) -> dict:
    '''
    A wrapper around requests.request to shorten repetitive tasks
    (like checking the status and converting to json).
    There is a special case where the API returns an empty response
    if there are too many requests rather than an error code.

    Note: if you are caching responses, you will have to remove this empty
    response from the cache.

    Returns
    -------
    dict
        The JSON response converted to a dict.
    '''
    r = requests.request(*args, **kwargs)
    r.raise_for_status()
    if not r.content:
        # Too many requests returns as 200 with empty content
        time.sleep(1)
        return request(*args, **kwargs)
    return r.json()


def wide_to_long[T, U](record: dict[T, U]) -> Iterable[dict[T, U]]:
    '''
    Converts a record in long format to wide format. Converts dictionaries
    from {name: value} format to an iterable with items {"name": name, "value": value}.

    %LAST_UPDATE% and %LAST_UPDATE_F% are special fields to include
    with each record. That is, if given the record:
    {
        "%LAST_UPDATE%": 1780020530,
	    "%LAST_UPDATE_F%": "29 May 2026 02:08:50 (UTC)",
        "Abyssal whip": 90000,
        "Dragon scimitar": 125000
    }
    Then the function will yield two dicts:
    {
        "%LAST_UPDATE%": 1780020530,
        "%LAST_UPDATE_F%": "29 May 2026 02:08:50 (UTC)",
        "name": "Abyssal whip",
        "value": 90000
    }
    and
    {
        "%LAST_UPDATE%": 1780020530,
        "%LAST_UPDATE_F%": "29 May 2026 02:08:50 (UTC)",
        "name": "Dragon scimitar",
        "value": 125000
    }

    Parameters
    ----------
    record : dict
        The long-form record to convert.
    
    Returns
    -------
    Iterable[dict]
        The wide-form records.
    '''
    special = {
        key: record[key] for key in ['%LAST_UPDATE%', '%LAST_UPDATE_F%']
    }
    for k, v in record.items():
        if k not in special:
            yield {
                'name': k,
                'value': v,
                **special
            }


@dlt.resource
def item_details() -> Iterable[dict]:
    '''
    Iterates over the API to get all item details, yielding one at a time.
    
    Returns
    -------
    Iterable[dict]
        Dictionaries of each item's properties.
    '''
    for category in range(44):
        j = request(
            'GET',
            'https://secure.runescape.com/m=itemdb_rs/api/catalogue/category.json',
            params = {'category': category})
        for d in j['alpha']:
            # item count doesn't seem to match what the API returns.
            yield from get_items_from_pages(category, d['letter'], d['items'])


def get_items_from_pages(category: int, alpha: str, count: int) -> Iterable[dict]:
    '''
    Iterates through item pages, yielding one at a time.
    
    Parameters
    ----------
    category : int
        The category ID. Currently there are categories 0-43.
    alpha : str
        The first letter of the item. Note that all numbrs are '#' instead.
    count : int
        The count of items that the API has.
    
    Returns
    -------
    Iterable[dict]
        Dictionaries of each item's properties.
    '''
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
    '''Sets configurations before invoking the pipeline.'''

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
    def exchange_history(parent_item: dict) -> Iterable[dict]:
        '''
        The exchange_history endpoint needs item IDs from the parent resource.
        It yields all the daily trade aggregate stats, one at a time.
        
        Parameters
        ----------
        parent_item : dict
            The parent item, which must contain the id under the "value" field (as in the module endpoints).
        
        Returns
        -------
        Iterable[dict]
            Each day's trade statistics as a dict.
        '''
        j = request(
            'GET'
            'https://api.weirdgloop.org/exchange/history/rs/all',
            params = {'id': parent_item['value']})
        yield from itertools.chain.from_iterable(j.values())


    pipeline = dlt.pipeline(
        pipeline_name = 'rs_gemw',
        destination = dlt.destinations.duckdb(
            credentials = 'duckdb:///data/RS_GEMW/db.duckdb'),
        dataset_name = 'raw',
        progress = 'tqdm')
    
    load_info = pipeline.run(
        [
            source, 
            exchange_history,
            item_details,
        ],
        write_disposition = 'replace'),
    pprint(load_info)


if __name__ == '__main__':
    main()
