import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from decimal import Decimal

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "toor",
    "database": "jogos"
}

def conectar_banco():
    """Conecta ao banco de dados MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao conectar ao MySQL: {e}")
        return None

def listar_produtos_db():
    conn = conectar_banco()
    produtos = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            query = """
            SELECT p.pro_id, p.pro_nome, p.prod_desc, p.prod_preco, p.qntd_estoque,
                   c.nome_cat AS categoria, f.forn_nome AS fornecedor
            FROM tb_produtos p
            JOIN tb_categoria c ON p.cat_id = c.cat_id
            JOIN tb_fornecedor f ON p.forn_id = f.forn_id
            ORDER BY p.pro_nome
            """
            cursor.execute(query)
            produtos = cursor.fetchall()
        except Error as e:
            messagebox.showerror("Erro de Banco de Dados", f"Erro ao listar produtos: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return produtos

def adicionar_produto_db(nome, descricao, preco, estoque, categoria_id, fornecedor_id):
    """Adiciona um novo produto ao banco de dados."""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            INSERT INTO tb_produtos
            (pro_nome, prod_desc, prod_preco, qntd_estoque, cat_id, forn_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nome, descricao, preco, estoque, categoria_id, fornecedor_id))
            conn.commit()
            return True
        except Error as e:
            messagebox.showerror("Erro ao Adicionar Produto", f"Erro: {e}")
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return False

def atualizar_produto_db(produto_id, nome, descricao, preco, estoque):
    """Atualiza os dados de um produto existente."""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            query = """
            UPDATE tb_produtos
            SET pro_nome = %s, prod_desc = %s, prod_preco = %s, qntd_estoque = %s
            WHERE pro_id = %s
            """
            cursor.execute(query, (nome, descricao, preco, estoque, produto_id))
            conn.commit()
            return True
        except Error as e:
            messagebox.showerror("Erro ao Atualizar Produto", f"Erro: {e}")
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return False

def remover_produto_db(produto_id):
    """Remove um produto do banco de dados."""
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            # Verificar se o produto existe
            cursor.execute("SELECT pro_id FROM tb_produtos WHERE pro_id = %s", (produto_id,))
            if not cursor.fetchone():
                messagebox.showwarning("Produto Não Encontrado", "Produto com o ID especificado não encontrado.")
                return False

            cursor.execute("DELETE FROM tb_produtos WHERE pro_id = %s", (produto_id,))
            conn.commit()
            # Opcional: verificar cursor.rowcount para ter certeza que algo foi deletado.
            # if cursor.rowcount == 0:
            #     messagebox.showwarning("Aviso", "Nenhum produto foi removido (ID pode não existir mais).")
            #     return False
            return True
        except Error as e:
            messagebox.showerror("Erro ao Remover Produto", f"Erro: {e}")
            return False
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return False

def obter_categorias_fornecedores_db():
    """Retorna listas de categorias e fornecedores."""
    conn = conectar_banco()
    categorias = []
    fornecedores = []
    if conn:
        try:
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT cat_id, nome_cat FROM tb_categoria ORDER BY nome_cat")
            categorias = cursor.fetchall()
            cursor.execute("SELECT forn_id, forn_nome FROM tb_fornecedor ORDER BY forn_nome")
            fornecedores = cursor.fetchall()
        except Error as e:
            messagebox.showerror("Erro ao Carregar Dados", f"Erro ao carregar categorias/fornecedores: {e}")
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if conn:
                conn.close()
    return categorias, fornecedores

# --- CLASSE PRINCIPAL DA APLICAÇÃO ---

class LojaJogosApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gerenciamento de Loja de Jogos")
        self.root.geometry("1000x700") # Aumentei o tamanho da janela
        self.root.minsize(800, 500)

        # --- Frames para organização ---
        self.frame_botoes = ttk.Frame(root, padding="15")
        self.frame_botoes.pack(pady=10)

        self.frame_produtos = ttk.Frame(root, padding="15")
        self.frame_produtos.pack(expand=True, fill="both")

        # --- Botões de Ação ---
        self.btn_listar = ttk.Button(self.frame_botoes, text="Listar Produtos", command=self.exibir_produtos)
        self.btn_listar.grid(row=0, column=0, padx=10, pady=5)

        self.btn_adicionar = ttk.Button(self.frame_botoes, text="Adicionar Produto", command=self.abrir_tela_adicionar)
        self.btn_adicionar.grid(row=0, column=1, padx=10, pady=5)

        self.btn_atualizar = ttk.Button(self.frame_botoes, text="Atualizar Produto", command=self.abrir_tela_atualizar)
        self.btn_atualizar.grid(row=0, column=2, padx=10, pady=5)

        self.btn_remover = ttk.Button(self.frame_botoes, text="Remover Produto", command=self.remover_produto)
        self.btn_remover.grid(row=0, column=3, padx=10, pady=5)

        # --- Treeview para exibir os produtos ---
        self.tree = ttk.Treeview(self.frame_produtos, columns=("ID", "Nome", "Preço", "Estoque", "Categoria", "Fornecedor", "Descrição"), show="headings")

        # Configurar cabeçalhos das colunas
        self.tree.heading("ID", text="ID", anchor="center")
        self.tree.heading("Nome", text="Nome")
        self.tree.heading("Preço", text="Preço", anchor="e")
        self.tree.heading("Estoque", text="Estoque", anchor="center")
        self.tree.heading("Categoria", text="Categoria")
        self.tree.heading("Fornecedor", text="Fornecedor")
        self.tree.heading("Descrição", text="Descrição")

        # Configurar larguras das colunas
        self.tree.column("ID", width=50, stretch=tk.NO, anchor="center")
        self.tree.column("Nome", width=200)
        self.tree.column("Preço", width=90, anchor="e")
        self.tree.column("Estoque", width=80, anchor="center")
        self.tree.column("Categoria", width=120)
        self.tree.column("Fornecedor", width=120)
        self.tree.column("Descrição", width=250)

        self.tree.pack(expand=True, fill="both", side="left") # Adicionado side="left"

        # --- Scrollbar para o Treeview ---
        vsb = ttk.Scrollbar(self.frame_produtos, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)

        hsb = ttk.Scrollbar(self.frame_produtos, orient="horizontal", command=self.tree.xview) # Deveria estar fora do frame_produtos ou o treeview não deveria preencher 'both' antes
        hsb.pack(side='bottom', fill='x')
        self.tree.configure(xscrollcommand=hsb.set)
        
        # Ajuste para scrollbars: Colocar Treeview e Scrollbars em um frame próprio ou ajustar o pack
        # Para simplificar, vou ajustar o pack do treeview para não cobrir onde as scrollbars seriam colocadas
        # self.tree.pack(expand=True, fill="both") # Original
        # A scrollbar horizontal estava sendo coberta, vamos reordenar o pack ou usar grid.
        # Uma forma mais simples é garantir que o treeview não preencha sobre a scrollbar hsb.
        # No entanto, o usual é o treeview estar à esquerda e a vsb à direita, hsb abaixo.

        # Carrega os produtos na inicialização
        self.exibir_produtos()

    def exibir_produtos(self):
        """Atualiza a Treeview com os produtos do banco de dados."""
        # Limpa a treeview antes de adicionar novos dados
        for i in self.tree.get_children():
            self.tree.delete(i)

        produtos = listar_produtos_db()
        if produtos:
            for prod in produtos:
                preco_formatado = f"R${prod['prod_preco']:.2f}" if prod['prod_preco'] is not None else "N/A"
                self.tree.insert("", "end", values=(
                    prod['pro_id'],
                    prod['pro_nome'],
                    preco_formatado,
                    prod['qntd_estoque'],
                    prod['categoria'],
                    prod['fornecedor'],
                    prod['prod_desc']
                ), iid=prod['pro_id'])
        else:
            # Não exibir messagebox aqui, pois pode ser chamado em atualizações silenciosas.
            # Se desejar feedback, pode ser um label na UI.
            pass # messagebox.showinfo("Informação", "Nenhum produto encontrado no banco de dados.")


    def abrir_tela_adicionar(self):
        """Abre uma nova janela para adicionar um produto."""
        AddProdutoWindow(self.root, self.exibir_produtos)

    def abrir_tela_atualizar(self):
        """Abre uma nova janela para atualizar um produto."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Por favor, selecione um produto para atualizar.")
            return

        produto_id = int(selected_item)
        UpdateProdutoWindow(self.root, self.exibir_produtos, produto_id)


    def remover_produto(self):
        """Remove o produto selecionado na Treeview."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Aviso", "Por favor, selecione um produto para remover.")
            return

        produto_id = int(selected_item)
        resposta = messagebox.askyesno("Confirmar Remoção", f"Tem certeza que deseja remover o produto ID {produto_id}?")

        if resposta:
            if remover_produto_db(produto_id):
                messagebox.showinfo("Sucesso", "Produto removido com sucesso!")
                self.exibir_produtos()
            # Erro já é tratado na função remover_produto_db


# --- CLASSE PARA JANELA DE ADICIONAR PRODUTO ---

class AddProdutoWindow(tk.Toplevel):
    def __init__(self, master, refresh_callback):
        super().__init__(master)
        self.title("Adicionar Novo Produto")
        self.geometry("400x450")
        self.transient(master)
        self.grab_set()
        self.refresh_callback = refresh_callback

        self.categorias, self.fornecedores = obter_categorias_fornecedores_db()

        if not self.categorias:
            messagebox.showwarning("Aviso", "Nenhuma categoria cadastrada. Cadastre uma categoria primeiro.")
            self.destroy()
            return
        if not self.fornecedores:
            messagebox.showwarning("Aviso", "Nenhum fornecedor cadastrado. Cadastre um fornecedor primeiro.")
            self.destroy()
            return

        self._create_widgets()

    def _create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        ttk.Label(form_frame, text="Nome do Jogo:").grid(row=0, column=0, sticky="w", pady=5)
        self.nome_entry = ttk.Entry(form_frame, width=40)
        self.nome_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(0,10)) # Adicionado padx

        ttk.Label(form_frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
        self.desc_entry = ttk.Entry(form_frame, width=40)
        self.desc_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(0,10))

        ttk.Label(form_frame, text="Preço (R$):").grid(row=2, column=0, sticky="w", pady=5)
        self.preco_entry = ttk.Entry(form_frame, width=40)
        self.preco_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(0,10))

        ttk.Label(form_frame, text="Quantidade em Estoque:").grid(row=3, column=0, sticky="w", pady=5)
        self.estoque_entry = ttk.Entry(form_frame, width=40)
        self.estoque_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=(0,10))

        ttk.Label(form_frame, text="Categoria:").grid(row=4, column=0, sticky="w", pady=5)
        self.categoria_combobox = ttk.Combobox(form_frame, state="readonly", width=37)
        self.categoria_combobox['values'] = [cat['nome_cat'] for cat in self.categorias]
        self.categoria_combobox.grid(row=4, column=1, sticky="ew", pady=5, padx=(0,10))
        if self.categorias: self.categoria_combobox.current(0)


        ttk.Label(form_frame, text="Fornecedor:").grid(row=5, column=0, sticky="w", pady=5)
        self.fornecedor_combobox = ttk.Combobox(form_frame, state="readonly", width=37)
        self.fornecedor_combobox['values'] = [forn['forn_nome'] for forn in self.fornecedores]
        self.fornecedor_combobox.grid(row=5, column=1, sticky="ew", pady=5, padx=(0,10))
        if self.fornecedores: self.fornecedor_combobox.current(0)

        form_frame.columnconfigure(1, weight=1) # Faz a coluna 1 expandir

        btn_frame = ttk.Frame(form_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Adicionar", command=self._adicionar).pack(side="left", padx=10)
        ttk.Button(btn_frame, text="Cancelar", command=self.destroy).pack(side="left", padx=10)

    def _adicionar(self):
        nome = self.nome_entry.get().strip()
        descricao = self.desc_entry.get().strip()
        preco_str = self.preco_entry.get().strip().replace(',', '.')
        estoque_str = self.estoque_entry.get().strip()

        categoria_nome = self.categoria_combobox.get()
        fornecedor_nome = self.fornecedor_combobox.get()

        if not nome or not categoria_nome or not fornecedor_nome:
            messagebox.showwarning("Campos Obrigatórios", "Nome, Categoria e Fornecedor são obrigatórios.")
            return
        if not preco_str: # Garante que preco não seja vazio
            messagebox.showwarning("Campo Obrigatório", "Preço é obrigatório.")
            return
        if not estoque_str: # Garante que estoque não seja vazio
            messagebox.showwarning("Campo Obrigatório", "Estoque é obrigatório.")
            return

        try:
            preco = Decimal(preco_str)
            if preco < 0:
                messagebox.showerror("Erro de Entrada", "Preço não pode ser negativo.")
                return
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Preço deve ser um número válido.")
            return
        
        try:
            estoque = int(estoque_str)
            if estoque < 0:
                messagebox.showerror("Erro de Entrada", "Estoque não pode ser negativo.")
                return
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Estoque deve ser um número inteiro válido.")
            return

        categoria_id = next((cat['cat_id'] for cat in self.categorias if cat['nome_cat'] == categoria_nome), None)
        fornecedor_id = next((forn['forn_id'] for forn in self.fornecedores if forn['forn_nome'] == fornecedor_nome), None)

        if categoria_id is None or fornecedor_id is None:
            messagebox.showerror("Erro de Seleção", "Categoria ou Fornecedor inválidos. Isso não deveria acontecer se foram selecionados da lista.")
            return

        if adicionar_produto_db(nome, descricao, preco, estoque, categoria_id, fornecedor_id):
            messagebox.showinfo("Sucesso", "Produto adicionado com sucesso!")
            self.refresh_callback()
            self.destroy()


# --- CLASSE PARA JANELA DE ATUALIZAR PRODUTO ---

class UpdateProdutoWindow(tk.Toplevel):
    def __init__(self, master, refresh_callback, produto_id):
        super().__init__(master)
        self.title(f"Atualizar Produto ID: {produto_id}")
        self.geometry("400x350") # Ajustar conforme necessidade
        self.transient(master)
        self.grab_set()
        self.refresh_callback = refresh_callback
        self.produto_id = produto_id

        self.produto_atual = None # CORREÇÃO: Inicializar para garantir que o atributo exista
        self._load_product_data() # Carrega os dados, pode definir self.produto_atual como None

        if self.produto_atual is None: # CORREÇÃO: Verifica se o produto de fato não foi carregado
            # A mensagem de "Produto Não Encontrado" já é exibida por _load_product_data()
            self.destroy()
            return # Impede a continuação para _create_widgets()

        self._create_widgets()

    def _load_product_data(self):
        """Carrega os dados do produto pelo ID para pré-preencher o formulário."""
        conn = conectar_banco()
        if conn:
            try:
                cursor = conn.cursor(dictionary=True)
                # Modificado para buscar também nome da categoria e fornecedor, se necessário para exibição (opcional)
                # Mas para atualização, só precisamos dos dados de tb_produtos.
                cursor.execute("SELECT * FROM tb_produtos WHERE pro_id = %s", (self.produto_id,))
                self.produto_atual = cursor.fetchone()
                if not self.produto_atual:
                    messagebox.showwarning("Produto Não Encontrado", f"Produto com ID {self.produto_id} não encontrado no banco de dados.")
            except Error as e:
                messagebox.showerror("Erro ao Carregar Produto", f"Erro ao carregar dados do produto: {e}")
                self.produto_atual = None # Garante que fique None em caso de erro
            finally:
                if 'cursor' in locals() and cursor:
                    cursor.close()
                if conn:
                    conn.close()
        else:
             self.produto_atual = None # Garante que fique None se a conexão falhar

    def _create_widgets(self):
        form_frame = ttk.Frame(self, padding="20")
        form_frame.pack(fill="both", expand=True)

        ttk.Label(form_frame, text="Nome do Jogo:").grid(row=0, column=0, sticky="w", pady=5)
        self.nome_entry = ttk.Entry(form_frame, width=40)
        self.nome_entry.insert(0, self.produto_atual.get('pro_nome', ''))
        self.nome_entry.grid(row=0, column=1, sticky="ew", pady=5, padx=(0,10))

        ttk.Label(form_frame, text="Descrição:").grid(row=1, column=0, sticky="w", pady=5)
        self.desc_entry = ttk.Entry(form_frame, width=40)
        self.desc_entry.insert(0, self.produto_atual.get('prod_desc', ''))
        self.desc_entry.grid(row=1, column=1, sticky="ew", pady=5, padx=(0,10))

        ttk.Label(form_frame, text="Preço (R$):").grid(row=2, column=0, sticky="w", pady=5)
        self.preco_entry = ttk.Entry(form_frame, width=40)
        preco_val = self.produto_atual.get('prod_preco')
        self.preco_entry.insert(0, f"{preco_val:.2f}" if preco_val is not None else "")
        self.preco_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(0,10))

        ttk.Label(form_frame, text="Quantidade em Estoque:").grid(row=3, column=0, sticky="w", pady=5)
        self.estoque_entry = ttk.Entry(form_frame, width=40)
        self.estoque_en
