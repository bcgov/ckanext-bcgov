"""edc_tags command line interface

Usage:
    edc_tags <action> [VOCAB ...] (-r SITE_URL) [options]

Arguments:
    <action>                Update, Create or Delete
    [VOCAB ...]             List of vocabularys by name or id
    -r --remote=URL         URL of CKAN server for remote actions

Options:
    -h --help               Show Usage
    -V, --version           Show version
    -v, --verbose           Show action messages
    -a, --apikey=APIKEY     API key to use for remote actions
    -d, --data-file=FILE    File location for the Vocabulary list
                             [default: ./data/edc-vocabs.json]
"""
import json

from docopt import docopt
from ckanapi import RemoteCKAN


args = docopt(__doc__, version='1')

action = args.get('<action>')
vocab_names = args.get('VOCAB')

url = args.get('--remote')
api_key = args.get('--apikey')
all_fields = args.get('--all-fields', True)
verbose = args.get('--verbose')

edc_vocab_location = args.get('--data-file')
edc_vocabs = None


def _get_vocab_list(vocab_name):
    for i in edc_vocabs:
        if i['name'] == vocab_name:
            return i['tags']


def _new_tags(api, vocab_id, vocab_name):
    new_vocab_list = _get_vocab_list(vocab_name)

    for new_item in new_vocab_list:
        tag = api.action.tag_create(name=new_item, vocabulary_id=vocab_id)
        yield tag
        if verbose:
            print(tag)


def create_tags(api, vocab_name):
    if verbose:
        print("Creating vocabulary %s @ %s ..." % (vocab_name, url))

    created = api.action.vocabulary_create(name=vocab_name)
    print(created)
    vocab_id = created['id']

    if verbose:
        print('New vocabulary list %s created.' % created['name'])

    new_tags = [tag for tag in _new_tags(api, vocab_id, vocab_name)]

    if verbose:
        print("Finished creating %s.\n" % vocab_name)


def update_tags(api, vocab_name):
    if verbose:
        print("Updating vocabulary %s @ %s ..." % (vocab_name, url))

    # Need to delete the tag item individually first because
    # deleting the vocabulary itself by id throws integraty error
    vocab_id = delete_tags(api, vocab_name, display_msg=False)

    new_tags = [tag for tag in _new_tags(api, vocab_id, vocab_name)]

    if verbose:
        print("Finished updating %s.\n" % vocab_name)


def delete_tags(api, vocab_name, display_msg=True):
    if verbose and display_msg:
        print("Deleting vocabulary %s @ %s ..." % (vocab_name, url))

    vocab_id = api.action.vocabulary_show(id=vocab_name).get('id')

    tag_list = api.action.tag_list(vocabulary_id=vocab_id,
                                   all_fields=all_fields)

    for tag in tag_list:
        api.action.tag_delete(id=tag['id'],
                              vocabulary_id=tag['vocabulary_id'])

    if verbose and display_msg:
        print("Finished deleting %s." % vocab_name)

    return vocab_id  # for usage in update_tags


if __name__ == '__main__':
    with open(edc_vocab_location) as json_file:
        edc_vocabs = json.loads(json_file.read())

    with RemoteCKAN(url, apikey=api_key) as api:
        for vocab_name in vocab_names:
            if action in ['update', 'u']:
                update_tags(api, vocab_name)
            elif action in ['create', 'c']:
                create_tags(api, vocab_name)
            elif action in ['delete', 'd']:
                delete_tags(api, vocab_name)
            else:
                print("%s is not an action. "
                      "Avaiable actions: update | create | delete" % action)
                exit(1)

        if verbose:
            print("Done.")

    exit(0)
