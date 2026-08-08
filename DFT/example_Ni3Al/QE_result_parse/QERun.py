# -*- coding: utf-8 -*-
"""Обёртка QERun: один QE-расчёт (каталог + префикс).

Public API: QERun.
"""

import os

from .pw import PWIn, PWOut
from .DataFileSchema import DataFileSchema
from .projwfc import load_tdos, load_element_dos


class QERun:
    """Обёртка над одним QE-расчётом.

    Основной расчёт — relax/scf: {prefix}.pw.in -> {prefix}.pw.out.
    Из него берутся все физические величины (etot, E_F, магнетизация,
    nelec). XML (data-file-schema.xml) соответствует последнему запуску
    pw.x в каталоге (обычно утилитный nscf для DOS/зон) и служит
    источником структуры и k-сетки.

    Args:
        work_dir (str): Каталог расчёта.
        prefix (str, optional): Префикс. По умолчанию — имя каталога.

    Attributes:
        dir (str): Каталог расчёта.
        prefix (str): Префикс расчёта.
        pw_in (PWIn): Входной файл основного расчёта.
        pw_out (PWOut): Вывод основного расчёта (relax/scf).
        xml (DataFileSchema): data-file-schema.xml.
    """

    def __init__(self, work_dir, prefix=None):
        self.dir = work_dir
        self.prefix = prefix or os.path.basename(work_dir)
        self.pw_in = PWIn(work_dir, self.prefix)
        self.pw_out = PWOut(work_dir, self.prefix)
        self.xml = DataFileSchema(work_dir, self.prefix)

    def etot(self, units='eV'):
        """Возвращает полную энергию релаксации из {prefix}.pw.out.

        Args:
            units (str, optional): 'eV', 'Ry' или 'Ha'. По умолчанию 'eV'.

        Returns:
            float | None: Энергия в units; None, если нет.
        """
        return self.pw_out.etot(units=units)

    @property
    def total_mag(self):
        """Возвращает магнетизацию из {prefix}.pw.out.

        Returns:
            float: Магнетизация в мюБ/ячейку; 0, если расчёт неспиновый.
        """
        return self.pw_out.total_mag

    def efermi(self, units='eV'):
        """Возвращает уровень Ферми из {prefix}.pw.out.

        Args:
            units (str, optional): 'eV', 'Ry' или 'Ha'. По умолчанию 'eV'.

        Returns:
            float | None: Уровень Ферми в units; None, если нет.
        """
        return self.pw_out.efermi(units=units)

    @property
    def nelec(self):
        """Возвращает число электронов из {prefix}.pw.out.

        Returns:
            int | None: Число электронов; None, если нет.
        """
        return self.pw_out.nelec

    @property
    def kmesh_xml(self):
        """Возвращает k-сетку из XML (последний запуск pw.x, обычно nscf).

        Returns:
            tuple[int, int, int] | None: (nk1, nk2, nk3); None, если нет.
        """
        return self.xml.kmesh

    @property
    def kmesh_in(self):
        """Возвращает k-сетку из входного файла.

        Returns:
            tuple[int, int, int] | None: (nk1, nk2, nk3); None, если нет.
        """
        return self.pw_in.kmesh

    @property
    def structure(self):
        """Возвращает pymatgen Structure.

        Returns:
            pymatgen.core.Structure: В ангстремах.
        """
        return self.xml.structure

    def scf_cycle(self, units='eV'):
        """Возвращает SCF-итерации из .pw.out.

        Args:
            units (str, optional): 'eV', 'Ry' или 'Ha'. По умолчанию 'eV'.

        Returns:
            pd.DataFrame: См. PWOut.scf_cycle.
        """
        return self.pw_out.scf_cycle(units=units)

    def ion_forces(self, units='eV/A'):
        """Возвращает max|F| по ионным шагам из .pw.out.

        Args:
            units (str, optional): 'eV/A' или 'Ry/bohr'. По умолчанию 'eV/A'.

        Returns:
            pd.DataFrame: См. PWOut.ion_forces.
        """
        return self.pw_out.ion_forces(units=units)

    @property
    def converged(self):
        """Признак успешного завершения расчёта.

        Returns:
            bool: True, если в логе есть 'JOB DONE.'.
        """
        return self.pw_out.converged

    @property
    def bfgs_steps(self):
        """Возвращает число ионных шагов bfgs.

        Returns:
            int | None: Число bfgs-шагов; None, если нет.
        """
        return self.pw_out.bfgs_steps

    def tdos(self):
        """Возвращает полный DOS.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray]: (E, dos_up, dos_dn).
                См. projwfc.load_tdos.
        """
        return load_tdos(os.path.join(self.dir, 'result', f'{self.prefix}.pdos_tot'))

    def element_dos(self):
        """Возвращает парциальный DOS по элементам.

        Returns:
            dict[str, dict]: {elem: {'energy', 'up', 'dn'}}.
                См. projwfc.load_element_dos.
        """
        return load_element_dos(os.path.join(self.dir, 'result'), self.prefix)

    def __repr__(self):
        e = self.etot()
        s = f'<QERun {self.prefix}'
        if e is not None:
            s += f' etot={e:.2f} eV'
        return s + '>'
