from tkinter import Label, Button, ttk, END, Tk, messagebox, Toplevel, Entry
from tkinter.simpledialog import askstring
from tkinter.ttk import Combobox
import sqlite3
import tkinter as tk
from pathlib import Path
import logging
from datetime import datetime 

logging.basicConfig(filename='logs.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s: %(message)s')
current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def log(message):
    logging.info(f'{current_time} - {message}')

logging.info('Logs de stock management')
logging.info('------------------------')
log("Stock management aberto")

ROOT_DIR = Path(__file__).parent
DB_NAME = "stockManagement.sqlite3"
DB_FILE = ROOT_DIR / DB_NAME
TABLE_NAME = "stock"

con = sqlite3.connect(DB_FILE)
cursor = con.cursor()

cursor.execute(
    f'CREATE TABLE IF NOT EXISTS {TABLE_NAME}'
    '('
        'codigoProduto INTEGER PRIMARY KEY AUTOINCREMENT,'
        'nome TEXT,'
        'precoBase REAL,'
        'iva INT,'
        'stock INT,'
        'valorStock REAL'
    ')'
)
con.commit()

def new_user_window():
    window = novo_produto_form()
    center(window)
    window.mainloop()

def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height()
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    win.deiconify()

window = Tk()
window.geometry('725x400')
window.title("Gestão produtos")
center(window)

def confirm_exit():
    if messagebox.askyesno('Confirmação', 'Are you sure you want to exit the application?'):
        window.destroy()
        log('Stock management fechado')
        logging.info('-------------------------')
        logging.info('Logs de stock management')

def isPreenchido(nome_entry, precoBase_entry, iva_entry, stock_entry):
    nome = nome_entry.get()
    precoBase = precoBase_entry.get()
    iva = iva_entry.get()
    stock = stock_entry.get() 

    # Verifica se todos os campos estão preenchidos
    if nome and precoBase and iva and stock:
        # Verifica se os campos de preço base, IVA e estoque são números válidos
        try:
            precoBase = float(precoBase)
            iva = int(iva)
            stock = int(stock)
        except ValueError:
            messagebox.showwarning("Erro", "Os campos de preço base, IVA e estoque devem ser números válidos.")
            return False
        
        # Chama a função save_produto se todos os campos estiverem preenchidos e forem números válidos
        return save_produto(nome_entry, precoBase_entry, iva_entry, stock_entry, nome, precoBase, iva, stock)
    else:
        messagebox.showwarning("Erro", "Preencha todos os campos antes de tentar salvar.")
        new_user_window()
        return False
    # nome = nome_entry.get()
    # precoBase = float(precoBase_entry.get())
    # iva = int(iva_entry.get())
    # stock = int(stock_entry.get()) 
    # if nome and precoBase and iva and stock:
    #     return save_produto(nome_entry, precoBase_entry, iva_entry, stock_entry, nome, precoBase, iva, stock)
    # else:
    #     messagebox.showwarning("Erro", "Preencha todos os campos antes de tentar salvar.")

def iSelected(tree, funcao):
    selecionada = tree.selection()
    if funcao == 1:
        if selecionada:
            delete_produto(selecionada)
        else:
            messagebox.showwarning("Erro", "Selecione um produto antes de tentar eliminar.")
    elif funcao == 2:
        if selecionada:
            update_produto(selecionada)
        else:
            messagebox.showwarning("Erro", "Selecione um produto antes de tentar atualizar.")

def eliminarDadosTreeView():
    for item in trv_lista_produtos.get_children():
        trv_lista_produtos.delete(item)

