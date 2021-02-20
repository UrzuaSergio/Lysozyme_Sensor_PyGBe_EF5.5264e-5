#!/bin/bash

#SBATCH -p gpuk
#SBATCH --gres=gpu:1
#SBATCH -J 1hel_84-100_EF-5.5264e-4
#SBATCH -o 1hel_84-100_EF-5.5264e-4-%j.out
#SBATCH -e 1hel_84-100_EF-5.5264e-4-%j.err
#SBATCH --mem=2G
#SBATCH --time=55:00:00
#SBATCH --mail-user=sergio.urzua.13@sansano.usm.cl
#SBATCH --mail-type=BEGIN,END,FAIL

use cuda10
use anaconda3

export PYTHONPATH=/user/s/surzua/PyCuda/pycuda/lib/python

cd ../../Lysozyme_Sensor_PyGBe_EF-5.5264e-4/
###############################################################################################################################################################
echo "Simulación que contempla las siguientes Orientaciones:"
echo "Tilt begin: 84° - Tilt_end: 100° - Ntilt: 5 -- Rot begin: 0° - Rot end: 360° - Nrot: 36"
echo "...................................................................................."
echo "Proteina: Lisozima."
echo "Separación: 0.2 nm"
python generador_config_file.py 1hel_isolated 1hel mesh/1hel_d16_split 84 100 2

echo "Se ha Creado Config File Auxiliar"
echo "Comenzo Ejecucion de PyGBe para Caso Proteina-Superficie Interactuando"
echo "%%%%%%%% Simulando %%%%%%%%"

python conformation_1hel.py 1hel_isolated 1hel_isolated/1hel 1hel_isolated/mesh/1hel_d16_split 84 100 5 2 1hel-isolated_84-100-2_EF-5.5264e-4

echo "Termino Ejecucion de PyGBe para Caso Proteina-Superficie Interactuando"
##############################################################################################################################################################
