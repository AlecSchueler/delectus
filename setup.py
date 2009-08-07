#!/usr/bin/env
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(
    name="delectus",
    version="0.9α",
    author="Alec Schuele ",
    author_email="johannalecschueler@googlemail.com",
    url="http://github.com/AlecSchueler/delectus",
    license="LGPL v2",
    data_files=[('man/man1',['man/delectus.1'])],
    scripts=["delectus"],
    classifiers=[
        'Development Status :: 3 -Alpha',
        'Enviroment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        ]
)