def combobox(event):
    if filtros_combobox.get() == "Ordenar por código":
        eliminarDadosTreeView()
        cursor.execute(f"SELECT codigoProduto, nome, precoBase, iva, stock, valorStock FROM {TABLE_NAME}")
        produtos = cursor.fetchall()
        for codigoProduto, nome, precoBase, iva, stock, valorStock in produtos:
            if stock < 5:
                trv_lista_produtos.insert("", END, values=(codigoProduto, nome, precoBase, iva, stock, valorStock), tags=("stockLow",))
            else:
                trv_lista_produtos.insert("", END, values=(codigoProduto, nome, precoBase, iva, stock, valorStock), tags=("stockNormal",))
        trv_lista_produtos.tag_configure('stockLow', background='red')   

        log("Ordem da tabela alterada para codigo dos produtos.")

    elif filtros_combobox.get() == "Ordenar por um iva":
        iva = askstring('IVA', 'Por que iva deseja ordenar?')
        eliminarDadosTreeView()
        cursor.execute(f"SELECT codigoProduto, nome, precoBase, iva, stock, valorStock FROM {TABLE_NAME} WHERE iva = {iva}")
        produtos = cursor.fetchall()
        for codigoProduto, nome, precoBase, iva, stock, valorStock in produtos:
            if stock < 5:
                trv_lista_produtos.insert("", END, values=(codigoProduto, nome, precoBase, iva, stock, valorStock), tags=("stockLow",))
            else:
                trv_lista_produtos.insert("", END, values=(codigoProduto, nome, precoBase, iva, stock, valorStock), tags=("stockNormal",))
        trv_lista_produtos.tag_configure('stockLow', background='red')

        log("Ordem da tabela alterada para " + str(iva) + " de iva")

# Criação dos controles
title_label = Label(window, text="Gestão de produtos", font=("Consolas", 15))
title_label.grid(row=0, column=0, columnspan=3, padx=10, pady=0, sticky="W")

subtitle_label = Label(window, text="* Produtos a vermelho estão com baixo stock", font=("Consolas", 11))
subtitle_label.grid(row=1, column=0, columnspan=3, padx=7, pady=0, sticky="W")

filtros_combobox = Combobox(window, text="Lista de Produtos", font=("Consolas", 10))
filtros_combobox.grid(row=0, column=4, padx=10, pady=10, sticky="E")
filtros_combobox['state'] = 'readonly'
filtros_combobox['values'] = ('Ordenar por código', 'Ordenar por um iva')
filtros_combobox.set('Ordenar por')
filtros_combobox.bind('<<ComboboxSelected>>', combobox)

# Criar a Treeview
trv_lista_produtos = ttk.Treeview(window, columns=("codigoProduto", "nome", "precoBase", "iva", "stock", "valorStock"), show='headings')

# Nome das colunas do Treeview
trv_lista_produtos.heading("codigoProduto", text="Código")
trv_lista_produtos.heading("nome", text="Nome")
trv_lista_produtos.heading("precoBase", text="Preço Base")
trv_lista_produtos.heading("iva", text="Iva")
trv_lista_produtos.heading("stock", text="Stock")
trv_lista_produtos.heading("valorStock", text="Valor em stock")

# Tamanho de cada coluna
trv_lista_produtos.column("codigoProduto", width=75)
trv_lista_produtos.column("nome", width=150)
trv_lista_produtos.column("precoBase", width=75)
trv_lista_produtos.column("iva", width=75)
trv_lista_produtos.column("stock", width=75)
trv_lista_produtos.column("valorStock", width=75)

# Inserção dos dados dos produtos no Treeview
cursor = con.cursor()
cursor.execute(f"SELECT codigoProduto, nome, precoBase, iva, stock, valorStock FROM {TABLE_NAME}")
produtos = cursor.fetchall()
for codigoProduto, nome, precoBase, iva, stock, valorStock in produtos:
        if stock < 5:
            trv_lista_produtos.insert("", END, values=(codigoProduto, nome, precoBase, iva, stock, valorStock), tags=("stockLow",))
        else:
            trv_lista_produtos.insert("", END, values=(codigoProduto, nome, precoBase, iva, stock, valorStock), tags=("stockNormal",))
        
trv_lista_produtos.tag_configure('stockLow', background='red')
                       
trv_lista_produtos.grid(row=2, column=0, columnspan=5, padx=10, pady=10, sticky="NSEW")

# Adicionar botões
btn_save_produto = Button(window, text="Inserir novo produto", font=("Consolas", 11), command=new_user_window)
btn_delete_produto = Button(window, text="Eliminar produto", font=("Consolas", 11), command=lambda: iSelected(trv_lista_produtos,1))
btn_update_produto = Button(window, text="Atualizar produto", font=("Consolas", 11), command=lambda: iSelected(trv_lista_produtos,2))
btn_exit = Button(window, text="Fechar Aplicação", font=("Consolas", 11), command=confirm_exit)

btn_save_produto.grid(row=3, column=1, padx=10, pady=10, sticky="W")
btn_delete_produto.grid(row=3, column=2, padx=10, pady=10, sticky="W")
btn_update_produto.grid(row=3, column=3, padx=10, pady=10, sticky="E")
btn_exit.grid(row=3, column=4, padx=10, pady=10, sticky="E")

