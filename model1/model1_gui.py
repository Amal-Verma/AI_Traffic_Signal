IMAGE_FOLDER_PATH = "../assets/examples/images"
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os,sys
sys.path.append(os.path.abspath(os.path.join('..')))
from model1.VehicleCounter import VehicleCounter
vehicle_counter = VehicleCounter()

# initialize the main window
root = tk.Tk()
root.title("Vehicle Counter")
root.geometry("800x800")

# load and place the central intersection image
intersection_image = Image.open(f"{IMAGE_FOLDER_PATH}/intersection.png")
intersection_image = intersection_image.resize((200, 200), Image.Resampling.LANCZOS)
intersection_img = ImageTk.PhotoImage(intersection_image)

intersection_label = tk.Label(root, image=intersection_img)
intersection_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

image_paths = {
    "North": None,
    "South": None,
    "East": None,
    "West": None
}

# function to upload and display images
def upload_image(panel,direction):
    file_path = filedialog.askopenfilename()
    if file_path:
        image_paths[direction] = file_path
        image = Image.open(file_path)
        image = image.resize((150, 150), Image.Resampling.LANCZOS)  # resize image to fit panel
        img = ImageTk.PhotoImage(image)
        panel.config(image=img, text="")
        panel.image = img  # keep reference to avoid garbage collection

# create panels for images
north_panel = tk.Label(root, text="North Image", bg="gray")
north_panel.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

south_panel = tk.Label(root, text="South Image", bg="gray")
south_panel.place(relx=0.5, rely=0.8, anchor=tk.CENTER)

east_panel = tk.Label(root, text="East Image", bg="gray")
east_panel.place(relx=0.8, rely=0.5, anchor=tk.CENTER)

west_panel = tk.Label(root, text="West Image", bg="gray")
west_panel.place(relx=0.2, rely=0.5, anchor=tk.CENTER)

# buttons for uploading images
upload_north_button = tk.Button(root, text="Upload North Image", command=lambda: upload_image(north_panel,"North"))
upload_north_button.place(relx=0.5, rely=0.08, anchor=tk.CENTER)

upload_south_button = tk.Button(root, text="Upload South Image", command=lambda: upload_image(south_panel,"South"))
upload_south_button.place(relx=0.5, rely=0.68, anchor=tk.CENTER)

upload_east_button = tk.Button(root, text="Upload East Image", command=lambda: upload_image(east_panel,"East"))
upload_east_button.place(relx=0.8, rely=0.37, anchor=tk.CENTER)

upload_west_button = tk.Button(root, text="Upload West Image", command=lambda: upload_image(west_panel,"West"))
upload_west_button.place(relx=0.2, rely=0.37, anchor=tk.CENTER)

# function to replace images with vehicle count results
def count_vehicles():
    for panel, direction in zip([north_panel, south_panel, east_panel, west_panel], ["North", "South", "East", "West"]):
        image_path = image_paths[direction]
        if not image_path:
            result = "No image"
            panel.config(text=result, image='')
            continue
        print(image_path)
        total,(car,bike,bus,truck) = vehicle_counter.count(image_path)
        result = f"Cars : {car}"
        result += f"\nBikes : {bike}"
        result += f"\nBuses : {bus}"
        result += f"\nTrucks : {truck}"
        result += f"\n\nWeighted Count: {total}"
        panel.config(text=result, image='')

# count button to trigger the vehicle counting
count_button = tk.Button(root, text="COUNT", command=count_vehicles)
count_button.place(relx=0.75, rely=0.75, anchor=tk.CENTER)

# start the Tkinter loop
root.mainloop()
