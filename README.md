# BC_coast_animation.py

`BC_coast_animation.py` generates a geospatial map of Vancouver Island and the BC Central Coast, visualizing both topography and bathymetry using high-resolution GEBCO data. The script uses Cartopy and Matplotlib to plot the region with a custom terrain colormap and TwoSlopeNorm normalization, clearly distinguishing land and ocean elevations.

A key feature of the script is an animated expanding circle, simulating a seismic wave propagating from a central point near Duncan, BC. The animation is saved as a GIF (`vancouver_bc_wave_animation.gif`).

**Main features:**
- Loads and visualizes bathymetry/topography from a GeoTIFF file using rioxarray
- Plots the region with Lambert Conformal projection
- Uses a custom terrain colormap and TwoSlopeNorm for elevation
- Adds coastlines, borders, and gridlines
- Animates a propagating wave (expanding circle)
- Saves the animation as a GIF

**Dependencies:**
- matplotlib
- cartopy
- rioxarray
- xarray
- shapely
- numpy

**Usage:**
1. Place a GEBCO GeoTIFF file (e.g., `gebco_2025_n54.0_s48.0_w-130.0_e-122.0.tif`) in the project directory.
2. Run the script: `python BC_coast_animation.py`
3. The output GIF will be saved as `vancouver_bc_wave_animation.gif`.
