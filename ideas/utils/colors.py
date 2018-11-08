import numpy as np
import vtk
import matplotlib.cm as cm


def MakeLUTFromCTF(data_camera):
    """
    Use a color transfer Function to generate the colors in the lookup table.
    See: http://www.vtk.org/doc/nightly/html/classvtkColorTransferFunction.html

    :param data_camera: the camera_folder
    :return: the LUT
    """
    max_col = np.max(data_camera)
    tablesize = data_camera.shape[0]

    ctf = vtk.vtkColorTransferFunction()
    ctf.SetColorSpaceToDiverging()

    cmap = cm.viridis
    for i in range(cmap.N):
        pivot = cmap.colors[i]
        ctf.AddRGBPoint(i/cmap.N, pivot[0], pivot[1], pivot[2])

    lut = vtk.vtkLookupTable()
    lut.SetNumberOfTableValues(tablesize)
    lut.Build()

    for i in range(tablesize):
        rgb = list(ctf.GetColor(data_camera[i] / max_col)) + [1]
        lut.SetTableValue(i, rgb)

    return lut
