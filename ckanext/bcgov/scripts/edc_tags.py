"""edc_tags command line interface

Usage:
    edc_tags update <vocab_list> (-r SITE_URL) [-a APIKEY] [ -f ]

Arguments:
    -r --remote=URL           URL of CKAN server for remote actions

Options:
    -h --help                 Show Usage
    --version                 Show version
    -a --apikey=APIKEY        API key to use for remote actions
    -f --all-fields           update: option for getting all info from fields
                               in the vocabulary list, default is True

Todo:
    Add other commands like create and delete
    If no <vocab_list> is provided, should update all lists

    Add this option:
    -d --data-file            File location for the Vocabulary list,
                               default is ./data/edc-vocabs.json in
                               ckanext-bcgov
"""
import json

from docopt import docopt
from ckanapi import RemoteCKAN


args = docopt(__doc__, version='1')

url = args.get('--remote')
api_key = args.get('--apikey')
all_fields = args.get('--all-fields', True)
vocab_name = args.get('<vocab_list>')
vocab_id = ''
edc_vocab_location = ''
edc_vocabs = None


with open('./data/edc-vocabs.json') as json_file:
    edc_vocabs = json.loads(json_file.read())


with RemoteCKAN(url, apikey=api_key) as api:
    print("Updating vocabulary %s @ %s ..." % (vocab_name, url))

    vocab_id = api.action.vocabulary_show(id=vocab_name).get('id')

    tag_list = api.action.tag_list(vocabulary_id=vocab_id,
                                   all_fields=all_fields)

    # Need to delete the tag item individually first because
    # deleting the vocabulary by id throws integraty error
    for tag in tag_list:
        api.action.tag_delete(id=tag['id'],
                              vocabulary_id=tag['vocabulary_id'])

    new_vocab_list = [j for i in edc_vocabs for j in i['tags'] if i['name'] == vocab_name]

    for new_item in new_vocab_list:
        created = api.action.tag_create(name=new_item, vocabulary_id=vocab_id)
        print(created)

    print("Finished updating %s." % vocab_name)
