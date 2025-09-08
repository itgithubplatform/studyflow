#!/usr/bin/env python3
"""
Create placeholder images for StudyFlow using PIL
Run this script to generate basic placeholder images
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    def create_favicon():
        """Create a simple favicon"""
        img = Image.new('RGBA', (32, 32), (13, 110, 253, 255))  # Blue background
        draw = ImageDraw.Draw(img)
        
        # Draw graduation cap shape
        draw.rectangle([8, 12, 24, 16], fill=(255, 255, 255, 255))  # Cap base
        draw.polygon([(6, 12), (16, 8), (26, 12)], fill=(255, 255, 255, 255))  # Cap top
        draw.rectangle([15, 16, 17, 20], fill=(255, 255, 255, 255))  # Tassel
        
        return img
    
    def create_logo():
        """Create StudyFlow logo"""
        img = Image.new('RGBA', (200, 60), (0, 0, 0, 0))  # Transparent background
        draw = ImageDraw.Draw(img)
        
        # Try to use a font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        # Draw text
        draw.text((10, 15), "StudyFlow", fill=(13, 110, 253, 255), font=font)
        
        # Draw graduation cap icon
        draw.rectangle([160, 20, 180, 25], fill=(13, 110, 253, 255))
        draw.polygon([(155, 20), (170, 15), (185, 20)], fill=(13, 110, 253, 255))
        
        return img
    
    def create_hero_placeholder():
        """Create hero background placeholder"""
        img = Image.new('RGB', (1920, 1080), (248, 249, 250))  # Light gray
        draw = ImageDraw.Draw(img)
        
        # Create gradient effect
        for y in range(1080):
            color_value = int(248 - (y / 1080) * 50)  # Gradient from light to darker
            draw.line([(0, y), (1920, y)], fill=(color_value, color_value + 5, color_value + 10))
        
        # Add some geometric shapes
        draw.ellipse([400, 200, 800, 600], fill=(13, 110, 253, 50))  # Semi-transparent blue circle
        draw.ellipse([1200, 400, 1600, 800], fill=(25, 135, 84, 30))  # Semi-transparent green circle
        
        return img
    
    def create_achievement_badge(color, text):
        """Create achievement badge"""
        img = Image.new('RGBA', (128, 128), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw badge circle
        draw.ellipse([10, 10, 118, 118], fill=color)
        draw.ellipse([20, 20, 108, 108], fill=(255, 255, 255, 255))
        draw.ellipse([30, 30, 98, 98], fill=color)
        
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (128 - text_width) // 2
        y = (128 - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        return img
    
    def create_empty_state_svg(filename, title, description):
        """Create SVG for empty states"""
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="300" height="200" viewBox="0 0 300 200" xmlns="http://www.w3.org/2000/svg">
    <defs>
        <linearGradient id="grad1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.1" />
            <stop offset="100%" style="stop-color:#764ba2;stop-opacity:0.1" />
        </linearGradient>
    </defs>
    
    <!-- Background -->
    <rect width="300" height="200" fill="url(#grad1)" rx="10"/>
    
    <!-- Icon placeholder -->
    <circle cx="150" cy="80" r="30" fill="#e9ecef" stroke="#dee2e6" stroke-width="2"/>
    <text x="150" y="90" text-anchor="middle" font-family="Arial" font-size="24" fill="#6c757d">📋</text>
    
    <!-- Title -->
    <text x="150" y="130" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="#495057">{title}</text>
    
    <!-- Description -->
    <text x="150" y="150" text-anchor="middle" font-family="Arial" font-size="12" fill="#6c757d">{description}</text>
</svg>'''
        
        with open(f'static/img/{filename}', 'w') as f:
            f.write(svg_content)
    
    def main():
        """Create all placeholder images"""
        # Create img directory if it doesn't exist
        os.makedirs('static/img', exist_ok=True)
        
        print("Creating placeholder images for StudyFlow...")
        
        # Create favicon
        favicon = create_favicon()
        favicon.save('static/img/favicon.ico', format='ICO', sizes=[(32, 32), (16, 16)])
        print("✓ Created favicon.ico")
        
        # Create logo
        logo = create_logo()
        logo.save('static/img/logo.png', format='PNG')
        print("✓ Created logo.png")
        
        # Create hero background
        hero = create_hero_placeholder()
        hero.save('static/img/hero-bg.jpg', format='JPEG', quality=85, optimize=True)
        print("✓ Created hero-bg.jpg")
        
        # Create achievement badges
        badges = [
            ((205, 133, 63), "bronze-badge.png", "Bronze"),  # Bronze
            ((192, 192, 192), "silver-badge.png", "Silver"),  # Silver
            ((255, 215, 0), "gold-badge.png", "Gold"),  # Gold
            ((229, 228, 226), "platinum-badge.png", "Plat")  # Platinum
        ]
        
        for color, filename, text in badges:
            badge = create_achievement_badge(color, text)
            badge.save(f'static/img/{filename}', format='PNG')
            print(f"✓ Created {filename}")
        
        # Create empty state SVGs
        empty_states = [
            ("no-tasks.svg", "No Tasks Yet", "Start by adding your first task"),
            ("no-data.svg", "No Data Available", "Complete some tasks to see analytics"),
            ("completed-tasks.svg", "All Done!", "Great job completing all tasks")
        ]
        
        for filename, title, description in empty_states:
            create_empty_state_svg(filename, title, description)
            print(f"✓ Created {filename}")
        
        print("\n🎉 All placeholder images created successfully!")
        print("\nImages created in static/img/:")
        print("- favicon.ico (32x32)")
        print("- logo.png (200x60)")
        print("- hero-bg.jpg (1920x1080)")
        print("- bronze-badge.png (128x128)")
        print("- silver-badge.png (128x128)")
        print("- gold-badge.png (128x128)")
        print("- platinum-badge.png (128x128)")
        print("- no-tasks.svg (300x200)")
        print("- no-data.svg (300x200)")
        print("- completed-tasks.svg (300x200)")
        
        print("\n💡 To use custom images:")
        print("1. Replace these files with your own designs")
        print("2. Keep the same filenames and dimensions")
        print("3. Optimize images for web (use tools like TinyPNG)")
        
    if __name__ == "__main__":
        main()

except ImportError:
    print("PIL (Pillow) not installed. Install with: pip install Pillow")
    print("\nAlternatively, use these free online tools:")
    print("🎨 Favicon: https://favicon.io/favicon-generator/")
    print("🖼️ Logo: https://www.canva.com/")
    print("📸 Hero: https://unsplash.com/s/photos/studying")
    print("🏆 Badges: https://www.flaticon.com/")
    print("📋 Icons: https://heroicons.com/")