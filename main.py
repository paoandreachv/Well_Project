import src.well_data as data
import src.vtk_objects as vtk_objects
import src.visualization as visualization
import src.edges as edges_mod


def main():
    # Load data
    well_data = data.load_well_data()
    well_trajectories = data.load_well_trajectories()
    scalar_bar, lut = visualization.create_potential_legend()


    edges_actors = edges_mod.select_edges(
        wd= data,  # módulo donde está tu lista wd.edges
        connect_edges_with_potential=edges_mod.connect_edges_with_potential,
        lut = lut
    )
    
    # Create geometry
    polydata, unique_markers = vtk_objects.create_points(well_data)
    point_actors = vtk_objects.create_filledpolygon_actor(polydata, unique_markers)
    line_actors = vtk_objects.create_well_line_actors(well_trajectories)
    
    # Calculate center of wind rose
    min_x = well_data["X"].min()
    max_x = well_data["X"].max()
    min_y = well_data["Y"].min()
    min_z = well_data["Z"].min()

    corner_x = max_x
    corner_y = min_y
    corner_z = min_z

    offset = 0.2 * (max_x - min_x)
    corner_x += offset
    corner_y -= offset

    # Create wind rose
    wind_rose_actors = visualization.create_wind_rose(center=(corner_x, corner_y, corner_z), size=1000)

    # Setup visualization
    renderer = visualization.create_renderer()
    
    # Add actors to renderer
    for actor in point_actors + line_actors + edges_actors + wind_rose_actors:
        renderer.AddActor(actor)

    renderer.AddViewProp(scalar_bar)
    
    render_window = visualization.create_render_window(renderer)
    interactor = visualization.create_interactor(render_window)

    # Render
    render_window.Render()
    interactor.Start()

if __name__ == "__main__":
    main()
