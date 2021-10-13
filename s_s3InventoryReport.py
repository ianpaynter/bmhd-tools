import c_s3Intentory
import s3InventoryProcessing
import os
import datetime
import json
import numpy as np
from matplotlib import pyplot as plt
import matplotlib as mpl
import requests
import json

# Set matplotlib defaults for fonts
mpl.rc('font', family='Times New Roman')
mpl.rc('axes', labelsize=12)
mpl.rc('xtick', labelsize=10)
mpl.rc('ytick', labelsize=10)

# Specify a date for the report or "latest"
report_date = "latest"
# Cost per GB per month ($)
cost_per_month = 0.023

# Root directory for manifest files
root_dir = "F:/USRA/BMHDTools/manifests/"

# Run the inventory processing to make sure everything is up to date
s3InventoryProcessing.main()

# Latest manifest
latest_manifest = None

# For each file
for root, directory, files in os.walk(f'{root_dir}'):
    # For each file
    for file in files:
        # If it's a manifest
        if "manifest.json" in file:
            # Split it to get the date as datetime object
            manifest_date = datetime.datetime.strptime(file.split('_')[0], "%Y-%m-%d")
            # If there is no latest manifest yet
            if latest_manifest is None:
                # Set current manifest
                latest_manifest = manifest_date
            # Otherwise, if the new manifest date is later
            elif manifest_date.date() > latest_manifest.date():
                # Set current manifest
                latest_manifest = manifest_date

# Print update
print(f"All manifest files up to date. Latest manifest is from {latest_manifest.date()}.")

# Summary results object
currSummary = c_s3Intentory.InventorySummary()

# Open the friendly json file for the latest manifest
with open(f'{root_dir}{latest_manifest.date()}_files/{latest_manifest.date()}_inventory.json', 'r') as f:
    # Load the list of dictionaries from the file
    inventory_dicts_list = json.load(f)
    # List to receive inventory objects
    inventory_objects = []
    # For each dictionary in the list
    for in_dict in inventory_dicts_list:
        # Create object
        currInv = c_s3Intentory.InvObject()
        # Load attributes from the dictionary
        currInv.load_from_json(in_dict)
        # Append to the list
        inventory_objects.append(currInv)
# Object sizes
object_sizes = []
# Large objects
large_objects = []
large_object_size = 0
# Dormant objects
dormant_objects = []
dormant_object_size = 0
# For each inventory object in the manifest
for invObj in inventory_objects:
    # Append the size converted to GB
    object_sizes.append(invObj.size * 1e-9)
    # Add to running totals
    currSummary.total_size += invObj.size * 1e-9
    currSummary.total_objects += 1
    # If the size of the object is over a threshold
    if invObj.size > 5 * 1e9:
        # Add to large objects
        large_objects.append(invObj)
        # Add to large object size
        large_object_size += invObj.size
    # Get time delta between object's last access and report date
    objTimeDelta = datetime.timedelta(days=30)
    if latest_manifest.date() - invObj.last_accessed.date() > objTimeDelta:
        # Append to dormant objects
        dormant_objects.append(invObj)
        # Add to size monitoring
        dormant_object_size += invObj.size

# Finish summary
currSummary.mean_size = np.mean(object_sizes)
currSummary.maximum_size = np.max(object_sizes)

# Assemble Slack message
slack_message = {"blocks": [{"type": "header",
                  "text": {
                            "type": "plain_text",
                            "text": f"USRA AWS s3 Bucket Report for {latest_manifest.date()}"
                            }
                    },
                            {"type": "divider"},
                  {"type": "section",
                    "text": {
                                "type": "mrkdwn",
                                "text": f"*Total objects:* {c_s3Intentory.prettify(currSummary.total_objects)}\n"
                                        f"*Total size:* {c_s3Intentory.prettify(np.around(currSummary.total_size, decimals=2))} GB\n"
                                        f"*Total cost per month:*  ${c_s3Intentory.prettify(np.around(currSummary.total_size * cost_per_month, decimals=2))}\n"
                                        f"*Mean object size:* {c_s3Intentory.prettify(np.around(currSummary.mean_size, decimals=2))} GB"
                            }
                    },
                            {"type": "divider"}]
                 }

