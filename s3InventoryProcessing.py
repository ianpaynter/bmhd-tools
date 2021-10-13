import boto3
import os
import gzip
import datetime
import c_s3Intentory
import json

# Main function to get all manifests and files up to date
def main():

    # Create s3 resource
    s3 = boto3.resource('s3')

    # Bucket object
    analytics_bucket = s3.Bucket('usra-analytics')

    # Print message
    print("Checking for new s3 inventory manifests and files.")

    # For each object in the bucket
    for obj in analytics_bucket.objects.all():
        # If the object is a manifest
        if "manifest.json" in obj.key:
            # Split the key on the '/'
            split_key = obj.key.split('/')
            # Create a datetime object from the second to last element
            manifest_date = datetime.datetime.strptime(split_key[-2], "%Y-%m-%dT%H-%MZ")
            # Check if the manifest file was already downloaded
            if os.path.exists(f'F:/USRA/BMHDTools/manifests/{manifest_date.date()}_manifest.json') is False:
                # Print message
                print(f"Downloading manifest for {manifest_date.date()}")
                # Download the file
                analytics_bucket.Object(obj.key).download_file(f'F:/USRA/BMHDTools/manifests/{manifest_date.date()}_manifest.json')

    # For each file
    for root, directory, files in os.walk(f'F:/USRA/BMHDTools/manifests/'):
        # For each file
        for file in files:
            # If it's a manifest
            if "manifest.json" in file:
                # Get manifest date
                manifest_date = datetime.datetime.strptime(file.split('_')[0], "%Y-%m-%d")
                # Open each manifest
                with open(f'{root}{file}', 'r') as f:
                    # Load the json dictionary
                    manifest_dict = json.load(f)
                    # If there is no directory for the inventory files
                    if os.path.exists(f'{root}{manifest_date.date()}_files/') is False:
                        # Print message
                        print(f"Creating directory for {manifest_date.date()} manifest.")
                        # Create directory
                        os.mkdir(f'{root}{manifest_date.date()}_files/')
                    # If there is no friendly json format of the inventory objects
                    if os.path.exists(f'{root}{manifest_date.date()}_files/{manifest_date.date()}_inventory.json') is False:
                        # Print message
                        print(f"Creating .json file from inventory files for {manifest_date.date()} manifest.")
                        # Make a list for the objects
                        object_list = []
                        # For each inventory file in the manifest
                        for inventory_file in manifest_dict["files"]:
                            # Get the name
                            file_name = inventory_file["key"].split('/')[-1]
                            # If the inventory file is not downloaded
                            if os.path.exists(f'{root}{manifest_date.date()}_files/{file_name}') is False:
                                # Print message
                                print(f"Downloading inventory file {file_name[0:5]}...{file_name[-6:]} for {manifest_date.date()} manifest.")
                                # Download the file
                                s3.Object('usra-analytics',
                                          inventory_file["key"]).download_file(f'{root}{manifest_date.date()}_files/{file_name}')
                            # Load the inventory file
                            with gzip.open(f'{root}{manifest_date.date()}_files/{file_name}', 'rb') as f:
                                # For each line
                                for line in f:
                                    # Divide up the line entry
                                    inventory_line = line.decode().strip().split(',')
                                    # Create an inventory object
                                    currInv = c_s3Intentory.InvObject()
                                    # Load the attributes from the inventory line
                                    currInv.load_from_inventory(inventory_line)
                                    # Add flattened version to the object list
                                    object_list.append(currInv.flatten())
                        # Save the object list as a json file
                        with open(f'{root}{manifest_date.date()}_files/{manifest_date.date()}_inventory.json', 'w') as of:
                            # Dump the output list to the file
                            json.dump(object_list, of, indent=4)

# If run as main
if __name__ == "__main__":
    # Run main
    main()

