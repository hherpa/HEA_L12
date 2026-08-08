# -*- coding: utf-8 -*-
"""Парсеры pw.x: PWIn (вход), PWOut (вывод).

Public API: PWIn, PWOut, parse_namelist, _read_text.
Константы: HA_TO_EV, RY_TO_EV, BOHR_TO_A, FORCE_EV_PER_A, EV_TO_KJ_PER_MOL,
    ENERGY_UNITS, LENGTH_UNITS, FORCE_UNITS.
Единицы: аргумент units при вызове метода; по умолчанию эВ/Å/ангстрем.
"""

import os
import re

import numpy as np
import pandas as pd

HA_TO_EV = 27.211386        # Хартри -> эВ
RY_TO_EV = HA_TO_EV / 2.0   # Ридберг -> эВ
BOHR_TO_A = 0.529177        # бор -> ангстрем
# силы в QE даются в Ry/бор -> перевод в эВ/А
FORCE_EV_PER_A = RY_TO_EV / BOHR_TO_A
# постоянная Фарадея: эВ на частицу -> кДж/моль (1 эВ/частицу = 96.485 кДж/моль)
EV_TO_KJ_PER_MOL = 96.485

# Перевод из БАЗОВЫХ единиц (эВ, ангстрем, эВ/А) в запрошенные.
# Ключ (нижний регистр) -> (множитель от базовой единицы, каноническая подпись).
ENERGY_UNITS = {
    'ev': (1.0, 'eV'),
    'ry': (1.0 / RY_TO_EV, 'Ry'),
    'ha': (1.0 / HA_TO_EV, 'Ha'),
}
LENGTH_UNITS = {
    'angstrom': (1.0, 'Å'),
    'a': (1.0, 'Å'),
    'bohr': (1.0 / BOHR_TO_A, 'a0'),
    'au': (1.0 / BOHR_TO_A, 'a0'),
}
FORCE_UNITS = {
    'ev/a': (1.0, 'эВ/Å'),
    'ev/angstrom': (1.0, 'эВ/Å'),
    'ry/bohr': (1.0 / FORCE_EV_PER_A, 'Ry/a0'),
}


def _unit(units_map, units):
    """Возвращает пару (множитель, подпись) для единицы.

    Args:
        units_map (dict): {ключ: (множитель, подпись)}.
        units (str): Имя единицы (нижний регистр).

    Returns:
        tuple[float, str]: (множитель, подпись).

    Raises:
        ValueError: Неизвестная единица.
    """
    try:
        return units_map[units.lower()]
    except (KeyError, AttributeError):
        raise ValueError(f'Неизвестная единица {units!r}; доступно: {sorted(units_map)}')


def _read_text(path):
    with open(path, encoding='utf-8', errors='replace') as f:
        return f.read()


def _to_number(value):
    """Типизирует строку параметра.

    Args:
        value (str): Строковое значение.

    Returns:
        int | float | str: int/float, если value — число; иначе str.
    """
    try:
        return float(value) if any(c in value for c in '.eE') else int(value)
    except ValueError:
        return value


def parse_namelist(text):
    """Разбирает namelist-строки 'key = value' в dict.

    Args:
        text (str): Содержимое входного файла QE.

    Returns:
        dict[str, int | float | str]: Параметры; числовые значения
            типизированы, остальные — str.
    """
    params = {}
    for line in text.splitlines():
        line = line.split('!')[0].strip()
        if '=' in line and not line.startswith('&'):
            key, val = line.split('=', 1)
            params[key.strip()] = _to_number(val.strip().rstrip(',').strip("'\""))
    return params


