import vtk


def arrow_2d(event, tel_id, pointing):

    tel_coords = event.inst.subarray.tel_coords

    tel_x_pos = tel_coords.x[tel_id - 1].value
    tel_y_pos = tel_coords.y[tel_id - 1].value
    tel_z_pos = tel_coords.z[tel_id - 1].value

    transform_arrow = vtk.vtkTransform()
    transform_arrow.Translate(tel_x_pos, tel_y_pos, tel_z_pos)
    transform_arrow.RotateY(-pointing[tel_id]['alt'])
    transform_arrow.Translate(28.0, 0.0, 0.0)
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
