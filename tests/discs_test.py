import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import vtk
from src.detailed_functions import orient_disc_with_manteo, create_transformed_geometry

