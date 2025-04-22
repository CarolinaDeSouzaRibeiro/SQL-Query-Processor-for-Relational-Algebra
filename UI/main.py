import gradio as gr
from plantando_arvores.processamento_consultas import processar_consulta


def test(comando):
    #ALGEBRA RELACIONAL
    algebra_relacional = comando #TODO: chamar funcao de algebra relacional
    algebra_relacional_otimizado = algebra_relacional #TODO: chamar funcao de otimizar comando

    #GRAFOS
    grafo_otimizado = processar_consulta(algebra_relacional_otimizado)
    grafo = processar_consulta(algebra_relacional_otimizado)

    #ORDEM DE EXECUCAO
    ordem_execucao = '<div id="ordem"><ol><li>aaa</li><li>bbb</li></ol></div>'

    return algebra_relacional, algebra_relacional_otimizado, grafo_otimizado, grafo, ordem_execucao

with gr.Blocks() as demo:
    gr.Markdown("## Processador de consultas")
    with gr.Row():
        with gr.Column():
            cmd_sql = gr.Textbox(label="Comando SQL")
            btn = gr.Button("Submit")
        with gr.Column():
            gr.Markdown("## Algebra Relacional")
            algeb_relac_otim = gr.Textbox(label="Algebra Relacional (Otimizado)")
            algeb_relac = gr.Textbox(label="Algebra Relacional (Não otimizado)")

            gr.Markdown("## Grafos")
            grafo_otim = gr.Plot()
            grafo = gr.Plot()

            gr.Markdown("## Ordem de execução")
            ordem_exec = gr.HTML()

        #comando do botao
        btn.click(test, inputs=[cmd_sql], outputs=[algeb_relac_otim, algeb_relac, grafo_otim, grafo, ordem_exec])

demo.launch()