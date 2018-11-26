CREED_VTK
========
CTA Rendering Event by Event Display with VTK
----------
This library relies on top of [ctapipe](https://github.com/cta-observatory/ctapipe) and it is intended to create 3D renderings 
in [VTK](https://www.vtk.org) for [CTA](www.cta-observatory.org) (the Cherenkov Telescope Array).

This library uses ctapipe to perform the analysis (import simtel file, extract telescopes positions, calibration, tailcut cleaning, etc...), so the standalone usage is not yet forecast. 

There is another similar package in my github repository called CREED, which uses OpenSCAD and SolidPython for the rendering: whether this is "easier" to be used, it is quite slow and not really nice to see (even though somehow it works). In order to create a more good looking, reliable and faster rendering library, I decided to use [VTK](https://www.vtk.org) (The Visualization Toolkit) which offers really better results (with a bit more of coding behind).

In a "ctapipe pipeline" one can introduce this library in this way (more or less...expect changes):

- Plot the telescopes as spheres

        try:
            render = CREED_VTK(event, telescopes_ids=list(layout))
        except:
            render = CREED_VTK(event, telescopes_ids= event.inst.subarray.tel_ids.tolist())
        render.add_gnd_tels()
        render.add_gnd_frame(size=2000)
        render.tel_labels() 

        render.add_tilted_tels()
        render.add_tilted_frame(size=2000)

        render.camera_view(elev=20)
        render.show(width= 1000, height=800)

- Plot telescopes without event (this can plot also telescopes with no data):

        render = CREED_VTK(event, telescopes_ids=list(layout))
        render.event_type(clean_level = "None")
        render.add_arrows_camera_frame()
        render.add_gnd_frame(size=300)
        render.camera_view(elev=20)
        render.tel_labels()
        render.show(width= 1000, height=800)

- Plot telescopes with data:
        
        render = CREED_VTK(event)
        render.event_type(clean_level = "clean", clean_dict=cleaned_dict)
        render.add_arrows_camera_frame()
        render.add_gnd_frame(size=300)
        render.camera_view(elev=20)
        render.tel_labels()
        render.show(width= 1000, height=800)

Where:
- `event` is an event from a simtel file
- `telescopes_ids` is optional: if not provided is taken from event.r0.tels_with_data
- `clean_level` can be: "r0", "dl1", "clean" (need to pass a dictionary with a `cleaned_image` as value and `telelscope_id` as key) or "None"
- the camera has just elevation for now (in degrees "above horizon")

This will pop-out an OpenGL window with the camera, telescopes, etc... 

Installation
------------
The installation is very easy and **for the moment** I recommend to install this library in the same ctapipe environment. After the activation of the environment, just do:

    git clone https://github.com/thomasgas/CREED_VTK.git
    cd CREED_VTK
    python setup.py install

and from now on you should be able to use the library without problems.

If you have any requests just open an issue or send an e-mail to thomas.gasparetto@ts.infn.it or thomas.gasparetto@lapp.in2p3.fr
