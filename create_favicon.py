from PIL import Image
import os

def create_optimal_favicon():
    """Create a 64x64 pixel favicon from logo_small.png for optimal browser display"""
    try:
        # Open the original logo
        with Image.open("picture/logo/logo_small.png") as img:
            # Convert to RGBA if not already
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Resize to 64x64 pixels (largest standard favicon size)
            favicon = img.resize((64, 64), Image.Resampling.LANCZOS)
            
            # Save as favicon.png
            favicon.save("picture/logo/favicon.png", "PNG")
            print("✅ Created optimal favicon (64x64 pixels) at picture/logo/favicon.png")
            
    except FileNotFoundError:
        print("❌ logo_small.png not found in picture/logo/")
    except Exception as e:
        print(f"❌ Error creating favicon: {e}")

if __name__ == "__main__":
    create_optimal_favicon() 