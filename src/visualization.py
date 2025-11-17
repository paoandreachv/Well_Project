import vtk

def create_renderer():
    """ Creates and returns a VTK renderer """
    renderer = vtk.vtkRenderer()
    renderer.SetBackground(1.0, 1.0, 1.0)  # white background
    return renderer

def create_render_window(renderer):
    """ Creates and returns a VTK render window """
    render_window = vtk.vtkRenderWindow()
    render_window.AddRenderer(renderer)
    render_window.SetSize(800, 700)
    return render_window

def create_interactor(render_window):
    """ Creates and returns a VTK render window interactor """
    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(render_window)
    
    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)
    
    return interactor

def create_potential_legend():
    """Creates and return a color bar (legend) for the potencial."""
    # Create the colormap (blue to red)
    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(256)
    lut.SetTableRange(0.0, 1.0)
    lut.SetHueRange(0.667, 0.0) 
    lut.Build()

    # Create color bar
    scalar_bar = vtk.vtkScalarBarActor()
    scalar_bar.SetLookupTable(lut)
    scalar_bar.SetTitle("Potential")
    scalar_bar.SetNumberOfLabels(5)
    scalar_bar.SetMaximumWidthInPixels(100)
    scalar_bar.SetMaximumHeightInPixels(500)
    scalar_bar.SetPosition(0.88, 0.1)  # relative position in the window
    scalar_bar.SetWidth(0.08)
    scalar_bar.SetHeight(0.8)

    return scalar_bar, lut

def create_wind_rose(center, size=500):
    """Creates a wind rose with  N, S, E, W lines and labels"""
    cx, cy, cz = center
    directions = {
        "N": (0, size, 0),
        "S": (0, -size, 0),
        "E": (size, 0, 0),
        "W": (-size, 0, 0)
    }
    
    actors = []

    # Create cardinal lines
    for label, (dx, dy, dz) in directions.items():
        line_source = vtk.vtkLineSource()
        line_source.SetPoint1(cx, cy, cz)
        line_source.SetPoint2(cx + dx, cy + dy, cz + dz)
        
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(line_source.GetOutputPort())
        
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0, 0, 0)  
        actor.GetProperty().SetLineWidth(3)
        actors.append(actor)
        
        # Create labels
        text = vtk.vtkBillboardTextActor3D()
        text.SetInput(label)
        text.SetPosition(cx + dx * 1.1, cy + dy * 1.1, cz + dz * 1.05)
        text.GetTextProperty().SetColor(0, 0, 0)
        text.GetTextProperty().BoldOn()
        text.GetTextProperty().SetFontSize(20)
        actors.append(text)

    # Circle at the center to highlight
    circle = vtk.vtkRegularPolygonSource()
    circle.SetCenter(cx, cy, cz)
    circle.SetRadius(size * 0.1)
    circle.SetNumberOfSides(50)
    circle.Update()

    circle_mapper = vtk.vtkPolyDataMapper()
    circle_mapper.SetInputConnection(circle.GetOutputPort())

    circle_actor = vtk.vtkActor()
    circle_actor.SetMapper(circle_mapper)
    circle_actor.GetProperty().SetColor(0, 0, 0)
    circle_actor.GetProperty().SetOpacity(1)
    actors.append(circle_actor)

    return actors

