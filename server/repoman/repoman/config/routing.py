"""Routes configuration

The more specific and detailed routes should be defined first so they
may take precedent over the more generic routes. For more information
refer to the routes manual at http://routes.groovie.org/docs/
"""
from routes import Mapper
import logging

log = logging.getLogger(__name__)

def make_map(config):
    """Create, configure and return the routes Mapper"""
    map = Mapper(directory=config['pylons.paths']['controllers'],
                 always_scan=config['debug'])
    map.minimization = False
    map.explicit = False

    # The ErrorController route (handles 404/500 error pages); it should
    # likely stay at the top, ensuring it can always be resolved
    map.connect('/error/{action}', controller='error')
    map.connect('/error/{action}/{id}', controller='error')

    # CUSTOM ROUTES HERE
    ####################

    # TODO:mvliet: name the routes

    # Whoami
    map.connect(None, '/api/whoami', controller='api/whoami',
                action='whoami',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/env', controller='api/whoami',
                action='env',
                conditions=dict(method=['GET']))

    # User Routes
    map.connect("users", '/api/users', controller='api/users',
                action='list_all',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/users', controller='api/users',
                action='new_user',
                conditions=dict(method=['POST']))

    map.connect('user', '/api/users/:(user)', controller='api/users',
                action='modify_user',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/users/:(user)', controller='api/users',
                action='delete_user',
                conditions=dict(method=['DELETE']))

    map.connect(None, '/api/users/:(user)', controller='api/users',
                action='show',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/users/:(user)/images', controller='api/users',
                action='list_images',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/users/:(user)/groups', controller='api/users',
                action='list_groups',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/users/:(user)/permissions', controller='api/users',
                action='list_permissions',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/users/:(user)/shared', controller='api/users',
                action='get_shared_with_me',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/users/:(user)/sharing', controller='api/users',
                action='list_my_shared_images',
                conditions=dict(method=['GET']))

    # Group Routes
    map.connect("groups", '/api/groups', controller='api/groups',
                action='list_all',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/groups', controller='api/groups',
                action='new_group',
                conditions=dict(method=['POST']))

    map.connect("group", '/api/groups/:(group)', controller='api/groups',
                action='show',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/groups/:(group)', controller='api/groups',
                action='delete',
                conditions=dict(method=['DELETE']))

    map.connect(None, '/api/groups/:(group)', controller='api/groups',
                action='modify_meta',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/groups/:(group)/shared', controller='api/groups',
                action='list_shared_images',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/groups/:(group)/users', controller='api/groups',
                action='list_users',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/groups/:(group)/users/:(user)', controller='api/groups',
                action='add_user',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/groups/:(group)/users/:(user)', controller='api/groups',
                action='remove_user',
                conditions=dict(method=['DELETE']))

    map.connect(None, '/api/groups/:(group)/permissions', controller='api/groups',
                action='list_permissions',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/groups/:(group)/permissions/:(permission)',
                controller='api/groups',
                action='add_permission',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/groups/:(group)/permissions/:(permission)',
                controller='api/groups',
                action='remove_permission',
                conditions=dict(method=['DELETE']))

    # Image Routes
    map.connect(None, '/api/images/:(user)/:(image)/share/user/:(share_with)',
                controller='api/images',
                action='user_share_by_user',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/images/:(user)/:(image)/share/group/:(share_with)',
                controller='api/images',
                action='group_share_by_user',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/images/:(user)/:(image)/share/user/:(share_with)',
                controller='api/images',
                action='user_unshare_by_user',
                conditions=dict(method=['DELETE']))

    map.connect(None, '/api/images/:(user)/:(image)/share/group/:(share_with)',
                controller='api/images',
                action='group_unshare_by_user',
                conditions=dict(method=['DELETE']))

    map.connect(None, '/api/images/:(image)/share/user/:(share_with)', controller='api/images',
                action='user_share',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/images/:(image)/share/user/:(share_with)', controller='api/images',
                action='user_unshare',
                conditions=dict(method=['DELETE']))

    map.connect(None, '/api/images/:(image)/share/group/:(share_with)', controller='api/images',
                action='group_share',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/images/:(image)/share/group/:(share_with)', controller='api/images',
                action='group_unshare',
                conditions=dict(method=['DELETE']))






    map.connect('get_raw_by_user', '/api/images/raw/:(user)/:(hypervisor)/:(image)', controller='api/raw',
                action='get_raw_by_user',
                conditions=dict(method=['GET']))

    map.connect('get_raw', '/api/images/raw/:(hypervisor)/:(image)', controller='api/raw',
                action='get_raw',
                conditions=dict(method=['GET']))

    # The following 2 maps are to allow clients to test for existence of image uploaded files via
    # the HEAD HTTP request.
    map.connect('test_raw_by_user', '/api/images/raw/:(user)/:(hypervisor)/:(image)', controller='api/raw',
                action='test_raw_by_user',
                conditions=dict(method=['HEAD']))

    map.connect('test_raw', '/api/images/raw/:(hypervisor)/:(image)', controller='api/raw',
                action='test_raw',
                conditions=dict(method=['HEAD']))

    map.connect(None, '/api/images/raw/:(user)/:(hypervisor)/:(image)', controller='api/images',
                action='put_raw_by_user',
                conditions=dict(method=['PUT']))

    map.connect(None, '/api/images/raw/:(hypervisor)/:(image)', controller='api/images',
                action='put_raw',
                conditions=dict(method=['PUT']))





    map.connect('image_by_user', '/api/images/:(user)/:(image)', controller='api/images',
                action='show_meta_by_user',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/images/:(user)/:(image)', controller='api/images',
                action='modify_meta_by_user',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/images/:(user)/:(image)', controller='api/images',
                action='delete_by_user',
                conditions=dict(method=['DELETE']))

    map.connect('image', '/api/images/:(image)', controller='api/images',
                action='show_meta',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/images/:(image)', controller='api/images',
                action='modify_meta',
                conditions=dict(method=['POST']))

    map.connect(None, '/api/images/:(image)', controller='api/images',
                action='delete',
                conditions=dict(method=['DELETE']))

    map.connect('images', '/api/images', controller='api/images', action='list_all',
                conditions=dict(method=['GET']))

    map.connect(None, '/api/images', controller='api/images', action='new',
                conditions=dict(method=['POST']))

    # Actions
    map.connect(None, 'api/actions/clone/image/:(image)', controller='api/actions',
                action='clone_image',
                conditions=dict(method=['GET']))

    #######################
    # End of custom routes

    map.connect('/{controller}/{action}')
    map.connect('/{controller}/{action}/{id}')

    log.debug('Routing map created.')

    return map

