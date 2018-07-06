# -*- coding: utf-8 -*-
import re

def addEmailTitle(html, titler):
    m = re.search(r'</\s*head>', html, re.IGNORECASE)
    if m is not None:
        s = m.start()
    else:
        s = len(html)
    return html[:s] + titler + html[s:]