import h5py

# File name variables
base_file = "VNP46A2.A2016009.h29v05.001.2020258174450"
base_path = "/content/drive/My Drive/ColabVNP46A2Data/"

# Load h5 file
h5file = h5py.File(f"{base_path}{base_file}.h5", 'r')
# Get the metadata
metadata = str(h5file["HDFEOS INFORMATION"]['StructMetadata.0'][()])
# Split metadata on newlines
metadata = metadata.split('\\n')
# Digest the strings down to the coordinates (details are boring)
upper_left = metadata[7].split('=')
upper_left = upper_left[1].split(',')
ulx = upper_left[0].replace('(', '')
uly = upper_left[1].replace(')', '')
ulx = ulx.split('.')[0][:-6]
uly = uly.split('.')[0][:-6]

lower_right = metadata[8].split('=')
lower_right = lower_right[1].split(',')
lrx = lower_right[0].replace('(', '')
lry = lower_right[1].replace(')', '')
lrx = lrx.split('.')[0][:-6]
lry = lry.split('.')[0][:-6]

# Print the bounding box coordinates
print(ulx, uly, lrx, lry)

