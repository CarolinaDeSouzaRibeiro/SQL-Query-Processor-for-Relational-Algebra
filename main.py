import gradio as gr
from plantando_arvores.processamento_consultas import processar_consulta


def funcao_btn(comando):
    #ALGEBRA RELACIONAL
    algebra_relacional = comando #TODO: chamar funcao de algebra relacional

    #GRAFOS
    processar_consulta(algebra_relacional)#prepara grafos

    return algebra_relacional, 'arvore_consulta_processada.png', 'arvore_consulta_otimizada.png'

with gr.Blocks() as demo:
    gr.Markdown("## Processador de consultas")
    with gr.Row():
        with gr.Column():
            cmd_sql = gr.Textbox(label="Comando SQL")
            btn = gr.Button("Submit")
        with gr.Column():
            gr.Markdown("## Algebra Relacional")
            algeb_relac = gr.Textbox(label="Algebra Relacional")
            algeb_relac.interactive = False # desabilita edição do campo de algebra relacional

            gr.Markdown("## Grafos")
            gr.Markdown("#### Não-Otimizado")
            grafo = gr.Image(label="Grafo Não-Otimizado")
            gr.Markdown("#### Otimizado")
            grafo_otim = gr.Image(label="Grafo Otimizado")

        #comando do botao
        btn.click(funcao_btn, inputs=[cmd_sql], outputs=[algeb_relac, grafo, grafo_otim])

demo.launch()