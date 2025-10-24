import vtk
import numpy as np
from visualization import create_renderer, create_render_window, create_interactor
import well_data as wd
from vtk.util import numpy_support #type: ignore

# Hay que activar cada grafo por separado -> hagamos que el usuario pueda elegir qué grafo activar
# Verificar las líneas de rumbo y manteo, pues parecieran estar chuecas 
# Ver si podemos fijar la rosa de los vientos en una esquina y que rote cuando rotemos la escena, pero que no se mueva de lugar
# Añadir potencial con marca de los números que también sea fijo
# Se tiene que agregar lo de los grafos en la misma ventana y que se le de la opción de si quiere agrearlos o no, y cuál quisiera agregar

# -----------------------------
# 1️⃣ Función para crear puntos
# -----------------------------
def create_points(df):
    """Crea puntos VTK a partir de las columnas X, Y, Z de un DataFrame."""
    coords = df[["X", "Y", "Z"]].to_numpy(dtype=float)
    
    points = vtk.vtkPoints()
    points.SetData(numpy_support.numpy_to_vtk(coords))
    
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    
    return polydata

# -----------------------------
# 2️⃣ Función para crear líneas coloreadas según Seg_id y potential
# -----------------------------
def connect_edges_with_potential(edges):
    """Crea vtkPolyData con líneas conectadas y coloreadas según potential."""
    append_filter = vtk.vtkAppendPolyData()

    for df in edges:
        for seg_id, group in df.groupby("Seg_id"):
            if len(group) < 2:
                continue  # necesitamos al menos 2 puntos para la línea

            points_polydata = create_points(group)
            points = points_polydata.GetPoints()

            line = vtk.vtkLine()
            line.GetPointIds().SetId(0, 0)
            line.GetPointIds().SetId(1, 1)

            lines = vtk.vtkCellArray()
            lines.InsertNextCell(line)

            potential_array = numpy_support.numpy_to_vtk(
                group["potential"].to_numpy(dtype=float)
            )
            potential_array.SetName("potential")

            line_polydata = vtk.vtkPolyData()
            line_polydata.SetPoints(points)
            line_polydata.SetLines(lines)
            line_polydata.GetPointData().SetScalars(potential_array)

            append_filter.AddInputData(line_polydata)

    append_filter.Update()
    return append_filter.GetOutput()

# -----------------------------
# 3️⃣ Función para renderizar usando tus funciones existentes
# -----------------------------
def render_edges_with_custom_renderer(polydata):
    # Crear renderer, render window e interactor usando tus funciones
    renderer = create_renderer()
    render_window = create_render_window(renderer)
    interactor = create_interactor(render_window)

    # Mapper y actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polydata)
    mapper.SetScalarModeToUsePointData()
    mapper.SetColorModeToMapScalars()
    mapper.SetScalarRange(0, 1)
    mapper.ScalarVisibilityOn()

    # Crear lookup table azul → rojo
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.SetTableRange(0.0, 1.0)
    lut.SetHueRange(0.667, 0.0)  # azul → rojo
    lut.Build()
    mapper.SetLookupTable(lut)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetLineWidth(3)

    # Agregar actor y barra de color
    renderer.AddActor(actor)

    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(lut)
    scalar_bar.SetTitle("Potential")
    scalar_bar.SetNumberOfLabels(5)
    renderer.AddActor2D(scalar_bar)

    # Iniciar render
    render_window.Render()
    interactor.Start()

# -----------------------------
# 4️⃣ Uso
# -----------------------------
# edges = wd.edges  # tu lista de DataFrames
polydata_edges = connect_edges_with_potential(wd.edges)
render_edges_with_custom_renderer(polydata_edges)