# If there are any large object warnings
if len(large_objects) > 0:
    # Add a header to the message
    slack_message["blocks"].append({"type": "header",
                  "text": {
                            "type": "plain_text",
                            "text": f"Large objects (>5GB)"
                            }
                    })

    # Add a section
    slack_message["blocks"].append({"type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": f"*Total large objects:* {c_s3Intentory.prettify(len(large_objects))}\n"
                                                f"*Total size:* {c_s3Intentory.prettify(np.around(large_object_size * 1e-9, decimals=2))} GB\n"
                                                f"*Total cost per month:*  ${c_s3Intentory.prettify(np.around(large_object_size * 1e-9 * cost_per_month, decimals=2))}"
                                    }
                                    })

    # If there are too many to report individually
    if len(large_objects) > 10:
        # Add a section
        slack_message["blocks"].append({"type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": f"Too many large files to report them individually."}
                                        })

    # Otherwise
    else:
        # Add a section
        slack_message["blocks"].append({"type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": "*Individual large objects:*"}
                                        })
        # For each large object
        for large_object in large_objects:
            # Add a section
            slack_message["blocks"].append({"type": "section",
                                            "text": {
                                                "type": "mrkdwn",
                                                "text": f'*Object Key:* {large_object.key_name}\n'
                                                        f'*Size:* {c_s3Intentory.prettify(np.around(large_object.size * 1e-9, decimals=2))} GB\n'
                                                        f'*Cost per Month:* ${c_s3Intentory.prettify(np.around(large_object.size * 1e-9 * cost_per_month, decimals=2))}\n'
                                                        f'*Last accessed:* {large_object.last_accessed.date()}\n\n'}
                                            })

# Otherwise
else:
    # Add a header to the message
    slack_message["blocks"].append({"type": "header",
                          "text": {
                              "type": "plain_text",
                              "text": f"No large objects (>5GB) to report"
                          }
                          })
# Add divider
slack_message["blocks"].append({"type": "divider"})

# If there are any dormant objects
if len(dormant_objects) > 0:
    # Add a header to the message
    slack_message["blocks"].append({"type": "header",
                                    "text": {
                                        "type": "plain_text",
                                        "text": f"Dormant objects (>30 days since last access)"
                                    }
                                    })
    # Add a section
    slack_message["blocks"].append({"type": "section",
                                    "text": {
                                        "type": "mrkdwn",
                                        "text": f"*Total dormant objects:* {c_s3Intentory.prettify(len(dormant_objects))}\n"
                                                f"*Total size:* {c_s3Intentory.prettify(np.around(dormant_object_size * 1e-9, decimals=2))} GB\n"
                                                f"*Total cost per month:*  ${c_s3Intentory.prettify(np.around(dormant_object_size * 1e-9 * cost_per_month, decimals=2))}"
                                    }
                                    })
    # If there are too many to report individually
    if len(dormant_objects) > 10:
        # Add a section
        slack_message["blocks"].append({"type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": f"Too many dormant files to report them individually."}
                                        })
    # Otherwise
    else:
        # Add a section
        slack_message["blocks"].append({"type": "section",
                                        "text": {
                                            "type": "mrkdwn",
                                            "text": "*Individual dormant objects:*"}
                                        })
        # For each dormant object
        for dormant_object in dormant_objects:
            # Add a section
            slack_message["blocks"].append({"type": "section",
                                            "text": {
                                                "type": "mrkdwn",
                                                "text": f'*Object Key:* {dormant_object.key_name}\n'
                             f'*Size:* {c_s3Intentory.prettify(np.around(dormant_object.size * 1e-9, decimals=2))} GB\n'
                             f'*Cost per Month:* ${c_s3Intentory.prettify(np.around(dormant_object.size * 1e-9 * cost_per_month, decimals=2))}\n'
                             f'*Last accessed:* {dormant_object.last_accessed.date()}\n\n'}
                                            })
# Otherwise (no dormant objects)
else:
    # Add a header to the message
    slack_message["blocks"].append({"type": "header",
                          "text": {
                              "type": "plain_text",
                              "text": f"No dormant objects (>30 days since last access) to report"
                          }
                          })

#print(slack_message)

r = requests.post("https://hooks.slack.com/services/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",
                  data=json.dumps(slack_message),
                  headers={'Content-Type': 'application/json'})

#print(r.status_code)