import gradio as gr
import numpy as np
# import pandas as pd 
# import os
# from matplotlib import pyplot as plt
import torch
# import cv2
from PIL import Image
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
sam_checkpoint = "D:\\segment-anything-main\\checkpoint\\sam_vit_b_01ec64.pth"
model_type = "vit_b"
device = 'cuda' if torch.cuda.is_available() else 'cpu'
sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
sam.to(device=device)
#mask_generator = SamAutomaticMaskGenerator(sam, points_per_batch=16)
predictor = SamPredictor(sam)

def segment_image(image, segmentation_mask):
    image_array = np.array(image)
    segmented_image_array = np.zeros_like(image_array)
    segmented_image_array[segmentation_mask] = image_array[segmentation_mask]
    segmented_image = Image.fromarray(segmented_image_array)
    black_image = Image.new("RGBA", image.size, (0, 0, 0,0))
    transparency_mask = np.zeros_like(segmentation_mask, dtype=np.uint8)
    transparency_mask[segmentation_mask] = 255
    transparency_mask_image = Image.fromarray(transparency_mask, mode='L')
    black_image.paste(segmented_image, mask=transparency_mask_image)
    return black_image

with gr.Blocks() as demo:
    with gr.Row():
        input_img = gr.Image(label="Input", type="numpy").style(height=480, width=480)
        output_img = gr.Image(label="Selected Segment", type="numpy").style(height=480, width=480)

    def on_image_change(img):
        return img

    def get_select_coords(img, evt: gr.SelectData):
        h, w = img.shape[:2]
        input_point = np.array([evt.index])
        input_label = np.array([1])
        #mask = mask_generator.generate(img)
        predictor.set_image(img)
        masks, scores, logits = predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True, # 在prompt不明确时建议打开multimask
        )
        #outimg = Image.new("RGBA", (w,h), (255, 255, 255, 0))
        for i, (mask, score) in enumerate(zip(masks, scores)):
            if score > 0.9:
                sub_img = segment_image(Image.fromarray(img), mask)
                sub_img.save('crop.png', "PNG")
                half = 0.5
                sub_img = sub_img.resize( [int(half * s) for s in sub_img.size] )
                return sub_img

    input_img.select(get_select_coords, [input_img], output_img)
    input_img.upload(on_image_change, [input_img], [input_img])

if __name__ == "__main__":
    try:
        demo.launch()
    except Exception:
        demo.launch(share=True)