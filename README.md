text-plistlib
=============

A library that parses text plists from OpenStep and GNUstep as well as `.strings` files. Has a [plistlib](https://docs.python.org/3/library/plistlib.html)-style API.

Uses a Packrat parser from [tatsu](https://github.com/neogeny/TatSu), because I am too lazy to manually write a recursive descent thing.

Format
------

Text plists are [Property lists](https://en.wikipedia.org/wiki/Property_list) written in a
human-readable, textual form. They roamed the Earth in the times of OpenStep, and is
generally better for humans than the new XML format. This form, `NSPropertyListOpenStepFormat`, only supports strings, hexdata, arrays, and dictionaries.

The GNUstep project created an extension based on the old ASCII format called `NSPropertyListGNUstepFormat`. This format adds support for integers, floats, and dates, making it as expressive as the XML and binary formats. 

The format of textual plists are quite easy to grasp:
```plist
{
    /* Strings can be unquoted, or quoted for C-style escapes */
    "loremIpsum" = "A story about the good, \n the bad \u0000, and the ugly\x2E";
    foo = bar;
    hexdata = <deadbeef>;
    int = <*I3>;
    date = <*D2006-01-02 15:04:05 -0700>;

    // collection objects
    array = (1, 2, 3);
    object = {
        a = (1, 2, 3);
        d = ();
        e = {};
        f = <>;
    };
}
```

### `.strings` files
`.strings` files are similar to OpenStep plist dictionaries, except that the braces are omitted. By convention all values are strings, and the `= value` part can be omitted for a null or empty value.

Extensions
----------

This library accepts the following extensions to textual plists:
* Custom encoding: historically, plists may be written in a wide variety of encodings. We default to UTF-8, but this is configurable.
* Trailing commas for arrays: everyone loves trailing commas. Seems to be in GNUstep and Apple.
* Values in collections are nullable. This means that all dictionaries can use the `.strings` extension of `key;` and null elements of arrays can be denoted by commas. In Python they translate to `None`.
  * On a second thought, it does make more sense to use something like `<*N>` instead of the JavaScript-like handling of array gaps.
* UID. Unsigned values of the `plistlib.UID` classes are serialized in the dialect as `<*U12345>`. In other dialects, they are encoded as `{ "CF$UID" = <*I12345> }`.
* The top level of dictionary is assumed as in `.strings` files, no matter how complex the inner data structures are. This makes for better config files.

The generation of these extension elements can be turned off by a dialect control.

License
-------
MIT/Expat license or Python Software Foundation License. 

See also
--------
* [go-plist](https://github.com/DHowett/go-plist)


Useful commands 
-----

* python3 -m text_plistlib.impl ./tests/oneval.plist 
