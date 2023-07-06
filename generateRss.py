import datetime
import xml.etree.ElementTree as ET


class Post:
    def __init__(self, title="", atomId="", updated="", content=""):
        self.title = title
        self.atomId = atomId
        self.updated = updated
        self.content = content


class RssGen:

    def __init__(self):
        self.title = "Ryan's Blog"
        self.link = "https://blog.ryanramsdell.dev"
        self.description = "RSS feed for my blog"
        self.id = "https://blog.ryanramsdell.dev"
        self.feed = ET.Element("feed", {"xmlns": "http://www.w3.org/2005/Atom"})
        ET.SubElement(self.feed, "title").text = self.title
        ET.SubElement(self.feed, "link", {"rel": "alternate", "href": self.link})
        ET.SubElement(self.feed, "description").text = self.description
        ET.SubElement(self.feed, "id").text = self.id
        ET.SubElement(self.feed, "updated").text = datetime.datetime.now().strftime("%d-%m-%YT%H:%M:%SZ")

    def append(self, post):
        entry = ET.SubElement(self.feed, "entry")
        ET.SubElement(entry, "title").text = post.title
        ET.SubElement(entry, "id").text = post.atomId
        ET.SubElement(entry, "updated").text = post.updated
        ET.SubElement(entry, "content", {"type": "html"}).text = '{}'.format(post.content)
        ET.SubElement(entry, "link", {"rel": "alternate", "href": '{}/{}'.format(self.id, post.atomId)})

    def __str__(self):
        ET.indent(self.feed)
        return ET.tostring(self.feed, encoding='unicode')

    def save(self):
        tree = ET.ElementTree(self.feed)
        ET.indent(tree)
        tree.write("./build/feed.xml")
