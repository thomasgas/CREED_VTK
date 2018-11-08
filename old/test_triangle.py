import vtk
points = vtk.vtkPoints()
points.InsertNextPoint(1.0, 0.0, 0.0)
points.InsertNextPoint(0.0, 0.0, 0.0)
points.InsertNextPoint(0.0, 1.0, 0.0)

# setup colors (setting the name to "Colors" is nice but not necessary)
Colors = vtk.vtkUnsignedCharArray()
Colors.SetNumberOfComponents(3)
Colors.SetName("Colors")
Colors.InsertNextTuple3(255, 0, 0)

triangles = vtk.vtkCellArray()
triangle = vtk.vtkTriangle()
triangle.GetPointIds().SetId(0, 0)
triangle.GetPointIds().SetId(1, 1)
triangle.GetPointIds().SetId(2, 2)

triangles.InsertNextCell(triangle)


polydata = vtk.vtkPolyData()
polydata.SetPoints(points)
polydata.SetPolys(triangles)
polydata.GetCellData().SetScalars(Colors)


mapper = vtk.vtkPolyDataMapper()
mapper.SetInputData(polydata)
# mapper.SetScalarModeToUseCellData()
# mapper.Update()

# Set Actors
actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create a renderer, render window, and interactor
WIDTH = 640
HEIGHT = 480
renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindow.SetSize(WIDTH, HEIGHT)


# Add the actors to the scene
renderer.AddActor(actor)
renderer.SetBackground(0.7, 0.7, 0.7)  # Background color dark red

# Render and interact
renderWindowInteractor.Initialize()
renderWindow.Render()
renderWindowInteractor.Start()
