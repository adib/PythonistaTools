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
 5. The script will invoke IA Writer to edit the new markdown file.

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
        title_separators = ['|', ':', '-']
        result = requests.get(page_url)
        contents = result.text
        soup = BeautifulSoup(contents, 'html5lib')
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
        f"\n## Hidden Pains\n\n"
        f"\n## Jargons\n\n"
        f"\n## Recommendations\n\n"
        f"\n## Worldviews\n\n"
    )
    return subst_result


def safari_url(thread_url: str) -> str:
    info = PostInfo.from_url(thread_url)
    now = datetime.now()
    analysis_date_str = now.strftime('%Y-%m-%d')
    return make_safari_template(thread_url, info.thread_title, info.site_name, analysis_date_str)


if __name__ == '__main__':
    import appex
    import webbrowser
    import console
    result_cmd = None
    console.show_activity()
    try:
        url_list = appex.get_urls()
        result_list = []
        for url in url_list:
            markdown_template = safari_url(url)
            result_list.append(markdown_template)
        all_docs = "\n---\n".join(result_list)
        docs_url = quote(all_docs, safe='')
        # Open IA Writer to handle the new document
        result_cmd = 'ia-writer://new?&text={}'.format(docs_url)
    finally:
        console.hide_activity()
        appex.finish()
    if result_cmd is not None:
        webbrowser.open(result_cmd)

