import os
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, CENTER
import requests

# Classe auxiliar que representa um jogador, incluindo estatísticas.
class Player:
    def __init__(
        self,
        id,
        nome,
        numero,
        posicao,
        escalao,
        clube,
        foto=None,
        golosMarcados=0,
        assistencias=0,
        TTU=0,
        jogosParticipados=0,
        CA=0,
        CV=0,
    ):
        self.id = id
        self.nome = nome
        self.numero = numero
        self.posicao = posicao
        self.escalao = escalao
        self.clube = clube
        self.foto = foto
        self.golosMarcados = golosMarcados
        self.assistencias = assistencias
        self.TTU = TTU
        self.jogosParticipados = jogosParticipados
        self.CA = CA
        self.CV = CV

    def __str__(self):
        return f"{self.numero} - {self.nome}"

    def __repr__(self):
        return self.__str__()

class TeamTrackerMobile(toga.App):
    def __init__(self, *args, **kwargs):
        # Inicializa a aplicação com o nome formal e o app_id.
        super().__init__(
            formal_name="Team Tracker Mobile",
            app_id="com.example.teamtrackermobile",
            *args,
            **kwargs
        )
        self.token = None
        self.user_info = None
        self.api_url = "https://teamtracker-production.up.railway.app"
        self.players = []
        self.selected_player = None
        self.last_selected_player=None

    def startup(self):
        # Inicia a aplicação exibindo a tela de login.
        self.show_login_screen()

    # ---------------------------
    # Telas de Login e Home
    # ---------------------------
    def show_login_screen(self):
        main_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                alignment=CENTER,
                padding=20,
                background_color="#e5e7eb"
            )
        )

        image_path = os.path.join(os.path.dirname(__file__), "resources", "logo.png")
        try:
            logo = toga.Image(image_path)
            logo_view = toga.ImageView(
                logo,
                style=Pack(width=128, height=128, padding_bottom=20)
            )
        except Exception as e:
            logo_view = toga.Label("Logo não encontrada", style=Pack(padding_bottom=20))
            print("Erro ao carregar a imagem:", e)

        login_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                alignment=CENTER,
                padding=20,
                background_color="#ffffff",
                width=300
            )
        )
        welcome_label = toga.Label(
            "Bem-vindo ao Team Tracker",
            style=Pack(
                font_size=18,
                font_weight="bold",
                text_align=CENTER,
                padding_bottom=10
            )
        )
        self.username_input = toga.TextInput(
            placeholder="Usuário",
            style=Pack(width=200, padding_bottom=10)
        )
        self.password_input = toga.PasswordInput(
            placeholder="Senha",
            style=Pack(width=200, padding_bottom=10)
        )
        login_button = toga.Button(
            "Entrar",
            on_press=self.do_login,
            style=Pack(width=200, padding_top=10)
        )
        login_box.add(welcome_label)
        login_box.add(logo_view)
        login_box.add(self.username_input)
        login_box.add(self.password_input)
        login_box.add(login_button)
        main_box.add(login_box)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

    def do_login(self, widget):
        username = self.username_input.value
        password = self.password_input.value

        if not username or not password:
            self.main_window.error_dialog("Erro", "Preencha usuário e senha.")
            return

        try:
            login_endpoint = f"{self.api_url}/api/auth/login"
            payload = {"username": username, "password": password}
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            response = requests.post(login_endpoint, data=payload, headers=headers)
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                if self.token:
                    self.get_user_info()
                else:
                    self.main_window.error_dialog("Erro", "Token não recebido.")
            else:
                error_message = response.json().get("detail", "Usuário ou senha inválidos.")
                self.main_window.error_dialog("Erro", error_message)
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    def get_user_info(self):
        try:
            endpoint = f"{self.api_url}/api/auth/me"
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.get(endpoint, headers=headers)
            if response.status_code == 200:
                self.user_info = response.json()
                self.show_homepage()
            else:
                self.main_window.error_dialog("Erro", "Não foi possível recuperar as informações do usuário.")
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    def show_homepage(self):
        main_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                alignment=CENTER,
                padding=20,
                background_color="#e5e7eb"
            )
        )
        user_info_text = "Usuário: {}\nCargo: {}\nClube: {}\nEscalão: {}".format(
            self.user_info.get("username", "N/A"),
            self.user_info.get("cargo", "N/A"),
            self.user_info.get("clube", "N/A"),
            self.user_info.get("escalao", "N/A")
        )
        user_label = toga.Label(user_info_text, style=Pack(padding_bottom=20, text_align="left"))
        main_box.add(user_label)

        btn_jogadores = toga.Button("Jogadores", on_press=self.show_jogadores, style=Pack(width=200, padding=10))
        btn_jogos = toga.Button("Jogos", on_press=self.show_jogos, style=Pack(width=200, padding=10))
        btn_estatisticas = toga.Button("Estatísticas", on_press=self.show_estatisticas, style=Pack(width=200, padding=10))
        main_box.add(btn_jogadores)
        main_box.add(btn_jogos)
        main_box.add(btn_estatisticas)

        self.main_window.content = main_box

    # ---------------------------
    # Tela de Jogadores
    # ---------------------------
    def show_jogadores(self, widget):
        # Cria a caixa principal para a tela de jogadores com fundo claro
        players_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                alignment=CENTER,
                padding=20,
                background_color="#e5e7eb"
            )
        )

        # Define a tabela com os headings desejados:
        # "Foto", "Número", "Nome", "Posição", "Escalão" e "Clube"
        self.players_table = toga.Table(
            headings=["Foto", "Número", "Nome", "Posição", "Escalão", "Clube"],
            data=[],
            on_select=self.on_select_player,
            style=Pack(flex=1)
        )
        players_box.add(self.players_table)

        # Caixa para os botões (placeholders)
        buttons_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                alignment=CENTER,
                padding_top=20
            )
        )
        btn_add = toga.Button("Adicionar Jogador", on_press=self.show_add_player_window, style=Pack(padding=5))
        btn_edit = toga.Button("Editar Jogador", on_press=self.edit_player_placeholder, style=Pack(padding=5))
        btn_remove = toga.Button("Remover Jogador", on_press=self.remove_player, style=Pack(padding=5))
        btn_back = toga.Button("Voltar", on_press=lambda w: self.show_homepage(), style=Pack(padding=5))
        buttons_box.add(btn_add)
        buttons_box.add(btn_edit)
        buttons_box.add(btn_remove)
        buttons_box.add(btn_back)
        
        players_box.add(buttons_box)
        
        self.main_window.content = players_box
        self.load_players()

    def edit_player_placeholder(self, widget):
        if self.selected_player:
            self.main_window.info_dialog("Editar Jogador", f"Funcionalidade de editar jogador {self.selected_player} em desenvolvimento.")
        else:
            self.main_window.error_dialog("Erro", "Nenhum jogador selecionado para editar.")

    def load_players(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/api/jogadores", headers=headers)
            if response.status_code == 200:
                players_data = response.json()
                self.players = []
                rows = []
                for p in players_data:
                    player = Player(
                        id=p.get("id"),
                        nome=p.get("nome"),
                        numero=p.get("numero"),
                        posicao=p.get("posicao"),
                        escalao=p.get("escalao"),
                        clube=p.get("clube"),
                        foto=p.get("foto"),
                        golosMarcados=p.get("golosMarcados", 0),
                        assistencias=p.get("assistencias", 0),
                        TTU=p.get("TTU", 0),
                        jogosParticipados=p.get("jogosParticipados", 0),
                        CA=p.get("CA", 0),
                        CV=p.get("CV", 0)
                    )
                    self.players.append(player)
                    
                    # Verifica se há foto; se não, exibe "Sem foto"
                    if player.foto:
                        photo_view = "Foto"
                    else:
                        photo_view = "Sem foto"
                    
                    # Adiciona um marcador visual (→) para o jogador selecionado
                    if self.selected_player and self.selected_player.id == player.id:
                        marker = "→ "
                        nome_str = marker + player.nome
                    else:
                        nome_str = player.nome
                    
                    rows.append([photo_view, str(player.numero), nome_str, player.posicao, player.escalao, player.clube])
                self.players_table.data = rows
            else:
                self.main_window.error_dialog("Erro", "Não foi possível carregar os jogadores.")
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    # ---------------------------
    # Método para capturar a seleção do jogador na tabela
    # ---------------------------
    def on_select_player(self, widget):
        """
        Callback chamado quando uma linha da tabela for selecionada.
        Obtém a seleção diretamente do widget, acessando os atributos do objeto Row.
        """
        # Obter a seleção real do widget
        selected = self.players_table.selection
        if not selected:
            print("Nenhuma linha selecionada.")
            return

        # Se a seleção for múltipla, pega a primeira linha; caso contrário, utiliza o único item.
        row = selected[0] if isinstance(selected, list) else selected

        print("Linha selecionada:", row)

        try:
            # Tenta acessar os atributos diretamente; note que alguns atributos podem ter nomes com acento.
            # Use getattr para ser mais robusto, tentando "número" e, se não existir, "numero".
            numero_str = getattr(row, "número", None) or getattr(row, "numero", None)
            nome_str = getattr(row, "nome", None)

            if not numero_str or not nome_str:
                # Se os atributos não forem encontrados, tenta acessar via row.cells (caso exista)
                if hasattr(row, "cells"):
                    cells = row.cells
                    numero_str = str(cells[1])
                    nome_str = cells[2]
                else:
                    print("Não foi possível extrair 'número' ou 'nome' da linha.")
                    return

            # Procura o jogador correspondente na lista de jogadores usando os dados obtidos
            self.selected_player = None
            for player in self.players:
                if str(player.numero) == str(numero_str) and player.nome == nome_str:
                    self.selected_player = player
                    self.last_selected_player = player
                    print("Jogador selecionado:", player)
                    break

            if self.selected_player is None:
                print("Nenhum jogador correspondente encontrado para Número:", numero_str, "e Nome:", nome_str)

            # Atualiza a tabela para refletir alterações visuais, como um marcador na linha selecionada
            self.load_players()

        except Exception as e:
            print("Erro ao processar a seleção:", e)
            self.selected_player = None

    # ---------------------------
    # Placeholders para outras telas
    # ---------------------------
    def show_jogos(self, widget):
        self.main_window.info_dialog("Jogos", "Tela de Jogos (em desenvolvimento)")

    def show_estatisticas(self, widget):
        self.main_window.info_dialog("Estatísticas", "Tela de Estatísticas (em desenvolvimento)")

    # Método para remover jogador utilizando o endpoint DELETE /api/jogadores/{jogador_id}
    async def remove_player(self, widget):
        # Usa a seleção atual; se estiver vazia, utiliza a última seleção válida.
        player_to_remove = self.selected_player if self.selected_player is not None else getattr(self, 'last_selected_player', None)
        if not player_to_remove:
            self.main_window.error_dialog("Erro", "Nenhum jogador selecionado para remover.")
            return

        # Cria o diálogo de confirmação
        confirm_dialog = toga.ConfirmDialog(
            "Confirmação", f"Tem certeza que deseja remover {player_to_remove.nome}?"
        )
        # Aguarda o resultado do diálogo (True se confirmado, False caso contrário)
        result = await self.main_window.dialog(confirm_dialog)
        if not result:
            return

        try:
            url = f"{self.api_url}/api/jogadores/{player_to_remove.id}"
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.delete(url, headers=headers)
            if response.status_code in (200, 204):
                self.main_window.info_dialog("Sucesso", "Jogador removido com sucesso!")
                self.selected_player = None
                self.last_selected_player = None
                self.load_players()
            else:
                self.main_window.error_dialog("Erro", f"Erro ao remover jogador: {response.text}")
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    # ---------------------------
    # Métodos para Adicionar Jogador
    # ---------------------------
    def show_add_player_window(self, widget):
        # Cria uma nova janela para adicionar jogador
        self.add_player_window = toga.Window(title="Adicionar Jogador")
        main_box = toga.Box(
            style=Pack(
                direction=COLUMN,
                align_items=CENTER,
                margin=20
            )
        )

        # Campo Nome
        name_label = toga.Label("Nome:", style=Pack(margin_bottom=5))
        self.new_player_name = toga.TextInput(
            placeholder="Nome do jogador",
            style=Pack(width=200, margin_bottom=10)
        )
        main_box.add(name_label)
        main_box.add(self.new_player_name)

        # Campo Número
        number_label = toga.Label("Número:", style=Pack(margin_bottom=5))
        self.new_player_number = toga.TextInput(
            placeholder="Número da camisa",
            style=Pack(width=200, margin_bottom=10)
        )
        main_box.add(number_label)
        main_box.add(self.new_player_number)

        # Campo Posição (seleção)
        position_label = toga.Label("Posição:", style=Pack(margin_bottom=5))
        self.new_player_position = toga.Selection(
            items=["Guarda-Redes", "Defesa Central", "Defesa Lateral",
                "Médio Centro", "Médio Lateral", "Extremo", "Ponta de Lança"],
            style=Pack(width=200, margin_bottom=10)
        )
        main_box.add(position_label)
        main_box.add(self.new_player_position)

        # Campo Escalão
        escalão_label = toga.Label("Escalão:", style=Pack(margin_bottom=5))
        if self.user_info.get("escalao", "") == "Todos":
            escaloes = [
                "Petizes 1ºano(Sub-6)", "Petizes 2ºano(Sub-7)",
                "Traquinas 1ºano(Sub-8)", "Traquinas 2ºano(Sub-9)",
                "Benjamins 1ºano(Sub-10)", "Benjamins 2ºano(Sub-11)",
                "Infantis 1ºano(Sub-12)", "Infantis 2ºano(Sub-13)",
                "Iniciados 1ºano(Sub-14)", "Iniciados 2ºano(Sub-15)",
                "Juvenis 1ºano(Sub-16)", "Juvenis 2ºano(Sub-17)",
                "Juniores 1ºano(Sub-18)", "Juniores 2ºano(Sub-19)"
            ]
            self.new_player_escalao = toga.Selection(
                items=escaloes,
                style=Pack(width=200, margin_bottom=10)
            )
        else:
            self.new_player_escalao = toga.TextInput(
                value=self.user_info.get("escalao", ""),
                style=Pack(width=200, margin_bottom=10)
            )
            self.new_player_escalao.enabled = False
        main_box.add(escalão_label)
        main_box.add(self.new_player_escalao)

        # Campo Clube
        clube_label = toga.Label("Clube:", style=Pack(margin_bottom=5))
        if self.user_info.get("clube", "") == "Todos":
            self.new_player_clube = toga.TextInput(
                placeholder="Nome do clube",
                style=Pack(width=200, margin_bottom=10)
            )
        else:
            self.new_player_clube = toga.TextInput(
                value=self.user_info.get("clube", ""),
                style=Pack(width=200, margin_bottom=10)
            )
            self.new_player_clube.enabled = False
        main_box.add(clube_label)
        main_box.add(self.new_player_clube)

        # Botão para upload de foto
        foto_label = toga.Label("Foto:", style=Pack(margin_bottom=5))
        main_box.add(foto_label)
        self.new_player_photo_path = None  # Armazena o caminho da foto selecionada
        self.upload_photo_btn = toga.Button(
            "Escolher Foto",
            on_press=self.choose_photo,
            style=Pack(width=200, margin_bottom=10)
        )
        main_box.add(self.upload_photo_btn)

        # Botão para submeter o formulário
        submit_btn = toga.Button(
            "Adicionar",
            on_press=self.add_new_player,
            style=Pack(width=200, margin_top=10)
        )
        main_box.add(submit_btn)

        self.add_player_window.content = main_box
        self.add_player_window.show()

    def choose_photo(self, widget):
        # Abre o diálogo para selecionar um ficheiro de imagem
        try:
            chosen = self.main_window.open_file_dialog("Escolha a foto", file_types=["*.png", "*.jpg", "*.jpeg"])
            if chosen:
                self.new_player_photo_path = chosen[0]
                self.upload_photo_btn.label = "Foto Selecionada"
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    def add_new_player(self, widget):
        # Recolhe os dados do formulário
        nome = self.new_player_name.value
        numero = self.new_player_number.value
        posicao = self.new_player_position.value
        # Obtém o valor do escalão (se for Selection, usa .value)
        if hasattr(self.new_player_escalao, "value"):
            escalao = self.new_player_escalao.value
        else:
            escalao = self.new_player_escalao.value
        clube = self.new_player_clube.value

        # Cria o payload conforme esperado pelo endpoint POST /api/jogadores
        payload = {
            "nome": nome,
            "numero": numero,
            "posicao": posicao,
            "escalao": escalao,
            "clube": clube
        }

        try:
            url = f"{self.api_url}/api/jogadores"
            response = requests.post(url, json=payload)
            if response.status_code in (200, 201):
                novo_jogador = response.json()
                jogador_id = novo_jogador.get("id")
                # Se existir foto selecionada, faz upload da mesma
                if self.new_player_photo_path and jogador_id:
                    upload_url = f"{self.api_url}/api/jogadores/{jogador_id}/upload-foto"
                    with open(self.new_player_photo_path, "rb") as f:
                        files = {"file": f}
                        upload_resp = requests.post(upload_url, files=files)
                        if upload_resp.status_code not in (200, 201):
                            self.main_window.error_dialog("Erro", "Jogador criado, mas falha no upload da foto.")
                self.main_window.info_dialog("Sucesso", "Jogador adicionado com sucesso!")
                self.add_player_window.close()
                self.load_players()
            else:
                error_message = response.json().get("detail", "Erro ao adicionar jogador.")
                self.main_window.error_dialog("Erro", error_message)
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

def main():
    return TeamTrackerMobile()

if __name__ == "__main__":
    app = main()
    app.main_loop()
