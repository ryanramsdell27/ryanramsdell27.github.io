title: Static Site Generator
date: 2023-03-03
tags: meta,programming
codehilite: true
---

# Why blog?
This is a project I've been meaning to start for a long time. I make a lot of things, and am terrible at documenting them. The best parts of the diy community are how much people share, their willingness to help someone learn, and their interest in taking what others have done and improving it even more. This site will hopefully help keep me accountable for recording the things I do, if not for other people, then at least as a personal journal.

There have been several attempts at starting this up. Usually trying to use cutting edge stacks and fancy site design. They have never panned out and sit on backup drives waiting to be purged when I eventually decide to clean up all that digital garbage. Hopefully this project won't meet the same fate.

# Why write my own site generator? 

- I prefer writing in markdown over html 
- I don't want to deal with existing generators (Jekyll)
- Full control over what is built
- Seems like a fun project

The web has transformed a lot in even the short few years that I've been exposed to it. I'm sure I'm not the only one nostalgic for the way it used to be: online tutorials were, be default, text articles, sometimes with images, rarely with videos. It was searchable, you could easily flip back and forth between things, re-read passages without having to scrub through a youtube video. Look at project progress pictures without having to pause a tik-tok. Read a recipe without 6000 ads just begging you to click on them (well maybe there were a lot of banners back in the day too, but it was much easier to ignore on a desktop than on your phone).

I love the new frameworks: react, vue, angular, next --- they make my day-to-day flow at my 9 to 5 so much easier. Enterprise grade apps are a breeze to build and API integration is beyond easy. But this is a blog site, and all I'm serving is static content.  I don't need the bloat of a full react app, or any other framework for that matter, so I've opted to build this by hand. It certainly isn't the most optimized code, or the prettiest, but I figured there is some value to having full control over what I'm publishing. Plus it's an interesting way to go back over the fundamentals.

# Project Fundamentals
## File Structure
I'm not building this script for general purpose use, so I get to be as opinionated as I want. 

The basic structure is something along these lines

```{linenums=False}
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
```

- The `pages` directory stores blog posts, organized by topics.
- The `template` directory stores `.html` [template files](#templates) that have special fields in them for replacement during the build script. It also stores any necessary styling information in `.css` files that are added to a `template` folder in the build destination.

## Post Structure
Posts are `.md` files using markdown syntax with a special header that has metadata in it. 

For example, the header for this page is:

```
title: Static Site Generator
date: 2023-03-03
tags: meta,coding
---
```

- `title` is used for the page title and to populate the index files with links. 
- `date` is in the `yyyy-mm-dd` format and is the author date of the page.
- `tags` is a comma-separated list of keywords related to the post

The rest of the content under the header is processed as standard markdown syntax (for now). References to images stored under the `pages` directory will work in the static build output.


## Templates <a name="templates"/>
I've added a basic templating flow to ensure page consistency. Templates are `.html` files that contain keys `{{example}}` that get replaced with corresponding values. 

Consider this basic post template
```html
<html>
    <head>
        <link rel="stylesheet" href="/template/main.css">
        <title>{{title}}</title>
    </head>
    <body>
        <header></header>
        <article>
            {{content}}
        </article>
    </body>
</html>
```

In the build script then I just need to do this to create a static `.html` file with whatever content I want in lieu of the `{{title}}` and `{{content}}` keys.

```python
temp_html = "<div><p>Hello World</p></div>"
title = "Hello World Page"
build_template('src/template/post.html', [['content', temp_html], ['title', title]])
```

## Build Process

The build process is pretty straight forward. At its core I walk the file tree of `src` and proces each file accordingly, building `.html` pages or copying over files to the build directory as needed. Some higher-level pages are then generated with information from the file-walk.

1. Recursively iterate over file tree of `.src`
   1. If file is `.md`:
      1. Extract metadata header
      2. Convert markdown to html
      3. Use metadata and markdown-html with post template to build a full html page
      4. Write `.html` file to build directory with matching path
      5. Add page information to an index data structure to be used later
   2. If file is anything else but `.md`, copy it to the matching path in the build directory
1. Build an index/table of contents file from index data structure populated in the file walk and a template

The script is written in Python for two main reasons. One, it's incredibly easy to read and work with. I can't imagine I'll be making many changes once I have a working script, meaning that when I do decide to make updates the code base will be absolutely foreign to me: readability will be key when the time for edits arrives. Secondly, Python has a lot of ease of use functionality and several modules that make coding with it just plain simple. I didn't particularly want to write a markdown compiler, so having that capability with a well maintained library I knew how to use made it a good choice.

# What's Next
There's still so many things I want to do with this script and this process. I'll give a list here, in no particular order and with no promises of these features being completed.

- Custom markdown extensions
  - Generate post-level table of contents
  - Auto generate links for headers with `<a name="link"/>`
  - Image gallery components (I think this will be useful for image heavy posts)
  - `LaTeX` support for math stuff
- Index pages for posts with specific tags
- Index pages for topics folders (subdirectories under `src/pages`)
- Easier templating composition/reusable components
- Post editor
- Built in server
  - Live rebuild on changed item
  - Hot swapping/forced refresh
- Only rebuild changed items
