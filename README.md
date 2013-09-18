# What

`tiddlywebplugins.fastly` is a [TiddlyWeb](http://tiddlyweb.com/)
plugin that works with the [Fastly](http://fastly.com) dynamic CDN to
effectively cache single
[recipes](http://tiddlyweb.tiddlyspace.com/recipe),
[bags](http://tiddlyweb.tiddlyspace.com/bag), [tiddlers](http://tiddlyweb.tiddlyspace.comtiddler) and collections thereof.

See [the design notes](DESIGNNOTES.md) for background info.

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
to use this plugin as follows (_note_: The first step is not yet true
as the plugin has not been released to PyPI yet, please clone the repo
and install from there):

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

# Caveats

At this time the plugin is not fully complete:

* Authenticated scenarios are not handled.
* URIs which are within the standard TiddlyWeb API are not purged.

These will be fixed.
