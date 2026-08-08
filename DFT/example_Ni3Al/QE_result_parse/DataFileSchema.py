# -*- coding: utf-8 -*-
"""Парсер data-file-schema.xml: XML-схемы результатов QE.

Public API: DataFileSchema.
Константы-источники: HA_TO_EV, BOHR_TO_A, RY_TO_EV, ENERGY_UNITS, LENGTH_UNITS.
Единицы: аргумент units при вызове метода; по умолчанию эВ/ангстрем.
"""

import os
import xml.etree.ElementTree as ET

import numpy as np

from .pw import (HA_TO_EV, BOHR_TO_A, RY_TO_EV, ENERGY_UNITS, LENGTH_UNITS, _unit)


class DataFileSchema:
    """Парсер data-file-schema.xml.

    Args:
        path (str): Путь к XML либо каталог расчёта.
        prefix (str, optional): Префикс; читается
            '{path}/result/data-file-schema.xml'. По умолчанию None.

    Attributes:
        path (str): Полный путь к файлу.
        prefix (str): Префикс расчёта.
        root (xml.etree.ElementTree.Element): Корень XML.
    """

    def __init__(self, path, prefix=None):
        if prefix is not None:
            self.path = os.path.join(path, 'result', 'data-file-schema.xml')
            self.prefix = prefix
        else:
            self.path = path
            self.prefix = prefix or os.path.basename(os.path.dirname(path))
        self.root = ET.parse(self.path).getroot()

    def _text(self, xpath):
        el = self.root.find(xpath)
        if el is not None and el.text:
            return el.text.strip()
        return None

    @property
    def calculation(self):
        return self._text('.//input/control_variables/calculation')

    def etot(self, units='eV'):
        """Возвращает полную энергию из XML.

        Args:
            units (str, optional): 'eV', 'Ry' или 'Ha'. По умолчанию 'eV'.

        Returns:
            float | None: Энергия в units; None, если отсутствует (nscf etot=0).
        """
        t = self._text('.//output/total_energy/etot')
        if t is None:
            return None
        v = float(t)
        if abs(v) < 1e-12:
            return None
        return v * HA_TO_EV * _unit(ENERGY_UNITS, units)[0]

    def efermi(self, units='eV'):
        """Возвращает уровень Ферми.

        Args:
            units (str, optional): 'eV', 'Ry' или 'Ha'. По умолчанию 'eV'.

        Returns:
            float | None: Уровень Ферми в units; None, если отсутствует.
        """
        t = self._text('.//output/band_structure/fermi_energy')
        if t is None:
            return None
        return float(t) * HA_TO_EV * _unit(ENERGY_UNITS, units)[0]

    @property
    def nelec(self):
        """Возвращает число электронов.

        Returns:
            int | None: Число электронов; None, если отсутствует.
        """
        t = self._text('.//output/band_structure/nelec')
        return None if t is None else int(round(float(t)))

    @property
    def total_mag(self):
        """Возвращает магнетизацию.

        Returns:
            float | None: Магнетизация в мюБ/ячейку; None, если отсутствует.
        """
        t = self._text('.//output/magnetization/total')
        return None if t is None else float(t)

    @property
    def kmesh(self):
        """Возвращает k-сетку из monkhorst_pack.

        Returns:
            tuple[int, int, int] | None: (nk1, nk2, nk3); None, если отсутствует.
        """
        mp = self.root.find('.//k_points_IBZ/monkhorst_pack')
        if mp is None:
            return None
        return tuple(int(mp.get(k)) for k in ('nk1', 'nk2', 'nk3'))

    @property
    def n_atoms(self):
        """Возвращает число атомов.

        Returns:
            int | None: Число атомов; None, если отсутствует.
        """
        el = self.root.find('.//input/atomic_structure')
        return int(el.get('nat')) if el is not None else None

    def cell(self, units='angstrom'):
        """Возвращает ячейку.

        Args:
            units (str, optional): 'angstrom' или 'bohr'. По умолчанию 'angstrom'.

        Returns:
            np.ndarray: Матрица (3, 3) в units.
        """
        cs = self.root.find('.//input/atomic_structure/cell')
        c = np.array([[float(x) for x in cs.find(f'a{i}').text.split()]
                      for i in range(1, 4)])
        return c * BOHR_TO_A * _unit(LENGTH_UNITS, units)[0]

    def atoms(self, units='angstrom'):
        """Возвращает позиции атомов.

        Args:
            units (str, optional): 'angstrom' или 'bohr'. По умолчанию 'angstrom'.

        Returns:
            list[dict]: [{name: str, coords_<ед.>: list[float] (3)}].
        """
        pos = self.root.find('.//input/atomic_structure/atomic_positions')
        factor, label = _unit(LENGTH_UNITS, units)
        out = []
        for a in pos.findall('atom'):
            out.append({'name': a.get('name'),
                        f'coords_{label}': [float(x) * BOHR_TO_A * factor
                                            for x in a.text.split()]})
        return out

    @property
    def structure(self):
        """Возвращает pymatgen Structure.

        Returns:
            pymatgen.core.Structure: В ангстремах, декартовы координаты.
        """
        from pymatgen.core import Structure
        species = [a['name'] for a in self.atoms(units='angstrom')]
        coords = [a['coords_Å'] for a in self.atoms(units='angstrom')]
        return Structure(lattice=self.cell(units='angstrom').tolist(),
                         species=species, coords=coords,
                         coords_are_cartesian=True)

    def __repr__(self):
        return f'<DataFileSchema {self.path} calc={self.calculation}>'
