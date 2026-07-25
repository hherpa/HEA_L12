# QE_run.ipynb

QE_run.ipynb предназначен для запуска **релаксации кристаллических структур (pw.x), расчёта плотности состояний и парциальных DOS (projwfc.x), а также визуализации плотности заряда и потенциала Хартри (pp.x)** для Ni, Al и Ni₃Al в Google Colab.

# Ni3Al_QE_analysis.ipynb

Ni3Al_QE_analysis.ipynb предназначен для анализа результатов расчётов, полученных в QE_run.ipynb (извлечение энергий, параметров решётки, магнитных моментов, построение DOS и PDOS, проверка сходимости) и сравнения с данными VASP (run_03). Расчёт pp.x (плотность заряда и потенциал Хартри) в этом блокноте не используется — анализ опирается на файлы `.pdos_tot`, `.pdos_atm*`, `.pw.out` и `data-file-schema.xml`.

# Структура файлов

```
├── Al
│   ├── Al_charge.in                     # ВХ: расчёт заряда (pp.x)
│   ├── Al_hartree.in                    # ВХ: расчёт потенциала Хартри (pp.x)
│   ├── Al_projwfc.in                    # ВХ: расчёт PDOS (projwfc.x)
│   ├── Al.pw.in                         # ВХ: основной SCF-расчёт (pw.x)
│   └── result
│       ├── Al_charge.out                # ВЫХ: текстовый вывод заряда
│       ├── Al_charge.xsf                # ВЫХ: 3D-карта заряда
│       ├── Al_hartree.out               # ВЫХ: текстовый вывод потенциала Хартри
│       ├── Al_hartree.xsf               # ВЫХ: 3D-карта потенциала Хартри
│       ├── Al_projwfc.out               # ВЫХ: вывод projwfc
│       ├── Al.pw.out                    # ВЫХ: основной вывод pw.x
│       ├── Al.pw.err                    # ВЫХ: ошибки/отладка pw.x
│       ├── Al.dat                       # ВЫХ: пользовательские данные (например, DOS)
│       ├── Al.pdos_tot                  # ВЫХ: полная DOS
│       ├── Al.pdos_atm#1(Al)_wfc#1(s)   # ВЫХ: PDOS атом #1, s
│       ├── Al.pdos_atm#1(Al)_wfc#2(p)   # ВЫХ: PDOS атом #1, p
│       ├── Al.pdos_atm#2(Al)_wfc#1(s)   # ВЫХ: PDOS атом #2, s
│       ├── Al.pdos_atm#2(Al)_wfc#2(p)   # ВЫХ: PDOS атом #2, p
│       ├── Al.pdos_atm#3(Al)_wfc#1(s)   # ВЫХ: PDOS атом #3, s
│       ├── Al.pdos_atm#3(Al)_wfc#2(p)   # ВЫХ: PDOS атом #3, p
│       ├── Al.pdos_atm#4(Al)_wfc#1(s)   # ВЫХ: PDOS атом #4, s
│       ├── Al.pdos_atm#4(Al)_wfc#2(p)   # ВЫХ: PDOS атом #4, p
│       ├── data-file-schema.xml         # ВЫХ: из tmp_Al/Al.save/Al.xml
│       └── Al.xml                       # ВЫХ: из tmp_Al/Al.xml
│
├── Ni
│   ├── Ni_charge.in                     # ВХ
│   ├── Ni_hartree.in                    # ВХ
│   ├── Ni_projwfc.in                    # ВХ
│   ├── Ni.pw.in                         # ВХ
│   └── result
│       ├── Ni_charge.out                # ВЫХ
│       ├── Ni_charge.xsf                # ВЫХ
│       ├── Ni_hartree.out               # ВЫХ
│       ├── Ni_hartree.xsf               # ВЫХ
│       ├── Ni_projwfc.out               # ВЫХ
│       ├── Ni.pw.out                    # ВЫХ
│       ├── Ni.pw.err                    # ВЫХ
│       ├── Ni.dat                       # ВЫХ
│       ├── Ni.pdos_tot                  # ВЫХ
│       ├── Ni.pdos_atm#1(Ni)_wfc#1(s)   # ВЫХ
│       ├── Ni.pdos_atm#1(Ni)_wfc#2(s)   # ВЫХ
│       ├── Ni.pdos_atm#1(Ni)_wfc#3(p)   # ВЫХ
│       ├── Ni.pdos_atm#1(Ni)_wfc#4(d)   # ВЫХ
│       ├── Ni.pdos_atm#2(Ni)_wfc#1(s)   # ВЫХ
│       ├── Ni.pdos_atm#2(Ni)_wfc#2(s)   # ВЫХ
│       ├── Ni.pdos_atm#2(Ni)_wfc#3(p)   # ВЫХ
│       ├── Ni.pdos_atm#2(Ni)_wfc#4(d)   # ВЫХ
│       ├── Ni.pdos_atm#3(Ni)_wfc#1(s)   # ВЫХ
│       ├── Ni.pdos_atm#3(Ni)_wfc#2(s)   # ВЫХ
│       ├── Ni.pdos_atm#3(Ni)_wfc#3(p)   # ВЫХ
│       ├── Ni.pdos_atm#3(Ni)_wfc#4(d)   # ВЫХ
│       ├── Ni.pdos_atm#4(Ni)_wfc#1(s)   # ВЫХ
│       ├── Ni.pdos_atm#4(Ni)_wfc#2(s)   # ВЫХ
│       ├── Ni.pdos_atm#4(Ni)_wfc#3(p)   # ВЫХ
│       ├── Ni.pdos_atm#4(Ni)_wfc#4(d)   # ВЫХ
│       ├── data-file-schema.xml         # ВЫХ: из tmp_Ni/Ni.save/Ni.xml
│       └── Ni.xml                       # ВЫХ: из tmp_Ni/Ni.xml
│
├── Ni3Al
│   ├── Ni3Al_charge.in                  # ВХ
│   ├── Ni3Al_hartree.in                 # ВХ
│   ├── Ni3Al_projwfc.in                 # ВХ
│   ├── Ni3Al.pw.in                      # ВХ
│   └── result
│       ├── Ni3Al_charge.out             # ВЫХ
│       ├── Ni3Al_charge.xsf             # ВЫХ
│       ├── Ni3Al_hartree.out            # ВЫХ
│       ├── Ni3Al_hartree.xsf            # ВЫХ
│       ├── Ni3Al_projwfc.out            # ВЫХ
│       ├── Ni3Al.pw.out                 # ВЫХ
│       ├── Ni3Al.pw.err                 # ВЫХ
│       ├── Ni3Al.dat                    # ВЫХ
│       ├── Ni3Al.pdos_tot               # ВЫХ
│       ├── Ni3Al.pdos_atm#1(Al)_wfc#1(s)   # ВЫХ
│       ├── Ni3Al.pdos_atm#1(Al)_wfc#2(p)   # ВЫХ
│       ├── Ni3Al.pdos_atm#2(Ni)_wfc#1(s)   # ВЫХ
│       ├── Ni3Al.pdos_atm#2(Ni)_wfc#2(s)   # ВЫХ
│       ├── Ni3Al.pdos_atm#2(Ni)_wfc#3(p)   # ВЫХ
│       ├── Ni3Al.pdos_atm#2(Ni)_wfc#4(d)   # ВЫХ
│       ├── Ni3Al.pdos_atm#3(Ni)_wfc#1(s)   # ВЫХ
│       ├── Ni3Al.pdos_atm#3(Ni)_wfc#2(s)   # ВЫХ
│       ├── Ni3Al.pdos_atm#3(Ni)_wfc#3(p)   # ВЫХ
│       ├── Ni3Al.pdos_atm#3(Ni)_wfc#4(d)   # ВЫХ
│       ├── Ni3Al.pdos_atm#4(Ni)_wfc#1(s)   # ВЫХ
│       ├── Ni3Al.pdos_atm#4(Ni)_wfc#2(s)   # ВЫХ
│       ├── Ni3Al.pdos_atm#4(Ni)_wfc#3(p)   # ВЫХ
│       ├── Ni3Al.pdos_atm#4(Ni)_wfc#4(d)   # ВЫХ
│       ├── data-file-schema.xml         # ВЫХ: из tmp_Ni3Al/Ni3Al.save/Ni3Al.xml
│       └── Ni3Al.xml                    # ВЫХ: из tmp_Ni3Al/Ni3Al.xml
```