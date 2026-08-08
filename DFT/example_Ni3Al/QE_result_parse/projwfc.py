# -*- coding: utf-8 -*-
"""Чтение DOS projwfc.x: полный (*.pdos_tot) и по элементам (*.pdos_atm#*).

Public API: load_tdos, load_element_dos.
"""

import glob
import os
import re

import numpy as np


def load_tdos(path):
    """Читает полный DOS из *.pdos_tot.

    Args:
        path (str): Путь к файлу *.pdos_tot.

    Returns:
        tuple[np.ndarray, np.ndarray, np.ndarray]: (E, dos_up, dos_dn).
            E: энергия, эВ.
            dos_up: DOS спина up.
            dos_dn: DOS спина down; 0, если файл без спина.
    """
    data = np.loadtxt(path, skiprows=1)
    e = data[:, 0]
    if data.shape[1] >= 5:
        return e, data[:, 1], data[:, 2]
    return e, data[:, 1], np.zeros_like(e)


def _pdos_files(result_dir, prefix):
    return sorted(glob.glob(os.path.join(result_dir, f'{prefix}.pdos_atm#*')))


def load_element_dos(result_dir, prefix):
    """Суммирует парциальный DOS по элементам.

    Args:
        result_dir (str): Каталог с файлами *.pdos_atm#*.
        prefix (str): Префикс расчёта.

    Returns:
        dict[str, dict]: {elem: {'energy': np.ndarray, 'up': np.ndarray,
            'dn': np.ndarray}}. energy — эВ; up/dn — сумма всех l,m-компонент.
    """
    files = _pdos_files(result_dir, prefix)
    element_files = {}
    for f in files:
        elem = re.search(r'atm#\d+\((\w+)\)', os.path.basename(f)).group(1)
        element_files.setdefault(elem, []).append(f)

    element_dos = {}
    for elem, elem_files in element_files.items():
        energy = None
        up = dn = None
        for f in elem_files:
            data = np.loadtxt(f, skiprows=1)
            if energy is None:
                energy = data[:, 0]
                up = np.zeros_like(energy)
                dn = np.zeros_like(energy)
            n = data.shape[1]
            if n >= 5:
                # колонки 0=E, 1=ldosup, 2=ldosdw, далее пары pdosup/pdosdw по m
                up += data[:, 3::2].sum(axis=1)
                dn += data[:, 4::2].sum(axis=1)
            elif n == 3:
                up += data[:, 2]
        element_dos[elem] = {'energy': energy, 'up': up, 'dn': dn}
    return element_dos
