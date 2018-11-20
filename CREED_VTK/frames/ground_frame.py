import numpy as np
import vtk

from ..utils.transf_utils import scale_object


def create_ground_frame(size=300):
    planeSource = vtk.vtkPlaneSource()
    planeSource.SetXResolution(10)
    planeSource.SetYResolution(10)
    planeSource.SetCenter(0.0, 0.0, 0.0)
    planeSource.SetNormal(0.0, 0.0, 1.0)
    planeSource.Update()

    scaled_plane = scale_object(planeSource, size)

    # Create a mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(scaled_plane.GetOutput())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().LightingOff()
    actor.GetProperty().SetOpacity(0.5)
    return actor
