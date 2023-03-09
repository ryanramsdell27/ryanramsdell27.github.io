import markdown
import shutil
from pathlib import Path
from typing import List
from datetime import date

SOURCE_DIR = 'src/pages/'
TEMPLATE_DIR = 'src/template'
COMPONENT_DIR = 'src/component'
OUTPUT_DIR = 'build/'

buildPath = lambda file, src, target: Path(str(file).replace('.md', '.html').replace(src, target))

md = markdown.Markdown(extensions=['fenced_code'])


def clean():
    shutil.rmtree(OUTPUT_DIR)


def read_meta_data(file):
    t_header = file.split('---', 1)
    if len(t_header) <= 1:
        return {'title': 'Post', 'date': '2023-01-01'}, file
    meta_data = {}
    for line in t_header[0].split('\n'):
        attribute = line.split(': ')
        if len(attribute) > 1:
            meta_data[attribute[0]] = attribute[1]
    return [meta_data, t_header[1]]


def convert_md_file(file: Path):
    print('Converting', file)
    with open(file, 'r') as f:
        temp_md = f.read()
    [meta_data, file_md] = read_meta_data(temp_md)
    md.reset()
    temp_html = md.convert(file_md)
    temp_html = build_template('src/template/post.html',
                               [['content', temp_html],
                                ['title', meta_data['title']],
                                ['date', date.fromisoformat(meta_data['date']).strftime("%A %d, %B %Y")]])

    output_file = buildPath(file, SOURCE_DIR, OUTPUT_DIR)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(output_file, 'w') as f:
        f.write(temp_html)
    return meta_data


def copy_to_build_dir(file: Path, src: str, target: str):
    output_file = buildPath(file, src, target)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    shutil.copyfile(file, output_file)


def build_template(template, var_arr):
    with open(template, 'r') as f:
        temp_f = f.read()
    for component in components:
        temp_f = temp_f.replace('{{component.%s}}' % component['name'], component['value'])
    for [key, value] in var_arr:
        temp_f = temp_f.replace('{{%s}}' % key, value)
    return temp_f


def build_index(index: List):
    links = []
    for file in index:
        links.append('<li><a href={}>{}<span style="float:right;font-size:smaller;">{}</span></a></li>'.format(
            str(file['path']).replace(OUTPUT_DIR, ''),
            file['meta_data']['title'],
            date.fromisoformat(file['meta_data']['date']).strftime("%A %d, %B %Y"),
        ))
    link_list = '<ul>{}</ul>'.format(''.join(links))
    temp_f = build_template('src/template/contents.html', [['index', link_list]])

    output_file = buildPath(OUTPUT_DIR + 'index.html', SOURCE_DIR, OUTPUT_DIR)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(output_file, 'w') as f:
        f.write(temp_f)


def read_components():
    components_list = []
    for file in Path(COMPONENT_DIR).glob('**/*'):
        if file.suffix == '.html':
            with open(file, 'r') as f:
                temp_f = f.read()
            components_list.append({'name': file.name.removesuffix(file.suffix), 'value': temp_f})
    return components_list


def process_files():
    files = Path(SOURCE_DIR).glob('**/*')
    index = []
    for file in files:
        if not file.is_file():
            continue
        if file.suffix == '.md':
            meta_data = convert_md_file(file)
            index.append({'path': buildPath(file, SOURCE_DIR, OUTPUT_DIR), 'meta_data': meta_data})
        else:
            copy_to_build_dir(file, SOURCE_DIR, OUTPUT_DIR)
    build_index(index)
    for file in Path(TEMPLATE_DIR).glob('**/*'):
        if file.suffix == '.css':
            copy_to_build_dir(file, TEMPLATE_DIR, OUTPUT_DIR + '/template')


components = read_components()
clean()
process_files()
