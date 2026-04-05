# pymatgen Structure

> Объект **Structure** — это центральное понятие в Pymatgen, содержащее всю информацию о кристаллической решетке, ее атомах и их координатах.

Вы можете создать минимальную структуру, задав:
1. **Параметры решетки (Lattice)**
2. **Типы атомов (species)**
3. **Дробные координаты (coords)**
4. **Пространственную группу (sg)**

Пример на примитивной ячейке:
```python
# Параметры структуры
a = 5.4307
lattice = Lattice.cubic(a)
species = ["Si", "Si"]
coords = [[0, 0, 0], [0.25, 0.25, 0.25]]

# Создаем объект Structure
structure = Structure(lattice, species, coords)

# Экспорт в CIF
writer = CifWriter(si_structure)
writer.write_file("Si_elementary_cell.cif")
```

### Параметры решетки (Lattice)
1. Выбор сингонии
* Пример *(по количеству аргументов)*:
    1. `Lattice.cubic(a)`
    2. `Lattice.tetragonal(a, c)` 
    3. `Lattice.orthorhombic(a, b, c)`
    4. `Lattice.monoclinic(a, b, c, beta)`

2. Указание аргументов сингоний. 
    1. Длина решетки указываается в ангстремах. Например, для кремния `a = 5.43 Å` — это экспериментальная постоянная решётки.
    2. Угол между векторами `beta` указывается просто в градусах.

### Сохранение в CIF с CifWriter:

```python
from pymatgen.io.cif import CifWriter

# Предположим, у нас есть объект 'structure'
cif_writer = CifWriter(structure)
cif_writer.write_file("my_crystal.cif")
```

### Пространственная группа (sg)

> **Пространственная группа (sg)** — это математическое понятие, описывающее полную симметрию кристаллической решетки, включая все возможные операции симметрии (повороты, отражения, инверсии, сдвиги и их комбинации). Всего существует 230 пространственных групп, и каждая имеет свой уникальный номер и символ.

Указание пространственной группы дает построение симметричной ячейки:
```python
# Параметры структуры
a = 5.4307
lattice = Lattice.cubic(a)
species=["Si"]
coords=[[0, 0, 0]]
sg="Fd-3m"

# Создаем объект Structure
structure = Structure.from_spacegroup(sg, lattice, species, coords)

# Экспорт в CIF
writer = CifWriter(structure)
writer.write_file("Si_Fd3m.cif")
```
