import logging
import operator

import ckan.lib.base as base
import ckan.model as model
from ckan.logic import get_action

from ckanext.ga_report.ga_model import GA_Url, GA_Publisher
from ckanext.ga_report.controller import _get_publishers
_log = logging.getLogger(__name__)

def popular_datasets(count=10):
    import random

    publisher = None
    publishers = _get_publishers(30)
    total = len(publishers)
    while not publisher or not datasets:
        rand = random.randrange(0, total)
        publisher = publishers[rand][0]
        if not publisher.state == 'active':
            publisher = None
            continue
        datasets = _datasets_for_publisher(publisher, 10)[:count]

    ctx = {
        'datasets': datasets,
        'publisher': publisher
    }
    return base.render_snippet('ga_report/ga_popular_datasets.html', **ctx)

def single_popular_dataset(top=20):
    '''Returns a random dataset from the most popular ones.

    :param top: the number of top datasets to select from
    '''
    import random

    top_datasets = model.Session.query(GA_Url).\
                   filter(GA_Url.url.like('/dataset/%')).\
                   order_by('ga_url.pageviews::int desc')
    num_top_datasets = top_datasets.count()

    dataset = None
    if num_top_datasets:
        count = 0
        while not dataset:
            rand = random.randrange(0, min(top, num_top_datasets))
            ga_url = top_datasets[rand]
            dataset = model.Package.get(ga_url.url[len('/dataset/'):])
            if dataset and not dataset.state == 'active':
                dataset = None
            # When testing, it is possible that top datasets are not available
            # so only go round this loop a few times before falling back on
            # a random dataset.
            count += 1
            if count > 10:
                break
    if not dataset:
        # fallback
        dataset = model.Session.query(model.Package)\
                  .filter_by(state='active').first()
        if not dataset:
            return None
    dataset_dict = get_action('package_show')({'model': model,
                                               'session': model.Session,
                                               'validate': False},
                                              {'id':dataset.id})
    return dataset_dict

def single_popular_dataset_html(top=20):
    dataset_dict = single_popular_dataset(top)
    groups = package.get('groups', [])
    publishers = [ g for g in groups if g.get('type') == 'organization' ]
    publisher = publishers[0] if publishers else {'name':'', 'title': ''}
    context = {
        'dataset': dataset_dict,
        'publisher': publisher_dict
        }
    return base.render_snippet('ga_report/ga_popular_single.html', **context)


def most_popular_datasets(publisher, count=20, preview_image=None):

    if not publisher:
        _log.error("No valid publisher passed to 'most_popular_datasets'")
        return ""

    results = _datasets_for_publisher(publisher, count)

    ctx = {
        'dataset_count': len(results),
        'datasets': results,

        'publisher': publisher,
        'preview_image': preview_image
    }

    return base.render_snippet('ga_report/publisher/popular.html', **ctx)

def _datasets_for_publisher(publisher, count):
    datasets = {}
    entries = model.Session.query(GA_Url).\
        filter(GA_Url.department_id==publisher.name).\
        filter(GA_Url.url.like('/dataset/%')).\
        order_by('ga_url.pageviews::int desc').all()
    for entry in entries:
        if len(datasets) < count:
            p = model.Package.get(entry.url[len('/dataset/'):])

            if not p:
                _log.warning("Could not find Package for {url}".format(url=entry.url))
                continue

            if not p.state == 'active':
                _log.warning("Package {0} is not active, it is {1}".format(p.name, p.state))
                continue

            if not p in datasets:
                datasets[p] = {'views':0, 'visits': 0}

            datasets[p]['views'] = datasets[p]['views'] + int(entry.pageviews)
            datasets[p]['visits'] = datasets[p]['visits'] + int(entry.visits)

    results = []
    for k, v in datasets.iteritems():
        results.append((k,v['views'],v['visits']))

    return sorted(results, key=operator.itemgetter(1), reverse=True)

def month_option_title(month_iso, months, day):
    month_isos = [ iso_code for (iso_code,name) in months ]
    try:
        index = month_isos.index(month_iso)
    except ValueError:
        _log.error('Month "%s" not found in list of months.' % month_iso)
        return month_iso
    month_name = months[index][1]
    if index==0:
        return month_name + (' (up to %s)'%day)
    return month_name


