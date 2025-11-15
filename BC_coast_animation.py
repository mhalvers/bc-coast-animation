# %%
"""
Geospatial map of Vancouver Island and BC Central Coast with topography and bathymetry.
"""
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from matplotlib.animation import FuncAnimation
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.geodesic import Geodesic
import numpy as np
import shapely.geometry as sgeom
import rioxarray
import cmocean


OUTPUT_GIF = "bc_coast_seismic_toy_example.gif"
FPS = 15
N_FRAMES = 60
FIGSIZE = (10, 8)
TOPO_FILE = "exportImage.tiff"  # Path to GeoTIFF file with bathymetry/topography data

# Fictitious epicenter on west coast of Vancouver Island
EPICENTER_COORDS = (
    -126.5,
    49.7,
)
RADIUS_MIN, RADIUS_MAX = 1, 100  # km, initial and final circle radius

# Region bounds
LON_MIN, LON_MAX = -130, -123
LAT_MIN, LAT_MAX = 48, 53

CIRCLE_KWARGS = {
    "facecolor": "red",
    "alpha": 0.3,
    "edgecolor": "black",
}

# %% Load bathymetry/topography from GeoTIFF using rioxarray
try:
    da = rioxarray.open_rasterio(TOPO_FILE, masked=True).squeeze()
except Exception:
    print(f"{TOPO_FILE} not found or rioxarray error. Using placeholder data.")
    cols, rows = 100, 100
    xs = np.linspace(LON_MIN, LON_MAX, cols)
    ys = np.linspace(LAT_MIN, LAT_MAX, rows)
    data = np.full((rows, cols), np.nan)

# %% set up the colormap
terrain_map = cmocean.cm.topo

# %% Plot
fig = plt.figure(figsize=FIGSIZE)
central_lon = (LON_MIN + LON_MAX) / 2
central_lat = (LAT_MIN + LAT_MAX) / 2
ax = plt.axes(
    projection=ccrs.LambertConformal(
        central_longitude=central_lon,
        central_latitude=central_lat,
        standard_parallels=(LAT_MIN, LAT_MAX),
    )
)
ax.set_extent([LON_MIN + 0.5, LON_MAX - 0.5, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())
im = ax.pcolormesh(
    da.x,
    da.y,
    da.values,
    cmap=terrain_map,
    vmin=-3000,
    vmax=3000,
    shading="auto",
    rasterized=True,
    transform=ccrs.PlateCarree(),
)
cb = plt.colorbar(im, ax=ax, label="Elevation (m)", shrink=0.6)
cb.set_ticks([-3000, -2000, -1000, 0, 1000, 2000, 3000])

# Coastlines and borders
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.LAND, facecolor="none")
ax.add_feature(cfeature.OCEAN, facecolor="none")

# gridlines
gl = ax.gridlines(
    draw_labels=True,
    linewidth=0.7,
    color="gray",
    alpha=0.5,
    linestyle="--",
    x_inline=False,
    y_inline=False,
)
gl.top_labels = False
gl.right_labels = False
ax.set_title("Vancouver Island & BC Central Coast")


# %% Animation: expanding circle
circle_artist = None
gd = Geodesic()

def init():
    global circle_artist
    # Draw initial circle
    radius = RADIUS_MIN
    circle_points = gd.circle(*EPICENTER_COORDS, radius * 1000, 100)
    circle_polygon = sgeom.Polygon(circle_points)
    if circle_artist:
        circle_artist.remove()
    circle_artist = ax.add_geometries(
        [circle_polygon], ccrs.PlateCarree(), **CIRCLE_KWARGS
    )
    return (circle_artist,)


def update(frame):
    global circle_artist
    radius = RADIUS_MIN + (RADIUS_MAX - RADIUS_MIN) * frame / (N_FRAMES - 1)
    circle_points = gd.circle(*EPICENTER_COORDS, radius * 1000, 100)
    circle_polygon = sgeom.Polygon(circle_points)
    if circle_artist:
        circle_artist.remove()
    circle_artist = ax.add_geometries(
        [circle_polygon], ccrs.PlateCarree(), **CIRCLE_KWARGS
    )
    return (circle_artist,)


ani = FuncAnimation(
    fig, update, frames=N_FRAMES, init_func=init, blit=False, repeat=False
)

# %% Save animation as GIF (uses PillowWriter)
ani.save(OUTPUT_GIF, writer=PillowWriter(fps=FPS))
