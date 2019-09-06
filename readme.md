##Purpose
This repo demonstrates current issues importing GES camera data into Blender 2.8.

##Requirements
* [Blender 2.8](https://blender.org/download)
* [BlenderGIS](https://github.com/domlysz/BlenderGIS)
* [(optionally) QGIS 3.8](https://qgis.org/en/site/forusers/download.html)

##How to use
Open `GESExport/GESblender.esp` in GES (or view the footage next to it) to get an idea of what the expected output should be.

Then launch GES.blend and execute the attached script `import_GES.py`. It will create and animate a camera according to data exported from GES in local origin tracking mode. It will also import buildings (courtesy of [Microsoft building footprints](https://github.com/microsoft/USBuildingFootprints)) to add some reference. Finally, it will import a set of track points of the expected camera position (these points were manually tracked and NOT exported from GES). 

Open the animation workspace, set the left viewport to camera view (num0) and the right viewport to top view (num7) and scrub the timeline. You will notice, the camera animation does not follow the expected position track nor does its rotation follow as you would expect.

Go back to the scripting workspace, and change line 8 to `TRACK_TO_EXPECTED = True`. This will tell the script to set the camera to match the exact lon, lat, alt from GES (manually recorded with copy-paste and a lot of effort, not exported). Now run the script again, go back to the animation workspace and scrub the timeline again. This time, the camera will animate thru the proper positions but the rotation is still incomprehensible.

##Details
###How it works
The script works by using BlenderGIS to set Blender's origin to the same point in space as the local origin track point in GES. Because both Blender and GES units default to meters, and because GES local origin export is ENU tangent to the local origin, once Blender's origin is set to the same, the import should be simple.

However, this is not the case. It appears GES local tracking export is not in fact exporting ENU relative to the local origin in meters. Looking at the exported data, the first camera position is marked as `{"x":356.7595198894851,"y":-1203.3675427399576,"z":-1370.1738190231845}`. A negative z value in this context does not make sense because the local origin is set at an altitude of 2m, so any negative value would mean the camera is underground.

To check these actual position against the expected values, I created `manual_tracking.csv` where I went frame-by-frame recording the lon, lat, and alt of the camera position. I then imported that spreadsheet into QGIS and exported those points as a shapefile so they can be imported into Blender. Once imported, these appear to be the correct positions. However, I was still unable to make sense of the rotation data exported by GES for any variant of `Euler XYZ`. You can edit the script animate the camera to these positions by setting `TRACK_TO_EXPECTED` to  `True` and rerunning the script.

I would have liked to try manually tracking the camera pan, rotation, and tilt and using those values to set rotation, however I wasn't able to extract those values from GES because I used camera targeting in the animation so clicking on camera rotation values and copy-pasting was giving me the non-overridden values.

###Files
* `GESExport/`
    * `footage/*.jpg` - Rendered output from GES project
    * `GESblender.esp` - GES project file
    * `GESblender.json` - Export of GES project using ENU coordinates relative to local origin (coordinate space `local`)
* `shapefiles/`
    * `building_harn` - these are the MS Building Footprints of Florida projected into ESPG:2882 (best fit projection for Florida)
    * `clip_path` - This is a clipping path used to limit the building footprints imported to those actually useful
    * `clipped_buildings` - This is the building footprints, clipped and ready for import
    * `manually_tracked_cam_positions` - These is a shapefile import of `manual_tracking.csv` so we can import the expected cam positions into blender
* `GES.blend` - A blank blender project with `import_GES.py` attached, ready to run
* `manual_tracking.csv` - A csv with exact lon, lat, and alt values copied manually frame-by-frame from GES to compare against the ENU coordinate export.
* `qgis_project.qgz` - The QGIS project I used to clip the buildings and transform the manually tracked cam positions from a `csv` to a shapefile.