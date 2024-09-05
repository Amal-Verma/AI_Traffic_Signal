import tkinter as tk
from PIL import Image, ImageTk
from tkinter.filedialog import askopenfilename
import os

def get_line_points(image_path):
    # Load the image using PIL
    img = Image.open(image_path)
    img_width, img_height = img.size

    # Set up the tkinter window
    root = tk.Tk()
    root.title("Select Line Points")
    root.geometry(f"{img_width}x{img_height}")

    # Convert the image to a format that tkinter can use
    tk_img = ImageTk.PhotoImage(img)

    # Create a canvas to display the image
    canvas = tk.Canvas(root, width=img_width, height=img_height)
    canvas.pack()

    # Display the image on the canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

    # List to store the selected points
    points = []

    # Function to handle mouse clicks
    def click_event(event):
        if len(points) < 2:
            # Store the clicked point
            points.append((event.x, event.y))
            # Draw a small circle to indicate the point
            canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, fill='green')
        if len(points) == 2:
            # Draw the line between the two selected points
            canvas.create_line(points[0][0], points[0][1], points[1][0], points[1][1], fill='red', width=2)

    # Function to handle the Enter key press
    def on_enter(event):
        if len(points) == 2:
            root.quit()  # Close the window when Enter is pressed

    # Bind the click event to the canvas
    canvas.bind("<Button-1>", click_event)
    # Bind the Enter key event to the root window
    root.bind("<Return>", on_enter)

    # Start the tkinter main loop
    root.mainloop()
    root.destroy()
    return points

def get_two_lines(image_path):
    # Load the image using PIL
    img = Image.open(image_path)
    img_width, img_height = img.size

    # Set up the tkinter window
    root = tk.Tk()
    root.title("Select Two Lines")
    root.geometry(f"{img_width}x{img_height}")

    # Convert the image to a format that tkinter can use
    tk_img = ImageTk.PhotoImage(img)

    # Create a canvas to display the image
    canvas = tk.Canvas(root, width=img_width, height=img_height)
    canvas.pack()

    # Display the image on the canvas
    canvas.create_image(0, 0, anchor=tk.NW, image=tk_img)

    # List to store the selected points
    points = []

    # Function to handle mouse clicks
    def click_event(event):
        if len(points) < 4:
            # Store the clicked point
            points.append((event.x, event.y))
            # Draw a small circle to indicate the point
            canvas.create_oval(event.x-3, event.y-3, event.x+3, event.y+3, fill='green')
            # Draw a line if there are two points
            if len(points) == 2 or len(points) == 4:
                canvas.create_line(points[-2][0], points[-2][1], points[-1][0], points[-1][1], fill='blue', width=2)
            if len(points) == 4:
                # Draw both lines
                canvas.create_line(points[0][0], points[0][1], points[1][0], points[1][1], fill='red', width=2)
                canvas.create_line(points[2][0], points[2][1], points[3][0], points[3][1], fill='red', width=2)
    
    # Function to handle the Enter key press
    def on_enter(event):
        if len(points) == 4:
            root.quit()  # Close the window when Enter is pressed

    # Bind the click event to the canvas
    canvas.bind("<Button-1>", click_event)
    # Bind the Enter key event to the root window
    root.bind("<Return>", on_enter)

    # Start the tkinter main loop
    root.mainloop()
    
    root.destroy()

    # Save the annotated image
    save_path = image_path + "_lines.jpg"
    img.save(save_path)
    print(f"Annotated image saved as {save_path}")

    return points

def select_video():
    # Hide the root window
    root = tk.Tk()
    root.withdraw()
    
    # Open a file dialog to select a video file
    video_path = askopenfilename(
        title="Select a Video File",
        filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")]
    )
    
    # If a file was selected
    if video_path:
        # Extract the directory and filename
        dir_name = os.path.dirname(video_path)
        base_name = os.path.basename(video_path)
        
        # Split the filename and extension
        file_name, ext = os.path.splitext(base_name)
        
        # Generate the output path by appending '_out' before the extension
        output_path = os.path.join(dir_name, f"{file_name}_out{ext}")
        
        root.destroy()  # Properly close the Tkinter instance
        return video_path, output_path
    else:
        root.destroy()  # Properly close the Tkinter instance
        return None, None