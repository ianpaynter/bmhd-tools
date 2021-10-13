import matplotlib as mpl
from matplotlib import pyplot as plt
import numpy as np

# Set matplotlib defaults for fonts
mpl.rc('font', family='Times New Roman')
mpl.rc('axes', labelsize=12)
mpl.rc('xtick', labelsize=10)
mpl.rc('ytick', labelsize=10)

# ARL dict
arl_dict = {}

# For each ARL
for arl in np.arange(1, 10):
    arl_dict[arl] = []

# Applications and ARLs
apps_n_arls = [["Fishing", 3],
               ["COVID", 4],
               ["Electrification", 5],
               ["Electricity Reliability", 8],
               ["Figure Metadata", 8]]

# Start a figure
fig = plt.figure(figsize=(10, 10))
# Add a subplot
ax = fig.add_subplot(1, 1, 1)

# For each app/ARL
for app in apps_n_arls:
    arl_dict[app[1]].append(app[0])

# App count
app_count = 0

x_labels = []

# For each ARL
for arl in sorted(arl_dict.keys(), reverse=True):
    # For each app
    for app in arl_dict[arl]:
        # Add to labels
        x_labels.append(app)
        # Add to count
        app_count += 1
        # Make a patch
        curr_patch = mpl.patches.Rectangle((app_count - 0.45,
                                            0.5),
                                           width=0.9,
                                           height=arl + 0.5,
                                           facecolor='royalblue',
                                           fill=True,
                                           linewidth=1,
                                           edgecolor='k')
        # Add patch
        ax.add_patch(curr_patch)

#ax.set_title(f'{scan_year}, scan {scan_id} voxels with {plot_type}(s)')
ax.set_xlabel('Application')
ax.set_ylabel('ARL')

ax.set_xlim(0.25, app_count + 0.75)
ax.set_ylim(0.5, 9.5)
ax.set_yticks(np.arange(1, 10))
ax.set_xticks(np.arange(1, app_count + 1))
ax.set_xticklabels(x_labels)

plt.show()
# Set title and axes labels


