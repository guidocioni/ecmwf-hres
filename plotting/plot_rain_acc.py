import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Pool
from functools import partial
import utils
import sys
import xarray as xr

debug = False
if not debug:
    import matplotlib
    matplotlib.use('Agg')


# The one employed for the figure name when exported
variable_name = 'precip_acc'

utils.print_message('Starting script to plot '+variable_name)

# Get the projection as system argument from the call so that we can
# span multiple instances of this script outside
if not sys.argv[1:]:
    utils.print_message(
        'Projection not defined, falling back to default (nh)')
    projection = 'nh'
else:
    projection = sys.argv[1]


def main():
    """In the main function we basically read the files and prepare the variables to be plotted.
    This is not included in utils.py as it can change from case to case."""
    dset = xr.open_dataset(f'{utils.folder}/vars_2D.grib2')
    dset['msl'] = dset['msl'].metpy.convert_units('hPa').metpy.dequantify()
    dset['tp'] = dset['tp'].metpy.convert_units('mm').metpy.dequantify()

    levels_precip = list(np.arange(1, 50, 0.4)) + \
        list(np.arange(51, 100, 2)) +\
        list(np.arange(101, 200, 3)) +\
        list(np.arange(201, 500, 6)) + \
        list(np.arange(501, 1000, 50)) + \
        list(np.arange(1001, 2000, 100))

    cmap, norm = utils.get_colormap_norm(
        'rain_acc_wxcharts', levels=levels_precip)

    _ = plt.figure(figsize=(utils.figsize_x, utils.figsize_y))
    ax = plt.gca()
    m, x, y, mask = utils.get_projection(dset, projection)
    # Subset dataset only on the area
    dset = dset.where(mask, drop=True)
    # m.arcgisimage(service='Canvas/World_Dark_Gray_Base', xpixels=1000)
    m.drawmapboundary(fill_color='whitesmoke')
    m.fillcontinents(color='lightgray',lake_color='whitesmoke', zorder=1)

    dset = dset.load()

    levels_mslp = np.arange(dset['msl'].min().astype("int"),
                            dset['msl'].max().astype("int"), 5.)

    # All the arguments that need to be passed to the plotting function
    args = dict(x=x, y=y, ax=ax,
                levels_precip=levels_precip,
                levels_mslp=levels_mslp,
                time=dset.time,
                projection=projection,
                cmap=cmap, norm=norm)

    utils.print_message('Pre-processing finished, launching plotting scripts')
    if debug:
        plot_files(dset.isel(time=slice(-2, -1)), **args)
    else:
        # Parallelize the plotting by dividing into chunks and processes
        dss = utils.chunks_dataset(dset, utils.chunks_size)
        plot_files_param = partial(plot_files, **args)
        p = Pool(utils.processes)
        p.map(plot_files_param, dss)


def plot_files(dss, **args):
    # Using args we don't have to change the prototype function if we want to add other parameters!
    first = True
    for time_sel in dss.step:
        data = dss.sel(step=time_sel)
        time, run, cum_hour = utils.get_time_run_cum(data)
        # Build the name of the output image
        filename = utils.subfolder_images[projection] + \
            '/' + variable_name + '_%s.png' % cum_hour

        cs = args['ax'].contourf(args['x'], args['y'], data['tp'],
                                 extend='max', cmap=args['cmap'], norm=args['norm'],
                                 levels=args['levels_precip'])

        c = args['ax'].contour(args['x'], args['y'], data['msl'],
                               levels=args['levels_mslp'], colors='black', linewidths=0.5, antialiased=True)

        labels = args['ax'].clabel(
            c, c.levels, inline=True, fmt='%4.0f', fontsize=5)

        maxlabels = utils.plot_maxmin_points(args['ax'], args['x'], args['y'], data['msl'],
                                             'max', 60, symbol='H', color='royalblue', random=True)
        minlabels = utils.plot_maxmin_points(args['ax'], args['x'], args['y'], data['msl'],
                                             'min', 60, symbol='L', color='coral', random=True)

        an_fc = utils.annotation_forecast(args['ax'], time)
        an_var = utils.annotation(args['ax'], 'Accumulated precipitation [mm] and MSLP [hPa]',
                                  loc='lower left', fontsize=6)
        an_run = utils.annotation_run(args['ax'], run)

        if first:
            plt.colorbar(cs, orientation='horizontal', label='Accumulated precipitation [mm]',
                         pad=0.03, fraction=0.04)

        if debug:
            plt.show(block=True)
        else:
            plt.savefig(filename, **utils.options_savefig)

        utils.remove_collections([c, cs, labels, an_fc, an_var, an_run, maxlabels, minlabels])

        first = False


if __name__ == "__main__":
    import time
    start_time = time.time()
    main()
    elapsed_time = time.time()-start_time
    utils.print_message(
        "script took " + time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
