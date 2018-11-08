import vtk
import numpy as np
from vtk.util.colors import tomato

cam_height = 28


def LST_tel_structure():
    # ARCH CREATOR
    res_arch = 100
    nsidestube = 8

    dist = np.linspace(-11.5, 11.5, res_arch)
    points = vtk.vtkPoints()
    for i in range(len(dist)):
        x_coord = -28/300*dist[i]**2 - 0.001*dist[i]**4 + cam_height
        y_coord = 0
        z_coord = dist[i]
        points.InsertPoint(i, x_coord, y_coord, z_coord)
    lines = vtk.vtkCellArray()
    lines.InsertNextCell(res_arch)

    for i in range(len(dist)):
        lines.InsertCellPoint(i)

    polyData = vtk.vtkPolyData()
    polyData.SetPoints(points)
    polyData.SetLines(lines)

    tube = vtk.vtkTubeFilter()
    tube.SetInputData(polyData)
    tube.SetNumberOfSides(nsidestube)
    tube.SetRadius(0.2)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(tube.GetOutputPort())
    # mapper.ScalarVisibilityOn()
    mapper.SetScalarModeToUsePointFieldData()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor(tomato)

    return actor


def LST_create_mirror_plane():
    # create a sphere
    sphere = vtk.vtkSphere()
    sphere.SetRadius(12)
    sphere.SetCenter(0, 0, 0)

    # create a box
    box = vtk.vtkSphere()
    box.SetRadius(28.)
    box.SetCenter(25, 0, 0)

    # box = vtk.vtkBox()
    # box.SetBounds(-1, 1, -1, 1, -1, 1)

    # combine the two implicit functions
    boolean = vtk.vtkImplicitBoolean()
    boolean.SetOperationTypeToDifference()

    # boolean.SetOperationTypeToUnion()
    # boolean.SetOperationTypeToIntersection()
    boolean.AddFunction(sphere)
    boolean.AddFunction(box)

    # The sample function generates a distance function from the implicit
    # function. This is then contoured to get a polygonal surface.
    sample = vtk.vtkSampleFunction()
    sample.SetImplicitFunction(boolean)
    sample.SetModelBounds(-50, 50, -50, 50, -50, 50)
    sample.SetSampleDimensions(200, 200, 200)
    sample.ComputeNormalsOff()

    # contour
    surface = vtk.vtkContourFilter()
    surface.SetInputConnection(sample.GetOutputPort())
    surface.SetValue(0, 0.0)

    # mapper
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(surface.GetOutputPort())
    #mapper.ScalarVisibilityOff()
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    #actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().SetColor(tomato)

    return actor
