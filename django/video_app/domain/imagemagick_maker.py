import os

from wand.color import Color
from wand.drawing import Drawing
from wand.image import Image
from django_project.settings import VIDEOS_TEMPLATES

FONT_DIR = os.path.join(VIDEOS_TEMPLATES, 'fonts')


class TextAligment(object):
    H_CENTER = V_CENTER = 'center'
    H_LEFT = 'left'


class TextTemplate(object):
    def __init__(self, width, height, font_size, font_path, text_color, alignment='center', angle=0, interline=1.3,
                 vertical_alig='center', shadow_line=0, shadow_color=None, font_resize=1):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.font_path = font_path
        self.text_color = text_color
        self.alignment = alignment
        self.angle = angle
        self.interline = interline
        self.shadow_line = shadow_line
        self.shadow_color = shadow_color
        self.font_resize = font_resize

    def get_dict(self):
        return {
            'width': self.width,
            'height': self.height,
            'font_size': self.font_size,
            'font_path': self.font_path,
            'text_color': self.text_color,
            'alignment': self.alignment,
            'angle': self.angle,
            'interline': self.interline,
            'shadow_line': self.shadow_line,
            'shadow_color': self.shadow_color,
        }


class ImageTemplate(object):
    def __init__(self, width, height, angle=0, shadow_line=0, shadow_color=None, border_width=0, border_color=None):
        self.width = width
        self.height = height
        self.angle = angle
        self.shadow_line = shadow_line
        self.shadow_color = shadow_color
        self.border_width = border_width
        self.border_color = border_color

    def get_dict(self):
        return {
            'width': self.width, 'height': self.height, 'angle': self.angle, 'shadow_line': self.shadow_line,
            'shadow_color': self.shadow_color, 'border_width': self.border_width, 'border_color': self.border_color
        }


class ImageMagickMaker(object):
    def __init__(self):
        self.file = None

    def make(self):
        raise NotImplementedError()


class ImageMagickTextMaker(ImageMagickMaker):
    def __init__(self, file_name, text_template, lines, demo=False):
        self.file_name = file_name
        self.text_template = text_template
        self.lines = [l if len(l) else ' ' for l in lines]
        self.paragraph = self.get_paragraph()
        self.demo = demo
        super(ImageMagickTextMaker, self).__init__()

    def make(self):
        width = self.text_template.width
        height = self.text_template.height
        with Image(width=width, height=height,
                   background=Color('transparent')) as image:
            if self.text_template.shadow_line > 0:
                with Drawing() as draw_s:
                    self._draw_text(draw_s, image, shadow=True)
            with Drawing() as draw:
                self._draw_text(draw, image)
                if self.demo:
                    self._draw_border(draw, image)
            image.rotate(self.text_template.angle)
            image.save(filename=self.file_name)
        self.file = self.file_name
        return self.file

    def _draw_text(self, draw, image, shadow=False):
        global x
        draw.font = os.path.join(FONT_DIR, self.text_template.font_path)
        index = 0
        if self.text_template.alignment == 'center':
            x = image.width / 2
        elif self.text_template.alignment == 'left':
            x = 0
        elif self.text_template.alignment == 'right':
            x = image.width
        y = int(self.paragraph.top_margin + self.paragraph.font_size)
        if shadow:
            x += self.paragraph.shadow_line
            y += self.paragraph.shadow_line
        for line in self.lines:
            self._draw_line(draw, image, line, x, y, self.paragraph.font_size, shadow)
            y += int(self.paragraph.font_size * self.paragraph.interline)
            index += 1
        if shadow:
            image.resize(width=image.width + 1, height=image.height + 1, blur=self.paragraph.shadow_line * 2)

    def _draw_line(self, draw, image, line, x, y, font_size, shadow):
        draw.fill_color = Color(
            'rgba(%(red)s, %(green)s, %(blue)s,0.8)' % self.text_template.shadow_color) if shadow else Color(
            'rgb(%(red)s, %(green)s, %(blue)s)' % self.text_template.text_color)
        draw.font_size = font_size
        draw.text_alignment = self.text_template.alignment
        draw.text(x, y, line)
        draw(image)

    class Paragraph(object):
        def __init__(self, font_size, interline, shadow_line, top_margin=None):
            self.font_size = font_size
            self.interline = interline
            self.top_margin = top_margin if top_margin else int(font_size * interline / 2)
            self.shadow_line = shadow_line

        def __unicode__(self):
            return u"%s [%s] +%s" % (self.font_size, self.interline, self.top_margin)

        def __str__(self):
            return self.__unicode__()

    def get_paragraph(self):
        width = self.text_template.width
        height = self.text_template.height
        # font size
        font_size = self.text_template.font_size
        max_len = max([len(line) * 0.8 for line in self.lines] + [1])
        font_size = min(font_size, width / max_len)
        font_size *= self.text_template.font_resize
        font_size = min(font_size, height / (len(self.lines) + 1))
        # interline
        interline = self.text_template.interline
        max_interline = round((1.0 * height / (len(self.lines) + 1)) / font_size, 2)
        interline = max(1, min(interline, max_interline))
        # paragraph
        shadow_line = self.text_template.shadow_line
        shadow_line = shadow_line if shadow_line > 1 else int(shadow_line * font_size)
        return self.Paragraph(font_size, interline, shadow_line)

    def _draw_border(self, draw, image):
        draw.fill_color = Color('transparent')
        draw.stroke_color = Color('rgb(%s, %s, %s)' % (100, 255, 200))
        draw.stroke_width = 10
        draw.rectangle(0, 0, width=image.width, height=image.height)
        draw(image)


class ImageMagickImageMaker(ImageMagickMaker):
    def __init__(self, file_name, image_template, image_path):
        self.file_name = file_name
        self.image_template = image_template
        self.image_path = image_path
        super(ImageMagickImageMaker, self).__init__()

    def make(self):
        with Image(filename=self.image_path) as image:
            image.resize(self.image_template.width, self.image_template.height)
            if self.image_template.border_color:
                with Drawing() as draw:
                    draw.fill_color = Color('transparent')
                    draw.stroke_color = Color('rgb(%(red)s, %(green)s, %(blue)s)' % self.image_template.border_color)
                    draw.stroke_width = self.image_template.border_width
                    draw.rectangle(0, 0, width=image.width, height=image.height)
                    draw(image)
            if not self.image_template.angle == 0:
                image.rotate(self.image_template.angle)
            # if self.image_template.shadow_color:
            image.save(filename=self.file_name)
            # width = self.image_template.width
            # height = self.image_template.height
            # with Image(width=width + 20, height=height + 20, format='png',
            #            background=Color('transparent')) as back_image:
            #     with Drawing() as draw:
            #         draw.draw(image)
            #         draw(back_image)
            #     back_image.save(filename=self.file_name[:-4] + '___' + self.file_name[-4:])
        self.file = self.file_name
        return self.file

# rad = math.radians(abs(self.text_template.angle))
# y = max(0, int(image.width * math.sin(rad) / math.cos(rad)) + 1) if not rad == 0 else 0
