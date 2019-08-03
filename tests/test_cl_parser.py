#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# halive test suite
# Copyright © 2019, gnc.
# See /LICENSE for licensing information.


import halive
from  halive.cl_parser import parse_args


def test_parse_args_one_file(files=None):
    # Test single file as input
    if files is None:
        args = parse_args(['tests/data/urls.txt'])
    else:
        args = parse_args(files)
    assert args.inputfiles
    urls = []
    for f in args.inputfiles:
        lines = f.read().splitlines() 
        print(lines)
        urls.append(lines)
    urls = [n for l in urls for n in l]


def test_parse_args_two_files(files=None):
    # Test multiple files as input
    if args is None:
        args = parse_args(['tests/data/urls.txt','tests/data/urls2.txt'])
        assert len(args.inputfiles) == 2
    else:
        args = parse_args(files)
    urls = []
    for f in args.inputfiles:
        lines = f.read().splitlines() 
        print(lines)
        urls.append(lines)
    urls = [n for l in urls for n in l]
    



def test_import():
    """Test imports."""
    halive
