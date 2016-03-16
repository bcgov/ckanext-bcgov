# original script: https://github.com/ckan/ckanapi/blob/master/ckanapi/remoteckan.py.
# modified by mbrown to load entire catalogue (each request can only return 1000 records at a time)

import sys
import argparse

import ckanapi
import losser.losser
import losser.cli
# added by mb
import requests

VERSION = '0.0.5'


# TODO: Make this more generic, accept search params as param.
def get_datasets_from_ckan(url, apikey):
    user_agent = ('ckanapi-exporter/{version} '
                  '(+https://github.com/ckan/ckanapi-exporter)').format(
                          version=VERSION)
    base_url = url + '/api/3/action/package_search?q='
    request = requests.get(base_url)
    total_records_count = request.json()["result"]["count"]
    full_record_result_list = []
    for i in range(0, total_records_count / 1000 + 1):
        full_url = base_url + "&rows=1000&start=" + str(i) + "000"
        api = ckanapi.RemoteCKAN(full_url, apikey=apikey, user_agent=user_agent)
        request = requests.get(full_url)
        results_list = request.json()["result"]["results"]
        for record in results_list:
            full_record_result_list.append(record)
    return full_record_result_list

# Original code
# def get_datasets_from_ckan(url, apikey):
#     user_agent = ('ckanapi-exporter/{version} '
#                   '(+https://github.com/ckan/ckanapi-exporter)').format(
#                           version=VERSION)
#     api = ckanapi.RemoteCKAN(url, apikey=apikey, user_agent=user_agent)
#     response = api.action.package_search(rows=1000000)
#     return response["results"]

def extras_to_dicts(datasets):
    for dataset in datasets:
        extras_dict = {}
        for extra in dataset.get("extras", []):
            key = extra["key"]
            value = extra["value"]
            assert key not in extras_dict
            extras_dict[key] = value
        dataset["extras"] = extras_dict


def export(url, columns, apikey=None, pretty=False):
    datasets = get_datasets_from_ckan(url, apikey)
    extras_to_dicts(datasets)
    csv_string = losser.losser.table(datasets, columns, csv=True,
                                     pretty=pretty)
    return csv_string


def main(args=None):
    parent_parser = losser.cli.make_parser(
        add_help=False, exclude_args=["-i"])
    parser = argparse.ArgumentParser(
        description="Export datasets from a CKAN site to JSON or CSV.",
        parents=[parent_parser],
    )
    parser.add_argument(
        "--url",
        help="the root URL of the CKAN site to export datasets from, "
             "for example: 'http://demo.ckan.org'",
        required=True,
    )
    parser.add_argument(
        "--apikey",
        help="the API key to use when fetching datasets from the CKAN site, "
             "use this option if you want to export private datasets as well "
             "as public ones",
        )
    try:
        parsed_args = losser.cli.parse(parser=parser)
    except losser.cli.CommandLineExit as err:
        sys.exit(err.code)
    except losser.cli.CommandLineError as err:
        if err.message:
            parser.error(err.message)
    csv_string = export(
        parsed_args.url, parsed_args.columns, parsed_args.apikey,
        pretty=parsed_args.pretty)
    sys.stdout.write(csv_string)



if __name__ == "__main__":
    main()