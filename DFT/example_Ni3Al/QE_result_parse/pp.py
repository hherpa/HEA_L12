# -*- coding: utf-8 -*-
"""Парсеры pp.x: PPIn (вход), PPOut (вывод), read_xsf (объёмные данные).

Public API: PPIn, PPOut, read_xsf.
"""

import os
import re

import numpy as np

from .pw import _read_text, parse_namelist


def parse_namelists(text):
    """Разбирает namelist-блоки в dict.

    Args:
        text (str): Содержимое входного файла pp.x.

    Returns:
        dict[str, dict[str, str]]: {block: {key: value}}.
    """
    blocks = {}
    name = None
    for line in text.splitlines():
        s = line.split('!')[0].strip()
        if not s:
            continue
        m = re.match(r'&(\w+)', s)
        if m:
            name = m.group(1)
            blocks[name] = {}
            s = s[m.end():]
        if name is None or '=' not in s:
            continue
        key, val = s.split('=', 1)
        blocks[name][key.strip()] = val.strip().rstrip(',').strip("'\"")
    return blocks


class PPIn:
    """Парсер входного файла pp.x (*.in).

    Args:
        path (str): Путь к файлу либо каталог расчёта.
        prefix (str, optional): Префикс; читается '{path}/{prefix}_{kind}.in'.
            По умолчанию None.
        kind (str, optional): Тип: 'charge', 'hartree' и т.п.
            По умолчанию 'charge'.

    Attributes:
        path (str): Полный путь к файлу.
        prefix (str): Префикс расчёта.
        text (str): Содержимое файла.
        blocks (dict): Namelist-блоки {block: {key: value}}.
    """

    def __init__(self, path, prefix=None, kind='charge'):
        if prefix is not None:
            self.path = os.path.join(path, f'{prefix}_{kind}.in')
        else:
            self.path = path
        self.prefix = prefix or os.path.splitext(os.path.basename(path))[0]
        self.text = _read_text(self.path)
        self.blocks = parse_namelists(self.text)

    @property
    def inputpp(self):
        """Возвращает блок &INPUTPP.

        Returns:
            dict[str, str]: Параметры блока.
        """
        return self.blocks.get('INPUTPP', {})

    @property
    def plot(self):
        """Возвращает блок &PLOT.

        Returns:
            dict[str, str]: Параметры блока.
        """
        return self.blocks.get('PLOT', {})

    @property
    def plot_num(self):
        """Возвращает plot_num из &INPUTPP.

        Returns:
            str | None: plot_num; None, если нет.
        """
        return self.inputpp.get('plot_num')

    @property
    def prefix_pp(self):
        """Возвращает prefix из &INPUTPP.

        Returns:
            str | None: prefix; None, если нет.
        """
        return self.inputpp.get('prefix')

    @property
    def outdir(self):
        """Возвращает outdir из &INPUTPP.

        Returns:
            str | None: outdir; None, если нет.
        """
        return self.inputpp.get('outdir')

    @property
    def filplot(self):
        """Возвращает filplot из &INPUTPP.

        Returns:
            str | None: filplot; None, если нет.
        """
        return self.inputpp.get('filplot')

    @property
    def fileout(self):
        """Возвращает fileout из &PLOT.

        Returns:
            str | None: fileout; None, если нет.
        """
        return self.plot.get('fileout')

    def __repr__(self):
        return f'<PPIn {self.path} plot_num={self.plot_num}>'


class PPOut:
    """Парсер вывода pp.x (*.out).

    Args:
        path (str): Путь к файлу либо каталог расчёта.
        prefix (str, optional): Префикс; читается
            '{path}/result/{prefix}_{kind}.out'. По умолчанию None.
        kind (str, optional): Тип: 'charge', 'hartree' и т.п.
            По умолчанию 'charge'.

    Attributes:
        path (str): Полный путь к файлу.
        prefix (str): Префикс расчёта.
        text (str): Содержимое файла.
    """

    def __init__(self, path, prefix=None, kind='charge'):
        if prefix is not None:
            self.path = os.path.join(path, 'result', f'{prefix}_{kind}.out')
        else:
            self.path = path
        self.prefix = prefix or os.path.splitext(os.path.basename(path))[0]
        self.text = _read_text(self.path)

    @property
    def converged(self):
        """Признак успешного завершения pp.x.

        Returns:
            bool: True, если в логе есть 'JOB DONE.'.
        """
        return 'JOB DONE.' in self.text

    @property
    def plot_num(self):
        """Возвращает plot_num из лога.

        Returns:
            int | None: plot_num; None, если нет.
        """
        m = re.search(r'plot_num\s*=\s*(\d+)', self.text)
        return int(m.group(1)) if m else None

    @property
    def fileout(self):
        """Возвращает имя записанного файла.

        Returns:
            str | None: Имя файла; None, если нет.
        """
        m = re.search(r"fileout\s*=\s*'([^']+)'", self.text)
        return m.group(1) if m else None

    def __repr__(self):
        return f'<PPOut {self.path} converged={self.converged}>'


def read_xsf(path):
    """Читает объёмные данные (cube или XSF datagrid).

    Args:
        path (str): Путь к файлу.

    Returns:
        dict: {'shape': tuple[int], 'origin': list[float],
            'vectors': np.ndarray (3, 3), 'atoms': list[dict],
            'data': np.ndarray (nz, ny, nx)}.
    """
    text = _read_text(path)
    lines = text.splitlines()

    if any(l.strip().upper().startswith('BEGIN_BLOCK_DATAGRID') for l in lines):
        return _read_xsf_datagrid(lines)

    return _read_cube(path, lines)


def _read_cube(path, lines):
    natom, ox, oy, oz = lines[2].split()
    natom = int(natom)
    vecs = np.zeros((3, 3))
    shape = []
    for i in range(3):
        parts = lines[3 + i].split()
        shape.append(int(parts[0]))
        vecs[i] = [float(x) for x in parts[1:4]]
    atoms = []
    for i in range(natom):
        parts = lines[6 + i].split()
        atoms.append({'Z': int(float(parts[0])), 'coords': [float(x) for x in parts[2:5]]})
    vals = np.array([float(x) for line in lines[6 + natom:] for x in line.split()])
    nx, ny, nz = shape
    vals = vals.reshape((nz, ny, nx))
    return {'shape': tuple(shape), 'origin': [float(ox), float(oy), float(oz)],
            'vectors': vecs, 'atoms': atoms, 'data': vals}


def _read_xsf_datagrid(lines):
    vecs = np.zeros((3, 3))
    shape = None
    origin = [0.0, 0.0, 0.0]
    in_grid = False
    vals = []
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        low = s.lower()
        if low.startswith('primvec'):
            for j in range(3):
                vecs[j] = [float(x) for x in lines[i + 1 + j].split()[:3]]
            i += 4
            continue
        if low.startswith('origin'):
            origin = [float(x) for x in s.split()[1:4]]
        if low.startswith('datagrid'):
            shape = [int(x) for x in s.split()[1:4]]
            in_grid = True
            i += 1
            continue
        if low.startswith('end_datagrid'):
            in_grid = False
        if in_grid and shape:
            vals.extend(float(x) for x in s.split())
        i += 1
    nx, ny, nz = shape
    data = np.array(vals).reshape((nz, ny, nx))
    return {'shape': (nx, ny, nz), 'origin': origin, 'vectors': vecs,
            'atoms': [], 'data': data}
