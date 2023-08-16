from tkinter import filedialog
import tkinter as tk
import subprocess
import os
import shutil
os.environ["RUST_BACKTRACE"] = "1"

# Path to WhiteboxTools executable
whitebox_path = ".\WBT\whitebox_tools.exe"

# Set the root Tkinter window
root = tk.Tk()
root.withdraw()

# Select the clipped DEM file using a file dialog
clipped_dem_path = filedialog.askopenfilename(title="Select Clipped DEM File")

# Create a folder for the outputs
output_folder = "HydrologicalAnalysis"
os.makedirs(output_folder, exist_ok=True)


def run_whitebox_command(command, output_file):
    try:
        subprocess.call(command)
        if os.path.exists(output_file):
            return True
        else:
            print(f"Error: Output file '{output_file}' not found.")
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
    return False


# Perform filling
filled_dem_path = os.path.join(output_folder, "FilledDEM.tif")
fill_command = [
    whitebox_path,
    "--run=fill_depressions_planchon_and_darboux",
    f"--input='{clipped_dem_path}'",
    f"--fix_flats=true",
    # f"--flat_increment=none",
    f"--output='{filled_dem_path}'"
]
if run_whitebox_command(fill_command, filled_dem_path):
    print("Filling completed.")
else:
    print("Error occurred during filling.")

# Perform flow direction
flow_direction_path = os.path.join(output_folder, "FlowDirection.tif")
flow_direction_command = [
    whitebox_path,
    "--run=D8Pointer",
    f"--dem='{filled_dem_path}'",
    f"--output='{flow_direction_path}'",
    f"--esri_pntr=true"
]
if run_whitebox_command(flow_direction_command, flow_direction_path):
    print("Flow direction calculation completed.")
else:
    print("Error occurred during flow direction calculation.")

# Perform flow accumulation

flow_accumulation_path = os.path.join(output_folder, "FlowAccumulation.tif")
flow_accumulation_command = [
    whitebox_path,
    "--run=d8_flow_accumulation",
    f"--dem='{flow_direction_path}'",
    f"--out_type='Specific Contributing Area'",
    f"--output='{flow_accumulation_path}'",
    f"--outputtype='cells'",
    f"--esri-pntr=true",
    f"--pntr=true"
]
if run_whitebox_command(flow_accumulation_command, flow_accumulation_path):
    print("Flow accumulation calculation completed.")
else:
    print("Error occurred during flow accumulation calculation.")


# Perform raster calculator
raster_calculator_path = os.path.join(output_folder, "RasterCalculator.tif")
raster_calculator_command = [
    whitebox_path,
    "--run=RasterCalculator",
    f"--statement='{flow_accumulation_path}' <= 0.11)",
    f"--output='{raster_calculator_path}'"
]
if run_whitebox_command(raster_calculator_command, raster_calculator_path):
    print("Raster calculator completed.")
else:
    print("Error occurred during raster calculator.")

# Perform extract streams
extracted_streams_path = os.path.join(output_folder, "ExtractedStreams.tif")
subprocess.call([
    whitebox_path,
    "--run=extract_streams",
    f"--flow_accum='{flow_accumulation_path}'",
    f"--threshold=0.090",
    # "--zero_background",
    f"--output='{extracted_streams_path}'"
])

# Perform stream order
stream_order_path = os.path.join(output_folder, "StreamOrder.tif")
stream_order_command = [
    whitebox_path,
    "--run=strahler_stream_order",
    f"--streams='{extracted_streams_path}'",
    f"--d8_pntr='{flow_direction_path}'",
    f"--output='{stream_order_path}'",
    f"--esri_pntr=true"
]
if run_whitebox_command(stream_order_command, stream_order_path):
    print("Stream order calculation completed.")
else:
    print("Error occurred during stream order calculation.")

# Perform hack stream order
hack_stream_order_path = os.path.join(output_folder, "HackStreamOrder.tif")
hack_stream_order_command = [
    whitebox_path,
    "--run=hack_stream_order",
    f"--streams='{extracted_streams_path}'",
    f"--d8_pntr='{flow_direction_path}'",
    f"--output='{hack_stream_order_path}'",
    f"--esri_pntr=true"
]
if run_whitebox_command(hack_stream_order_command, hack_stream_order_path):
    print("Stream order calculation completed.")
