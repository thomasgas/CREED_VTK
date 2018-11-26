import vtk

from ..utils.transf_utils import scale_object

from ctapipe.coordinates import TiltedGroundFrame


def create_tilted_frame(array_pointing, size=300):
    planeSource = vtk.vtkPlaneSource()
    planeSource.SetXResolution(10)
    planeSource.SetYResolution(10)
    planeSource.SetCenter(0.0, 0.0, 0.0)
    planeSource.SetNormal(0.0, 0.0, 1.0)
    planeSource.Update()

    transform_text = vtk.vtkTransform()
    transform_text.Scale(size, size, size)
    transform_text.RotateZ(array_pointing.az.value)
    transform_text.RotateY(90 - array_pointing.alt.value)
    transform_text_axes = vtk.vtkTransformFilter()
    transform_text_axes.SetTransform(transform_text)
    transform_text_axes.SetInputConnection(planeSource.GetOutputPort())
    transform_text_axes.Update()

    # Create a mapper and actor
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(transform_text_axes.GetOutput())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    actor.GetProperty().EdgeVisibilityOn()
    actor.GetProperty().LightingOff()
    actor.GetProperty().SetOpacity(0.3)
    actor.GetProperty().SetColor([0, 255, 0])

    return actor


def add_tilted_positions(tel_coords_gnd, list_tel_ids, array_pointing):
    # subarray = event.inst.subarray
    # tel_coords_gnd = subarray.tel_coords

    tilted_system = TiltedGroundFrame(pointing_direction=array_pointing)
    tilt_tel_pos = tel_coords_gnd.transform_to(tilted_system)

    # lut = MakeLUTFromCTF(image_cal)
    points = vtk.vtkPoints()

    for tel_id in list_tel_ids:
        tel_x_pos = tilt_tel_pos.x[tel_id - 1].value
        tel_y_pos = tilt_tel_pos.y[tel_id - 1].value
        tel_z_pos = 0
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
    actor.GetProperty().SetColor([0, 255, 0])
    actor.RotateZ(array_pointing.az.value)
    actor.RotateY(90 - array_pointing.alt.value)

    return actor
