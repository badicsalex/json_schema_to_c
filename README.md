JSON Schema to C parser generator
=================================

A tool to generate C structure declarations and a parser for a specific JSON Schema.

It generates a single, self-contained .c file, and a .h interface file, which can then be integrated into an existing project. Written with embedded use-cases in mind, and suitable for very small systems. It does not use dynamic allocations, and does not have any dependencies (neither the generator, nor the generated code).

The following schema features are supported:

* Types: `integer`, `number`, `bool`, `string`, `array`, `object`
* Min and max length for arrays and strings
* Min and max values for integers
* In-document path-like `$ref` resoltion
* Default values:
  * Full support for simple types (`int`, `bool`, `string`)
  * Implicit default value for object, where all fields have a default value
  * Implicit default value (empty array) for arrays with `minItems: 0`
* Required fields
* `additionalProperties: true`, i.e. skipping unknown fields

Important limitations:

* Strings and arrays must have a `maxLength` or `maxItems` field
* All object fields must either be required or have a default value
* All object property names must be valid C tokens
* `null` are is not supported
* More advanced `$ref` declarations (especially pointing to another file) are not supported

Example
-------

Using the [example schema](example/schema.json), and the following data:
```javascript
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

Extensions to JSON Schema
-------------------------

The following extra features are implemented:
* The `js2cDefault` field on data fields. It is similar to `default`, but it is pasted into the parser C code as-is, so it can be any C expression. It is recommended to still set `default` for interoperability, but it will be ignored by js2c. This is the only way to set non-trivial default values for arrays and objects.
* The `js2cType` and `js2cParseFunction` on `string` fields. `js2cType` specifies a forces a specific C type in the struct, and `js2cParseFunction` specifies a custom function (probably included with `c-parser-prefix`) which takes a string and outputs this custom type. Useful for something like base64 decoding a string and storing the bytes.
* The `js2cType` on `integer` fields. `js2cType` specifies a forces a specific C type in the struct (can only be `u?int(8|16|32|64)_t`). The integer will be parsed as a full 64 bit variable and truncated after range checks.
* `js2cSettings` in the schema root. Can be used to specify parameters that are normally command line parameters. Both camelCase and snake_case forms are accepted. If the same parameters are given through command line arguments, the settings in the schema take precedence.

Contribution
------------

I love to receive pull requests, especially if it's a bugifx or a nice feature, and `make check` was successful on it.

Thanks
------

The JSON tokenizer used is [JSMN](https://github.com/zserge/jsmn). It works great.

Licence
-------

This software is distributed under [MIT license](http://www.opensource.org/licenses/mit-license.php).
