# What

`tiddlywebplugins.fastly` is a [TiddlyWeb](http://tiddlyweb.com/)
plugin that works with the [Fastly](http://fastly.com) dynamic CDN to
effectively cache single
[recipes](http://tiddlyweb.tiddlyspace.com/recipe),
[bags](http://tiddlyweb.tiddlyspace.com/bag), [tiddlers](http://tiddlyweb.tiddlyspace.comtiddler) and collections thereof.

See [the design notes](DESIGNNOTES.md) for background info.

This plugin is an experiment to explore what hurdles need to be
overcome to get TiddlyWeb working in the Fastly context and generally
to explore the Fastly ecosystem.

# Why

For fast.

Depending on the usage profile (the ratio of reads to writes) of the
TiddlyWeb service the number of hits against the backend will drop
_dramatically_ and the effective latency for the end user will be
significantly improved. This means the backend can be quite
lightweight while still providing zoom to the users.

# How 

An existing TiddlyWeb
[instance](http://tiddlyweb.tiddlyspace.com/instance) can be updated
to use this plugin as follows (*note*: The second step is not yet true
as the plugin has not been released to PyPI yet, please clone this
repo and install from there):

* Install [fastly-py](https://github.com/fastly/fastly-py).
* Install the plugin: `pip install -U tiddlywebplugins.fastly`.
* Edit
  [tiddlywebconfig.py](http://tiddlyweb.tiddlyspace.com/tiddlywebconfig.py)
  to add `tiddlywebplugins.fastly` to
  [system_plugins](http://tiddlyweb.tiddlyspace.com/system_plugins)
  and
  [twanager_plugins](http://tiddlyweb.tiddlyspace.com/twanager_plugins) and
  add keys and values for `fastly.server_id` and `fastly.api_key`
  (found in the analytics and configuration app at
  <http://fastly.com/>:


        'system_plugins': ['tiddlywebwiki', 'tiddlywebwplugins.fastly'],
        'twanager_plugins': ['tiddlywebwiki', 'tiddlywebwplugins.fastly'],
        'fastly.server_id': 'your_server_id',
        'fastly.api_key': 'your_api_key'

* Restart the instance.

Once installed three new pieces of functionality will be present:

* There are several new
  [twanager](http://tiddlyweb.tiddlyspace.com/twanager) commands for
  inspecting and manipulating the Fastly configuration and manually
  purging URLs and keys. Run `twanager` to see them listed.
* Outgoing responses to `GET` requests are augmented with appropriate
  `Surrogate-Key` headers.
* When entities are written to the store (via `store.put`) a `HOOK`
  sends a `purge_key` request to the Fastly API.

# Non-Caching URIs

By default Fastly will cache anything you give it. If you need to
avoid this you can write custom VCL for various rules that will cause
a `pass`. One convenient catch-all is to `pass` on anything which has
not provided a `Surrogate-Key` header:

```
    if ( !beresp.http.surrogate-key ) { 
        set beresp.ttl = 0s;
        set beresp.grace = 0s;
        return(pass);
    }
```

This, however, is a sledgehammer. It is generally better to let most
URIs cache and configure `pass` on specific URIs.

# Custom URI Handlers

The code for surrogate keys can be extended to generate keys for
custom routes provided by plugins. For example to generate keys for
the friendlywiki route provided by
[tiddlywebwiki](https://pypi.python.org/pypi/tiddlywebwiki) a plugin
with the following code could be used:

```
from tiddlywebplugins.fastly.surrogates import recipe_tiddlers_uri_keys

def init(config):
    def friendly_keys(environ, start_response):
        return recipe_tiddlers_uri_keys(environ)

    config['fastly.selector'].add('/{recipe_name:segment}', GET=friendly_keys)
```

This is a hack to utilize the WSGI dispatching routines in
[Selector](https://pypi.python.org/pypi/selector) to call a function
which returns a list of keys. The function should return whatever keys
make sense for the given route. In this example since the route
returns a collection of tiddlers generated by a recipe the
`recipe_tiddlers_uri_keys` method is used.

# Caveats

At this time the plugin is not fully complete: Authenticated scenarios
are not handled. See the [design notes](DESIGNNOTES.md) for comments on
authentication.

If you need a quick fix for dealing with Auth you can add cookies to
the request hash. This will create a per user cache. See:

* [How do I change the hash
  key](https://fastly.zendesk.com/entries/23686118-How-do-I-change-what-the-cache-key-is-defined-as-)
* [Caching even when cookies are
  present](https://www.varnish-cache.org/trac/wiki/VCLExampleCacheCookies#Addingthecookietothehash)
* [Issue #2](https://github.com/cdent/tiddlywebplugins.fastly/issues/2)

