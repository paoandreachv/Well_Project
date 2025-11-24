import vtk, random

##################################################################
# ---------------------------COLORS----------------------------- #
##################################################################
def generate_distinct_colors(n_colors):
    """ Build a random color table for each marker """
    table = vtk.vtkLookupTable()
    table.SetNumberOfTableValues(n_colors)
    table.Build()
    random.seed(0)
    for i in range(n_colors):
        table.SetTableValue(i, random.random(), random.random(), random.random(), 1.0)
    return table