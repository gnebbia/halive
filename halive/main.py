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
    print("""
 _   _    _    _     _____     _______
| | | |  / \  | |   |_ _\ \   / / ____|
| |_| | / _ \ | |    | | \ \ / /|  _|
|  _  |/ ___ \| |___ | |  \ V / | |___
|_| |_/_/   \_\_____|___|  \_/  |_____|


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
    for i in range(len(urls)):
        if not scheme_rgx.match(urls[i]):
            urls[i] = 'http://' + urls[i]
    return urls


async def download(urls,num_workers,show_only_success,outputfile,only_urls):
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
                        if only_urls:
                            print(response['url'])
                        else:
                            print('{:70.70} {}'.format(response['url'],response['status']))
                else:
                    if only_urls:
                        print(response['url'])
                    else:
                        print('{:70.70} {}'.format(response['url'],response['status']))
        if outputfile:
            for d in outputfiledata:
                if not d['status'] == -1:
                    if only_urls:
                        outputfile.write('{}\n'.format(d['url']))
                    else:
                        outputfile.write('{},{}\n'.format(d['url'],d['status']))


def make_request(url):
    response = {}
    try:
        r = requests.head(url, allow_redirects=False, timeout=1)
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
    if args.only_urls:
        print("URL")
    else:
        print('{:70.70} {}'.format("URL","Response"))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(download(urls,\
                                    args.concurrency,\
                                    args.only_success,\
                                    args.outputfile,\
                                    args.only_urls))