class PWIn:
    """Парсер входного файла pw.x (*.pw.in).

    Args:
        path (str): Путь к файлу либо каталог расчёта.
        prefix (str, optional): Префикс; читается '{path}/{prefix}.pw.in'.
            По умолчанию None.

    Attributes:
        path (str): Полный путь к файлу.
        prefix (str): Префикс расчёта.
        text (str): Содержимое файла.
        params (dict): Параметры namelist; числа типизированы (float/int).
    """

    def __init__(self, path, prefix=None):
        if prefix is not None:
            self.path = os.path.join(path, f'{prefix}.pw.in')
        else:
            self.path = path
        self.prefix = prefix or os.path.splitext(os.path.basename(path))[0]
        self.text = _read_text(self.path)
        self.params = parse_namelist(self.text)

    @property
    def calculation(self):
        return self.params.get('calculation')

    def conv_thr(self, units='eV'):
        """Возвращает порог сходимости SCF conv_thr из .pw.in.

        Args:
            units (str, optional): 'eV', 'Ry' или 'Ha'. По умолчанию 'eV'.

        Returns:
            float: conv_thr в units.
        """
        factor, _ = _unit(ENERGY_UNITS, units)
        return float(self.params['conv_thr']) * RY_TO_EV * factor

    @property
    def kmesh(self):
        """Возвращает k-сетку из блока K_POINTS.

        Returns:
            tuple[int, int, int] | None: (nk1, nk2, nk3); None, если нет.
        """
        lines = self.text.splitlines()
        for i, line in enumerate(lines):
            if line.strip().upper().startswith('K_POINTS'):
                for cand in (i + 1, i + 2):
                    if cand < len(lines):
                        nums = lines[cand].split()
                        if len(nums) >= 3 and all(x.lstrip('-').isdigit() for x in nums[:3]):
                            return tuple(int(x) for x in nums[:3])
                return None
        return None

    def _alat_angstrom(self):
        """Возвращает alat в ангстремах.

        Источник: celldm(1) (боры) либо A (ангстремы) из &system.

        Returns:
            float: alat в ангстремах.

        Raises:
            ValueError: Если alat нельзя определить.
        """
        celldm1 = self.params.get('celldm(1)')
        if celldm1 is not None:
            return float(celldm1) * BOHR_TO_A
        if 'A' in self.params:
            return float(self.params['A'])
        raise ValueError('Единица "alat" требует celldm(1) или A в &system')

    @property
    def structure(self):
        """Возвращает pymatgen Structure из входного файла.

        Читает блоки CELL_PARAMETERS и ATOMIC_POSITIONS из *.in.
        Поддерживаются единицы angstrom, bohr, alat и кристаллические
        координаты (crystal).

        Returns:
            pymatgen.core.Structure: Стартовая структура в ангстремах.

        Raises:
            ValueError: Если CELL_PARAMETERS/ATOMIC_POSITIONS не найдены
                либо единица alat не определяется.
        """
        from pymatgen.core import Structure
        lines = [ln.strip() for ln in self.text.splitlines()]
        lattice = None
        species, coords = [], []
        cart = True
        i = 0
        while i < len(lines):
            line = lines[i]
            if line.upper().startswith('CELL_PARAMETERS'):
                parts = line.split()
                unit = parts[1].lower() if len(parts) > 1 else 'alat'
                lattice = np.array([[float(x) for x in lines[i + j].split()]
                                    for j in (1, 2, 3)])
                if unit == 'bohr':
                    lattice = lattice * BOHR_TO_A
                elif unit == 'alat':
                    lattice = lattice * self._alat_angstrom()
                elif unit != 'angstrom':
                    raise ValueError(f'Неизвестная единица CELL_PARAMETERS: {unit!r}')
                i += 4
            elif line.upper().startswith('ATOMIC_POSITIONS'):
                parts = line.split()
                style = parts[1].lower() if len(parts) > 1 else 'crystal'
                j = i + 1
                while j < len(lines) and lines[j]:
                    p = lines[j].split()
                    if len(p) >= 4:
                        species.append(p[0])
                        coords.append([float(x) for x in p[1:4]])
                    j += 1
                if style == 'crystal':
                    cart = False
                elif style == 'bohr':
                    coords = [[c * BOHR_TO_A for c in r] for r in coords]
                elif style == 'alat':
                    coords = [[c * self._alat_angstrom() for c in r] for r in coords]
                elif style != 'angstrom':
                    raise ValueError(f'Неизвестный стиль ATOMIC_POSITIONS: {style!r}')
                break
            else:
                i += 1
        if lattice is None:
            raise ValueError('CELL_PARAMETERS не найден во входном файле')
        if not species:
            raise ValueError('ATOMIC_POSITIONS не найден во входном файле')
        return Structure(lattice, species, coords, coords_are_cartesian=cart)

    def __repr__(self):
        return f'<PWIn {self.path} calc={self.calculation} kmesh={self.kmesh}>'


