import json
import os
from django_project.settings import VIDEOS_TEMPLATES
from video_app.domain.ffmpeg_maker import EffectTemplate, TransitionTemplate
from video_app.domain.imagemagick_maker import TextTemplate, ImageTemplate


class FfTemplateException(Exception):
    pass


def from_json(filename):
    with open(filename, 'r') as f:
        return parse_key(json.load(f), recursive=True)


class FfmpegTemplate(object):
    def __init__(self, template_name):
        self.filename = os.path.join(VIDEOS_TEMPLATES, '%s.json') % template_name
        self.video_file = os.path.join(VIDEOS_TEMPLATES, '%s.mp4') % template_name
        if not os.path.exists(self.filename):
            raise FfTemplateException("%s.json file doesn't exist" % template_name)
        if not os.path.exists(self.video_file):
            raise FfTemplateException("%s.mp4 file doesn't exist" % template_name)
        self.template = from_json(self.filename)

    def get_screens(self):
        return [{'index': index,
                 'data': {
                     'text_count': len(screen.get('texts', {})),
                     'image_count': len(screen.get('images', {}))}
                 } for index, screen in self.template.get('screens', {}).iteritems()]

    def load_template(self, screens):
        template_texts = []
        template_images = []
        template_guest = None
        thumbnail_frame = 0
        for sc_index, screen in self.template.get('screens', {}).iteritems():
            for tx_index, text in screen.get('texts', {}).iteritems():
                effects = text['transition'].get('effects', None)
                if effects:
                    text['transition']['effects'] = [EffectTemplate(**e) for e in effects]
                template = TextTemplate(**text['template'])
                transition = TransitionTemplate(**text['transition'])
                if text.get('guest_field', False):
                    template_guest = {'template': template, 'transition': transition}
                    thumbnail_frame = text.get('frame', 80)
                else:
                    lines = screens[sc_index]['texts'][tx_index]['text'].split('|')
                    template_texts.append({'template': template, 'transition': transition, 'lines': lines})
            for im_index, image in screen.get('images', {}).iteritems():
                effects = image['transition'].get('effects', None)
                if effects:
                    image['transition']['effects'] = [EffectTemplate(**e) for e in effects]
                template_images.append({
                    'template': ImageTemplate(**image['template']),
                    'file': screens[sc_index]['images'][im_index]['image'],
                    'transition': TransitionTemplate(**image['transition'])
                })
        return {'video_file': self.video_file, 'template_texts': template_texts, 'template_images': template_images,
                'template_guest': template_guest, 'thumbnail_frame': thumbnail_frame,
                'upper': self.template.get('upper', False)}


def parse_key(d, recursive=True):
    result = {}
    for k, v in d.iteritems():
        value = parse_key(v, recursive) if isinstance(v, dict) and recursive else v
        if k == "margins" and isinstance(value, list):
            value = [tuple(x) if isinstance(x, list) else x for x in value]
        if k.isdigit():
            result[int(k)] = value
        else:
            result[k] = value
    return result
