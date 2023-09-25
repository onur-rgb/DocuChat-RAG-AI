import gradio as gr
from utils import MyApp
from os import environ

# Set up YOUR_API_KEY
environ["OPENAI_API_KEY"] = "YOUR_API_KEY"

def add_text(history, text: str):
    if not text:
        raise gr.Error('Enter text')
    history = history + [(text, '')]
    return history

def get_response(history, query, files):
    if not files:
        raise gr.Error(message='Upload a file')
    
    chain = app(files)
    result = chain({"question": query, 'chat_history': app.chat_history}, return_only_outputs=True)
    app.chat_history += [(query, result["answer"])]

    for char in result['answer']:
        history[-1][-1] += char
        yield history, ''

app = MyApp()
title = 'DocuChat AI'
description = """Introducing "DocuChat AI," a versatile tool for engaging in intelligent conversations with a wide range of document formats, including PDFs, text files, docx documents, and classic doc files."""

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(f'<center><h1>{title}</h1></center>')
    gr.Markdown(f'<center>{description}</center>')
    
    with gr.Row():
        with gr.Group():
            file = gr.File(
                label='📂 You can upload multiple files separately, with the following allowed extensions: .pdf, .docx, .doc, .txt.',
                file_types=['.pdf', '.docx', '.doc', '.txt'], file_count="multiple")
            question = gr.Textbox(label='Enter your question here', placeholder="Enter text and press enter or submit").style(height=200)
            
        with gr.Group():
            chatbot = gr.Chatbot(value=[], elem_id='chatbot').style(height=600)

    with gr.Row():
        btn = gr.Button('Submit')
        clear = gr.Button("Clear Chat")
        delete_files_button = gr.Button("Delete Files")

    btn.click(
        fn=add_text,
        inputs=[chatbot, question],
        outputs=[chatbot, ],
        queue=False).success(
        fn=get_response,
        inputs=[chatbot, question, file],
        outputs=[chatbot, question])
    
    question.submit(
        fn=add_text,
        inputs=[chatbot, question],
        outputs=[chatbot, ],
        queue=False).success(
        fn=get_response,
        inputs=[chatbot, question, file],
        outputs=[chatbot, question])
    
    clear.click(lambda: None, None, chatbot, queue=False)
    delete_files_button.click(lambda: None, None, file, queue=False)
    
demo.queue()

if __name__ == "__main__":
    demo.launch()
