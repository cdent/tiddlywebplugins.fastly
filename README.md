
# Introduction

`tiddlywepblugins.fastly` will provide the necessary tools to run a
[TiddlyWeb](http://tiddlyweb.com/) instance behind
[Fastly's](http://fastly.com) dynamic CDN. This is not straightforward
because of two things:

* Fastly uses [Varnish](https://www.varnish-cache.org) which by
  default ignores `Cache-Control: no-cache` headers in the sense
  that it does not do validation of conditional requests back to
  the origin server. Instead it expects that any dynamic content
  will be purged from the cache.
* Just about everything pushed out over HTTP by TiddlyWeb has
  `Cache-Control: no-cache` set, as is expected for the user content
  driven wiki-like thing that TiddlyWeb is: We need browsers to
  validate content.

## Purging Hooks

Therefore this plugin needs to accomplish one primary thing:

* Send purges to the Fastly service when content is `PUT`. This is
  straightforward for single entities with Store HOOKS.

It is less straightforward with entity collections, especially
tiddlers produced by a recipe. Consider:

* If a single tiddler in a bag changes, any cache of the tiddlers
  collection in that bag needs to be invalidated. We easily know the
  bag involved so have an easy to generate key for the collection.
  That key can be purged.
* If, however, we want to cache the tiddlers produced by recipes,
  we don't have any easy way of knowing which of several recipes any
  singly changed tiddler might be a part of. What do we purge?

[Surrogate Keys](http://www.fastly.com/blog/surrogate-keys-part-1) to
the rescue. Any entity in the Fastly cache can be given one or more
surrogate keys via a `Surrogate-Key` header. These point into a data
structure which has as its value a container of all those resources
which use that key. With that it is possible to ask to purge a key
resulting in many resources being purged.

## Middleware

Therefore this plugin needs to accomplish a secondary thing:

* Via middlware, attach appropriate `Surrogate-Key` values to outgoing
  resources.

For example, a collection of tiddlers produced by a recipe should go
out with surrogate key values for all the bags in the recipe. Thus
when any tiddler changes, since we always know its bag, we can purge
everything (including the aforementioned recipe's tiddlers) that is
associated with the bag.

Unfortunately this still leaves search results as not very cacheable
and any tiddler change will need to purge all search related entities.

## Stats, Perhaps

A third thing the plugin might do is retrieve and present stats
from the Fastly API through a `twanager` command.

## Dealing with Auth

Finally, all of the above ignores authN and authZ. If we want to deal
with protected resources anywhere on the service we will have users
that log in and those users will then (most likely) have cookies. As
soon as Cookie shows up in the headers, the varnish cache will alway
pass. If on the other hand a user makes a request with basic
authentication it will work and the result will be cached. However
this cached result will then be available for anyone.

There are a variety of ways around this but some experimentation is
required. For now, some references:

* [Caching, even when cookies are preset](https://www.varnish-cache.org/trac/wiki/VCLExampleCacheCookies), including hashing the cookie and indicating certain paths that remove cookies from requests.
* [Caching logged in users](https://www.varnish-cache.org/trac/wiki/VCLExampleCachingLoggedInUsers)
* [Some ideas from Drupal](http://joshwaihi.com/content/authenticated-page-caching-varnish-drupal)

The main thrust is that we want to allow some resources to be cached
but when gettings things out of the cache confirm the current request
is allowed before releasing it. Checking that is the special magic.

By far the simplest options are:

* Add the `tiddlyweb_user` cookie to the hash.
* Always pass when the Authorization header is present in requests.
* Remove cookies from known always public paths.

This means that we end up with per-user caches for most URIs but may
be a valid second step (the first step is getting the purging
working).

# Implementation

[fastly-py](https://github.com/fastly/fastly-py) provides a Python
based interface to the Fastly API. We need to know a service id and an
API key. We can put these in `tiddlywebconfig.py`.

We then need two methods which describe the association of the current
URI with a set of keys and, similarly but not quite the same, the
entity currently being written. These answer the questions:

* What surrogate keys go out with this response?
* What keys do I purge with this (`PUT`) request?

The first is used in the middleware, the second in the store HOOKS.

# Discoveries, Hacks

* While experimenting it was discovered that 302 responses are cached.
  This is weird given the "temporarily" part and also got in the way
  while experimenting with auth, so for now is disabled against the test
  server with some generated VCL (edited for brevity):

```
if ( beresp.status == 302 ) {
    return(pass);
}
```
