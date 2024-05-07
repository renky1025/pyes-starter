### pip install gradio wordcloud
import gradio as gr
import wordcloud
import numpy as np
from pathlib import Path


def process(text, filepath, mask_img):
    """
    生成词云并保存为图片
    
    Args:
        text (str): 文本内容
        filepath (str): 文件路径
        mask_img (PIL.Image.Image): 掩膜图像
    
    Returns:
        str: 保存词云图片的文件名
    
    """
    # 读取mask图像
    mask = np.array(mask_img)

    # 创建词云
    wc = wordcloud.WordCloud(background_color="white", max_words=2000, mask=mask)
    if len(text) == 0:
        # 打开文件
        print(filepath)
        
        with open(filepath.name, 'r') as file:
            # 逐行读取并打印
            for line in file:
                # print(line, end='')  # 默认情况下，print会在每行末尾添加换行符，这里使用end=''来避免这个行为
                text += line
    wc.generate(text)


    # 返回图像
    wc.to_file("output_image.png")
    return "output_image.png"


# 创建Gradio界面
with gr.Blocks(css="footer {visibility: hidden}") as demo:
    with gr.Row():
        gr.HTML(value="""<h1 align="center">词云服务</h1>""")
    with gr.Row():
        with gr.Column():
            text = gr.Textbox(label="文本框输入【优先】")
            file = gr.File(label="文本输入")
            mask = gr.Image(label="上传Mask图像")
        with gr.Column():
            output_image = gr.Image(label="词云输出")
    with gr.Row():
        send_btn = gr.Button("❤️❤️❤️Submit❤️❤️❤️")
        clear_btn = gr.Button("😍😍😍Clear😍😍😍")
        send_btn.click(process, inputs=[text, file, mask], outputs=[output_image])
        clear_btn.click(lambda _: (None, None, None, None), inputs=clear_btn, outputs=[text, file, mask, output_image])
    with gr.Row():
        examples = [
            [
                "",
                "D:\\pyes-starter\\wordcloud\\alice_license.txt",
                "D:\\pyes-starter\\wordcloud\\alice_mask.png"  # 替换为你的mask图像路径
            ]
        ]
        gr_examples = gr.Examples(examples=examples,
                                  label="输入示例 (点击选择例子)",
                                  inputs=[text, file, mask],
                                  examples_per_page=20)

demo.launch()