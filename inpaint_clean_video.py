import os
import cv2
import numpy as np
import subprocess
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageDraw, ImageFont

font_main_path = r'C:\Windows\Fonts\arialbd.ttf'

def inpaint_frame(i):
    src_file = f'video_frames/frame_{i:04d}.png'
    dst_file = f'processed_frames/frame_{i:04d}.jpg'
    
    if not os.path.exists(src_file):
        return
        
    img = cv2.imread(src_file)
    h, w = img.shape[:2]
    mask = np.zeros((h, w), dtype=np.uint8)
    
    # Text region roughly y: 400..600, x: 500..1420
    # Scene 1-5 text removal:
    if 1 <= i <= 284:
        roi = img[420:580, 580:1340]
        # White text detection: high R, G, B with low saturation
        r, g, b = roi[:,:,2], roi[:,:,1], roi[:,:,0]
        white_mask = (r > 175) & (g > 175) & (b > 175) & (np.abs(r.astype(int) - g.astype(int)) < 30)
        mask[420:580, 580:1340][white_mask] = 255
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.dilate(mask, kernel, iterations=2)
        inpainted = cv2.inpaint(img, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
        
    elif 285 <= i <= 360:
        # Top text 'happy hens outside / tasty yolks inside'
        roi_top = img[170:360, 480:1440]
        r_t, g_t, b_t = roi_top[:,:,2], roi_top[:,:,1], roi_top[:,:,0]
        top_mask = (r_t > 175) & (g_t > 175) & (b_t > 175) & (np.abs(r_t.astype(int) - g_t.astype(int)) < 30)
        mask[170:360, 480:1440][top_mask] = 255
        
        # Carton logo 'HAPPY egg' area
        roi_carton = img[410:600, 580:830]
        r_c, g_c, b_c = roi_carton[:,:,2], roi_carton[:,:,1], roi_carton[:,:,0]
        carton_mask = (r_c > 160) & (g_c > 160) & (b_c > 160)
        mask[410:600, 580:830][carton_mask] = 255
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
        mask = cv2.dilate(mask, kernel, iterations=2)
        inpainted = cv2.inpaint(img, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
        
        # Add clean Nutrifresh branding on closing carton
        im_pil = Image.fromarray(cv2.cvtColor(inpainted, cv2.COLOR_BGR2RGB))
        draw = ImageDraw.Draw(im_pil)
        
        font_carton = ImageFont.truetype(font_main_path, 40)
        font_end = ImageFont.truetype(font_main_path, 56)
        
        # Top text
        line1 = 'Nutrifresh hens outside.'
        line2 = 'Tasty orange yolks inside.'
        bbox1 = draw.textbbox((0,0), line1, font=font_end)
        bbox2 = draw.textbbox((0,0), line2, font=font_end)
        draw.text(((w - (bbox1[2]-bbox1[0]))/2, 195), line1, font=font_end, fill=(255, 255, 255))
        draw.text(((w - (bbox2[2]-bbox2[0]))/2, 270), line2, font=font_end, fill=(255, 255, 255))
        
        # Clean carton badge
        draw.rounded_rectangle([605, 445, 815, 565], radius=14, fill=(255, 255, 255))
        draw.text((622, 458), 'NUTRI', font=font_carton, fill=(8, 28, 48))
        draw.text((622, 508), 'FRESH', font=font_carton, fill=(255, 87, 0))
        
        inpainted = cv2.cvtColor(np.array(im_pil), cv2.COLOR_RGB2BGR)

    cv2.imwrite(dst_file, inpainted, [cv2.IMWRITE_JPEG_QUALITY, 96])

if __name__ == '__main__':
    os.makedirs('processed_frames', exist_ok=True)
    print('Starting OpenCV inpainting for all 360 frames...')
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(inpaint_frame, range(1, 361)))
    print('All frames cleanly inpainted.')
    
    cmd = [
        'ffmpeg', '-y', '-r', '24000/1001',
        '-i', 'processed_frames/frame_%04d.jpg',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-crf', '18', '-preset', 'fast',
        'assets/videos/nutrifresh-hero.mp4'
    ]
    subprocess.run(cmd, check=True)
    print('Video rebuilt with crystal-clear inpainting!')
