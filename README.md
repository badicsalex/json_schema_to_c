JSON Schema to C parser generator
=================================

A tool to generate C structure declarations and a parser for a specific JSON Schema.

It generates a single, self-contained .c file, and a .h interface file, which can then be integrated into an existing project. Written with embedded use-cases in mind, and suitable for very small systems. It does not use dynamic allocations, and does not have any dependencies (neither the generator, nor the generated code).

The following schema features are supported:

* Types: `integer`, `number`, `bool`, `string`, `array`, `object`
* Min and max length for arrays and strings
* Min and max values for integers
* Path-like `$ref` resolution, in-document or into another local schema file
* Default values:
  * Full support for simple types (`int`, `bool`, `string`)
  * Implicit default value for object, where all fields have a default value
  * Implicit default value (empty array) for arrays with `minItems: 0`
* Required fields
* `additionalProperties: true`, i.e. skipping unknown fields
* `const` is supported for strings and integers
* `anyOf`, generated as a tagged union

Important limitations:

* Strings and arrays must have a `maxLength` or `maxItems` field
* All object fields must either be required or have a default value
* All object property names must be valid C tokens
* `null` is not supported
* Tuples (a specific form of array declarations) are not supported
* `$ref` must be path-like (not `$id`-based) and local; remote (`http(s)://`) references are not supported
* `oneOf` is not supported
* `$id` is required on the root and is used to define the prefix of the generated types name
* an invalid schema can make json_schema_to_c crash

Example
-------

Using the [example schema](example/schema.json), and the following data:
```json
{
    "fruits": ["apple", "pear", "strawberry"],
    "vegetables": [
        {
            "name": "carrot",
            "is_good": false
        },
        {
            "name": "potato",
            "is_good": true
        }
    ],
    "multidimensionals":[
        [
            [1,2,3,4],
            [5,6,7,8]
        ],
        [
            [11,12,13,14],
            [25,26,27,28]
        ]
    ]
}
```

You can access the fields like this:
```c
    example_schema_t root = {};
    json_parse_example_schema(json_string, &root);

    printf("Name of the second vegetable: ", root.vegetables.items[1].name);
    if (root.vegetables.items[1].is_good)
      printf("It's pretty good too");
    printf("The number of fruits: %lu\n", root.fruits.n);
    printf("Also, arrays are well-supported: %ld", root.multidimensionals.items[1].items[0].items[1]);
```

Usage
-----

Run the `json_schema_to_c.py --help` command, and go from there. Also see the example directory. You can test it by running `make run`. For more advanced functionality, check tests.

Naming
------

Types name are built by recursively ascending the schema graph and appending the name of the parent until an `$id` field is found.

Example with the following schema:

```json
{
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "$id": "example",
    "type": "object",
    "additionalProperties": false,
    "required": ["foo", "baz"],
    "properties": {
        "foo": {
            "type": "object",
            "additionalProperties": false,
            "required": ["bar", "baz"],
            "properties": {
                "bar": {
                    "type": "string",
                    "maxLength": 16
                },
                "baz": {
                    "$id": "baz",
                    "type": "string",
                    "maxLength": 16
                }
            }
        }
    }
}
```

It will generate the following types:

* `example_t_s`
* `example_foo_t_s`
* `example_foo_bar_t`
* `baz_t`

References
----------

A `$ref` may stay within the current file, as a path-like fragment:

```json
{ "$ref": "#/$defs/Address" }
```

or point into another schema file, as a relative path or a `file:` URI followed by such a fragment:

```json
{ "$ref": "common.json#/$defs/Address" }
```

Cross-file paths are resolved relative to the referring schema. As a safety measure, a file can only
be referenced if it lives under the schema's own directory, or under a path passed on the command
line with `--authorized-paths`. Anything else is rejected, and circular references are detected.

Extensions to JSON Schema
-------------------------

The following extra features are implemented:
* The `js2cDefault` field on data fields. It is similar to `default`, but it is pasted into the parser C code as-is, so it can be any C expression. It is recommended to still set `default` for interoperability, but it will be ignored by js2c. This is the only way to set non-trivial default values for arrays and objects.
* The `js2cType` field, which controls how a value is stored:
  * On `string` and `enum` fields it forces a specific C type in the struct. Pair it with `js2cParseFunction`, a custom function (probably included via `--c-prefix-file`) which takes the matched string and outputs this custom type. Useful for something like base64 decoding a string and storing the bytes.
  * On `integer` fields it forces a specific C type (can only be `u?int(8|16|32|64)_t`). The integer will be parsed as a full 64 bit variable and truncated after range checks.
  * The special values `void` and `raw` store a value differently instead of naming a C type. `void` validates the value then drops it (no field is generated); `raw` stores only a `{ index, length }` reference into the input text (type `<root>_json_ref_t`) instead of parsing it. Because a `void`/`raw` value is still tokenized, a composite one needs token headroom (`--allow-additional-properties`).
* `js2cSettings` in the schema root. Can be used to specify parameters that are normally command line parameters. Both camelCase and snake_case forms are accepted. If the same parameters are given through command line arguments, the settings in the schema take precedence.

Custom parser functions
-----------------------

`js2cType` sets a custom C type for a `string` or `enum` field, and `js2cParseFunction` names a
function that converts the matched string into that type. Define it in a file passed via
`--c-prefix-file <file>`, with this signature:

```c
static bool parse_xxx(const char *current_string, int current_string_len, xxx *out, const char **error) {
    // do stuff

    if (some_error) {
        *error = "something bad occurred";
        return true; // return true on error
    }

    *out = parsed_stuff;
    return false; // return false on success
}
```

Custom logger
-------------

Define `LOG_ERROR` in the file passed via `--c-prefix-file <file>` to capture parse errors. Its
first argument is the byte offset of the offending token; the rest are printf-style:

```c
#include <stdio.h>

#define LOG_ERROR(token_position, ...) printf(__VA_ARGS__)
```

Errors from an `anyOf` option that fails to match are suppressed, since trying each option is
expected to fail until one fits.

Contribution
------------

I love to receive pull requests, especially if it's a bugifx or a nice feature, and `make check` was successful on it.

Thanks
------

The JSON tokenizer used is [JSMN](https://github.com/zserge/jsmn). It works great.

Licence
-------

This software is distributed under [MIT license](http://www.opensource.org/licenses/mit-license.php).