window.grid_columnconfigure(0, weight=1)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)
window.grid_columnconfigure(3, weight=1)
window.grid_rowconfigure(1, weight=1)

class Produto:
    def __init__(self, nome, precoBase, iva, stock):
        self.nome = nome
        self.precoBase = precoBase
        self.iva = iva
        self.stock = stock

def clear_boxes(box1, *boxes):
    box1.delete(0,'end')
    for box in boxes:
        box.delete(0,'end')
    box1.focus_set()

def default_boxes(nome, precobase, iva, stock):
    clear_boxes(nome, precobase, iva, stock)
    nome.insert(0, "")
    precobase.insert(0, 0)
    iva.insert(0, 0)
    stock.insert(0, 0)

def save_produto(nome_entry, precoBase_entry, iva_entry, stock_entry, nome, precoBase, iva, stock):
    valorStock = precoBase * iva
    cursor.execute(f'INSERT INTO {TABLE_NAME} (nome, precoBase, iva, stock, valorStock) VALUES (?,?,?,?,?)', (nome, precoBase, iva, stock, valorStock))
    con.commit()
    last_id = cursor.lastrowid
    if stock < 5:
            trv_lista_produtos.insert("", END, values=(last_id, nome, precoBase, iva, stock, valorStock), tags=("stockLow",))
    else:
            trv_lista_produtos.insert("", END, values=(last_id, nome, precoBase, iva, stock, valorStock), tags=("stockNormal",))
    trv_lista_produtos.tag_configure('stockLow', background='red')
    
    log("Adicionado novo produto:")
    log("Nome: "+ nome)
    log("Preço Base: "+ str(precoBase))
    log("Iva: "+ str(iva))
    log("Stock: "+ str(stock))
    log("Valor Stock: "+ str(valorStock))

    clear_boxes(nome_entry, precoBase_entry, iva_entry, stock_entry)

def delete_produto(index):
    item_values = trv_lista_produtos.item(index, "values")
    db_id = item_values[0]
    sql = f'DELETE FROM {TABLE_NAME} WHERE codigoProduto = {db_id}'
    trv_lista_produtos.delete(index)
    cursor.execute(sql)
    con.commit()
    log("Produto com o id " + db_id + " deletado")

def update_produto(index):
    item_values = trv_lista_produtos.item(index, "values")
    db_id = item_values[0]
    window = atualizar_produto_form(db_id, index)
    center(window)
    window.mainloop()

def auxiliar_update_produto(db_id, index, nome_entry, precoBase_entry, iva_entry, stock_entry):
    nome = nome_entry.get()
    precoBase = float(precoBase_entry.get())
    iva = int(iva_entry.get())
    stock = int(stock_entry.get())
    valorStock = precoBase * iva

    log("Alterado o seguinte produto:")
    log("Nome: "+ nome)
    log("Preço Base: "+ str(precoBase))
    log("Iva: "+ str(iva))
    log("Stock: "+ str(stock))
    log("Valor Stock: "+ str(valorStock))

    cursor.execute(f'UPDATE {TABLE_NAME} SET nome = ?, precoBase = ?, iva = ?, stock = ?, valorStock = ? WHERE codigoProduto = ?', (nome, precoBase, iva, stock, valorStock, db_id))
    con.commit()
    if stock < 5:
            trv_lista_produtos.item(index, values=(db_id, nome, precoBase, iva, stock, valorStock), tags=("stockLow",))
    else:
            trv_lista_produtos.item(index, values=(db_id, nome, precoBase, iva, stock, valorStock), tags=("stockNormal",))
    trv_lista_produtos.tag_configure('stockLow', background='red')

    log("Para:")
    log("Nome: "+ nome)
    log("Preço Base: "+ str(precoBase))
    log("Iva: "+ str(iva))
    log("Stock: "+ str(stock))
    log("Valor Stock: "+ str(valorStock))

