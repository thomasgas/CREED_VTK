import vtk


def create_arrow():
    """
    Create arrow: specify here all the parameters
    :return: arrow
    """
    arrow = vtk.vtkArrowSource()
    arrow.Update()

    return arrow


def translate_object(object, center):
    """
    Translate object
    :param object: input object to translate
    :param center: (x, y, z) coordinates of the center
    :return:
    """
    transform_text = vtk.vtkTransform()
    transform_text.Translate(center[0], center[1], center[2])
    transform_text_axes = vtk.vtkTransformFilter()
    transform_text_axes.SetTransform(transform_text)
    transform_text_axes.SetInputConnection(object.GetOutputPort())
    transform_text_axes.Update()
    return transform_text_axes


def scale_object(object, length):
    """
    Scale object
    :param object: input object to scale
    :param length: uniform scaling along all directions
    :return:
    """
    transform_text = vtk.vtkTransform()
    transform_text.Scale(length, length, length)
    transform_text_axes = vtk.vtkTransformFilter()
    transform_text_axes.SetTransform(transform_text)
    transform_text_axes.SetInputConnection(object.GetOutputPort())
    transform_text_axes.Update()
    return transform_text_axes


def rotate_object(object, axis, angle):
    """
    Rotate object around axis. These are the axes that are attached to the object
    so that some rotation might bring no results. Check rotateWXVY for world coordinates (maybe).
    :param object: is the vtkArrowSource Object (or another one)
    :param axis: the rotation axis
    :param angle: in degrees
    :return: rotated object in the form of a transform filter (to be used later with GetOutput())
    """
    rotation_transform = vtk.vtkTransform()

    if axis == "x":
        rotation_transform.RotateX(angle)
    elif axis == "y":
        rotation_transform.RotateY(angle)
    elif axis == "z":
        rotation_transform.RotateZ(angle)

    rotation_transform_filter = vtk.vtkTransformFilter()
    rotation_transform_filter.SetTransform(rotation_transform)
    rotation_transform_filter.SetInputConnection(object.GetOutputPort())
    rotation_transform_filter.Update()
    return rotation_transform_filter


def create_extruded_text(text):
    """
    Create extruded text. To be then translated and rotated
    :param text: input text. Useful for axes and telescopes labelling,
    :return: return transformed source. need a mapper and an actor then.
    """
    textSource = vtk.vtkVectorText()
    textSource.SetText(text)
    textSource.Update()

    # Apply linear extrusion
    extrude = vtk.vtkLinearExtrusionFilter()
    extrude.SetInputConnection(textSource.GetOutputPort())
    extrude.SetExtrusionTypeToNormalExtrusion()
    extrude.SetVector(0, 0, 1)
    extrude.SetScaleFactor(0.1)

    triangleFilter = vtk.vtkTriangleFilter()
    triangleFilter.SetInputConnection(extrude.GetOutputPort())
    return triangleFilter
