#!/usr/bin/env python3
"""Creates a Safari Gold Template from a forum URL.

Install this inside _Pythonista 3_'s local script library and configure it as
an _App Extension_ accepting URLs. 

Typical workflow:

 1. Open Safari or other browsers.
 2. Use the share button to invoke the _Run Pythonista Script_ activity.
 3. Select this script.
 4. The script will get the URL and extract the page title and site name 
    create a markdown file.
 5. The script will invoke DevonThink To Go to edit the new markdown file.

"""

# Copyright (c) 2019, Sasmito Adibowo
# https://cutecoder.org
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# The views and conclusions contained in the software and documentation are those
# of the authors and should not be interpreted as representing official policies,
# either expressed or implied, of the PythonistaTools project.

from typing import NamedTuple, Optional
from datetime import datetime
from string import Template
from bs4 import BeautifulSoup
from urllib.parse import quote

import sys
import requests


class PostInfo(NamedTuple):
    thread_title: Optional[str]
    site_name: Optional[str]
    
    @classmethod
    def from_url(cls, page_url: str) -> 'PostInfo':
        title_separators = [' |', ' : ', ' - ']
        # need to configure a custom user agent
        # https://meta.m.wikimedia.org/wiki/User-Agent_policy
        result = requests.get(page_url, headers={'User-Agent': 'SafariThis/0.1'})
        contents = result.text
        soup = BeautifulSoup(contents, 'html5lib')
        if soup.title is None:       
            soup = BeautifulSoup(contents, 'html.parser')
        page_title = soup.title.string
        sep_char = None
        components = None
        for sep_candidate in title_separators:
            components = page_title.split(sep_candidate)
            if len(components) > 1:
                sep_char = sep_candidate
                break
        if sep_char is not None:
            site_name = components[-1].strip()
            thread_title = sep_char.join(components[0:-1]).strip()
        else:
            site_name = None
            thread_title = page_title.strip()
        return cls(thread_title=thread_title, site_name=site_name)


def make_safari_template(thread_url: str, post_title: str, site_name: str, current_date: str) -> str:
    subst_result = (
        f"# Safari Gold: (Summary)\n"
        f"\n> [{post_title}]({thread_url})\n\n"
        f"From: {site_name}  \n"
        f"Analysis date: {current_date}  \n"
        f"Post date: YYYY-MM-DD\n"
        f"\n## Painstorming\n\n"
        f"\n## Buys\n\n"
        f"\n## Recommendations\n\n"
        f"\n## Hidden Pains\n\n"
        f"\n## Jargons\n\n"
        f"\n## Worldviews\n\n"
    )
    return str(subst_result)


def safari_url(thread_url: str) -> (str, str):
    info = PostInfo.from_url(thread_url)
    now = datetime.now()
    analysis_date_str = now.strftime('%Y-%m-%d')
    return make_safari_template(thread_url, info.thread_title, info.site_name, analysis_date_str), info.thread_title

def main_app_extension() -> int:
    import appex
    import webbrowser
    import console
    result_cmd = None
    console.show_activity()
    last_url = None
    last_title = None
    try:
        url_list = appex.get_urls()
        result_list = []
        for url in url_list:
            last_url = url
            markdown_template, last_title = safari_url(url)
            result_list.append(markdown_template)
        all_docs = "\n---\n".join(result_list)
        docs_url = quote(all_docs, safe='')
        last_url_encoded = quote(last_url, safe='')
        last_title_encoded = quote(last_title, safe='')
        # Open IA Writer to handle the new document
        # result_cmd = f'ia-writer://new?&text={docs_url}&edit=true'
        #result_cmd = f'x-devonthink://clip?text={docs_url}&location={last_url_encoded}&title={last_title_encoded}'
        result_cmd = f'x-devonthink://createMarkdown?text={docs_url}&title={last_title_encoded}&tags=Safari%20Gold'
    finally:
        console.hide_activity()
        appex.finish()
    if result_cmd is not None:
        webbrowser.open(result_cmd)
    return 0


def main_pythonista() -> int:
    # TODO
    
    url_input = 'https://developer.apple.com/forums/thread/113123'
    #url_input = 'https://forums.swift.org/t/found-swift-through-swift-for-tensorflow-programming-background-python-c-haskell/22169/3'
    markdown_template, title = safari_url(url_input)
    print(f"Title: {title}")
    return 0


def main_cmdline() -> int:
    """
    Read standard input line by line and interpret is as a URL
    """
    cmd_factory = [
        lambda markdown_encoded, title_encoded: f'x-devonthink://createMarkdown?text={markdown_encoded}&title={title_encoded}&tags=Safari%20Gold',
        lambda markdown_encoded, title_encoded: f'ia-writer://new?&text={markdown_encoded}&edit=true'
    ]

    import subprocess
    try:
        while True:
            url_input = input()
            markdown_template, title = safari_url(url_input)
            markdown_encoded = quote(markdown_template, safe='')
            url_encoded = quote(url_input, safe='')
            title_encoded = quote(title, safe='')

            for cmd_gen in cmd_factory:
                cmd_line = cmd_gen(markdown_encoded, title_encoded)
                cmd_result = subprocess.run(['open', cmd_line])
                if cmd_result.returncode == 0:
                    break

    except EOFError:
        pass
    return 0


if __name__ == '__main__':
    try:
        import appex
        # Successful, running in Pythonista
        if appex.is_running_extension():
            sys.exit(main_app_extension())
        else:
            sys.exit(main_pythonista())
    except ModuleNotFoundError:
        pass
    sys.exit(main_cmdline())
