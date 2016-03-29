==========
 Indicium
==========

.. image:: https://readthedocs.org/projects/indicium/badge/?version=latest
   :target: https://indicium.readthedocs.org/en/latest
   :alt: Documentation Status

.. image:: https://img.shields.io/travis/aperezdc/indicium.svg?style=flat
   :target: https://travis-ci.org/aperezdc/indicium
   :alt: Build Status

.. image:: https://img.shields.io/coveralls/aperezdc/indicium/master.svg?style=flat
   :target: https://coveralls.io/r/aperezdc/indicium?branch=master
   :alt: Code Coverage

Pythonic, unified API to multiple key-value stores.

This base package includes:

* Abstract definition of the ``Store`` API, which all storage systems follow.
* In-memory `caching of data of values`__ from a store using LRU eviction.
* In-memory `transient storage`__ backed by Python dictionaries.
* Simple `filesystem-based storage`__ using directories and plain files.
* Adaptors for `transparent (de)serialization`__ of stored values.

__ http://indicium.readthedocs.org/en/latest/apiref.html#indicium.cache.LRUCache
__ http://indicium.readthedocs.org/en/latest/apiref.html#indicium.base.DictStore
__ http://indicium.readthedocs.org/en/latest/apiref.html#indicium.fs.FSStore
__ http://indicium.readthedocs.org/en/latest/apiref.html#indicium.base.Serializer

Support for additional storage system is by packages distributed separately:

* `indicium-git <https://github.com/aperezdc/indicium-git>`_.
* `indicium-ldap <https://github.com/aperezdc/indicium-ldap>`_.
* ``indicium-leveldb`` (planned, not yet available).
* ``indicium-memcache`` (planned, not yet available).


Usage
=====

Create a ``Store`` which saves content on-disk, using JSON for serialization,
and store somwthing that resembles an user account:

.. code-block:: python

    from indicium.base import Serializer
    import json

    filestore = Serializer(FSStore("./data", extension=".json"), pickle)
    filestore.put("/user/jdoe", { "id": "jdoe", "name": "John Doe",
            "email": "j@doe.org", "password": "supersekrit" })
    account = filestore.get("/user/jdoe")
    assert account["email"] == "j@doe.org"

The ``./data/user/jdoe.json`` file will contain the account data in JSON
format.

The following adds an in-memory cache to the above store, which holds up to
100 elements, to speed up access to data:

.. code-block:: python

    from indicium.cache import LRUCache

    cachedstore = LRUCache(filestore, size=100)
    account = cachedstore.get("/user/jdoe")
    assert account["email"] == "j@doe.org"

Once you have a collection of objects, you can run use queries to retrieve all
the elements whose keys match a certain pattern. For example, this obtains the
user accounts with an identifier starting with the letter ``j`` from the store
above:

.. code-block:: python

    for key, account cachedstore.query("/user/j*"):
        print(account["id"], account["name"])


Installation
============

All stable releases are uploaded to `PyPI <https://pypi.python.org>`_, so you
can install them and upgrade using ``pip``::

    pip install indicium

Alternatively, you can install the latest development code —at your own risk—
directly from the Git repository::

    pip install git://github.com/aperezdc/indicium


Development
===========

If you want to contribute, please use the usual GitHub workflow:

1. Clone the repository.
2. Hack on your clone.
3. Send a pull request for review.

If you do not have programming skills, you can still contribute by `reporting
issues <https://github.com/aperezdc/indicium/issues>`__ that you may
encounter. Contributions to the documentation are very welcome, too!


Inspiration
===========

* `Park <https://github.com/litl/park/>`_
* `datastore <https://github.com/datastore/datastore>`_ (unfortunately, it
  does not support Python 3.x).
