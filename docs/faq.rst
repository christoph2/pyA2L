
Frequently Asked Questions
==========================


Where to start?
---------------

*a2ldb* uses a `sqlite3 <http://www.sqlite3.org/>`_ database to store your A2L files to make the contained information easily accessible for your project work. You may start with the command-line script *a2ldb-imex*. There are two use-cases:

    - Read an A2L file and store it to an A2LDB (import). Use the *-i* option in this case. Optionally you may want to specify an encoding (s. next question) with the *-E* option, like ascii, latin-1, utf-8, ...

    .. code-block:: shell

        » a2ldb-imex -i XCPlite-0002E248-5555.A2L -E latin-1


    - Read an A2lDB file and write A2L data (export).

    .. code-block:: shell

        » a2ldb-imex -e XCPlite-0002E248-5555   # A2L data gets written to standard output.

File extensions can be ommited, then automatic addition happens: .a2l (while importing), .a2ldb (export). Note: Depending of your operating system, A2L and a2l may be different (Unix-like OSes)!
There's also a *-h*, resp. *--help* option, giving you some more details.



While importing my A2L file I'm getting strange Unicode decode errors, what can I do?
-------------------------------------------------------------------------------------

By default *pya2ldb* does its best to guess the encoding of your A2L file (by means of `chardet <https:github.com/chardet/chardet>`_,
but this may not work in any case. Then you need to specify an encoding:

.. code-block:: python

    from pya2l import DB

    db = DB()
    session = db.import_a2l("", encoding = "latin-1")

Note: There are also two command-line utilities to play around with, *file* and *chardetect*.

In action:

.. code-block:: shell

   ~ » file examples/tst.a2l
   examples/tst.a2l: UTF-8 Unicode (with BOM) text

   ~ » chardetect examples/tst.a2l
   examples/tst.a2l: UTF-8-SIG with confidence 1.0

   ~ » file XCPlite-0002E248-5555.A2L
   XCPlite-0002E248-5555.A2L: ASCII text, with very long lines

   ~ » chardetect XCPlite-0002E248-5555.A2L
   XCPlite-0002E248-5555.A2L: ascii with confidence 1.0


My A2L file includes tons of files, which in turn include other files. Do I have to copy all of them to my current working directory?
-------------------------------------------------------------------------------------------------------------------------------------

No. There's a environment variable called *ASAP_INCLUDE*, which -- if present, is used to search for */INCLUDE* files. Conventions of your operating system hold. Just like *C*/*C++* *INCLUDE* or good old *PATH*.


Any missing questions and answers?
----------------------------------

There's a `discussion <https://github.com/christoph2/pyA2l/discussions/33/>`_ on *Github*, feel free to ask, post, whatsoever!
