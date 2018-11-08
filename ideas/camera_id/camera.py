import vtk
import numpy as np
from vtk.util.colors import tomato

cam_height = 28
scaling_cam = 1.2


def camera_structure(type):
    if type == "LSTCam":

        coords_pix = np.loadtxt("LSTCam_coords.txt")
        x_px = coords_pix[:, 0]*scaling_cam
        y_px = coords_pix[:, 1]*scaling_cam

        points = vtk.vtkPoints()
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)

        for i in range(len(x_px)):
            points.InsertNextPoint(x_px[i], y_px[i], 0)
            # rgb = [0.0, 0.0, 0.0]
            # lut.GetColor(float(i) / (tableSize - 1), rgb)
            rgb = [0.0, 0.0, 1.0]
            ucrgb = list(map(int, [x * 255 for x in rgb]))
            colors.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])

        polydata = vtk.vtkPolyData()
        polydata.SetPoints(points)

        colors.SetNumberOfTuples(polydata.GetNumberOfPoints())
        polydata.GetPointData().SetScalars(colors)

        # # Now, let's control normal on each point composing or 'fake' surface
        # # We should say, let's give a direction to each point, a normal in strange for a point.
        # pointNormalsArray = vtkDoubleArray()
        # pointNormalsArray.SetNumberOfComponents(3)
        # pointNormalsArray.SetNumberOfTuples(polydata.GetNumberOfPoints())
        #
        # pN1 = [0.0, 1.0, 1.0]
        # pN2 = [0.0, 1.0, 1.0]
        # pN3 = [0.0, 1.0, 1.0]
        #
        # pointNormalsArray.SetTuple(0, pN1)
        # pointNormalsArray.SetTuple(1, pN2)
        # pointNormalsArray.SetTuple(2, pN3)
        #
        # polydata.GetPointData().SetNormals(pointNormalsArray)

        pixel_source = vtk.vtkCylinderSource()

        pixel_source.SetResolution(6)
        pixel_source.SetRadius(0.026*scaling_cam)
        pixel_source.SetHeight(0.8)
        pixel_source.Update()

        transform = vtk.vtkTransform()
        transform.RotateX(90)
        transform.RotateY(100.8+30)

        transformFilter = vtk.vtkTransformPolyDataFilter()
        transformFilter.SetTransform(transform)
        transformFilter.SetInputConnection(pixel_source.GetOutputPort())
        transformFilter.Update()

        glyph = vtk.vtkGlyph3D()

        glyph.SetInputData(polydata)
        glyph.SetSourceConnection(transformFilter.GetOutputPort())
        glyph.SetColorModeToColorByScalar()
        glyph.SetVectorModeToUseNormal()
        glyph.ScalingOff()
        glyph.Update()

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(glyph.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.RotateY(90)
        actor.SetPosition(28, 0, 0)

        return actor


def camera_frame(type):
    if type == "LSTCam":
        camera_frame_structure = vtk.vtkCubeSource()
        camera_frame_structure.SetXLength(3)
        camera_frame_structure.SetYLength(3)
        camera_frame_structure.SetZLength(0.75)

        # create a transform that rotates the cone
        transform = vtk.vtkTransform()
        transform_camera_frame_filter = vtk.vtkTransformPolyDataFilter()
        transform.RotateY(90)
        transform_camera_frame_filter.SetTransform(transform)
        transform_camera_frame_filter.SetInputConnection(camera_frame_structure.GetOutputPort())
        transform_camera_frame_filter.Update()

        camera_frame_mapper = vtk.vtkPolyDataMapper()
        camera_frame_mapper.SetInputConnection(transform_camera_frame_filter.GetOutputPort())

        camera_frame_actor = vtk.vtkActor()
        camera_frame_actor.SetMapper(camera_frame_mapper)
        camera_frame_actor.GetProperty().SetColor(tomato)
        camera_frame_actor.SetPosition(28, 0, 0)

        return camera_frame_actor
