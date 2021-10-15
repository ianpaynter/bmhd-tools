import h5py
import os
import subprocess as sub
from google.cloud import storage

# Point to the service account credentials
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'F:/USRA/BMHDTools/causal-armor-328417-b56dc4d9394b.json'
# Make Google Cloud client object linked to COG project
client = storage.Client('COG Project')
# Retrieve bucket for hosting COGs
bucket = client.get_bucket('mori')

# Set path to .h5 VNP46A2 files
path = r'F:\USRA\Quarantine\Original'
# Create list of paths to files
files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.h5')]
# File count
file_count = 0
# File total
file_total = len(files)

# For each file
for file in files:
    # Iterate file count
    file_count += 1
    # Form the base name of the file (removing the .h5 suffix)
    basename = os.path.splitext(os.path.basename(file))[0]
    # Print an update
    print(f'File {file_count} of {file_total}: {basename}.\n'
          f'Step 1 of 5: Get bounding box from h5 metadata.')
    # Load h5 file with h5py
    h5file = h5py.File(file, 'r')
    # Get the metadata
    metadata = str(h5file["HDFEOS INFORMATION"]['StructMetadata.0'][()])
    # Split metadata on newlines
    metadata = metadata.split('\\n')
    # Digest the strings down to the coordinates
    # Retrieve Upper Left (ul) coordinates of bounding box
    upper_left = metadata[7].split('=')
    upper_left = upper_left[1].split(',')
    ulx = upper_left[0].replace('(', '')
    uly = upper_left[1].replace(')', '')
    ulx = ulx.split('.')[0][:-6]
    uly = uly.split('.')[0][:-6]
    # Retrieve Lower Right (lr) coordinates of bounding box
    lower_right = metadata[8].split('=')
    lower_right = lower_right[1].split(',')
    lrx = lower_right[0].replace('(', '')
    lry = lower_right[1].replace(')', '')
    lrx = lrx.split('.')[0][:-6]
    lry = lry.split('.')[0][:-6]
    # Make the separate data set (sds) base name for the file (they will end up as <sdsname>_1.tif, <sdsname>_2.tif etc.
    sdsname = os.path.join(path.replace('Original', 'Separate'), basename + '.tif')
    # Form the gdal translate call to convert h5 to one tif per layer
    my_call = [r'C:\OSGeo4W\OSGeo4W.bat',
               'gdal_translate',
               '-sds',
               file,
               sdsname]
    # Print an update
    print(f'Step 2 of 5: Translate .h5 to .tif (one .tif for each band).')
    # Submit the call to the shell
    p = sub.Popen(my_call, stdout=sub.PIPE, stderr=sub.PIPE)
    # Read the response from the call
    stdout, stderr = p.communicate()
    # Print any errors
    if p.returncode != 0:
        print(stdout)
        print(stderr)
    # Form name for merged file
    merged_name = os.path.join(path.replace('Original', 'Merged'), basename + '_merged.tif')
    # Make path to separated band files
    separate_path = path.replace('Original', 'Separate')
    # Get the separate band files
    band_files = [str(f) for f in os.listdir(path.replace('Original', 'Separate')) if f.endswith('.tif')]
    # Form the call to gdal merge
    my_call = [r'C:\OSGeo4W\OSGeo4W.bat',
               'gdal_merge',
               '-separate',
               '-o',
               merged_name]
    # Append the band paths to the call (as input files)
    for band_file in band_files:
        my_call.append(os.path.join(separate_path, band_file))
    # Print an update
    print(f'Step 3 of 5: Merging per-band .tifs in a single .tif file.')
    # Submit the call to the shell
    p = sub.Popen(my_call, stdout=sub.PIPE, stderr=sub.PIPE)
    # Read the response from the call
    stdout, stderr = p.communicate()
    # Print any errors
    if p.returncode != 0:
        print(stdout)
        print(stderr)
    # For each per-band file
    for band_file in band_files:
        # Remove the band file
        os.remove(os.path.join(separate_path, band_file))
    # Name for the COG file
    cog_name = os.path.join(path.replace('Original', 'COG'), basename + '_cog.tif')
    # For the call to gdal translate
    my_call = [r'C:\OSGeo4W\OSGeo4W.bat',
               'gdal_translate',
               '-a_srs', 'EPSG:4326',
               '-a_ullr', ulx, uly, lrx, lry,
               merged_name,
               cog_name,
               '-of', 'COG',
               '-co', 'COMPRESS=DEFLATE']
    # Print an update
    print(f'Step 4 of 5: Converting merged .tif to COG.')
    # Submit the call to the shell
    p = sub.Popen(my_call, stdout=sub.PIPE, stderr=sub.PIPE)
    # Read the response from the call
    stdout, stderr = p.communicate()
    # Print any errors
    if p.returncode != 0:
        print(stdout)
        print(stderr)
    # Remove the merged file
    os.remove(merged_name)
    # Print an update
    print(f'Step 5 of 5: Hosting COG on Google Cloud Storage.')
    # Form the destination blob for the COG
    blob = bucket.blob(f'{basename}_cog.tif')
    # Open the COG
    with open(cog_name, 'rb') as upload_file:
        blob.upload_from_file(upload_file)
    # Make the COG public
    blob.make_public()