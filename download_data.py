from ecmwf.opendata import Client

client = Client(source="ecmwf")


# Retrieve latest run
date = '20220831'
time = '12'
stream = 'oper'
steps = list(range(0, 145, 3)) + list(range(150, 241, 6))

client.retrieve(
    type="fc",
    date=date,
    time=time,
    param=['2t','tp','10u','10v','msl'],
    target=f"/home/ekman/ssd/guido/ecmwf-hres/{date}{time}_2D.grib2",
    step=steps,
)

client.retrieve(
    type="fc",
    param=['t','d','r'],
    date=date,
    time=time,
    levelist=850,
    target=f"/home/ekman/ssd/guido/ecmwf-hres/{date}_{time}_3D_850.grib2",
    step=steps,
)

client.retrieve(
    type="fc",
    param=['gh','t'],
    date=date,
    time=time,
    levelist=500,
    target=f"/home/ekman/ssd/guido/ecmwf-hres/{date}{time}_3D_500.grib2",
    step=steps,
)

client.retrieve(
    type="fc",
    param=['u','v','gh'],
    date=date,
    time=time,
    levelist=250,
    target=f"/home/ekman/ssd/guido/ecmwf-hres/{date}{time}_3D_250.grib2",
    step=steps,
)