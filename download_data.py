from ecmwf.opendata import Client
import os
import sys

client = Client(source="ecmwf")

folder = os.getenv('MODEL_DATA_FOLDER')
date = sys.argv[1]
time = sys.argv[2]

if time in ['00', '12']:
    steps = list(range(3, 145, 3)) + list(range(150, 241, 6))
elif time in ['06', '18']:
    steps = list(range(3, 91, 3))

client.retrieve(
    type="fc",
    date=date,
    time=time,
    param=['2t','tp','10u','10v','msl','tcwv'],
    target=f"{folder}/vars_2D.grib2",
    step=steps,
)

client.retrieve(
    type="fc",
    param=['t','d','r','vo'],
    date=date,
    time=time,
    levelist=850,
    target=f"{folder}/vars_3D_850.grib2",
    step=steps,
)

client.retrieve(
    type="fc",
    param=['gh','t'],
    date=date,
    time=time,
    levelist=500,
    target=f"{folder}/vars_3D_500.grib2",
    step=steps,
)

client.retrieve(
    type="fc",
    param=['u','v','gh'],
    date=date,
    time=time,
    levelist=250,
    target=f"{folder}/vars_3D_250.grib2",
    step=steps,
)
