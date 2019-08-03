# -*- encoding: utf-8 -*-
# halive v0.1.0
# An http/s prober, to check which URLs are alive.
# Copyright © 2019, gnc.
# See /LICENSE for licensing information.

"""
Main module for halive.

:Copyright: © 2019, gnc.
:License: BSD (see /LICENSE).
"""

__all__ = ()

import re
import sys
import asyncio
import requests
import concurrent.futures
from halive.cl_parser import parse_args



def show_banner():
    print("""(H)ALIVE!

A super fast asynchronous http and https prober, to check who is (h)alive.
Developed by gnc
    """)


def get_urls(inputfiles):
    urls = []
    scheme_rgx = re.compile(r'^https?://')
    for f in inputfiles:
        lines = f.read().splitlines() 
        urls.append(lines)
    urls = set([n for l in urls for n in l])
    urls = list(filter(None, urls))
    urls = ["http://"+l for l in urls if not scheme_rgx.match(l)]
    return urls


async def download(urls,num_workers,show_only_success,outputfile):
    outputfiledata = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        loop = asyncio.get_event_loop()
        futures = []
        response = []
        for u in urls:
            futures.append(loop.run_in_executor(executor, make_request,u))

        for response in await asyncio.gather(*futures):
            outputfiledata.append(response)
            if not response['status'] == -1:
                if show_only_success:
                    if response['status'] < 400 or response['status'] >= 500:
                        print('{:70.70} {}'.format(response['url'],response['status']))
                else:
                    print('{:70.70} {}'.format(response['url'],response['status']))
        if outputfile:
            for d in outputfiledata:
                if not d['status'] == -1:
                    outputfile.write('{},{}\n'.format(d['url'],d['status']))


def make_request(url, timeout=3):
    response = {}
    try:
        r = requests.get(url)
        response['url'] = r.url
        response['status'] = r.status_code
    except:
        response['url'] = url
        response['status'] = -1


    return response


def main():
    """Main routine of halive."""
    show_banner()
    args = parse_args(sys.argv[1:])
    urls = get_urls(args.inputfiles)
    print('{:70.70} {}'.format("URL","Response"))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download(urls,args.concurrency,args.onlysuccess,args.outputfile))


