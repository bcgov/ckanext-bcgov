# Copyright  2015, Province of British Columbia
# License: https://github.com/bcgov/ckanext-bcgov/blob/master/license

# Author : Khalegh Mamakani, Highway Three Solutions  Inc.
# Date created : January 29 2014
# Last modified on January 29 2014

from ckan import model
from ckan.lib.cli import CkanCommand
from ckan.logic import get_action, NotFound
from ckan.lib.datapreview import (get_default_view_plugins,
                                  add_views_to_dataset_resources)
import ckan.lib.dictization.model_save as model_save


import logging
import re
import os
import sys
import csv
import json

from ckanapi import LocalCKAN, NotFound

import ckanext.bcgov
import ckan.lib.base as base

import ckan.plugins as plugins

_ = base._

log = logging.getLogger()


class EdcCommand(CkanCommand):
    '''
    This class contains commnds for creating special vocabularies and tags
    required for EDC-Dataset manipulation

    Commands:
        create-all-vocabs   Create all vocabularies
        delete-all-vocabs   Delete all vocabularies
        create-all-orgs     Create all organizations
        delete-all-orgs     Delete all organizations
        purge-records       Purge all already-deleted datasets
        purge-revisions     Purge all already-deleted revisions
        create-views        Create CKAN 2.3 resource views
        migrate-to-scheming Migrate Classic EDC Datasets to use ckanext_scheming
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__

    default_data_dir = os.path.join(ckanext.bcgov.__path__[0], 'scripts/data')

    default_vocab_file = os.path.join(default_data_dir, 'edc-vocabs.json')
    default_org_file = os.path.join(default_data_dir, 'orgs.json')
    default_sub_org_file = os.path.join(default_data_dir, 'suborgs.json')

    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print EdcCommand.__doc__
            return

        cmd = self.args[0]
        self._load_config()

        user = get_action('get_site_user')({
            'model': model,
            'ignore_auth': True
        }, {})

        self.user_name = user['name']

        self.api = LocalCKAN()

        # file_path is used by create-all-vocabs command
        vocab_file = self.args[1] if len(self.args) >= 2 else None

        if cmd == 'create-all-vocabs':
            self.create_all_vocabs()
        elif cmd == 'delete-all-vocabs':
            self.delete_all_vocabs()
        elif cmd == 'create-all-orgs':
            self.create_all_orgs()
        elif cmd == 'delete-all-orgs':
            self.delete_orgs()
        elif cmd == 'purge-records':
            self.purge_records()
        elif cmd == 'purge-revisions':
            self.purge_revisions()
        elif cmd == 'create-views':
            self.create_views()
        elif cmd == 'migrate-to-scheming':
            self.migrate_to_scheming()
        else:
            log.error('Command "%s" not defined' % (cmd, ))

    def _create_vocab(self, context, vocab_name, tags):
        print "Vocab ========> ", vocab_name, "tags ===> ", tags
        vocab = get_action('vocabulary_create')(context, {'name': vocab_name})
        for tag in tags:
            get_action('tag_create')(context, {
                'name': tag,
                'vocabulary_id': vocab['id']
            })

    def create_all_vocabs(self, vocab_file=None):
        if not vocab_file:
            vocab_file = self.default_vocab_file

        if not os.path.exists(vocab_file):
            log.error('File {0} does not exists'.format(vocab_file))
            sys.exit(1)

        context = {
            'model': model,
            'session': model.Session,
            'user': self.user_name
        }

        # Read vocabularies json file
        with open(vocab_file) as json_file:
            vocabs = json.loads(json_file.read())

        # Get the list of available vocabularies
        available_vocabs = get_action('vocabulary_list')(context)

        available_vocab_names = [vocab['name'] for vocab in available_vocabs]
        # for each vocabulary defined in json file
        for vocab_item in vocabs:

            vocab_name = vocab_item['name']
            vocab_tags = vocab_item['tags']

            # check if the vocabulary exists :
            if vocab_name not in available_vocab_names:
                # Create the vocabulary
                self._create_vocab(context, vocab_name, vocab_tags)
            else:
                # Get the vocab from the list of available vocabularies
                vocab = get_action('vocabulary_show')(context, {
                    'id': vocab_name
                })
                # Get the list of available tags for this vocab
                available_tags = get_action('tag_list')(
                    context, {
                        'vocabulary_id': vocab['id']
                    })

                # Add each tag that is not in the list of available tags
                for tag in vocab_tags:
                    if tag not in available_tags:
                        new_tag = {'name': tag, 'vocabulary_id': vocab['id']}
                        get_action('tag_create')(context, new_tag)

    def delete_all_vocabs(self):
        context = {
            'model': model,
            'session': model.Session,
            'user': self.user_name
        }
        # Get all available vocabularies
        all_vocabs = get_action('vocabulary_list')(context)

        for vocab in all_vocabs:
            log.info('Deleting vocabulary "{0}.'.format(vocab['name']))
            # Deleting all tags of the current vocab
            for tag in vocab.get('tags'):
                log.info('Deleting tag "%s".' % tag['name'])
                get_action('tag_delete')(context, {'id': tag['id']})

            # Deleting the vocabulary
            get_action('vocabulary_delete')(context, {'id': vocab['id']})

    def delete_orgs(self):
        context = {
            'model': model,
            'session': model.Session,
            'user': self.user_name
        }

        org_model = context['model']
        top_level_orgs = org_model.Group.get_top_level_groups(
            type="organization")

        for org in top_level_orgs:
            org = get_action('organization_show')(context, {
                'id': org.id,
                'include_datasets': False
            })
            print "Organization ------------> ", org['name']
            group = org_model.Group.get(orgg.id)
            branches = group.get_children_groups(type="organization")
            for branch in branches:
                branch_org = get_action('organization_show')(
                    context, {
                        'id': branch.id,
                        'include_datasets': False
                    })
                print "\t Branch ------------> ", branch_org['name']
                # get_action('memeber_delete')(context, {'id' : branch_org['id'], 'object': org['id'], 'object_type' : 'group'})
                get_action('organization_purge')(context, {
                    'id': branch_org['id']
                })
            get_action('organization_purge')(context, {'id': org['id']})

    def create_all_orgs(self):
        '''
        Creates BCgov Organizations from
        scripts/data/org_suborg_sector_mapping_forEDC.csv file

        Will create all top level orgs and sub-level orgs
        '''
        org_data = os.path.join(self.default_data_dir,
                                'org_suborg_sector_mapping_forEDC.csv')

        def title_to_name(title):
            return re.sub('[^0-9a-zA-Z]+', ' ', title).lower().strip().replace(
                ' ', '-')

        def _create_or_get_org(name, title, sector=None):
            try:
                # include_groups needs to be false otherwise
                # a too much recursion error happens
                return self.api.action.organization_show(
                            id=name, include_datasets=False,
                            include_groups=False)

            except NotFound as e:
                return self.api.action.organization_create(
                            name=name, title=title, sector=sector)

        with open(org_data, 'r') as csvfile:
            org_reader = csv.reader(csvfile, skipinitialspace=True)

            for i, row in enumerate(org_reader):
                if i == 0:
                    continue

                org_title = row[1]
                org_name = title_to_name(org_title)

                sub_title = row[2]
                sub_name = title_to_name(sub_title)

                sector = row[3]

                org = _create_or_get_org(org_name, org_title)
                sub_org = _create_or_get_org(sub_name, sub_title, sector)

                member = self.api.action.member_create(
                    id=sub_org['id'],
                    object=org['id'],
                    object_type='group',
                    capacity='admin')

    def purge_records(self):
        # Get the list of all deleted records
        deleted_packages = model.Session.query(
            model.Package).filter_by(state=model.State.DELETED)

        msgs = []

        revs_to_purge = []
        count = 0
        for pkg in deleted_packages:
            count += 1
            # pprint.pprint(pkg)
            revisions = [x[0] for x in pkg.all_related_revisions]
            # ensure no accidental purging of other(non-deleted)
            # packages initially just avoided purging revisions
            # where non-deleted packages were affected
            # however this lead to confusing outcomes e.g.
            # we successfully deleted revision in which package
            # was deleted (so package now active again) but no
            # other revisions
            problem = False
            for r in revisions:
                affected_pkgs = set(r.packages).difference(
                    set(deleted_packages))
                if affected_pkgs:
                    msg = _('Cannot purge package %s as '
                            'associated revision %s includes '
                            'non-deleted packages %s')
                    msg = msg % (pkg.id, r.id, [pkg.id for r in affected_pkgs])
                    msgs.append(msg)
                    problem = True
                    break
            if not problem:
                revs_to_purge += [r.id for r in revisions]
            print '.'
        model.Session.remove()

        revs_to_purge = list(set(revs_to_purge))
        for id in revs_to_purge:
            revision = model.Session.query(model.Revision).get(id)
            try:
                # TODO deleting the head revision corrupts the edit
                # page Ensure that whatever 'head' pointer is used
                # gets moved down to the next revision
                model.repo.purge_revision(revision, leave_record=False)
            except Exception, inst:
                msg = _('Problem purging revision %s: %s') % (id, inst)
                msgs.append(msg)

        print '------------------------------- Purge complete -------------------------------'

        print 'Total number of records : ' + str(count)
        print 'Purge errors : '
        for msg in msgs:
            print msg

    def purge_revisions(self):
        deleted_revisions = model.Session.query(
            model.Revision).filter_by(state=model.State.DELETED)

        msgs = []
        revs_to_purge = [rev.id for rev in deleted_revisions]
        revs_to_purge = list(set(revs_to_purge))
        for id in revs_to_purge:
            print id
            revision = model.Session.query(model.Revision).get(id)
            try:
                # TODO deleting the head revision corrupts the edit
                # page Ensure that whatever 'head' pointer is used
                # gets moved down to the next revision
                model.repo.purge_revision(revision, leave_record=False)
            except Exception, inst:
                msg = _('Problem purging revision %s: %s') % (id, inst)
                msgs.append(msg)
        print '------------------------------- Purge complete -------------------------------'

        print 'Purge errors : '
        for msg in msgs:
            print msg

    def create_views(self):
        # TODO: we need this method because of this bug - @deniszgonjanin
        # https://github.com/ckan/ckan/issues/2532
        view_plugins = [
            view_plugin.info()['name']
            for view_plugin in get_default_view_plugins()
        ]

        for p in get_action('package_list')({}, {}):
            package = get_action('package_show')({}, {'id': p})

            add_views_to_dataset_resources(
                {}, package, view_types=view_plugins)

    def migrate_to_scheming(self):
        context = {
            'model': model,
            'session': model.Session,
            'user': self.user_name
        }
        packages = model.Session.query(model.Package)
        for package in packages:
            context['package'] = package
            data = self.api.action.package_show(name_or_id=package.id)
            package_type = data['type']
            if len(package_type) < 1 or package_type == 'bcdc_dataset':
                continue
            data['dataset_type'] = package_type
            data['type'] = 'bcdc_dataset'

            rev = model.repo.new_revision()
            rev.message = _(u"EDC Command: Update object %s") % data['name']

            pkg = model_save.package_dict_save(data, context)

            if pkg.type == 'bcdc_dataset':
                model.repo.commit()
                print "Successfully updated {0} to BCDC Dataset".format(pkg.name)
            else:
                print "Failed to update {0} to BCDC Dataset".format(pkg.name)

        print '----------------------------- Migration complete -----------------------------'
