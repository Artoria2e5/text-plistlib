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
`.strings` files are similar to OpenStep plists, except that the outermost dictionary can be skipped, and by convention there is only one level of key-value nesting.

Extensions
----------

This library accepts the following extensions to textual plists:
* Custom encoding: historically, plists may be written in a wide variety of encodings. We default to UTF-8, but this is configurable.
* Trailing commas for arrays: everyone loves trailing commas.

License
-------
MIT/Expat license or Python Software Foundation License. 

See also
--------
* [go-plist](https://github.com/DHowett/go-plist)
