import qrcode
import random
import os

def generate_random_qr_code(filename="random_qrcode.png"):
    """
    Generates a QR code with a random data string and saves it as a PNG file.
    """
    # Generate a random integer between 10000 and 99999
    random_id = random.randint(10000, 99999)
    # Create the data string to encode
    data = f"https://yourwebsite.com{random_id}"

    # Create a QRCode object
    qr = qrcode.QRCode(
        version=1, # Controls the size; None makes it automatic
        error_correction=qrcode.constants.ERROR_CORRECT_L, # Less than 7% errors can be corrected
        box_size=10, # How many pixels each "box" of the QR code is
        border=4, # How many boxes thick the border should be
    )
    
    # Add the data to the QR code
    qr.add_data(data)
    qr.make(fit=True) # Adjusts size automatically to fit the data

    # Create the QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the image file
    img.save(filename)
    print(f"QR Code generated for data: {data}")
    print(f"QR Code saved as {os.path.abspath(filename)}")

if __name__ == "__main__":
    generate_random_qr_code()
