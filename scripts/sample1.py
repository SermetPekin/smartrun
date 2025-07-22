#!/usr/bin/env python3
"""Render a small Markdown snippet to HTML."""
import markdown

md_text = """
# Offline Markdown Test
* Bullet one
* Bullet two
"""
html = markdown.markdown(md_text)
print("_Rendered HTML:_\n")
print(html)
