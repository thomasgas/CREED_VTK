import vtk

from ..utils.transf_utils import scale_object


def create_tilted_frame(dict_pointing, size=300):
    planeSource = vtk.vtkPlaneSource()
    planeSource.SetXResolution(10)
    planeSource.SetYResolution(10)
    planeSource.SetCenter(0.0, 0.0, 0.0)
    planeSource.SetNormal(0.0, 0.0, 1.0)
    planeSource.Update()

    print(dict_pointing['alt'])
    transform_text = vtk.vtkTransform()
    transform_text.Scale(size, size, size)
    transform_text.RotateZ(dict_pointing['az'].value)
    transform_text.RotateY(90 - dict_pointing['alt'].value)
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
    actor.GetProperty().SetOpacity(0.5)
    return actor


def add_tilted_positions(event, list_tel_ids, array_pointing):
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
    actor.GetProperty().SetColor([0, 255, 0])
    actor.RotateZ(90 - array_pointing['alt'].value)
    actor.RotateY(array_pointing['az'].value)

    return actor
