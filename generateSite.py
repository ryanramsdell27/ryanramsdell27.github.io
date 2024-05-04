import markdown
import shutil
from PIL import Image
from pathlib import Path
from typing import List
from datetime import date
from markdown.extensions.toc import TocExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.footnotes import FootnoteExtension
from pymdownx.arithmatex import ArithmatexExtension
from generateRss import RssGen, Post

SOURCE_DIR = 'src/pages/'
STATIC_DIR = 'src/static'
TEMPLATE_DIR = 'src/template'
COMPONENT_DIR = 'src/component'
OUTPUT_DIR = 'build/'

THUMBNAIL_SIZE = (128, 128)

buildPath = lambda file, src, target: Path(str(file).replace('.md', '.html').replace(src, target))
md = markdown.Markdown(extensions=[CodeHiliteExtension(linenums=True),
                                   'fenced_code',
                                   TocExtension(permalink=True),
                                   'smarty',
                                   'tables',
                                   'md_in_html',
                                   FootnoteExtension(BACKLINK_TEXT="&#8617&#xFE0E"),
                                   ArithmatexExtension(generic=True)
                                   ])


def clean():
    shutil.rmtree(OUTPUT_DIR)


def read_meta_data(file):
    t_header = file.split('---', 1)
    if len(t_header) <= 1:
        return {'title': 'Post', 'date': '2023-01-01', 'tags': ''}, file
    meta_data = {}
    for line in t_header[0].split('\n'):
        attribute = line.split(': ')
        if len(attribute) > 1:
            meta_data[attribute[0]] = ': '.join(attribute[1:])
    return [meta_data, t_header[1]]


def find_thumbnail(file, path: Path):
    for l in file.split("\n"):
        if l.startswith("!["):
            file_name = l.split("](")[1].strip(")")
            original_file = './' + str(path.parent) + '/' + file_name
            thumbnail_file = str(path.parent) + '/thumbnail_' + file_name
            thumbnail_output_path = buildPath(thumbnail_file, SOURCE_DIR, OUTPUT_DIR)
            thumbnail_link = '/' + str(buildPath(thumbnail_file, SOURCE_DIR, ''))
            image = Image.open(original_file)
            image.thumbnail(THUMBNAIL_SIZE)
            thumbnail_output_path.parent.mkdir(exist_ok=True, parents=True)
            image.save(thumbnail_output_path)
            return thumbnail_link
    return None


def convert_md_file(file: Path):
    print('Converting', file)
    with open(file, 'r') as f:
        temp_md = f.read()
    [meta_data, file_md] = read_meta_data(temp_md)
    if 'thumbnail' not in meta_data:
        meta_data['thumbnail'] = find_thumbnail(temp_md, file)
    md.reset()
    temp_html = md.convert(file_md)
    tags = ''
    if 'tags' in meta_data:
        for tag in meta_data['tags'].split(','):
            tags += build_template(components['chip'], [['content', tag]])

    backdated = components['backdated'] if 'backdated' in meta_data and meta_data['backdated'] == 'true' else ''
    mathjax = components['mathjax'] if 'mathjax' in meta_data and meta_data['mathjax'] == 'true' else ''
    codehilite = components['codehilite'] if 'codehilite' in meta_data and meta_data['codehilite'] == 'true' else ''

    temp_html_serve = build_template(POST_TEMPLATE,
                                     [['content', temp_html],
                                      ['title', meta_data['title']],
                                      ['date', date.fromisoformat(meta_data['date']).strftime("%A %d, %B %Y")],
                                      ['tags', tags],
                                      ['backdated', backdated],
                                      ['mathjax', mathjax],
                                      ['codehilite', codehilite]])

    output_file = buildPath(file, SOURCE_DIR, OUTPUT_DIR)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(output_file, 'w') as f:
        f.write(temp_html_serve)
    return [meta_data, temp_html]


def copy_to_build_dir(file: Path, src: str, target: str):
    output_file = buildPath(file, src, target)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    shutil.copyfile(file, output_file)


def load_file(file):
    with open(file, 'r') as f:
        temp_f = f.read()
    return temp_f


def build_template(template, var_arr):
    for [key, value] in components.items():
        template = template.replace('{{component.%s}}' % key, value)
    for [key, value] in var_arr:
        template = template.replace('{{%s}}' % key, value)
    return template


def build_index(index: List, out: str, title: str):
    links = []
    index.sort(key=lambda k: k['meta_data']['date'], reverse=True)
    for file in index:
        thumbnail = build_template(components.get('thumbnail'), [['thumbnail', file['meta_data']['thumbnail']]]) if \
        file['meta_data']['thumbnail'] else ''
        t = build_template(components.get('content_list_item'), [
            ['link', str(file['path']).replace(OUTPUT_DIR, '')],
            ['title', file['meta_data']['title']],
            ['date', date.fromisoformat(file['meta_data']['date']).strftime("%d %B %Y")],
            ['thumbnail', thumbnail]])
        links.append(t)
    link_list = '<ul>{}</ul>'.format(''.join(links))
    temp_f = build_template(CONTENTS_TEMPLATE, [['index', link_list], ['title', title]])

    output_file = buildPath(OUTPUT_DIR + out + '/index.html', SOURCE_DIR, OUTPUT_DIR)
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(output_file, 'w') as f:
        f.write(temp_f)


def build_feed(index):
    gen = RssGen()
    index.sort(key=lambda k: k['meta_data']['date'], reverse=True)
    for file in index[:25]:
        post = Post()
        post.atomId = str(file['path']).replace(OUTPUT_DIR, '')
        post.updated = date.fromisoformat(file['meta_data']['date']).strftime("%Y-%m-%dT%H:%M:%SZ")
        post.title = file['meta_data']['title']
        post.content = file['html']
        gen.append(post)
    gen.save()


def read_components():
    components_list = {}
    for file in Path(COMPONENT_DIR).glob('**/*'):
        if file.suffix == '.html':
            with open(file, 'r') as f:
                temp_f = f.read()
            components_list[file.name.removesuffix(file.suffix)] = temp_f
    return components_list


def process_files():
    files = Path(SOURCE_DIR).glob('**/*')
    index = []
    tag_index = {}
    for file in files:
        if not file.is_file():
            continue
        if file.suffix == '.md':
            [meta_data, temp_html] = convert_md_file(file)
            index.append({'path': buildPath(file, SOURCE_DIR, OUTPUT_DIR), 'meta_data': meta_data, 'html': temp_html})
            if 'tags' in meta_data:
                for tag in meta_data['tags'].split(','):
                    details = {'path': buildPath(file, SOURCE_DIR, OUTPUT_DIR), 'meta_data': meta_data}
                    if tag in tag_index:
                        tag_index[tag].append(details)
                    else:
                        tag_index[tag] = [details]
        else:
            copy_to_build_dir(file, SOURCE_DIR, OUTPUT_DIR)
    build_index(index, '', 'All posts')
    build_feed(index)
    for tag in tag_index:
        build_index(tag_index[tag], 'tagged/' + tag, 'Tagged: ' + tag)
    for file in Path(TEMPLATE_DIR).glob('**/*'):
        if file.suffix in ['.css', '.ico', '.png']:
            copy_to_build_dir(file, TEMPLATE_DIR, OUTPUT_DIR + '/template')
    for file in Path(STATIC_DIR).glob('**/*'):
        if not file.is_file():
            continue
        copy_to_build_dir(file, STATIC_DIR, OUTPUT_DIR + '/static')


POST_TEMPLATE = load_file('src/template/post.html')
CONTENTS_TEMPLATE = load_file('src/template/contents.html')
components = read_components()
clean()
process_files()