else:
    print("Error occurred during stream order calculation.")


# Perform topological stream order
topological_stream_order_path = os.path.join(
    output_folder, "TopologicalStreamOrder.tif")
topological_stream_order_command = [
    whitebox_path,
    "--run=topological_stream_order",
    f"--streams='{extracted_streams_path}'",
    f"--d8_pntr='{flow_direction_path}'",
    f"--output='{topological_stream_order_path}'",
    "--esri_pntr=true"
]
if run_whitebox_command(topological_stream_order_command, topological_stream_order_path):
    print("Stream order calculation completed.")
else:
    print("Error occurred during stream order calculation.")


# Perform stream link
stream_link_path = os.path.join(output_folder, "StreamLink.tif")
stream_link_command = [
    whitebox_path,

    "--run=stream_link_class",
    f"--d8_pntr='{flow_direction_path}'",
    f"--streams='{stream_order_path}'",
    f"--output='{stream_link_path}'",
    f"--esri_pntr=true",
]
if run_whitebox_command(stream_link_command, stream_link_path):
    print("Stream Link conversion completed.")
else:
    print("Error occurred during stream link conversion.")

    # Perform remove short streams
remove_short_streams_path = os.path.join(
    output_folder, "RemoveShortStreams.tif")
remove_short_streams_command = [
    whitebox_path,
    "--run=remove_short_streams",
    f"--d8_pntr='{flow_direction_path}'",
    f"--streams='{stream_order_path}'",
    f"--output='{remove_short_streams_path}'",
    f"--esri_pntr=true"
]
if run_whitebox_command(remove_short_streams_command, remove_short_streams_path):
    print("Stream to feature conversion completed.")
else:
    print("Error occurred during stream to feature conversion.")

    # Perform find main stem
find_main_stem_path = os.path.join(output_folder, "Find_Main_Stem_Feature.tif")
find_main_stem_command = [
    whitebox_path,
    "--run=find_main_stem",
    f"--d8_pntr='{flow_direction_path}'",
    f"--streams='{hack_stream_order_path}'",
    f"--output='{find_main_stem_path}'",
    f"--esri_pntr=true"
]
if run_whitebox_command(find_main_stem_command, find_main_stem_path):
    print("Stream to feature conversion completed.")
else:
    print("Error occurred during stream to feature conversion.")

    # Perform shreve stream magnitude

shreve_stream_magnitude_path = os.path.join(
    output_folder, "ShreveStreamMagnitude.tif")
shreve_stream_magnitude_command = [
    whitebox_path,
    "--run=shreve_stream_magnitude",
    f"--d8_pntr='{flow_direction_path}'",
    f"--streams='{extracted_streams_path}'",
    f"--output='{shreve_stream_magnitude_path}'",
    f"--esri_pntr=true"

]
if run_whitebox_command(shreve_stream_magnitude_command, shreve_stream_magnitude_path):
    print("Stream to feature conversion completed.")
else:
    print("Error occurred during stream to feature conversion.")

# Perform basins
basins_path = os.path.join(output_folder, "Basins.tif")
subprocess.call([
    whitebox_path,
    "--run=basins",
    f"--d8_pntr='{flow_direction_path}'",
    f"--esri_pntr=true",
    f"--output='{basins_path}'"
])

# Perform sub basins
sub_basins_path = os.path.join(output_folder, "SubBasins.tif")
subprocess.call([
    whitebox_path,
    "--run=subbasins",
    f"--d8_pntr='{flow_direction_path}'",
    f"--streams='{extracted_streams_path}'",
    f"--output='{sub_basins_path}'",
    f"--esri_pntr=true"
])

# Perform prune streams
find_main_stem2_path = os.path.join(
    output_folder, "Find_Main_Stem_Feature2.tif")
find_main_stem2_command = [
    whitebox_path,
    "--run=find_main_stem",
    f"--d8_pntr='{flow_direction_path}'",
    f"--streams='{shreve_stream_magnitude_path}'",
    f"--output='{find_main_stem2_path}'",
    f"--esri_pntr=true"
]
if run_whitebox_command(find_main_stem2_command, find_main_stem2_path):
    print("Stream to feature conversion completed.")