class PWOut:
    """Парсер вывода pw.x (*.pw.out).

    Args:
        path (str): Путь к файлу либо каталог расчёта.
        prefix (str, optional): Префикс; читается '{path}/result/{prefix}.pw.out'.
            По умолчанию None.

    Attributes:
        path (str): Полный путь к файлу.
        prefix (str): Префикс расчёта.
        text (str): Содержимое файла.
    """

    def __init__(self, path, prefix=None):
        if prefix is not None:
            self.path = os.path.join(path, 'result', f'{prefix}.pw.out')
        else:
            self.path = path
        self.prefix = prefix or os.path.splitext(os.path.basename(path))[0]
        self.text = _read_text(self.path)
        self._scf_rows = self._parse_scf(self.text)

    @staticmethod
    def _parse_scf(text):
        rows = []
        cur = None
        for line in text.splitlines():
            s = line.strip()
            m = re.search(r'ethr\s*=\s*([\d.Ee+-]+)', s)
            if m:
                cur = {'ethr': float(m.group(1)), 'E_Ry': np.nan, 'mag': np.nan}
                rows.append(cur)
                continue
            m = re.search(r'total energy\s*=\s*([-\d.Ee+]+)\s*Ry', s)
            if m and cur is not None:
                cur['E_Ry'] = float(m.group(1))
                continue
            if 'total magnetization' in s and 'Bohr mag/cell' in s and cur is not None:
                cur['mag'] = float(s.split('=')[1].split()[0])
        return rows

    @property
    def converged(self):
        """Признак успешного завершения pw.x.

        Returns:
            bool: True, если в логе есть 'JOB DONE.'.
        """
        return 'JOB DONE.' in self.text

    def etot(self, units='eV'):
        """Возвращает полную энергию из последней строки '! total energy'.

        Args:
            units (str, optional): 'eV', 'Ry' или 'Ha'. По умолчанию 'eV'.

        Returns:
            float | None: Энергия в units; None, если строка не найдена.
        """
        last = None
        for line in self.text.splitlines():
            s = line.strip()
            if s.startswith('!') and 'total energy' in s:
                last = float(s.split('=')[1].split()[0]) * RY_TO_EV
        return None if last is None else last * _unit(ENERGY_UNITS, units)[0]

    @property
    def total_mag(self):
        """Возвращает последнюю total magnetization.

        Returns:
            float: Магнетизация в мюБ/ячейку; 0, если расчёт неспиновый.
        """
        last = 0.0
        for line in self.text.splitlines():
            s = line.strip()
            if 'total magnetization' in s and 'Bohr mag/cell' in s:
                last = float(s.split('=')[1].split()[0])
        return last

    def efermi(self, units='eV'):
        """Возвращает уровень Ферми из вывода pw.x.

        Уровень Ферми печатается и в scf, и в nscf, и в relax-запуске;
        берётся последнее вхождение.

        Args:
            units (str, optional): 'eV', 'Ry' или 'Ha'. По умолчанию 'eV'.

        Returns:
            float | None: Уровень Ферми в units; None, если строка не найдена.
        """
        last = None
        for line in self.text.splitlines():
            s = line.strip()
            if s.startswith('the Fermi energy is'):
                last = float(s.split()[-2])
        return None if last is None else last * _unit(ENERGY_UNITS, units)[0]

    @property
    def nelec(self):
        """Возвращает число электронов из вывода pw.x.

        Returns:
            int | None: Число электронов; None, если строка не найдена.
        """
        last = None
        for line in self.text.splitlines():
            m = re.search(r'number of electrons\s*=\s*([-\d.eE+]+)', line)
            if m:
                last = float(m.group(1))
        return None if last is None else int(round(last))

    @property
    def bfgs_steps(self):
        """Возвращает число ионных шагов bfgs.

        Returns:
            int | None: Число bfgs-шагов; None, если строка не найдена.
        """
        m = re.search(r'bfgs converged in\s+\d+\s+scf cycles and\s+(\d+)\s+bfgs steps', self.text)
        return int(m.group(1)) if m else None

    def scf_cycle(self, units='eV'):
        """Возвращает SCF-итерации таблицей.

        Args:
            units (str, optional): 'eV', 'Ry' или 'Ha'. По умолчанию 'eV'.

        Returns:
            pd.DataFrame: Колонки: iter, ethr_<ед.>, E_<ед.>, |dE| (<ед.>), mag.
                mag — в мюБ/ячейку; энергетические колонки — в units.
        """
        df = pd.DataFrame(self._scf_rows)
        if df.empty:
            return df
        factor, label = _unit(ENERGY_UNITS, units)
        df.insert(0, 'iter', range(1, len(df) + 1))
        df['ethr'] = df['ethr'] * RY_TO_EV * factor
        df['E'] = df.pop('E_Ry') * RY_TO_EV * factor
        df = df.rename(columns={'ethr': f'ethr_{label}', 'E': f'E_{label}'})
        df['|dE| (' + label + ')'] = df[f'E_{label}'].diff().abs()
        return df

    def _force_blocks(self):
        blocks, cur = [], None
        for line in self.text.splitlines():
            s = line.strip()
            if s.startswith('Forces acting on atoms'):
                cur = []
                blocks.append(cur)
            elif cur is not None and s.startswith('atom') and 'force =' in s:
                vec = [float(x) for x in s.split('force =')[1].split()]
                cur.append(np.array(vec))
            elif cur is not None and s.startswith('Total force'):
                cur = None
        return blocks

    def ion_forces(self, units='eV/A'):
        """Возвращает max|F| по каждому ионному шагу.

        Args:
            units (str, optional): 'eV/A' или 'Ry/bohr'. По умолчанию 'eV/A'.

        Returns:
            pd.DataFrame: Колонки: Ионный шаг, |F_max| (<ед.>).
        """
        factor, label = _unit(FORCE_UNITS, units)
        data = []
        for i, block in enumerate(self._force_blocks()):
            if not block:
                continue
            fmax = np.max(np.linalg.norm(np.array(block), axis=1)) * FORCE_EV_PER_A * factor
            data.append({'Ионный шаг': i, f'|F_max| ({label})': fmax})
        return pd.DataFrame(data)

    def __repr__(self):
        return f'<PWOut {self.path} converged={self.converged}>'
