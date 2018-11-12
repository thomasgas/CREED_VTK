import vtk
import numpy as np
from vtk.util.colors import tomato

from ..utils.colors import MakeLUTFromCTF
from ..utils.cam_utils import get_cam_height

from ..utils.arrows import arrow_2d

scaling_cam_dict = {"CHEC": 3,
                    "ASTRICam": 1,
                    "LSTCam": 1.2,
                    "FlashCam": 1.2,
                    "DigiCam": 1,
                    "NectarCam": 1.2,
                    "SCTCam": 1}


def camera_structure(event, tel_id, clean_level, cleaned_dict):

    telescope = event.inst.subarray.tel[tel_id]
    camera_type = telescope.camera
    scaling_cam = scaling_cam_dict[camera_type.cam_id]

    # coords_pix = np.loadtxt("LSTCam_coords.txt")
    # x_px = coords_pix[:, 0]*scaling_cam
    # y_px = coords_pix[:, 1]*scaling_cam

    x_px = camera_type.pix_x.value
    y_px = camera_type.pix_y.value

    tableSize = len(x_px)

    if clean_level == "clean":
        image_cal = cleaned_dict[tel_id]
    elif clean_level == "dl1":
        image_cal = event.dl1.tel[tel_id].image[0]
    elif clean_level == "r0":
        image_cal = event.r0.tel[tel_id].image[0]
    elif clean_level == "None":
        # insert by hand the number of pixels in the camera
        image_cal = np.zeros(tableSize)
    else:
        # TODO: fix this to make rendering without ctapipe
        image_cal = np.zeros(tableSize)
        print("Provide cleaning level ('None', 'dl1', 'r0', 'cleaned')")
        print("'None' is used as default now.")

    lut = MakeLUTFromCTF(image_cal)

    points = vtk.vtkPoints()
    colors = vtk.vtkUnsignedCharArray()
    colors.SetNumberOfComponents(3)

    for i in range(len(x_px)):
        points.InsertNextPoint(x_px[i]*scaling_cam, y_px[i]*scaling_cam, 0)
        rgb = [0.0, 0.0, 0.0]
        lut.GetColor(float(i) / (tableSize - 1), rgb)
        ucrgb = list(map(int, [x * 255 for x in rgb]))
        colors.InsertNextTuple3(ucrgb[0], ucrgb[1], ucrgb[2])

    polydata = vtk.vtkPolyData()
    polydata.SetPoints(points)

    colors.SetNumberOfTuples(polydata.GetNumberOfPoints())
    polydata.GetPointData().SetScalars(colors)

    pixel_source = vtk.vtkCylinderSource()

    if camera_type.cam_id == "LSTCam":
        pixel_source.SetResolution(6)
        pixel_source.SetRadius(0.029 * scaling_cam)
        pixel_source.SetHeight(0.8)
        pixel_source.Update()

        transform = vtk.vtkTransform()
        transform.RotateX(90)
        transform.RotateY(100.8+30)  # the "magic" rotation if the pixels + rotation due to default vtk behaviour

    elif camera_type.cam_id == "FlashCam":
        pixel_source.SetResolution(6)
        pixel_source.SetRadius(0.029 * scaling_cam)
        pixel_source.SetHeight(0.8)
        pixel_source.Update()
        transform = vtk.vtkTransform()
        transform.RotateX(90)

    elif camera_type.cam_id == "NectarCam":
        pixel_source.SetResolution(6)
        pixel_source.SetRadius(0.029 * scaling_cam)
        pixel_source.SetHeight(0.8)
        pixel_source.Update()
        transform = vtk.vtkTransform()
        transform.RotateX(90)
        transform.RotateY(100.8+30)  # the "magic" rotation if the pixels + rotation due to default vtk behaviour

    elif camera_type.cam_id in ['CHEC', 'ASTRICam', 'DigiCam']:
        pixel_source.SetResolution(4)
        pixel_source.SetRadius(0.0045 * scaling_cam)
        pixel_source.SetHeight(0.8)
        pixel_source.Update()

        transform = vtk.vtkTransform()
        transform.RotateX(90)
        transform.RotateY(45)


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
    actor.SetPosition(get_cam_height(camera_type.cam_id), 0, 0)

    # transform_assembly = vtk.vtkTransform()
    # transform_assembly.Translate(get_cam_height(camera_type.cam_id), 0, 0)
    #
    # axes_camera = arrow_2d(event, tel_id, {tel_id: {'alt': np.rad2deg(event.mc.tel[tel_id].altitude_raw)}})
    # assembly = vtk.vtkAssembly()
    # assembly.AddPart(axes_camera)
    # assembly.AddPart(actor)
    # assembly.SetUserTransform(transform_assembly)

    return actor


def camera_frame(cam_type):
    scaling_cam = scaling_cam_dict[cam_type]
    if cam_type == "LSTCam":
        camera_frame_structure = vtk.vtkCubeSource()
        camera_frame_structure.SetXLength(2.6 * scaling_cam)
        camera_frame_structure.SetYLength(2.6 * scaling_cam)
        camera_frame_structure.SetZLength(0.75)
    elif cam_type in ["FlashCam", "NectarCam"]:
        camera_frame_structure = vtk.vtkCubeSource()
        camera_frame_structure.SetXLength(2.6 * scaling_cam)
        camera_frame_structure.SetYLength(2.6 * scaling_cam)
        camera_frame_structure.SetZLength(0.75)
    elif cam_type in ['CHEC', 'ASTRICam', 'DigiCam']:
        camera_frame_structure = vtk.vtkCubeSource()
        camera_frame_structure.SetXLength(1.0 * (scaling_cam + 1) / 2)
        camera_frame_structure.SetYLength(1.0 * (scaling_cam + 1) / 2)
        camera_frame_structure.SetZLength(0.78)
    else:
        print("camera frame non implemented")

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
    camera_frame_actor.SetPosition(get_cam_height(cam_type), 0, 0)

    return camera_frame_actor
