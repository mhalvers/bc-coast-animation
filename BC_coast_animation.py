# %%
"""
Geospatial map of Vancouver Island and BC Central Coast with topography and bathymetry.
"""
import xarray as xr
import matplotlib.pyplot as plt
from matplotlib.animation import PillowWriter
from matplotlib import colors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.geodesic import Geodesic
import numpy as np
import shapely.geometry as sgeom
import rioxarray
from matplotlib.animation import FuncAnimation

# Region bounds (approximate)
lon_min, lon_max = -130, -123
lat_min, lat_max = 48, 54

TOPO_FILE = "gebco_2025_n54.0_s48.0_w-130.0_e-122.0.tif"

xr.set_options(display_style="text")

# %% Load bathymetry/topography from GeoTIFF using rioxarray
try:
    da = rioxarray.open_rasterio(TOPO_FILE, masked=True).squeeze()
except Exception:
    print(f"{TOPO_FILE} not found or rioxarray error. Using placeholder data.")
    cols, rows = 100, 100
    xs = np.linspace(lon_min, lon_max, cols)
    ys = np.linspace(lat_min, lat_max, rows)
    data = np.random.uniform(
        -5000, 2000, size=(rows, cols)
    )  # Random data as placeholder

# %%
colors_undersea = plt.cm.terrain(np.linspace(0, 0.17, 256))
colors_land = plt.cm.terrain(np.linspace(0.25, 1, 256))
all_colors = np.vstack((colors_undersea, colors_land))
terrain_map = colors.LinearSegmentedColormap.from_list("terrain_map", all_colors)
divnorm = colors.TwoSlopeNorm(vmin=-3000, vcenter=0, vmax=3000)

# %%
gd = Geodesic()
centre_lon, centre_lat = -126.5, 49.7  # Approximate center of Duncan, BC
radius_min = 10  # km, initial radius
radius_max = 200  # km, final radius
frames = 60  # number of animation frames

# %% Plot
fig = plt.figure(figsize=(10, 8))
central_lon = (lon_min + lon_max) / 2
central_lat = (lat_min + lat_max) / 2
ax = plt.axes(
    projection=ccrs.LambertConformal(
        central_longitude=central_lon,
        central_latitude=central_lat,
        standard_parallels=(lat_min, lat_max),
    )
)
ax.set_extent([lon_min + 0.5, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
im = ax.pcolormesh(
    da.x,
    da.y,
    da.values,
    cmap=terrain_map,
    shading="auto",
    rasterized=True,
    norm=divnorm,
    transform=ccrs.PlateCarree(),
)
cb = plt.colorbar(im, ax=ax, label="Elevation (m)", shrink=0.6)
cb.set_ticks([-3000, -2000, -1000, 0, 1000, 2000, 3000])

# Coastlines and borders
ax.add_feature(cfeature.COASTLINE)
ax.add_feature(cfeature.BORDERS)
ax.add_feature(cfeature.LAND, facecolor="none")
ax.add_feature(cfeature.OCEAN, facecolor="none")
# ax.set_boundary(sgeom.box(lon_min, lat_min, lon_max, lat_max), transform=ccrs.PlateCarree())

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


# %%
# Animation: expanding circle
circle_artist = None


def init():
    global circle_artist
    # Draw initial circle
    radius = radius_min
    circle_points = gd.circle(centre_lon, centre_lat, radius * 1000, 100)
    circle_polygon = sgeom.Polygon(circle_points)
    if circle_artist:
        circle_artist.remove()
    circle_artist = ax.add_geometries(
        [circle_polygon],
        ccrs.PlateCarree(),
        facecolor="blue",
        alpha=0.5,
        edgecolor="black",
    )
    return (circle_artist,)


def update(frame):
    global circle_artist
    radius = radius_min + (radius_max - radius_min) * frame / (frames - 1)
    circle_points = gd.circle(centre_lon, centre_lat, radius * 1000, 100)
    circle_polygon = sgeom.Polygon(circle_points)
    if circle_artist:
        circle_artist.remove()
    circle_artist = ax.add_geometries(
        [circle_polygon],
        ccrs.PlateCarree(),
        facecolor="blue",
        alpha=0.5,
        edgecolor="black",
    )
    return (circle_artist,)


ani = FuncAnimation(
    fig, update, frames=frames, init_func=init, blit=False, repeat=False
)

# %%
# Save animation as GIF (uses PillowWriter)
ani.save("vancouver_bc_wave_animation.gif", writer=PillowWriter(fps=15))
plt.show()