class novo_produto_form(Toplevel):
    def __init__(self):
        super().__init__()
        self.geometry('400x300')
        self.title('Novo produto')
        
        # Create controls
        my_nome_label = Label(self, text="Nome", justify="left")
        my_nome_text = Entry(self, width=62)
        my_preco_base_label = Label(self, text="Preço base")
        my_preco_base_text = Entry(self, width=62)
        my_iva_label = Label(self, text="Iva")
        my_iva_text = Entry(self, width=62)
        my_stock_label = Label(self, text="Stock")
        my_stock_text = Entry(self, width=62)
        btn_insert = Button(self, text="Inserir novo produto", width=21, padx= 10, pady=5, command=lambda: isPreenchido(my_nome_text, my_preco_base_text, my_iva_text, my_stock_text))
        btn_cancel = Button(self, text="Limpar campos", width=21, padx= 10, pady=5, command=lambda: clear_boxes(my_nome_text, my_preco_base_text, my_iva_text, my_stock_text))
        
        # Insert controls into the form
        my_nome_label.grid(row=0, column=0, padx=(10,0), sticky="W")
        my_nome_text.grid(row=1, column=0, columnspan=2, padx=(10,0), pady=(0,10))

        my_preco_base_label.grid(row=3, column=0, padx=(10,0), sticky="W")
        my_preco_base_text.grid(row=4, column=0, columnspan=2, padx=(10,0), pady=(0,10))

        my_iva_label.grid(row=6, column=0, padx=(10,0), sticky="W")
        my_iva_text.grid(row=7, column=0, columnspan=2, padx=(10,0), pady=(0,10))

        my_stock_label.grid(row=8, column=0, padx=(10,0), sticky="W")
        my_stock_text.grid(row=9, column=0, columnspan=2, padx=(10,0), pady=(0,10))

        btn_insert.grid(row=11, column=0, padx=(10,0))
        btn_cancel.grid(row=11, column=1, padx=(10,0))

class atualizar_produto_form(Toplevel):
    def __init__(self, db_id, index):
        super().__init__()
        self.geometry('400x300')
        self.title('Atualizar produto')
        
        # Create controls
        my_nome_label = Label(self, text="Nome", justify="left")
        cursor.execute(f"SELECT nome FROM {TABLE_NAME} WHERE codigoProduto = {db_id}")
        my_nome_text = Entry(self, width=62)
        my_nome_text.insert(0, cursor.fetchone()[0])
        my_preco_base_label = Label(self, text="Preço base")
        cursor.execute(f"SELECT precoBase FROM {TABLE_NAME} WHERE codigoProduto = {db_id}")
        my_preco_base_text = Entry(self, width=62)
        my_preco_base_text.insert(0, cursor.fetchone()[0])
        my_iva_label = Label(self, text="Iva")
        cursor.execute(f"SELECT iva FROM {TABLE_NAME} WHERE codigoProduto = {db_id}")
        my_iva_text = Entry(self, width=62)
        my_iva_text.insert(0, cursor.fetchone()[0])
        my_stock_label = Label(self, text="Stock")
        cursor.execute(f"SELECT stock FROM {TABLE_NAME} WHERE codigoProduto = {db_id}")
        my_stock_text = Entry(self, width=62)
        my_stock_text.insert(0, cursor.fetchone()[0])
        btn_insert = Button(self, text="Atualizar produto", width=21, padx= 10, pady=5, command=lambda: auxiliar_update_produto(db_id, index, my_nome_text, my_preco_base_text, my_iva_text, my_stock_text))
        btn_cancel = Button(self, text="Limpar campos", width=21, padx= 10, pady=5, command=lambda: default_boxes(my_nome_text, my_preco_base_text, my_iva_text, my_stock_text))
        
        # Insert controls into the form
        my_nome_label.grid(row=0, column=0, padx=(10,0), sticky="W")
        my_nome_text.grid(row=1, column=0, columnspan=2, padx=(10,0), pady=(0,10))

        my_preco_base_label.grid(row=3, column=0, padx=(10,0), sticky="W")
        my_preco_base_text.grid(row=4, column=0, columnspan=2, padx=(10,0), pady=(0,10))

        my_iva_label.grid(row=6, column=0, padx=(10,0), sticky="W")
        my_iva_text.grid(row=7, column=0, columnspan=2, padx=(10,0), pady=(0,10))

        my_stock_label.grid(row=8, column=0, padx=(10,0), sticky="W")
        my_stock_text.grid(row=9, column=0, columnspan=2, padx=(10,0), pady=(0,10))

        btn_insert.grid(row=11, column=0, padx=(10,0))
        btn_cancel.grid(row=11, column=1, padx=(10,0))

window.mainloop()