
import dlt
from dlt.sources.rest_api import rest_api_source


def main():
    source = rest_api_source({

    })

    pipeline = dlt.pipeline(
        pipeline_name = 'rs_gemw',
        destination = dlt.destinations.duckdb(
            credentials = 'duckdb:///data/db.duckdb'),
        dataset_name = 'raw')
    
    load_info = pipeline.run(source)
    print(load_info)


if __name__ == '__main__':
    main()
