import yaml
from jinja2 import Environment, FileSystemLoader, Undefined
import glob
import os
from markdown2 import Markdown
import logging
import copy
import shutil
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3NoHeaderError


DATA_DIR_PATTERN = 'dotastro*'
README_NAME = 'README.md'
YAML_TEMPLATE = 'template.yml'
EPISODES_FILE = 'episodes.yml'
LOGO_FILE = 'dotlogo_black.png'

OUTPUT_DIR = 'html'

TEMPLATE_LOADER = FileSystemLoader('templates')

def runner():
    make_file(filename='podcast.xml')
    make_file(filename='index.html')
    #make_rss()
    return

def parse_episodes_yml():
    stream = open(EPISODES_FILE, 'r')
    filedata = yaml.load(stream)
    return filedata

def metadata_to_file(filePath,data):
    try:
        meta = EasyID3(filePath)
    except mutagen.id3.ID3NoHeaderError:
        meta = mutagen.File(filePath, easy=True)
        meta.add_tags()
    meta['title'] = data.title
    meta['artist'] = "Edward Gomez"
    meta['genre'] = "Podcast"
    meta.save(filePath, v1=2)
    return

def make_file(filename):
    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    env = Environment(loader=TEMPLATE_LOADER)
    template = env.get_template(filename)
    episodes = parse_episodes_yml()
    output_from_parsed_template = template.render(episodes=episodes)
    with open(os.path.join(OUTPUT_DIR, filename), "w") as fh:
        print('Writing out', fh.name)
        fh.write(output_from_parsed_template)

    return


def load_yaml_style():
    stream = open(YAML_TEMPLATE, 'r')
    tmpl_data = yaml.load(stream)
    return tmpl_data

def parse_yaml_style(data,template):
    for k, v in template.items():
        if not data.get(k,''):
            data[k] = ''
    # Catch the case where images and creators are not lists
    if type(data['creators']) == str:
        data['creators'] = [data['creators']]
    if type(data['images']) == str:
        data['images'] = [data['images']]
    return data

def render_page_data(header, hacks_data, dirname):
    data = dict()
    env = Environment(loader=TEMPLATE_LOADER)
    template = env.get_template('page.html')
    events = parse_events_yml()
    data['events'] = events
    data['header'] = header
    data['event'] = dirname
    data['hacks'], fromimgs, toimgs = reprocess_image_names(hacks_data, dirname)

    output_from_parsed_template = template.render(**data )
    output_from_parsed_template.replace("–", " ")

    if not os.path.isdir(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)

    with open(os.path.join(OUTPUT_DIR, dirname) + ".html", "w") as fh:
        print('Writing out', fh.name)
        fh.write(output_from_parsed_template)

    for fromimg, toimg in zip(fromimgs, toimgs):
        toimg = os.path.join(OUTPUT_DIR, toimg)
        print('Copying', fromimg, 'to', toimg)
        shutil.copy(fromimg, toimg)
    return



if __name__ == '__main__':
    runner()
