Disqus Extension
================

The Disqus extension allows site visitors to comment on individual
packages using an AJAX-based commenting system. The downsides of
this plugin are that comments are not stored locally and user
information is not shared between CKAN and the commenting system.

**Note: This extension requires ckan 1.7 or higher**

Activating and Installing
-------------------------

In order to set up the Disqus plugin, you first need to go to
disqus.com and set up a forum with your domain name. You will be
able to choose a forurm name.

To install the plugin, enter your virtualenv and load the source::

 (pyenv)$ pip install -e git+https://github.com/okfn/ckanext-disqus#egg=ckanext-disqus

For ckan versions before 2.0, please use the `release-v1.8` branch.

This will also register a plugin entry point, so you now should be
able to add the following to your CKAN .ini file::

 ckan.plugins = disqus <other-plugins>
 disqus.name = YOUR_DISQUS_NAME

**At this point nothing will have happened**! To add comments into your pages
see the next section.

Using the Extension
-------------------

Comments Threads
~~~~~~~~~~~~~~~~

To have comment threads appear on pages, insert into templates where you want the comments to
appear::

    ${h.disqus_comments()}

Note for theme developers: the extensions tries to generate a disqus_identifier
of the form::

    {controller/domain-object-name}::{id}

Where controller = 'group' in the group section, 'dataset' in the dataset
section (note that this differs from controller name internally which is still
package), 'resource'  for resources etc. This identifier will be useful if you
want to then reference this comment (e.g. for comment counts) elsewhere in the
site.

Recent comments
~~~~~~~~~~~~~~~

Insert on pages where you want recent comments to appear::

    ${h.disqus_recent()}

The recent comments widget will show 5 recent comments by default.  To show 10 recent comments use the following::

    ${h.disqus_recent(num_comments=10)}

Other widgets
~~~~~~~~~~~~~

Disqus offers many other widgets. Rather than providing these automatically as
part of this extension we suggest that theme developers incorporate the code
directly (note that you access the relevant config variables from the config
object passed into all templates).

