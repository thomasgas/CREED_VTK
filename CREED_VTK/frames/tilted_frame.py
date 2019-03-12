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
    transform_text.RotateZ(- array_pointing.az.value)
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


def add_tilted_positions(tilted_positions, array_pointing):
    points = vtk.vtkPoints()

    for tel_id in tilted_positions.keys():
        tel_pos = tilted_positions[tel_id]
        points.InsertNextPoint(tel_pos[0],
                               tel_pos[1],
                               tel_pos[2])

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
    actor.RotateZ(- array_pointing.az.value)
    actor.RotateY(90 - array_pointing.alt.value)

    return actor
