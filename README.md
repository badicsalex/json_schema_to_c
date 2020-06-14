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
* Complex default values for objects and arrays are not supported
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

Run the `json_schema_to_c.py --help` command, and go from there. Also see the example directory. You can test it by running `make run`.

Extensions to JSON Schema
-------------------------

The following extra features are implemented:
* The `js2cDefault` field on data fields. It is the same as `default`, and has higher precedence, if both are present. Mostly usable to have a 'secret' or 'internal' default value that shouldn't be exposed to UI's. Especially good for cases where you want to signify the nonexistence of a field to the C code, but don't want UIs to display 18446744073709551616 in gray.

Contribution
------------

I love to receive pull requests, especially if it's a bugifx or a nice feature, and `make check` was successful on it.

Thanks
------

The JSON tokenizer used is [JSMN](https://github.com/zserge/jsmn). It works great.

Licence
-------

This software is distributed under [MIT license](http://www.opensource.org/licenses/mit-license.php).
