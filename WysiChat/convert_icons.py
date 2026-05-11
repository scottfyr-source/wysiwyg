import base64
import os

def image_to_base64(filename):
    """Reads an image and returns the base64 bytes string."""
    if not os.path.exists(filename):
        print(f"# Error: File not found: {filename}")
        return None
    
    with open(filename, "rb") as f:
        return base64.b64encode(f.read())

if __name__ == "__main__":
    # Assumes images are in the same folder as this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define your image filenames here
    logo_path = os.path.join(script_dir, "fyrlogo.png")
    alert_path = os.path.join(script_dir, "fyrlogo_alert.png")
    
    print("# --- COPY BELOW THIS LINE ---")
    
    logo_b64 = image_to_base64(logo_path)
    if logo_b64:
        print(f"ICON_DEFAULT = {logo_b64}")
    
    print("")
    
    alert_b64 = image_to_base64(alert_path)
    if alert_b64:
        print(f"ICON_ALERT = {alert_b64}")
        
    print("# --- COPY ABOVE THIS LINE ---")