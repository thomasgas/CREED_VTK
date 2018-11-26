import numpy as np
import vtk

from ..utils.transf_utils import scale_object
from ..utils.colors import MakeLUTFromCTF


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
    actor.GetProperty().SetOpacity(0.3)
    actor.GetProperty().SetColor([255, 0, 0])
    return actor


def create_ground_positions(event, list_tel_ids):
    subarray = event.inst.subarray
    tel_coords_gnd = subarray.tel_coords

    # lut = MakeLUTFromCTF(image_cal)
    points = vtk.vtkPoints()

    for tel_id in list_tel_ids:
        tel_x_pos = tel_coords_gnd.x[tel_id - 1].value
        tel_y_pos = tel_coords_gnd.y[tel_id - 1].value
        tel_z_pos = tel_coords_gnd.z[tel_id - 1].value
        points.InsertNextPoint(tel_x_pos, tel_y_pos, tel_z_pos)

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)

    tel_source = vtk.vtkSphereSource()
    tel_source.SetRadius(10)
    tel_source.SetThetaResolution(20)
    tel_source.SetPhiResolution(20)
    tel_source.Update()

    glyph = vtk.vtkGlyph3D()

    glyph.SetInputData(polydata)
    glyph.SetSourceConnection(tel_source.GetOutputPort())
    glyph.SetColorModeToColorByScalar()
    glyph.SetVectorModeToUseNormal()
    glyph.ScalingOff()
    glyph.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(glyph.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().SetColor([255, 0, 0])

    return actor

