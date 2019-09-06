from os.path import join, dirname
import bpy
from json import load
import BlenderGIS
from mathutils import Euler

# IF SET TO TRUE, CAMERA WILL TRACK TO POSITIONS TRACKED MANUALLY, FALSE WILL USE GES LOCAL ORIGIN EXPORT
TRACK_TO_EXPECTED = False

BASE = dirname(bpy.data.filepath)
GES_PATH = join(BASE, "GESExport")
TRACKING_DATA = join(GES_PATH, "GESblender.json")
SHAPEFILE = join(BASE, "shapefiles", "clipped_buildings.shp")
EXPECTED_CAM_POSITIONS = join(BASE, "shapefiles", "manually_tracked_cam_positions.shp")
CRS = "EPSG:2882"
ORIGIN_LAT, ORIGIN_LON, ORIGIN_ALT = (-82.6331167, 27.768472, 2)  # Local track point in esp file
CRS_X, CRS_Y = (451428.93288036, 1249058.37156790)  # from http://epsg.io/transform#s_srs=4326&t_srs=2882&x=-82.6331167&y=27.7684719

# GES doesn't specify euler rot mode so uncomment any of these to try different modes
EULER_MODE = "XYZ"
# EULER_MODE = "XZY"
# EULER_MODE = "YXZ"
# EULER_MODE = "YZX"
# EULER_MODE = "ZYX"
# EULER_MODE = "ZXY"

with open(TRACKING_DATA, "r") as f:
    GES_DATA = load(f)

scene = bpy.context.scene
scene.render.resolution_x = GES_DATA["width"]
scene.render.resolution_y = GES_DATA["height"]
scene.frame_start = 0
scene.frame_end = GES_DATA["numFrames"]


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    bpy.ops.object.camera_add(False)
    for ob in scene.objects:
        if ob.type == "CAMERA":
            scene.camera = ob
    return scene.camera



def init_geoscene(scene, crs, x, y, lat, lon):
    geo = BlenderGIS.geoscene.GeoScene(scn=scene)
    geo.crs = crs
    geo.crsx = x
    geo.crsy = y
    geo.lat = lat
    geo.lon = lon
    if not geo.hasValidCRS or not geo.isFullyGeoref:
        raise Exception("Invalid CRS")


def import_buildings(path, shpCRS, extrudeField):
    bpy.ops.importgis.shapefile(
        "INVOKE_DEFAULT",
        filepath=path,
        shpCRS=shpCRS,
        fieldExtrudeName=extrudeField,
        extrusionAxis="Z",
        separateObjects=False
    )


def import_expected_cam_positions(path, shpCRS, elevFieldName):
    bpy.ops.importgis.shapefile(
        "INVOKE_DEFAULT",
        filepath=path,
        shpCRS=shpCRS,
        elevSource="FIELD",
        fieldElevName=elevFieldName,
        separateObjects=True
    )


def animate_cam(cam, camPositions, expected):
    cam.animation_data_clear()
    for i, frame in enumerate(camPositions):
        scene.frame_set(i)

        if not expected:
            loc = frame["position"]
            cam.location = (float(loc["x"]), float(loc["y"]), float(loc["z"]) + ORIGIN_ALT)  # GES origin set to +2m on z axis but Blender origin is 0,0,0 so need to shift up here
        else:
            if i == 0:
                loc = bpy.data.objects["manually_tracked_cam_positions"].location
            else:
                loc = bpy.data.objects[f"manually_tracked_cam_positions.{str(i).zfill(3)}"].location
            cam.location = loc

        cam.keyframe_insert(data_path="location")

        rot = frame["rotation"]
        cam.rotation_euler = Euler((rot["x"], rot["y"], rot["z"]))
        cam.rotation_mode = EULER_MODE
        cam.keyframe_insert(data_path="rotation_euler")
        cam.keyframe_insert(data_path="rotation_mode")

if __name__ == "__main__":
    cam = clear_scene()
    init_geoscene(scene, CRS, CRS_X, CRS_Y, ORIGIN_LAT, ORIGIN_LON)
    import_buildings(SHAPEFILE, CRS, "Height")
    import_expected_cam_positions(EXPECTED_CAM_POSITIONS, CRS, "alt")
    animate_cam(cam, GES_DATA["cameraFrames"], TRACK_TO_EXPECTED)

