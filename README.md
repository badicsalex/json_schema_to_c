# JSON Schema to C parser generator

A tool to generate C structure declarations and a parser for a specific JSON Schema.

It generates a single, self-contained .c file, and a .h interface file, which can then be integrated into an existing project. Written with embedded use-cases in mind, and suitable for very small systems. It does not use dynamic allocations, and does not have any dependencies (neither the generator, nor the generated code).

The following schema features are supported:

* Types: `integer`, `number`, `bool`, `string`, `array`, `object`
* Min and max length for arrays and strings
* Min and max values for integers
* In-document path-like `$ref` resolution
* Default values:
  * Full support for simple types (`int`, `bool`, `string`)
  * Implicit default value for object, where all fields have a default value
  * Implicit default value (empty array) for arrays with `minItems: 0`
* Required fields
* `additionalProperties: true`, i.e. skipping unknown fields
* `const` is supported for strings and integers
* `anyOf` is supported
* `oneOf` is kinda supported (it's interpreted as `anyOf`)

Important limitations:

* Strings and arrays must have a `maxLength` or `maxItems` field
* All object fields must either be required or have a default value
* All object property names must be valid C tokens
* `null` is not supported
* Tuples (a specific form of array declarations) are not supported
* More advanced `$ref` declarations (especially pointing to another file) are not supported
* `$id` is required on the root and is used to define the prefix of the generated types name
* an invalid schema can make json_schema_to_c crash

## Example

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

## Usage

Run the `json_schema_to_c.py --help` command, and go from there. Also see the example directory. You can test it by running `make run`. For more advanced functionality, check tests.

### Extensions to JSON Schema

The following extra features are implemented:
* The `js2cDefault` field on data fields. It is similar to `default`, but it is pasted into the parser C code as-is, so it can be any C expression. It is recommended to still set `default` for interoperability, but it will be ignored by js2c. This is the only way to set non-trivial default values for arrays and objects.
* The `js2cType` and `js2cParseFunction` on `string` fields. `js2cType` specifies and forces a specific C type in the struct, and `js2cParseFunction` specifies a custom function (probably included with `c-parser-prefix`) which takes a string and outputs this custom type. Useful for something like base64 decoding a string and storing the bytes.
* The `js2cType`, `js2cParseFunction` and `js2cParseType` on `integer` fields. `js2cType` specifies and forces a specific C type in the struct (can only be `u?int(8|16|32|64)_t` if no `js2cParseFunction` is defined). `js2cParseFunction`, if defined, specifies a custom function (probably included with `c-parser-prefix`) which takes an integer having the `js2cParseType` type (defaulting to `int64_t`) and outputs the custom `js2cType` type.
* `js2cSettings` in the schema root. Can be used to specify parameters that are normally command line parameters. Both camelCase and snake_case forms are accepted. If the same parameters are given through command line arguments, the settings in the schema take precedence.
* The `js2cStorageFormat` field tells json-schema-to-c to generate a parser for the attached value that wills store the parsed data in an alternate format:
  * When set to `void`, the data will simply be dropped.
  * When set to `raw`, the generated parser will only save a reference (index + size) into the raw JSON input.

### Custom parser functions

In the JSON schema, `js2cType` can be used to specify a custom C type, and `js2cParseFunction` can be used to specify a custom parsing function.

The custom parsing function can then be defined in a file and passed via the `--c-prefix-file <file>` argument.

The parsing function must follow this signature/API:

```c
// js2c-start some_include
#include <stuff.h>
// js2c-end

// js2c-start parse_xxx (needs: some_include)
static bool parse_xxx(const char *current_string, int current_string_len, xxx *out, const char **error) {
    // do stuff

    if (some_error) {
        *error = "something bad occured";
        return true; // return true on error
    }

    *out = parsed_stuff;
    return false; // return false on success
}
// js2c-end
```

The `js2c-start` amd `js2c-end` tags are not required, but they are useful because they tell JS2C to prune this function if unused (the section name should be the same as the function name defined by `js2cParseFunction`).
You can also define code sections with the name you want, and then reference them by the `(needs: ..., ..., ...)` syntax to create a dependency graph.

### Custom logger

In the prefix file passed via the `--c-prefix-file <file>` argument, you can define a logger.

Example:

```c
#include <stdio.h>

#define LOG_ERROR(token_position, ...) printf(__VA_ARGS__);
```

## Codegen logic

### Naming

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

* `example_t`
* `example_foo_t`
* `example_foo_bar_t`
* `baz_t`

### Handling anyOf/oneOf

The parsing of anyOf/oneOf is done by trying successively each option until one can be parsed without error.
As a side effect, it can print errors with a valid JSON (this issue must be fixed in the future).

The generated `union` will be wrapped inside a `struct` also containing a `type` field to differentiate between each option.

Each `union` option will be named `option_{x}` with type `..._option_{x}_t`.
To have a nicer naming, add an `$id` in the anyOf/oneOf object and in its child objects.


## Contribution

I love to receive pull requests, especially if it's a bugifx or a nice feature, and `make check` was successful on it.

## Thanks

The JSON tokenizer used is [JSMN](https://github.com/zserge/jsmn). It works great.

## Licence

This software is distributed under [MIT license](http://www.opensource.org/licenses/mit-license.php).