else:
    print("Error occurred during stream to feature conversion.")

# Perform stream to feature
stream_to_feature_path = os.path.join(output_folder, "StreamToFeature.shp")
stream_to_feature_command = [
    whitebox_path,
    "--run=raster_streams_to_vector",
    f"--d8_pntr='{flow_direction_path}'",
    f"--streams='{stream_order_path}'",
    f"--output='{stream_to_feature_path}'",
    f"--esri_pntr=true"
]
if run_whitebox_command(stream_to_feature_command, stream_to_feature_path):
    print("Stream to feature conversion completed.")
else:
    print("Error occurred during stream to feature conversion.")



# Perform extract nodes
extract_nodes_path = os.path.join(output_folder, "PourPoints.shp")
extract_nodes_command = [
    whitebox_path,
    "--run=extract_nodes",
    f"--input='{stream_to_feature_path}'",
    f"--output='{extract_nodes_path}'"
]
if run_whitebox_command(extract_nodes_command, extract_nodes_path):
    print("Stream to feature conversion completed.")
else:
    print("Error occurred during stream to feature conversion.")

# Select the Pour Points file using a file dialog
pour_pnts_path = filedialog.askopenfilename(title="Select Pour Points File")

# Perform snap pour points
pour_points_path = os.path.join(output_folder, "SnapPourPoints.shp")
jenson_snap_pour_points_command = [
    whitebox_path,
    "--run=jenson_snap_pour_points",
    f"--pour_pts='{pour_pnts_path}'",
    f"--streams='{extracted_streams_path}'",
    f"--output='{pour_points_path}'",
    f"--snap_dist=5"
]
if run_whitebox_command(jenson_snap_pour_points_command, pour_points_path):
    print("Snap pour points completed.")
else:
    print("Error occurred during snap pour points.")

# Perform watershed
watershed_path = os.path.join(output_folder, "Watershed.tif")
watershed_command = [
    whitebox_path,
    "--run=Watershed",
    f"--d8_pntr='{flow_direction_path}'",
    f"--pour_pts='{extract_nodes_path}'",
    f"--output='{watershed_path}'",
    f"--esri_pntr=true"
]
if run_whitebox_command(watershed_command, watershed_path):
    print("Watershed calculation completed.")
else:
    print("Error occurred during watershed calculation.")


# Capitalize the process names
process_names = [
    "FilledDEM",
    "FlowDirection",
    "FlowAccumulation",
    "RasterCalculator",
    "StreamOrder",
    "Basins",
    "StreamLink",
    "StreamToFeature",
    "SnapPourPoints",
    "ExtractedStreams",
    "HackStreamOrder",
    "Find_Main_Stem_Feature",
    "Find_Main_Stem_Feature2",
    "RemoveShortStreams",
    "TopologicalStreamOrder",
    "PourPoints",
    "ShreveStreamMagnitude",
    "SubBasins",
    "Watershed"
]

# Create folders with capitalized process names
for process_name in process_names:
    folder_name = process_name.capitalize()
    process_folder = os.path.join(output_folder, folder_name)
    os.makedirs(process_folder, exist_ok=True)

    # Move the corresponding output file to the process folder
    extensions = [".tif", ".shp", ".dbf", ".prj", ".shx"]

    output_file = os.path.join(output_folder, folder_name + ".tif")
    output_file1 = os.path.join(output_folder, folder_name + ".shp")
    output_file2 = os.path.join(output_folder, folder_name + ".dbf")
    output_file3 = os.path.join(output_folder, folder_name + ".shx")
    output_file4 = os.path.join(output_folder, folder_name + ".prj")

    if os.path.exists(output_file):
        shutil.move(output_file, process_folder)

    if os.path.exists(output_file1):
        shutil.move(output_file1, process_folder)

    if os.path.exists(output_file2):
        shutil.move(output_file2, process_folder)

    if os.path.exists(output_file3):
        shutil.move(output_file3, process_folder)

    if os.path.exists(output_file4):
        shutil.move(output_file4, process_folder)

# Print completion message
print("Hydrological analysis completed.")
