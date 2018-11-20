import vtk
from .cam_utils import get_cam_height
from .transf_utils import *


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

    mbds = vtk.vtkMultiBlockDataSet()

    arrows = 2

    # allocate space for arrows and text
    mbds.SetNumberOfBlocks(2 * arrows + 1)

    # Leave block 1 NULL.  NULL blocks are valid and should be handled by
    # algorithms that process multiblock datasets.  Especially when
    # running in parallel where the blocks owned by other processes are
    # NULL in this process.

    arrow_length = 10
    single_arrow = scale_object(create_arrow(), length=arrow_length)

    X_arrow = single_arrow
    Y_arrow = rotate_object(single_arrow, "z", 90)
    # Z_arrow = rotate_object(single_arrow, "y", -90)

    x_text = translate_object(create_extruded_text("X"), [arrow_length, 0, 0])

    y_text = rotate_object(create_extruded_text("Y"), "z", 90)
    y_text = translate_object(y_text, [0, arrow_length, 0])

    # z_text = rotate_object(create_extruded_text("Z"), "y", -90)
    # z_text = translate_object(z_text, [0, 0, arrow_length])
    # Y_arrow = create_arrow_translated(0, 2 ,0)

    mbds.SetBlock(0, X_arrow.GetOutput())
    mbds.SetBlock(2, Y_arrow.GetOutput())
    # mbds.SetBlock(3, Z_arrow.GetOutput())
    mbds.SetBlock(3, x_text.GetOutput())
    mbds.SetBlock(4, y_text.GetOutput())
    # mbds.SetBlock(6, z_text.GetOutput())

    mapper = vtk.vtkCompositePolyDataMapper2()
    mapper.SetInputDataObject(mbds)

    cdsa = vtk.vtkCompositeDataDisplayAttributes()
    mapper.SetCompositeDataDisplayAttributes(cdsa)

    # You can use the vtkCompositeDataDisplayAttributes to set the color,
    # opacity and visibiliy of individual blocks of the multiblock dataset.
    # Attributes are mapped by block pointers (vtkDataObject*), so these can
    # be queried by their flat index through a convenience function in the
    # attribute class (vtkCompositeDataDisplayAttributes::DataObjectFromIndex).
    # Alternatively, one can set attributes directly through the mapper using
    # flat indices.
    #
    # This sets the block at flat index 3 red
    # Note that the index is the flat index in the tree, so the whole multiblock
    # is index 0 and the blocks are flat indexes 1, 2 and 3.  This affects
    # the block returned by mbds.GetBlock(2).
    # double color[] = {1, 0, 0}

    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    mapper.SetBlockColor(1, red)
    mapper.SetBlockColor(3, green)
    # mapper.SetBlockColor(4, blue)
    mapper.SetBlockColor(4, red)
    mapper.SetBlockColor(5, green)
    # mapper.SetBlockColor(7, blue)

    axes = vtk.vtkActor()
    axes.SetMapper(mapper)
    axes.SetUserTransform(transform_arrow)

    return axes


def arrow_3d(event, tel_id, pointing):
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

    mbds = vtk.vtkMultiBlockDataSet()

    arrows = 3

    # allocate space for arrows and text
    mbds.SetNumberOfBlocks(2 * arrows + 1)

    # Leave block 1 NULL.  NULL blocks are valid and should be handled by
    # algorithms that process multiblock datasets.  Especially when
    # running in parallel where the blocks owned by other processes are
    # NULL in this process.

    arrow_length = 10
    single_arrow = scale_object(create_arrow(), length=arrow_length)

    X_arrow = single_arrow
    Y_arrow = rotate_object(single_arrow, "z", 90)
    Z_arrow = rotate_object(single_arrow, "y", -90)

    x_text = translate_object(create_extruded_text("X"), [arrow_length, 0, 0])

    y_text = rotate_object(create_extruded_text("Y"), "z", 90)
    y_text = translate_object(y_text, [0, arrow_length, 0])

    z_text = rotate_object(create_extruded_text("Z"), "y", -90)
    z_text = translate_object(z_text, [0, 0, arrow_length])
    # Y_arrow = create_arrow_translated(0, 2 ,0)

    mbds.SetBlock(0, X_arrow.GetOutput())
    mbds.SetBlock(2, Y_arrow.GetOutput())
    mbds.SetBlock(3, Z_arrow.GetOutput())
    mbds.SetBlock(4, x_text.GetOutput())
    mbds.SetBlock(5, y_text.GetOutput())
    mbds.SetBlock(6, z_text.GetOutput())

    mapper = vtk.vtkCompositePolyDataMapper2()
    mapper.SetInputDataObject(mbds)

    cdsa = vtk.vtkCompositeDataDisplayAttributes()
    mapper.SetCompositeDataDisplayAttributes(cdsa)

    # You can use the vtkCompositeDataDisplayAttributes to set the color,
    # opacity and visibiliy of individual blocks of the multiblock dataset.
    # Attributes are mapped by block pointers (vtkDataObject*), so these can
    # be queried by their flat index through a convenience function in the
    # attribute class (vtkCompositeDataDisplayAttributes::DataObjectFromIndex).
    # Alternatively, one can set attributes directly through the mapper using
    # flat indices.
    #
    # This sets the block at flat index 3 red
    # Note that the index is the flat index in the tree, so the whole multiblock
    # is index 0 and the blocks are flat indexes 1, 2 and 3.  This affects
    # the block returned by mbds.GetBlock(2).
    # double color[] = {1, 0, 0}

    red = (255, 0, 0)
    green = (0, 255, 0)
    blue = (0, 0, 255)

    mapper.SetBlockColor(1, red)
    mapper.SetBlockColor(3, green)
    mapper.SetBlockColor(4, blue)
    mapper.SetBlockColor(5, red)
    mapper.SetBlockColor(6, green)
    mapper.SetBlockColor(7, blue)

    axes = vtk.vtkActor()
    axes.SetMapper(mapper)
    axes.SetUserTransform(transform_arrow)

    return axes