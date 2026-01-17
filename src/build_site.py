import os
import sys
import markdown
from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension
import xml.etree.ElementTree as etree


class TableWrapProcessor(Treeprocessor):
    def run(self, root):
        parent_map = {c: p for p in root.iter() for c in p}
        tables = list(root.iter('table'))
        for table in tables:
            parent = parent_map.get(table)
            if parent is None:
                continue
            for i, child in enumerate(list(parent)):
                if child is table:
                    wrapper = etree.Element('div')
                    wrapper.set('class', 'table-wrap')
                    parent.remove(table)
                    parent.insert(i, wrapper)
                    wrapper.append(table)
                    break
        return root


class TableWrapExtension(Extension):
    def extendMarkdown(self, md):
        md.treeprocessors.register(TableWrapProcessor(md), 'tablewrap', 15)


def main():
    # Args: input_markdown [output_dir]
    input_md = sys.argv[1] if len(sys.argv) > 1 else '../README.md'
    output_dir = sys.argv[2] if len(sys.argv) > 2 else '../_site'

    with open(input_md, 'r', encoding='utf-8') as f:
        md_content = f.read()

    with open('template.html', 'r', encoding='utf-8') as f:
        template = f.read()

    md = markdown.Markdown(extensions=['extra', 'toc', TableWrapExtension()], extension_configs={'toc': {'permalink': True, 'permalink_leading': True}})
    html_content = md.convert(md_content)

    full_html = template.replace('{{content}}', html_content)

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, 'index.html')
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f'Wrote site to {out_path}')


if __name__ == '__main__':
    main()
