import subprocess
from datetime import datetime

from django_project.settings import FFMPEG_CMD


class EffectKind(object):
    LINEAR = 'linear'


class EffectTemplate(object):
    def __init__(self, position, time, kind='linear'):
        self.position = position
        self.time = time
        self.kind = kind

    def get_script(self, p0, t0):
        x0, y0 = p0
        x1, y1 = self.position
        if self.time <= 0 or (x1 - x0 == 0 and y1 - y0 == 0):
            return "%s" % x1, "%s" % y1
        dx = int((x1 - x0) / self.time)
        dy = int((y1 - y0) / self.time)
        if self.kind == EffectKind.LINEAR:
            return "%s+(t-%s)*%s" % (x0, t0, dx), "%s+(t-%s)*%s" % (y0, t0, dy)
        return "%s" % x1, "%s" % y1

    def get_dict(self):
        return {
            'position': self.position,
            'time': self.time,
            'kind': self.kind,
        }


class TransitionTemplate(object):
    def __init__(self, position, time, effects=None, static=0):
        self.position = position
        self.time = time
        self.effects = effects if effects else [self._get_static_effect(static)]

    def get_script(self):
        result = "NAN", "NAN"
        ptx, pty = self.position
        tt = self.time
        for effect in self.effects:
            efx, efy = effect.get_script((ptx, pty), tt)
            result = ("if(gte(t,%(t0)s),%(efs)s,%(result)s)" % {'t0': tt, 'efs': efx, 'result': result[0]},
                      "if(gte(t,%(t0)s),%(efs)s,%(result)s)" % {'t0': tt, 'efs': efy, 'result': result[1]})
            tt += effect.time
            ptx = effect.position[0]
            pty = effect.position[1]
        return "overlay=enable='between(t,%s,%s)':x='%s':y='%s'" % (self.time, tt, result[0], result[1])

    def _get_static_effect(self, d_time):
        return EffectTemplate(self.position, d_time)

    def get_dict(self):
        return {
            'position': self.position,
            'time': self.time,
            'effects': [ef.get_dict() for ef in self.effects]
        }


class VideoTemplate(object):
    def __init__(self, video_file, templates):
        self.video_file = video_file
        self.templates = templates

    def make(self, output_file):
        files = self.get_files()
        effects = ",".join([t[1].get_script() for t in self.templates])
        arguments = ['-i', self.video_file]
        arguments += files + ['-filter_complex', effects, "-b:v", "3M", "-c:a",
                              "aac", "-strict", "-2", output_file]
        print([FFMPEG_CMD] + arguments)
        print(datetime.now())
        subprocess.call([FFMPEG_CMD] + arguments)

    def get_files(self):
        file_templates = [t[0] for t in self.templates]
        files = []
        for file_template in file_templates:
            if not file_template.file:
                file_template.make()
            files.append('-i')
            files.append(file_template.file)
        return files
