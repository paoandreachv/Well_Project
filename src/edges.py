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
    """ Creates a vtkPolyData with connected lines colored according to 'potential' """
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
    """ Ask user which indices to visualize """
    edges_list = wd.edges  # lista de DataFrames

    print("Files avaliables in wd.edges:")
    for i, df in enumerate(edges_list):
        print(f"{i}: {len(df)} points, unique Seg_id: {df['Seg_id'].nunique()}")

    print(
        "Type the number of the file you want to visualize. You can type several separated " 
        "by commas (e.g : 0,1,2) or 'none' to skip visualization.")
    
    choice = input("Your selection: ").strip().lower()
    if choice in ("none", "", "no", "n", " "):
        print("No graph will be displayed.")
        return []

    try:
        indices = [int(c.strip()) for c in choice.split(",") if c.strip().isdigit()]
        valid_indices = [i for i in indices if 0 <= i < len(edges_list)]

        if not valid_indices:
            print("No valid index was selected.")
            return []

        print(f"Showing files: {valid_indices}")

        append_filter = vtk.vtkAppendPolyData()
        has_data = False  
        for idx in valid_indices:
            polydata = connect_edges_with_potential(edges_list[idx])
            if polydata.GetNumberOfPoints() > 0:  
                append_filter.AddInputData(polydata)
                has_data = True

        if not has_data:
            print("No valid edges found in the selected files.")
            return []

        append_filter.Update()

        # Mapper and Actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(append_filter.GetOutput())
        mapper.SetLookupTable(lut)
        mapper.SetColorModeToMapScalars()
        mapper.SetScalarRange(0, 1)  
        mapper.ScalarVisibilityOn()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetLineWidth(2)

        return [actor]

    except ValueError:
        print("Invalid input. You must enter numbers or 'none'.")
        return []
