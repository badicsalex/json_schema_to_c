JSON Schema to C parser generator
=================================

This is a proof of concept script to generate a C parser for a specific JSON Schema

Only a very small subset of JSON schema features are usable currently.

The JSON tokenizer used is [JSMN](https://github.com/zserge/jsmn). It works great.

Usage
-----

For now, please see the example directory, and run `make run`

Contribution
------------

I love to receive pull requests, especially if it's a bugifx or a nice feature, and `make check` was successful on it.

Licence
-------

This software is distributed under [MIT license](http://www.opensource.org/licenses/mit-license.php).
