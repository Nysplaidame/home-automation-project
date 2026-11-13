# Selected display imagery

These three deliberately selected source images ship locally. No remote image
requests are made by the running display. Retrieved 2026-10-04.

| File | Source / credit | Use |
| --- | --- | --- |
| earth.jpg | NASA Blue Marble: https://eoimages.gsfc.nasa.gov/images/imagerecords/57000/57730/land_ocean_ice_2048.jpg | 2048x1024 land/ocean/ice colour composite, no live weather |
| moon.jpg | NASA's Scientific Visualization Studio; LROC data from NASA/GSFC/Arizona State University: https://svs.gsfc.nasa.gov/vis/a000000/a004700/a004720/lroc_color_2k.jpg | 2048x1024 LROC colour map |
| milky-way.jpg | ESO/S. Brunier: https://cdn.eso.org/images/screen/eso0932a.jpg | Screen-size photographic panorama, cropped/muted in CSS |

Moon source and credits: https://svs.gsfc.nasa.gov/4720/ . NASA material is
used with source attribution, without implying endorsement. Earth includes
pre-shaded topography, so this is a visual reference map, not a calibrated BRDF.

Sky source: https://www.eso.org/public/images/eso0932a/ . Distributed under
CC BY 4.0 per https://www.eso.org/public/outreach/copyright/ . Visible clickable
credit is retained in the viewport. Image bytes are unchanged; only presentation
is muted/cropped. This is an atmospheric backdrop, not an ICRF-aligned sky chart.

Both maps are centred on zero longitude, north up, east right. Earth/Moon now
use approximate IAU text-PCK attitude (see the app README for time limits).
No live cloud cover, precision EOP/binary lunar libration, displacement or
normal map is claimed. Two shared 2K RGBA textures with mipmaps require about
21.3 MiB of GPU storage, plus decoded images and the browser-managed sky image.
Actual device memory and frame times still require Pi acceptance testing.
