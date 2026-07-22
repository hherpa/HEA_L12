#!/bin/bash
#SBATCH -J TiAl_mkl17
#SBATCH -p hpc4-3d
#SBATCH -N 1
#SBATCH --ntasks-per-node=24
#SBATCH -t 72:00:00
#SBATCH -o %j.out
#SBATCH -e %j.err

module purge
module load intel-parallel-studio/2017

export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
ulimit -s unlimited

VASP=/s/ls4/users/mikk/bin/vasp.6.3.0-intel2017-mkl/vasp_std

echo "===== job ====="
hostname
date
echo "VASP=$VASP"
module list 2>&1
ldd "$VASP" | egrep -i "mkl|mpi|blas|lapack|scalapack" || true

mpirun "$VASP"