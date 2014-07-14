import json
import urllib2
import urllib

from ckan import model

from ckanext.edc_schema.commands.base import (site_url,
                                              api_key)


#     def delete_orgs(self):
#                     
#         context = {'model': model, 'session':model.Session, 'user':self.user_name}
# 
#         org_model = context['model']             
#         top_level_orgs = org_model.Group.get_top_level_groups(type="organization")
#         
#         for orgg in top_level_orgs :
#             org = get_action('organization_show')(context, {'id': orgg.id})
#             print "Organization ------------> ", org['name']
#             group = org_model.Group.get(orgg.id)
#             branches = group.get_children_groups(type="organization")
#             for branch in branches:
#                 branch_org = get_action('organization_show')(context, {'id': branch.id})
#                 print "\t Branch ------------> ", branch_org['name']
# #                get_action('memeber_delete')(context, {'id' : branch_org['id'], 'object': org['id'], 'object_type' : 'group'})
#                 get_action('organization_purge')(context, {'id' : branch_org['id']})
#             get_action('organization_purge')(context, {'id' : org['id']})
#                 
#                     

def delete_all_orgs():
    import pprint
    
    #Get the list of all top level organizations
    top_level_orgs = []
    context = {'model': model, 'session':model.Session, 'user':'admin'}

    org_model = context['model']             
    top_level_orgs = org_model.Group.get_top_level_groups(type="organization")
    pprint.pprint(top_level_orgs)
    
#     try :
#         data_string =  urllib.quote(json.dumps({'all_fields' : True }))
#         request = urllib2.Request(site_url + '/api/3/action/_list')
#         response = urllib2.urlopen(request, data_string)
#         assert response.code == 200
#         response_dict = json.loads(response.read())
#         assert response_dict['success'] is True
#         top_level_orgs = response_dict['result']
#         pprint.pprint(response_dict['result'])
#         print '------------------------------------------------------------------------------------------------------'
#     except Exception :
#         pass
        
    for top_org in top_level_orgs :
        
        #Get the list of sub-orgs of this org
        try:
            data_string =  urllib.quote(json.dumps({'id' : top_org.id, 'object_type' : 'organization', 'capacity': 'admin'}))
            request = urllib2.Request(site_url + '/api/3/action/member_list')
            request.add_header('Authorization', api_key)
            response = urllib2.urlopen(request, data_string)
            assert response.code == 200
            response_dict = json.loads(response.read())
            assert response_dict['success'] is True
        except Exception :
            pass


delete_all_orgs()