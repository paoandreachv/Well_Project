import vtk
from src.visualization import create_renderer, create_render_window, create_interactor
from vtk.util import numpy_support #type: ignore

def select_points(df):
    coords = df[["X", "Y", "Z"]].to_numpy(dtype=float)
    points = vtk.vtkPoints()
    points.SetData(numpy_support.numpy_to_vtk(coords))
    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)
    return polydata

def connect_edges_with_potential(df):
    """
    Crea vtkPolyData con líneas conectadas y coloreadas según 'potential'.
    Devuelve un vtkPolyData.
    """
    append_filter = vtk.vtkAppendPolyData()

    for seg_id, group in df.groupby("Seg_id"):
        if len(group) < 2 or seg_id == 0:
            continue

        points_polydata = select_points(group)
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


def select_edges(wd, connect_edges_with_potential, lut):
    """
    Pregunta al usuario qué grafos mostrar y devuelve lista de vtkActors.
    Cada actor se colorea según 'potential' usando el LUT proporcionado.
    """
    edges_list = wd.edges  # lista de DataFrames

    print("Archivos disponibles en wd.edges:")
    for i, df in enumerate(edges_list):
        print(f"{i}: {len(df)} puntos, Seg_id únicos: {df['Seg_id'].nunique()}")

    print("\n👉 Escribe el número del archivo que quieres visualizar.")
    print("   Puedes escribir varios separados por comas (ej: 0,2,3)")
    print("   O escribe 'ninguno' para no mostrar nada.\n")

    choice = input("Tu selección: ").strip().lower()
    if choice in ("ninguno", "", "no", "n"):
        print("❎ No se mostrará ningún grafo.")
        return []

    try:
        indices = [int(c.strip()) for c in choice.split(",") if c.strip().isdigit()]
        valid_indices = [i for i in indices if 0 <= i < len(edges_list)]

        if not valid_indices:
            print("⚠️ No se seleccionó ningún índice válido.")
            return []

        print(f"Mostrando archivos: {valid_indices}")

        # Combinar los edges seleccionados
        append_filter = vtk.vtkAppendPolyData()
        has_data = False  # bandera para saber si agregamos algo
        for idx in valid_indices:
            polydata = connect_edges_with_potential(edges_list[idx])
            if polydata.GetNumberOfPoints() > 0:  # ignorar archivos vacíos
                append_filter.AddInputData(polydata)
                has_data = True

        if not has_data:
            print("⚠️ No hay edges válidos para mostrar en los archivos seleccionados.")
            return []

        # Solo actualizar si hay datos
        append_filter.Update()

        
        # Mapper y actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(append_filter.GetOutput())
        mapper.SetLookupTable(lut)
        mapper.SetColorModeToMapScalars()
        mapper.SetScalarRange(0, 1)  # ajusta si tu rango de potential es diferente
        mapper.ScalarVisibilityOn()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(2)

        return [actor]

    except ValueError:
        print("⚠️ Entrada inválida. Debes ingresar números o 'ninguno'.")
        return []
