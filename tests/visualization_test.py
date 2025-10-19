import vtk
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.visualization import create_renderer, create_render_window, create_interactor

# Test to create a renderer
renderer = create_renderer()
assert isinstance(renderer, vtk.vtkRenderer)
r, g, b = renderer.GetBackground()
assert (r, g, b) == (1, 1, 1)
assert not (r, g, b) == ( 0, 0, 0)

# Test to create a render window
render_window = create_render_window(renderer)
assert isinstance(render_window, vtk.vtkRenderWindow)
assert render_window.HasRenderer(renderer)
width, height = render_window.GetSize()
assert (width, height) == (800, 700)
assert not (width, height) == (1000, 700)

# Test to create a render window interactor
interactor = create_interactor(render_window)
assert isinstance(interactor, vtk.vtkRenderWindowInteractor)
assert interactor.GetRenderWindow() is render_window
style = interactor.GetInteractorStyle()
assert isinstance(style, vtk.vtkInteractorStyleTrackballCamera)