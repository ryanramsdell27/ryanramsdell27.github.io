# Project Fundamentals
This repo serves two functions: firstly to be the source of my personal website, and secondly as vcs for the code to generate and test the website.

Codewise there are two main scripts here, `generateSite.py` and `server.py`, everything else is content for the site itself. Both of these scripts were developed against Python 3.9 and haven't been tested on other versions. 

`generateSite.py` is the script that reads the file structure tree in the `/src` folder and writes the "compiled" html/css/(js in future?) to the `/build` directory. It is run on the command line with no input, ie `python generateSite.py` from the root folder of this repo (ie one directory above `/src` and `/build`.

`server.py` is a lightweight python server that when run from the root directory of the project will serve the `/build` folder. Running it is a single command with no input `python server.py`

## File Structure

The basic structure is something along these lines

```
\src
    \pages
        \topic1
            - article1.md
            - article1Image.png
        \topic2
        ...
    \template
        - template1.html
        - template2.html
        - styles1.css
    \component
        - component1.html
```

- The `pages` directory stores blog posts, organized by topics.
- The `template` directory stores `.html` [template files](#templates) that have special fields in them for replacement during the build script. It also stores any necessary styling information in `.css` files that are added to a `template` folder in the build destination.
- The `component` directory is for reusable pieces of `html` [blocks](#components). They were designed to be static pieces originally, but there is a working model reusing the templating system that allows arguments to be passed in at build time. 

## Post Structure
Posts are `.md` files using markdown syntax with a special header that has metadata in it.

For example, the header for this page is:

```
title: Static Site Generator
date: 20230303
tags: meta,coding
---
```

The following metadata is read by the script:
- `title` is used for the page title and to populate the index files with links.
- `date` is in the `yyyy-mm-dd` format and is the author date of the page.
- `tags` is a comma-separated list of keywords related to the post. These are used to generate indicies of all posts sharing the same tag
- `backdated: true` is used to indicate if the date of the post has been set to reflect when a project was completed instead of the date of publishing. This comes from a personal preference to keep the history of my projects in order.

The rest of the content under the header is processed as standard markdown syntax (for now). References to images stored under the `pages` directory will work in the static build output.


## Templates <a name="templates"/>
I've added a basic templating flow to ensure page consistency. Templates are `.html` files that contain keys `{{example}}` that get replaced with corresponding values.

Consider this basic post template:

```html
<html>
    <head>
        <link rel="stylesheet" href="/template/main.css">
        <title>{{title}}</title>
    </head>
    <body>
        {{component.header}}
        <article>
            {{content}}
        </article>
        {{component.footer}}
    </body>
</html>
```

In the build script then I just need to do this to create a static `.html` file with whatever content I want in lieu of the `{{title}}` and `{{content}}` keys.

```python
temp_html = "<div><p>Hello World</p></div>"
title = "Hello World Page"
build_template('src/template/post.html', [['content', temp_html], ['title', title]])
```

## Components <a name="components"/>
Components are reusable chunks of `html` like this example for `footer.html`:

```html
<header>
    <ul>
        <li><a href="/">Home</a></li>
        <li><a href="/tagged/furniture">Furniture</a></li>
        <li><a href="/tagged/programming">Programming</a></li>
        <li><a href="/tagged/art">Art</a></li>
        <li><a href="/tagged/recipe">Recipes</a></li>
    </ul>
</header>
```

Inserting this into a templated page is easy, the components are loaded into memory during build time and will be substituted into `{{component.name}}` where `name` is the component filename without the `.html` suffix.

Since components are loaded in memory, there are parts of the script that also can pass in the component to the templating function and populate any `{{}}` fields. For example with the tags chip component:
```html
<div class="chip">
    <a href="/tagged/{{content}}">{{content}}</a>
</div>
```

and the python that generates the html for each tag:

```python
if 'tags' in meta_data:
    for tag in meta_data['tags'].split(','):
        tags += build_template(components['chip'], [['content', tag]])
```

and the sample output for a page with tags furniture, woodworking, and design:

```html
<div class="chip">
    <a href="/tagged/furniture">furniture</a>
</div>
<div class="chip">
    <a href="/tagged/woodworking">woodworking</a>
</div>
<div class="chip">
    <a href="/tagged/design">design</a>
</div>
```


## Build Process

The build process is pretty straight forward. At its core I walk the file tree of `src` and proces each file accordingly, building `.html` pages or copying over files to the build directory as needed. Some higher-level pages are then generated with information from the file-walk.

1. Recursively iterate over file tree of `.src`
    1. If file is `.md`:
        1. Extract metadata header
        2. Convert markdown to html
        3. Use metadata and markdown-html with post template and components to build a full html page
        4. Write `.html` file to build directory with matching path
        5. Add page information to an index data structure to be used later
        5. Add page information to an index data structure for each tag in the metadata to be used late
   2. If file is anything else but `.md`, copy it to the matching path in the build directory
1. Build an index/table of contents file from index data structure populated in the file walk and a template
1. Build an index/table for each tag


# What's Next
There's still so many things I want to do with this script and this process. I'll give a list here, in no particular order and with no promises of these features being completed.

- Custom markdown extensions
    - Generate post-level table of contents
    - Auto generate links for headers with `<a name="link"/>`
    - Image gallery components (I think this will be useful for image heavy posts)
    - `LaTeX` support for math stuff
- Index pages for topics folders (subdirectories under `src/pages`)
- Easier templating in components (no custom code in `generateSite.py`)
- Post editor
- Built in server
    - Live rebuild on changed item
    - Hot swapping/forced refresh
- Only rebuild changed items
