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

import re
import sys
import asyncio
import concurrent.futures
import requests
from halive.cl_parser import parse_args


def show_banner():
    """
    Shows the banner of Halive
    """
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
    """
    This function takes as input the list of files containing the hostnames
    and normalizes the format of the hostnames in order to be able to perform
    valid HTTP/HTTPS requests.

    Args:
    inputfiles -- list of inputfiles

    Returns:
    urls       -- list of normalized URLs which can be queries
    """
    urls = []
    scheme_rgx = re.compile(r'^https?://')
    for ifile in inputfiles:
        urls.append(ifile.read().splitlines())
    urls = set([n for l in urls for n in l])
    urls = list(filter(None, urls))
    for i in range(len(urls)):
        if not scheme_rgx.match(urls[i]):
            urls[i] = 'http://' + urls[i]
    return urls


async def download(urls, num_workers, show_only_success, outputfile, only_urls):
    """
    This function is responsible for performing the asynchrounous requests to
    the list of URLs.

    Args:
    urls              -- list of URLs to query
    num_workers       -- this is an integer determining the degree of concurrency
    show_only_success -- this is a boolean indicating if only the success
                         responses (not 4XX) should be shown 
    outputfile        -- the name of the output file where we want to save the
                         list of valid URLs
    only_urls         -- this is a boolean indicating if we want to ouput only
                         URLs without any response code
                         (this happens when it is set to True)
    """
    outputfiledata = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
        loop = asyncio.get_event_loop()
        futures = []
        response = []
        for url in urls:
            futures.append(loop.run_in_executor(executor, make_request, url))

        for response in await asyncio.gather(*futures):
            outputfiledata.append(response)
            if not response['status'] == -1:
                if show_only_success:
                    if response['status'] < 400 or response['status'] >= 500:
                        if only_urls:
                            print(response['url'])
                        else:
                            print(
                                '{:70.70} {}'.format(
                                    response['url'],
                                    response['status']))
                else:
                    if only_urls:
                        print(response['url'])
                    else:
                        print(
                            '{:70.70} {}'.format(
                                response['url'],
                                response['status']))
        if outputfile:
            for host in outputfiledata:
                if not host['status'] == -1:
                    if only_urls:
                        outputfile.write('{}\n'.format(host['url']))
                    else:
                        outputfile.write(
                            '{},{}\n'.format(
                                host['url'], host['status']))


def make_request(url):
    """
    This is an internal utility function which is responsible for performing 
    te request, it saves the results in a dictionary.
    """
    response = {}
    try:
        resp = requests.head(url, allow_redirects=False, timeout=1)
        response['url'] = resp.url
        response['status'] = resp.status_code
    except BaseException:
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
        print('{:70.70} {}'.format("URL", "Response"))

    loop = asyncio.get_event_loop()
    loop.run_until_complete(download(urls,
                                     args.concurrency,
                                     args.only_success,
                                     args.outputfile,
                                     args.only_urls))
