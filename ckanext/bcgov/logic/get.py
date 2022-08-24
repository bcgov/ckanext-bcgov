# encoding: utf-8

'''API functions for searching for and getting data from CKAN.'''

import logging

import sqlalchemy
from paste.deploy.converters import asbool

import ckan.logic as logic
import ckan.lib.navl.dictization_functions
import ckan.model as model

from ckan.logic import NotAuthorized

from ckan.logic.action.get import ( _unpick_search )
from ckanext.bcgov.util.util import (get_organization_branches, get_parent_orgs)

log = logging.getLogger('ckanext.bcgov.logic.bcgov.override')

# Define some shortcuts
# Ensure they are module-private so that they don't get loaded as available
# actions in the action API.
_validate = ckan.lib.navl.dictization_functions.validate
ValidationError = logic.ValidationError

_or_ = sqlalchemy.or_

def _group_or_org_list(context, data_dict, is_org=False):
    """
    Copied from ckan 2.7.2 ckan.logic.action.get

    Modified for the purposes of catching `asbool` value error 
    due to a bug in the function with missing or malformed argument value, eg. `None or 'tr'`

    See ticket #357 in bcgov repository
    """
    model = context['model']
    api = context.get('api_version')
    groups = data_dict.get('groups')
    group_type = data_dict.get('type', 'group')
    ref_group_by = 'id' if api == 2 else 'name'
    pagination_dict = {}
    limit = data_dict.get('limit')
    if limit:
        pagination_dict['limit'] = data_dict['limit']
    offset = data_dict.get('offset')
    if offset:
        pagination_dict['offset'] = data_dict['offset']
    if pagination_dict:
        pagination_dict, errors = _validate(
            data_dict, logic.schema.default_pagination_schema(), context)
        if errors:
            raise ValidationError(errors)
    sort = data_dict.get('sort') or 'title'
    q = data_dict.get('q')

    try:
        all_fields = asbool(data_dict.get('all_fields', None)) 
    except ValueError:
        all_fields = False

    # order_by deprecated in ckan 1.8
    # if it is supplied and sort isn't use order_by and raise a warning
    order_by = data_dict.get('order_by', '')
    if order_by:
        log.warn('`order_by` deprecated please use `sort`')
        if not data_dict.get('sort'):
            sort = order_by

    # if the sort is packages and no sort direction is supplied we want to do a
    # reverse sort to maintain compatibility.
    if sort.strip() in ('packages', 'package_count'):
        sort = 'package_count desc'

    sort_info = _unpick_search(sort,
                               allowed_fields=['name', 'packages',
                                               'package_count', 'title'],
                               total=1)

    if sort_info and sort_info[0][0] == 'package_count':
        query = model.Session.query(model.Group.id,
                                    model.Group.name,
                                    sqlalchemy.func.count(model.Group.id))

        query = query.filter(model.Member.group_id == model.Group.id) \
                     .filter(model.Member.table_id == model.Package.id) \
                     .filter(model.Member.table_name == 'package') \
                     .filter(model.Package.state == 'active')
    else:
        query = model.Session.query(model.Group.id,
                                    model.Group.name)

    query = query.filter(model.Group.state == 'active')

    if groups:
        query = query.filter(model.Group.name.in_(groups))
    if q:
        q = u'%{0}%'.format(q)
        query = query.filter(_or_(
            model.Group.name.ilike(q),
            model.Group.title.ilike(q),
            model.Group.description.ilike(q),
        ))

    query = query.filter(model.Group.is_organization == is_org)
    query = query.filter(model.Group.type == group_type)

    if sort_info:
        sort_field = sort_info[0][0]
        sort_direction = sort_info[0][1]
        if sort_field == 'package_count':
            query = query.group_by(model.Group.id, model.Group.name)
            sort_model_field = sqlalchemy.func.count(model.Group.id)
        elif sort_field == 'name':
            sort_model_field = model.Group.name
        elif sort_field == 'title':
            sort_model_field = model.Group.title

        if sort_direction == 'asc':
            query = query.order_by(sqlalchemy.asc(sort_model_field))
        else:
            query = query.order_by(sqlalchemy.desc(sort_model_field))

    if limit:
        query = query.limit(limit)
    if offset:
        query = query.offset(offset)

    groups = query.all()

    action = 'organization_show' if is_org else 'group_show'
    group_list = []
    for group in groups:
        data_dict['id'] = group.id
        data_dict['include_extras'] = True
        for key in ('include_tags', 'include_users',
                    'include_groups', 'include_followers'):
            if key not in data_dict:
                data_dict[key] = False

        try:
            group_detail = logic.get_action(action)(context, data_dict)
        except NotAuthorized:
            continue

        group_list.append(group_detail if all_fields else getattr(group, ref_group_by))

    return group_list

def organization_list_related(context, data_dict):
        '''
        Returns the list of organizations including parent_of and child_of relationships.
        '''
        org_list = get_action('organization_list')(context, data_dict)

        # Add the child orgs to the response:
        for org in org_list:
            children = []
            branches = get_organization_branches(org['id'])
            group_list = model_dictize.group_list_dictize(branches, context)
            for branch in group_list:
                d = {}
                d['title'] = branch['title']
                children.append(d)

            org['parent_of'] = children

            parents = []
            branches = get_parent_orgs(org['id'])
            group_list = model_dictize.group_list_dictize(branches, context)
            for branch in group_list:
                d = {}
                d['title'] = branch['title']
                parents.append(d)
            org['child_of'] = parents

        return_dict = {}
        return_dict['success'] = True
        return_dict['result'] = org_list
        return return_dict
