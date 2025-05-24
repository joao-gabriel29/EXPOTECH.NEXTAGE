import mysql.connector
from mysql.connector import Error
from decimal import Decimal

# Configurações do banco de dados
DB_CONFIG = {
    "host": "localhost",
    "user": "root",   
    "password": "sua_senha",      
    "database": "jogos"
}

def conectar_banco():
    """Conecta ao banco de dados MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None

# --- FUNÇÕES CRUD PARA PRODUTOS ---
def listar_produtos():
    """Lista todos os produtos com detalhes de categoria e fornecedor."""
    conn = conectar_banco()
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
            
            if not produtos:
                print("\nNenhum produto encontrado no banco de dados.")
                return
            
            print("\n--- LISTA DE PRODUTOS ---")
            for prod in produtos:
                print(f"\nID: {prod['pro_id']} | Nome: {prod['pro_nome']}")
                print(f"Descrição: {prod['prod_desc']}")
                print(f"Preço: R${prod['prod_preco']:.2f} | Estoque: {prod['qntd_estoque']}")
                print(f"Categoria: {prod['categoria']} | Fornecedor: {prod['fornecedor']}")
                print("-" * 50)
            
        except Error as e:
            print(f"Erro ao listar produtos: {e}")
        finally:
            cursor.close()
            conn.close()

def adicionar_produto():
    """Adiciona um novo produto ao banco de dados."""
    print("\n--- ADICIONAR PRODUTO ---")
    
    try:
        nome = input("Nome do jogo: ").strip()
        if not nome:
            print("O nome do jogo é obrigatório!")
            return
            
        descricao = input("Descrição: ").strip()
        preco = Decimal(input("Preço (R$): ").replace(',', '.'))
        estoque = int(input("Quantidade em estoque: "))
        
        conn = conectar_banco()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Listar e selecionar categoria
            cursor.execute("SELECT cat_id, nome_cat FROM tb_categoria ORDER BY nome_cat")
            categorias = cursor.fetchall()
            if not categorias:
                print("Nenhuma categoria cadastrada. Cadastre uma categoria primeiro.")
                return
                
            print("\nCategorias disponíveis:")
            for cat in categorias:
                print(f"{cat['cat_id']}: {cat['nome_cat']}")
                
            categoria_id = int(input("ID da categoria: "))
            if not any(cat['cat_id'] == categoria_id for cat in categorias):
                print("ID de categoria inválido!")
                return
            
            # Listar e selecionar fornecedor
            cursor.execute("SELECT forn_id, forn_nome FROM tb_fornecedor ORDER BY forn_nome")
            fornecedores = cursor.fetchall()
            if not fornecedores:
                print("Nenhum fornecedor cadastrado. Cadastre um fornecedor primeiro.")
                return
                
            print("\nFornecedores disponíveis:")
            for forn in fornecedores:
                print(f"{forn['forn_id']}: {forn['forn_nome']}")
                
            fornecedor_id = int(input("ID do fornecedor: "))
            if not any(forn['forn_id'] == fornecedor_id for forn in fornecedores):
                print("ID de fornecedor inválido!")
                return
            
            
            query = """
            INSERT INTO tb_produtos 
            (pro_nome, prod_desc, prod_preco, qntd_estoque, cat_id, forn_id)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nome, descricao, preco, estoque, categoria_id, fornecedor_id))
            conn.commit() 
            print("\nProduto adicionado com sucesso!")
            
    except ValueError as ve:
        print(f"Erro: Valor inválido inserido. Certifique-se de digitar números para preço, estoque e IDs. Detalhes: {ve}")
    except Error as e:
        print(f"Erro ao adicionar produto: {e}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()

def atualizar_produto():
    """Atualiza os dados de um produto existente."""
    listar_produtos()
    try:
        produto_id = int(input("\nID do produto a ser atualizado (0 para cancelar): "))
        if produto_id == 0:
            return
            
        conn = conectar_banco()
        if conn:
            cursor = conn.cursor(dictionary=True)
            
            # Buscar produto atual
            cursor.execute("SELECT * FROM tb_produtos WHERE pro_id = %s", (produto_id,))
            produto = cursor.fetchone()
            
            if not produto:
                print("\nProduto não encontrado.")
                return
                
            print(f"\nEditando: {produto['pro_nome']}")
            print(f"Descrição atual: {produto['prod_desc']}")
            print(f"Preço atual: R${produto['prod_preco']:.2f}")
            print(f"Estoque atual: {produto['qntd_estoque']}")
            
            novo_nome = input(f"\nNovo nome ({produto['pro_nome']}): ").strip() or produto['pro_nome']
            nova_desc = input(f"Nova descrição ({produto['prod_desc']}): ").strip() or produto['prod_desc']
            
            try:
                novo_preco = input(f"Novo preço ({produto['prod_preco']:.2f}): ").strip()
                novo_preco = Decimal(novo_preco.replace(',', '.')) if novo_preco else produto['prod_preco']
                
                novo_estoque = input(f"Novo estoque ({produto['qntd_estoque']}): ").strip()
                novo_estoque = int(novo_estoque) if novo_estoque else produto['qntd_estoque']
                
                # Atualizar produto
                query = """
                UPDATE tb_produtos
                SET pro_nome = %s, prod_desc = %s, prod_preco = %s, qntd_estoque = %s
                WHERE pro_id = %s
                """
                cursor.execute(query, (novo_nome, nova_desc, novo_preco, novo_estoque, produto_id))
                conn.commit()
                print("\nProduto atualizado com sucesso!")
                
            except ValueError:
                print("Erro: Valor inválido para preço ou estoque. Use números.")
                
    except ValueError:
        print("Erro: ID do produto deve ser um número.")
    except Error as e:
        print(f"Erro ao atualizar produto: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

def remover_produto():
    """Remove um produto do banco de dados."""
    listar_produtos()
    try:
        produto_id = int(input("\nID do produto a ser removido (0 para cancelar): "))
        if produto_id == 0:
            return
            
        confirmacao = input(f"Tem certeza que deseja remover o produto ID {produto_id}? (s/n): ").lower()
        if confirmacao != 's':
            print("Operação cancelada.")
            return
            
        conn = conectar_banco()
        if conn:
            cursor = conn.cursor()
            
            # Verificar se o produto existe
            cursor.execute("SELECT pro_id FROM tb_produtos WHERE pro_id = %s", (produto_id,))
            if not cursor.fetchone():
                print("\nProduto não encontrado.")
                return
                
            cursor.execute("DELETE FROM tb_produtos WHERE pro_id = %s", (produto_id,))
            conn.commit()
            print("\nProduto removido com sucesso!")
            
    except ValueError:
        print("Erro: ID do produto deve ser um número.")
    except Error as e:
        print(f"Erro ao remover produto: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

# --- MENU PRINCIPAL ---
def menu():
    """Exibe o menu de opções."""
    print("\n=== LOJA DE JOGOS ===")
    print("1. Listar produtos")
    print("2. Adicionar produto")
    print("3. Atualizar produto")
    print("4. Remover produto")
    print("5. Sair")

def main():
    while True:
        menu()
        opcao = input("\nEscolha uma opção: ").strip()
        
        if opcao == "1":
            listar_produtos()
        elif opcao == "2":
            adicionar_produto()
        elif opcao == "3":
            atualizar_produto()
        elif opcao == "4":
            remover_produto()
        elif opcao == "5":
            print("\nAté logo!")
            break
        else:
            print("\nOpção inválida! Tente novamente.")

if __name__ == "__main__":
    main()
