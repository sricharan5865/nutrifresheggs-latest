import os
import subprocess
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from concurrent.futures import ThreadPoolExecutor

font_main_path = r'C:\Windows\Fonts\arialbd.ttf'

def create_feathered_patch(im, box, blur_rad=24):
    x1, y1, x2, y2 = box
    w, h = x2 - x1, y2 - y1
    patch = im.crop(box).filter(ImageFilter.GaussianBlur(blur_rad))
    
    mask = Image.new('L', (w, h), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.rounded_rectangle([4, 4, w - 4, h - 4], radius=min(w, h)//3, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(14))
    
    im.paste(patch, (x1, y1), mask)
    return im

def process_single_frame(i):
    src_file = f'video_frames/frame_{i:04d}.png'
    dst_file = f'processed_frames/frame_{i:04d}.jpg'
    
    if not os.path.exists(src_file):
        return
        
    font_main = ImageFont.truetype(font_main_path, 72)
    font_carton = ImageFont.truetype(font_main_path, 40)
    font_end = ImageFont.truetype(font_main_path, 58)
    
    im = Image.open(src_file).convert('RGBA')
    W, H = im.size
    
    # Scene 1: Frames 1 - 48 ('happy' -> 'nutrifresh')
    if 1 <= i <= 48:
        im = create_feathered_patch(im, (710, 465, 1210, 575), blur_rad=24)
        draw = ImageDraw.Draw(im)
        text = 'nutrifresh'
        bbox = draw.textbbox((0, 0), text, font=font_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((W - tw)/2, 515 - th/2), text, font=font_main, fill=(255, 255, 255, 255))
        
    # Scene 2: Frames 49 - 95 ('happy flip.' -> 'nutrifresh flip.')
    elif 49 <= i <= 95:
        im = create_feathered_patch(im, (640, 445, 1280, 575), blur_rad=24)
        draw = ImageDraw.Draw(im)
        text = 'nutrifresh flip.'
        bbox = draw.textbbox((0, 0), text, font=font_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((W - tw)/2, 500 - th/2), text, font=font_main, fill=(255, 255, 255, 255))

    # Scene 3: Frames 96 - 150 ('happy whip.' -> 'nutrifresh whip.')
    elif 96 <= i <= 150:
        im = create_feathered_patch(im, (640, 445, 1280, 575), blur_rad=24)
        draw = ImageDraw.Draw(im)
        text = 'nutrifresh whip.'
        bbox = draw.textbbox((0, 0), text, font=font_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((W - tw)/2, 505 - th/2), text, font=font_main, fill=(255, 255, 255, 255))

    # Scene 4: Frames 151 - 234 ('happy brunch.' -> 'nutrifresh brunch.')
    elif 151 <= i <= 234:
        im = create_feathered_patch(im, (630, 435, 1290, 575), blur_rad=24)
        draw = ImageDraw.Draw(im)
        text = 'nutrifresh brunch.'
        bbox = draw.textbbox((0, 0), text, font=font_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((W - tw)/2, 495 - th/2), text, font=font_main, fill=(255, 255, 255, 255))

    # Scene 5: Frames 235 - 284 ('happy hen.' -> 'nutrifresh hen.')
    elif 235 <= i <= 284:
        im = create_feathered_patch(im, (640, 430, 1280, 570), blur_rad=24)
        draw = ImageDraw.Draw(im)
        text = 'nutrifresh hen.'
        bbox = draw.textbbox((0, 0), text, font=font_main)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        draw.text(((W - tw)/2, 495 - th/2), text, font=font_main, fill=(255, 255, 255, 255))

    # Scene 6: Frames 285 - 360 (Closing shot with carton and final copy)
    elif 285 <= i <= 360:
        im = create_feathered_patch(im, (500, 170, 1420, 365), blur_rad=24)
        im = create_feathered_patch(im, (570, 400, 840, 610), blur_rad=20)
        
        draw = ImageDraw.Draw(im)
        
        line1 = 'nutrifresh hens outside.'
        line2 = 'tasty yolks inside.'
        bbox1 = draw.textbbox((0,0), line1, font=font_end)
        bbox2 = draw.textbbox((0,0), line2, font=font_end)
        draw.text(((W - (bbox1[2]-bbox1[0]))/2, 200), line1, font=font_end, fill=(255, 255, 255, 255))
        draw.text(((W - (bbox2[2]-bbox2[0]))/2, 275), line2, font=font_end, fill=(255, 255, 255, 255))
        
        draw.rounded_rectangle([605, 445, 815, 565], radius=14, fill=(255, 255, 255, 250))
        draw.text((622, 458), 'NUTRI', font=font_carton, fill=(8, 28, 48, 255))
        draw.text((622, 508), 'FRESH', font=font_carton, fill=(255, 87, 0, 255))

    im.convert('RGB').save(dst_file, quality=95)

if __name__ == '__main__':
    os.makedirs('processed_frames', exist_ok=True)
    with ThreadPoolExecutor(max_workers=8) as executor:
        list(executor.map(process_single_frame, range(1, 361)))
    
    cmd = [
        'ffmpeg', '-y', '-r', '24000/1001',
        '-i', 'processed_frames/frame_%04d.jpg',
        '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        '-crf', '18', '-preset', 'fast',
        'assets/videos/nutrifresh-hero.mp4'
    ]
    subprocess.run(cmd, check=True)
    print('Clean re-encoding completed without any text artifacts!')
