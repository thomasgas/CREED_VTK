import vtk
from .cam_utils import get_cam_height


def arrow_2d(event, tel_id, pointing):
    """
    Create 2d arrow to be appended to the camera
    :param event: event from simtel file
    :param tel_id: tel_id given from the main.py loop
    :param pointing: dictionary of dictionaries: first key is the tel_id
                    second key are alt and az
    :return: return axes actor placed at the right height above the mirrors plane
    TODO: implement az rotation
    """

    tel_coords = event.inst.subarray.tel_coords

    telescope = event.inst.subarray.tel[tel_id]
    camera_type = telescope.camera.cam_id

    tel_x_pos = tel_coords.x[tel_id - 1].value
    tel_y_pos = tel_coords.y[tel_id - 1].value
    tel_z_pos = tel_coords.z[tel_id - 1].value

    transform_arrow = vtk.vtkTransform()
    transform_arrow.Translate(tel_x_pos, tel_y_pos, tel_z_pos)
    transform_arrow.RotateY(-pointing[tel_id]['alt'])
    transform_arrow.Translate(get_cam_height(camera_type), 0.0, 0.0)
    transform_arrow.RotateY(90)

    axes = vtk.vtkAxesActor()
    axes.SetZAxisLabelText("")
    axes.SetTotalLength(10, 10, 0)
    axes.SetShaftTypeToCylinder()
    axes.SetCylinderRadius(axes.GetCylinderRadius() * 0.8)
    axes.SetUserTransform(transform_arrow)
    axes.GetXAxisCaptionActor2D().GetTextActor().SetTextScaleMode(5)
    axes.GetYAxisCaptionActor2D().GetTextActor().SetTextScaleMode(5)

    return axes
