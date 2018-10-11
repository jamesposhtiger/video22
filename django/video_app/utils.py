# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import select
import subprocess

from django_project import settings


def clear_dir(path):
    if os.path.isdir(path):
        os.chmod(path, 0o777)
        names = os.listdir(path)
        for name in names:
            fullname = os.path.join(path, name)
            if os.path.isdir(fullname):
                continue
            try:
                os.remove(fullname)
            except OSError:
                pass
    else:
        make_dir(path)
        os.chmod(path, 0o777)


def make_dir(path):
    """
    Creates a directory with path and creates all of parent directories if they are not created
    :param path: path to directory
    :return: None
    """
    parent_path, name = os.path.split(path)
    dirs_to_create = [name]
    while not os.path.isdir(parent_path):
        parent_path, name = os.path.split(parent_path)
        dirs_to_create.append(name)

    path = parent_path
    for d in reversed(dirs_to_create):
        path = os.path.join(path, d)
        os.mkdir(path)
