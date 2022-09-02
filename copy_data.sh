#!/bin/bash

# Cd into our working directory in case we're not into it already
cd "$(dirname "$0")";

echo "ecmwf: Starting processing of ECMWF HRES model data - `date`"

export MODEL_DATA_FOLDER=/home/ekman/ssd/guido/ecmwf-hres/
export IMGDIR=/home/ekman/ssd/guido/ecmwf-hres/
export HOME_FOLDER=$(pwd)
export NCFTP_BOOKMARK="mid"
DATA_DOWNLOAD=true
DATA_PLOTTING=true
DATA_UPLOAD=true

# Make sure we're using bash
export SHELL=$(type -p bash)
# We need to open many files at the same time
ulimit -Sn 8192
########################################### 

mkdir -p ${MODEL_DATA_FOLDER}world
mkdir -p ${MODEL_DATA_FOLDER}us
mkdir -p ${MODEL_DATA_FOLDER}euratl
mkdir -p ${MODEL_DATA_FOLDER}nh_polar

##### COMPUTE the date variables to determine the run
export MONTH=$(date -u +"%m")
export DAY=$(date -u +"%d")
export YEAR=$(date -u +"%Y")
export HOUR=$(date -u +"%H")

if [ $HOUR -ge 8 ] && [ $HOUR -lt 13 ]
then
    export RUN=00
elif [ $HOUR -ge 13 ] && [ $HOUR -lt 17 ]
then
    export RUN=06
elif [ $HOUR -ge 20 ]
then
    export RUN=12
elif [ $HOUR -ge 1 ] && [ $HOUR -lt 8 ]
then
    DAY=$(date -u -d'yesterday' +"%d")
    export RUN=18
else
    echo "Invalid hour!"
fi

echo "----------------------------------------------------------------------------------------------"
echo "ecmwf: run ${YEAR}${MONTH}${DAY}${RUN}"
echo "----------------------------------------------------------------------------------------------"

# Move to the data folder to do processing
cd ${MODEL_DATA_FOLDER} || { echo 'Cannot change to DATA folder' ; exit 1; }

# SECTION 1 - DATA DOWNLOAD ############################################################

if [ "$DATA_DOWNLOAD" = true ]; then
    echo "-----------------------------------------------"
    echo "ecmwf: Starting downloading of data - `date`"
    echo "-----------------------------------------------"
    rm ${MODEL_DATA_FOLDER}/*.grib2
    rm ${MODEL_DATA_FOLDER}/*.idx
    cp ${HOME_FOLDER}/*.py ${MODEL_DATA_FOLDER}
    #loop through forecast hours
    python download_data.py "${YEAR}${MONTH}${DAY}" "${RUN}"
fi

# SECTION 2 - DATA PLOTTING ############################################################

if [ "$DATA_PLOTTING" = true ]; then
    echo "-----------------------------------------------"
    echo "ecmwf: Starting plotting of data - `date`"
    echo "-----------------------------------------------"
    cp ${HOME_FOLDER}/plotting/*.py ${MODEL_DATA_FOLDER}
    python --version
    export QT_QPA_PLATFORM=offscreen 
	
    scripts=("plot_jetstream.py" "plot_rain_acc.py" "plot_geop_500.py"\
			 "plot_mslp_wind.py" "plot_pres_t2m_wind.py")

	projections=("euratl" "nh" "nh_polar" "us" "world")
	parallel -j 4 python ::: "${scripts[@]}" ::: "${projections[@]}"
fi


# SECTION 3 - IMAGES UPLOAD ############################################################
# Use ncftpbookmarks to add a new FTP server with credentials
if [ "$DATA_UPLOAD" = true ]; then
    echo "-----------------------------------------------"
    echo "ecmwf: Starting FTP uploading - `date`"
    echo "-----------------------------------------------"

	images_output=("gph_500" "winds10m" "winds_jet" "precip_acc" "t_v_pres")
	# suffix for naming
	projections_output=("euratl/" "" "nh_polar/" "world/" "us/")
	# remote folder on server
	projections_output_folder=("ecmwf_euratl" "ecmwf_globe" "ecmwf_nh_polar" "ecmwf_world" "ecmwf_us")

	# Create a lisf of all the images to upload 
	upload_elements=()
	for i in "${!projections_output[@]}"; do
		for j in "${images_output[@]}"; do
			upload_elements+=("${projections_output_folder[$i]}/${j} ./${projections_output[$i]}${j}_*")
		done
	done

	# Finally upload the images 
	num_procs=5
	num_iters=${#upload_elements[@]}
	num_jobs="\j"  # The prompt escape for number of jobs currently running
	for ((i=0; i<num_iters; i++)); do
		while (( ${num_jobs@P} >= num_procs )); do
		wait -n
		done
	ncftpput -R -v -DD -m ${NCFTP_BOOKMARK} ${upload_elements[$i]} &
	done
fi

# SECTION 4 - CLEANING ############################################################

echo "-----------------------------------------------"
echo "ecmwf: Finished cleaning up - `date`"
echo "----------------------------------------------_"

############################################################

cd -
