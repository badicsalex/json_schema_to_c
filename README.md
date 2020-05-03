JSON Schema to C parser generator
=================================

A tool to generate C structure declarations and a parser for a specific JSON Schema.

It generates a single, self-contained .c file, and a .h interface file, which can then be integrated into an existing project. Written with embedded use-cases in mind, and suitable for very small systems. It does not use dynamic allocations, and does not have any dependencies (neither the generator, nor the generated code).

The following schema features are supported:

* Types: `integer`, `bool`, `string`, `array`, `object`
* Min and max length for arrays and strings
* Min and max values for integers
* In-document path-like `$ref` resoltion
* Default values for simple types (`int`, `bool`, `string`)
* Required fields

Important limitations:

* Strings and arrays must have a `maxLength` or `maxItems` field
* `additionalProperties` must be explicitly `false` for all objects.
* All object fields must either be required or have a default value
* Default values for objects and arrays are not supported
* All object property names must be valid C tokens
* Floats and `null` are not supported
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

Contribution
------------

I love to receive pull requests, especially if it's a bugifx or a nice feature, and `make check` was successful on it.

Thanks
------

The JSON tokenizer used is [JSMN](https://github.com/zserge/jsmn). It works great.

Licence
-------

This software is distributed under [MIT license](http://www.opensource.org/licenses/mit-license.php).
