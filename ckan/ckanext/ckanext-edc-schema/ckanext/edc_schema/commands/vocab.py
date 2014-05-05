#Author : Khalegh Mamakani, Highway Three Solutions  Inc.
#Date created : January 29 2014
#Last modified on January 29 2014

from ckan import model
from ckan.lib.cli import CkanCommand
from ckan.logic import get_action, NotFound

from ckanext.edc_schema.forms import dataset_form

import logging
import os
import sys
import json
import pprint

import ckan.plugins as plugins

log = logging.getLogger()


class EdcVocabCommand(CkanCommand):
    '''
    This class contains commnds for creating special vocabularies and tags
    required for EDC-Dataset manipulation
    '''
    summary = __doc__.split('\n')[0]
    usage = __doc__
    
    default_data_dir = os.path.dirname(os.path.abspath(__file__))
    default_vocab_file = default_data_dir + '/../../../data/edc-vocabs.json'  
    default_org_file =   default_data_dir + '/../../../data/orgs.json'
    
    def command(self):
        '''
        Parse command line arguments and call appropriate method.
        '''
        if not self.args or self.args[0] in ['--help', '-h', 'help']:
            print EdcVocabCommand.__doc__
            return
        
        cmd = self.args[0]
        self._load_config()

        user = get_action('get_site_user')(
            {'model': model, 'ignore_auth': True}, {}
        )
        self.user_name = user['name']

        # file_path is used by create-all-vocabs command
        vocab_file = self.args[1] if len(self.args) >= 2 else None


        
        if cmd == 'create-all-vocabs' :
            self.create_all_vocabs()
        elif cmd == 'delete-all-vocabs' :
            self.delete_all_vocabs()
        elif cmd == 'create-all-orgs' :
            self.create_orgs()
        elif cmd == 'delete-all-orgs' :
            self.delete_orgs()
        else:
            log.error('Command "%s" not defined' % (cmd,))
                   
    def _create_vocab(self, context, vocab_name, tags):
        print "Vocab ========> ", vocab_name, "tags ===> ", tags
        vocab = get_action('vocabulary_create')(context, {'name': vocab_name})
        for tag in tags:
            get_action('tag_create')(context, {'name': tag['id'] + '__' + tag['name'], 
                                                               'vocabulary_id': vocab['id']})
                                    
    def create_all_vocabs(self, vocab_file=None):
        
        if not vocab_file:
            vocab_file = self.default_vocab_file
         
        if not os.path.exists(vocab_file):
            log.error('File {0} does not exists'.format(vocab_file))
            sys.exit(1)
             
        context = {'model': model, 'session':model.Session, 'user':self.user_name}
#         
        #Read vocabularies json file
        with open(vocab_file) as json_file:
            vocabs = json.loads(json_file.read())
        
        #Get the list of available vocabularies
        available_vocabs = get_action('vocabulary_list')(context)
        
        available_vocab_names = [vocab['name'] for vocab in available_vocabs]
        #for each vocabulary defined in json file
        for vocab_item in vocabs :
            
            vocab_name = vocab_item['name']
            vocab_tags = vocab_item['tags']
            #check if the vocabulary exists :
            if not vocab_name in available_vocab_names:
                #Create the vocabulary 
                self._create_vocab(context, vocab_name, vocab_tags)
            else:
                #Get the vocab from the list of available vocabularies
                vocab = get_action('vocabulary_show')(context, {'id' : vocab_name})
                #Get the list of available tags for this vocab
                available_tags = get_action('tag_list')(context, {'vocabulary_id' : vocab['id']})
                
                #Add each tag that is not in the list of available tags
                for vocab_tag in vocab_tags:
                    tag = vocab_tag['id'] + '__' + vocab_tag['name']
                    if not tag in available_tags:
                        new_tag = {'name': tag,
                               'vocabulary_id': vocab['id']}
                        get_action('tag_create')(context, new_tag)
                        
    def delete_all_vocabs(self):
        
        context = {'model': model, 'session':model.Session, 'user': self.user_name}
        #Get all available vocabularies
        all_vocabs = get_action('vocabulary_list')(context)
        
        for vocab in all_vocabs:
            log.info('Deleting vocabulary "{0}.'.format(vocab['name']))
            #Deleting all tags of the current vocab
            for tag in vocab.get('tags') :
                log.info('Deleting tag "%s".' % tag['name'])
                get_action('tag_delete')(context, {'id': tag['id']})
            
            #Deleting the vocabulary
            get_action('vocabulary_delete')(context, {'id': vocab['id']})

     
    
    def delete_orgs(self):
                    
        context = {'model': model, 'session':model.Session, 'user':self.user_name}

        org_model = context['model']             
        top_level_orgs = org_model.Group.get_top_level_groups(type="organization")
        
        for orgg in top_level_orgs :
            org = get_action('organization_show')(context, {'id': orgg.id})
            print "Organization ------------> ", org['name']
            group = org_model.Group.get(orgg.id)
            branches = group.get_children_groups(type="organization")
            for branch in branches:
                branch_org = get_action('organization_show')(context, {'id': branch.id})
                print "\t Branch ------------> ", branch_org['name']
#                get_action('memeber_delete')(context, {'id' : branch_org['id'], 'object': org['id'], 'object_type' : 'group'})
                get_action('organization_purge')(context, {'id' : branch_org['id']})
            get_action('organization_purge')(context, {'id' : org['id']})
                
                    
                        
    def create_orgs(self, org_file=None):
        
        if not org_file:
            org_file = self.default_org_file
              
        if not os.path.exists(org_file):
            log.error('File {0} does not exists'.format(org_file))
            sys.exit(1)
               
        context = {'model': model, 'session':model.Session, 'user':self.user_name}
                  
        #Read the organizations json file
        with open(org_file) as json_file:
            orgs = json.loads(json_file.read())
          
          

        #Create each organization and all of its branches if it is not in the list of available organizations
        for org_item in orgs:
            org_name = org_item['name']
            branches = org_item['branches']
            org_title = org_item['title']
               
#            print "Organization ------> " ,org_name  
            try :
                org = get_action('organization_show')(context, {'id' : org_name })
            except NotFound:
                org = get_action('organization_create')(context, {'name' : org_name, 'title' : org_title })
                
            group = model.Group.get(org['id'])
              
#            pprint.pprint(branches)
            for branch in branches:
                branch_name = branch['name']
                branch_title = branch['title']
                   
#                print "Branch --------> ", branch_name 
                try:
                    sub_org = get_action('organization_show')(context, {'id' : branch_name })
                except NotFound:
                    sub_org = get_action('organization_create')(context, {'name' : branch_name, 'title' : branch_title })
                    
                sub_group = model.Group.get(sub_org['id'])
                        
                #Add the sub_org as a member of the org
                get_action('member_create')(context, {'id' : sub_org['id'], 'object' : org['id'], 'object_type' : 'group', 'capacity' : 'admin'})
          
        org_model = context['model']             
        top_level_org = org_model.Group.get_top_level_groups(type="organization")
        
        for org in top_level_org:
            print "Organization +---------> ", org.name
            group = org_model.Group.get(org.id)
            branches = group.get_children_groups(type = 'organization')
            for branch in branches:
                print '\t Branch +-------------> ', branch.name 
        
        

            