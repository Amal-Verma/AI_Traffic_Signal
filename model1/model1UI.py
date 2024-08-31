import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

from VehicleCounter import VehicleCounter  # Adjust import as necessary

class ImageClassifierApp(tk.Tk):
    def __init__(self, model):
        super().__init__()
        
        self.title("Image Classifier")
        self.geometry("500x500")
        
        # Store model and image path
        self.model = model
        self.image_path = None
        
        # Create containers for the pages
        self.frames = {}
        
        # Initialize pages
        for F in (StartPage, ResultPage):
            page_name = F.__name__
            frame = F(parent=self, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        self.show_frame("StartPage")
    
    def show_frame(self, page_name):
        """Show the frame for the given page name."""
        frame = self.frames[page_name]
        frame.tkraise()
    
    def process_image(self):
        """Calculate and display the model's output."""
        if self.image_path:
            try:
                # Load the image
                image = Image.open(self.image_path)
                
                # Here, you would typically preprocess the image as required by your model
                # For example:
                # image_tensor = preprocess(image)  # Replace with actual preprocessing
                # output = self.model.predict(image_tensor)  # Replace with actual model prediction
                
                # Assuming your model has a method that takes an image path and returns a number
                output = self.model.count(self.image_path)  # Replace with actual method
                
                # Pass the output to the result page
                result_page = self.frames["ResultPage"]
                result_page.show_result(output)
                
                # Navigate to the result page
                self.show_frame("ResultPage")
            except Exception as e:
                result_page = self.frames["ResultPage"]
                result_page.show_result(f"Error: {str(e)}")

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="Enter Image Path and Send to Model", font=("Helvetica", 16))
        label.pack(pady=20)
        
        # Entry for image path
        self.image_path_entry = tk.Entry(self, width=50)
        self.image_path_entry.pack(pady=10)
        
        self.image_label = tk.Label(self)
        self.image_label.pack(pady=10)
        
        load_button = tk.Button(self, text="Load Image", command=self.load_image)
        load_button.pack(pady=10)
        
        send_button = tk.Button(self, text="Send to Model", command=controller.process_image)
        send_button.pack(pady=10)
    
    def load_image(self):
        """Load and display the image based on the provided path."""
        image_path = self.image_path_entry.get()
        self.controller.image_path = image_path
        try:
            image = Image.open(image_path)
            image.thumbnail((300, 300))
            image = ImageTk.PhotoImage(image)
            self.image_label.config(image=image)
            self.image_label.image = image
        except Exception as e:
            self.image_label.config(text=f"Failed to load image: {str(e)}")
            self.image_label.image = None

class ResultPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        label = tk.Label(self, text="Model's Output", font=("Helvetica", 16))
        label.pack(pady=20)
        
        self.result_label = tk.Label(self, text="", font=("Helvetica", 14))
        self.result_label.pack(pady=10)
        
        back_button = tk.Button(self, text="Back", command=lambda: controller.show_frame("StartPage"))
        back_button.pack(pady=10)
    
    def show_result(self, result):
        """Display the result from the model."""
        self.result_label.config(text=f"Model Output: {result}")

# Initialize and run the app
if __name__ == "__main__":
    model = VehicleCounter()  # Replace with your actual model
    app = ImageClassifierApp(model)
    app.mainloop()
