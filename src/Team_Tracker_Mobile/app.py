import os
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
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
         # Inicializa as seleções para os Jogadores 
        self.players = []
        self.selected_player = None
        self.last_selected_player=None
        # Inicializa as seleções para os jogos
        self.games = []
        self.jogo_selecionado = None
        self.last_selected_jogo = None

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
        # Cria a janela de Jogos
        self.games_window = toga.Window(title="Jogos Agendados")
        main_box = toga.Box(
            style=Pack(direction=COLUMN, padding=20, alignment=CENTER, background_color="#e5e7eb")
        )

        # ---------------------------------------
        # Formulário para agendar novo jogo (compacto)
        # ---------------------------------------
        form_box = toga.Box(style=Pack(direction=COLUMN, padding=5, background_color="white", width=450))
        form_title = toga.Label(
            "Agendar Novo Jogo",
            style=Pack(font_size=16, font_weight="bold", padding_bottom=5)
        )
        form_box.add(form_title)

        # Linha 1: Data e Adversário
        row1 = toga.Box(style=Pack(direction=ROW, padding_bottom=5))
        
        # Caixa para Data
        data_box = toga.Box(style=Pack(direction=COLUMN, padding_right=20))
        data_label = toga.Label("Data:", style=Pack(padding_bottom=5))
        self.jogo_data_input = toga.TextInput(
            placeholder="AAAA-MM-DD",
            style=Pack(width=180)
        )
        data_box.add(data_label)
        data_box.add(self.jogo_data_input)
        
        # Caixa para Adversário
        adv_box = toga.Box(style=Pack(direction=COLUMN))
        adv_label = toga.Label("Adversário:", style=Pack(padding_bottom=5))
        self.jogo_adv_input = toga.TextInput(
            placeholder="Nome do adversário",
            style=Pack(width=180)
        )
        adv_box.add(adv_label)
        adv_box.add(self.jogo_adv_input)
        
        row1.add(data_box)
        row1.add(adv_box)
        form_box.add(row1)

        # Linha 2: Escalão e Clube
        row2 = toga.Box(style=Pack(direction=ROW, padding_bottom=5))
        
        # Escalão
        escalao_box = toga.Box(style=Pack(direction=COLUMN, padding_right=20))
        escalao_label = toga.Label("Escalão:", style=Pack(padding_bottom=5))
        predefined_escaloes = [
            "Petizes 1ºano(Sub-6)", "Petizes 2ºano(Sub-7)",
            "Traquinas 1ºano(Sub-8)", "Traquinas 2ºano(Sub-9)",
            "Benjamins 1ºano(Sub-10)", "Benjamins 2ºano(Sub-11)",
            "Infantis 1ºano(Sub-12)", "Infantis 2ºano(Sub-13)",
            "Iniciados 1ºano(Sub-14)", "Iniciados 2ºano(Sub-15)",
            "Juvenis 1ºano(Sub-16)", "Juvenis 2ºano(Sub-17)",
            "Juniores 1ºano(Sub-18)", "Juniores 2ºano(Sub-19)"
        ]
        user_escalao = self.user_info.get("escalao", "Todos")
        if user_escalao != "Todos":
            self.jogo_escalao_input = toga.TextInput(value=user_escalao, style=Pack(width=180))
            self.jogo_escalao_input.enabled = False
        else:
            items = ["Todos"] + predefined_escaloes
            self.jogo_escalao_input = toga.Selection(items=items, style=Pack(width=180))
            self.jogo_escalao_input.value = "Todos"
        escalao_box.add(escalao_label)
        escalao_box.add(self.jogo_escalao_input)
        
        # Clube
        clube_box = toga.Box(style=Pack(direction=COLUMN))
        clube_label = toga.Label("Clube:", style=Pack(padding_bottom=5))
        user_clube = self.user_info.get("clube", "Todos")
        if user_clube != "Todos":
            self.jogo_clube_input = toga.TextInput(value=user_clube, style=Pack(width=180))
            self.jogo_clube_input.enabled = False
        else:
            self.jogo_clube_input = toga.TextInput(placeholder="Clube", style=Pack(width=180))
        clube_box.add(clube_label)
        clube_box.add(self.jogo_clube_input)
        
        row2.add(escalao_box)
        row2.add(clube_box)
        form_box.add(row2)
        
        # Botão para agendar jogo (abaixo das duas linhas)
        agendar_button = toga.Button(
            "Agendar Jogo",
            on_press=self.agendar_jogo_method,
            style=Pack(padding_top=5)
        )
        form_box.add(agendar_button)
        main_box.add(form_box)

        # ---------------------------------------
        # Lista de Jogos Agendados e Filtros (com filtros em linha)
        # ---------------------------------------
        list_box = toga.Box(
            style=Pack(direction=COLUMN, padding=10, background_color="white", margin_top=20,height=200, width=500)
        )
        list_title = toga.Label(
            "Jogos Agendados",
            style=Pack(font_size=16, font_weight="bold", padding_bottom=10)
        )
        list_box.add(list_title)

        # Filtros dispostos em linha
        row_filter = toga.Box(style=Pack(direction=ROW, padding_bottom=10))
        
        # Caixa do filtro de Escalão
        esc_box = toga.Box(style=Pack(direction=COLUMN, padding_right=20))
        esc_label = toga.Label("Filtrar por Escalão:", style=Pack(padding_bottom=5))
        if user_escalao != "Todos":
            esc_items = [user_escalao]
            self.filter_esc_selection = toga.Selection(
                items=esc_items, style=Pack(width=200, padding_bottom=10)
            )
            self.filter_esc_selection.value = user_escalao
            self.filter_esc_selection.enabled = False
        else:
            esc_items = ["Todos"] + predefined_escaloes
            self.filter_esc_selection = toga.Selection(
                items=esc_items, style=Pack(width=200, padding_bottom=10)
            )
            self.filter_esc_selection.value = "Todos"
        esc_box.add(esc_label)
        esc_box.add(self.filter_esc_selection)
        
        # Caixa do filtro de Clube
        club_box = toga.Box(style=Pack(direction=COLUMN, padding_right=20))
        club_label = toga.Label("Filtrar por Clube:", style=Pack(padding_bottom=5))
        if user_clube != "Todos":
            club_items = [user_clube]
            self.filter_club_selection = toga.Selection(
                items=club_items, style=Pack(width=100, padding_bottom=10)
            )
            self.filter_club_selection.value = user_clube
            self.filter_club_selection.enabled = False
        else:
            self.filter_club_selection = toga.Selection(
                items=["Todos"], style=Pack(width=100, padding_bottom=10)
            )
            self.filter_club_selection.value = "Todos"
        club_box.add(club_label)
        club_box.add(self.filter_club_selection)
        
        # Caixa para o botão de filtro
        button_box = toga.Box(style=Pack(direction=COLUMN))
        refresh_filter_button = toga.Button(
            "Aplicar Filtro",
            on_press=self.refresh_games,
            style=Pack(width=100, padding_top=20)
        )
        button_box.add(refresh_filter_button)
        
        # Adiciona as caixas (Escalão, Clube e Botão) lado a lado
        row_filter.add(esc_box)
        row_filter.add(club_box)
        row_filter.add(button_box)
        list_box.add(row_filter)

        # Tabela para listar os jogos – com as colunas: Data, Adversário, Escalão, Clube, Estado
        self.games_table = toga.Table(
            headings=["Data", "Adversário", "Escalão", "Clube", "Estado"],
            data=[],
            on_select=self.on_select_game,
            style=Pack(flex=1)
        )
        list_box.add(self.games_table)

        # Botões de ação (Ver Jogo e Remover Jogo)
        actions_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding_top=10))
        self.ver_jogo_button = toga.Button(
            "Ver Jogo (em desenvolvimento)",
            on_press=self.ver_jogo,
            style=Pack(padding=5)
        )
        self.remover_jogo_button = toga.Button(
            "Remover Jogo",
            on_press=self.remover_jogo_method,
            style=Pack(padding=5)
        )
        actions_box.add(self.ver_jogo_button)
        actions_box.add(self.remover_jogo_button)
        list_box.add(actions_box)

        main_box.add(list_box)

        # Define o conteúdo e mostra a janela
        self.games_window.content = main_box
        self.games_window.show()

        # Carrega os jogos a partir da API
        self.load_games()


    def load_games(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/api/jogos", headers=headers)
            if response.status_code == 200:
                # Ordena os jogos por data
                jogos_data = sorted(response.json(), key=lambda j: j.get("data"))
                self.games = jogos_data
                # Atualiza o filtro de clubes se o usuário tiver "Todos" em clube
                if self.user_info.get("clube", "Todos") == "Todos":
                    clubs = sorted(list({ jogo.get("clube", "") for jogo in self.games }))
                    clubs = ["Todos"] + clubs
                    self.filter_club_selection.items = clubs
                    self.filter_club_selection.value = "Todos"
                self.refresh_games(None)
            else:
                self.main_window.error_dialog("Erro", "Não foi possível carregar os jogos.")
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    def refresh_games(self, widget):
        selected_esc = self.filter_esc_selection.value
        selected_club = self.filter_club_selection.value
        filtered = []
        for j in self.games:
            match_esc = (selected_esc == "Todos") or (j.get("escalao") == selected_esc)
            match_club = (selected_club == "Todos") or (j.get("clube") == selected_club)
            if match_esc and match_club:
                adv_field = j.get("adversario", "")
                if self.jogo_selecionado and self.jogo_selecionado.get("id") == j.get("id"):
                    adv_field = "→ " + adv_field
                row = [
                    j.get("data", ""),
                    adv_field,
                    j.get("escalao", ""),
                    j.get("clube", ""),
                    j.get("estado", "")
                ]
                filtered.append(row)
        self.games_table.data = filtered

    def on_select_game(self, widget):
        # Obter a seleção real do widget
        selected = self.games_table.selection
        if not selected:
            print("Nenhuma linha selecionada.")
            return

        # Se a seleção for múltipla, pega a primeira linha; caso contrário, utiliza o único item.
        row = selected[0] if isinstance(selected, list) else selected
        print("Linha selecionada:", row)
        
        try:
            # Tenta extrair os atributos utilizando os nomes com acentos.
            data_str = getattr(row, "data", None)
            adversario_str = getattr(row, "adversário", None) or getattr(row, "adversario", None)
            escalao_str = getattr(row, "escalão", None) or getattr(row, "escalao", None)
            clube_str = getattr(row, "clube", None)
            
            if not (data_str and adversario_str and escalao_str and clube_str):
                if hasattr(row, "cells"):
                    cells = row.cells
                    if len(cells) >= 4:
                        data_str = str(cells[0])
                        adversario_str = cells[1]
                        escalao_str = cells[2]
                        clube_str = cells[3]
                    else:
                        print("Dados insuficientes na linha para identificação do jogo.")
                        return
                else:
                    print("Não foi possível extrair os dados necessários da linha.")
                    return

            self.jogo_selecionado = None
            # Procura o jogo correspondente utilizando os quatro campos
            for jogo in self.games:
                if (jogo.get("data") == data_str and
                    jogo.get("adversario") == adversario_str and
                    jogo.get("escalao") == escalao_str and
                    jogo.get("clube") == clube_str):
                    self.jogo_selecionado = jogo
                    self.last_selected_jogo = jogo  # Guarda a última seleção válida
                    print("Jogo selecionado:", jogo)
                    break

            if self.jogo_selecionado is None:
                print("Nenhum jogo correspondente encontrado para Data:", data_str,
                    "Adversário:", adversario_str, "Escalão:", escalao_str, "Clube:", clube_str)

            # Opcional: atualiza a tabela para refletir visualmente a seleção
            self.refresh_games(None)
            
        except Exception as e:
            print("Erro ao processar a seleção:", e)
            self.jogo_selecionado = None



    def agendar_jogo_method(self, widget):
        # Recolhe os dados do formulário
        data = self.jogo_data_input.value
        adversario = self.jogo_adv_input.value
        # Para escalão, verifica se o widget é TextInput ou Selection
        if hasattr(self.jogo_escalao_input, "value"):
            escalao = self.jogo_escalao_input.value
        else:
            escalao = ""
        clube = self.jogo_clube_input.value
        # Valida a existência dos dados
        if not (data and adversario and escalao and clube):
            self.main_window.error_dialog("Erro", "Por favor, preencha todos os campos.")
            return
        # Valida que, se o usuário tem escalão/clube específicos, os valores devem coincidir
        if self.user_info.get("escalao", "Todos") != "Todos" and escalao != self.user_info.get("escalao"):
            self.main_window.error_dialog("Erro", f"Você só pode agendar jogos do seu escalão ({self.user_info.get('escalao')}).")
            return
        if self.user_info.get("clube", "Todos") != "Todos" and clube != self.user_info.get("clube"):
            self.main_window.error_dialog("Erro", f"Você só pode agendar jogos do seu clube ({self.user_info.get('clube')}).")
            return
        # Cria o payload para o POST
        payload = {
            "data": data,
            "adversario": adversario,
            "escalao": escalao,
            "clube": clube
        }
        try:
            url = f"{self.api_url}/api/jogos"
            response = requests.post(url, json=payload)
            if response.status_code in (200, 201):
                self.main_window.info_dialog("Sucesso", "Jogo agendado com sucesso!")
                # Limpa os campos do formulário
                self.jogo_data_input.value = ""
                self.jogo_adv_input.value = ""
                if hasattr(self.jogo_escalao_input, "value") and self.user_info.get("escalao", "Todos") == "Todos":
                    self.jogo_escalao_input.value = "Todos"
                if hasattr(self.jogo_clube_input, "value") and self.user_info.get("clube", "Todos") == "Todos":
                    self.jogo_clube_input.value = ""
                self.load_games()
            else:
                error_message = response.json().get("detail", "Erro ao agendar o jogo.")
                self.main_window.error_dialog("Erro", error_message)
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    async def remover_jogo_method(self, widget):
        # Utiliza self.jogo_selecionado ou, se ausente, self.last_selected_jogo
        jogo_to_remove = self.jogo_selecionado if self.jogo_selecionado is not None else getattr(self, 'last_selected_jogo', None)
        if not jogo_to_remove:
            self.main_window.error_dialog("Erro", "Selecione um jogo para remover.")
            return
        confirmar = await self.main_window.confirm_dialog("Confirmação", f"Tem certeza que deseja remover o jogo contra {jogo_to_remove.get('adversario')}?")
        if not confirmar:
            return
        try:
            url = f"{self.api_url}/api/jogos/{jogo_to_remove.get('id')}"
            headers = {"Authorization": f"Bearer {self.token}"}
            response = requests.delete(url, headers=headers)
            if response.status_code in (200, 204):
                self.main_window.info_dialog("Sucesso", "Jogo removido com sucesso!")
                # Limpa a seleção
                self.jogo_selecionado = None
                self.last_selected_jogo = None
                self.load_games()
            else:
                self.main_window.error_dialog("Erro", f"Erro ao remover jogo: {response.text}")
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

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
    def show_estatisticas(self, widget):
        # Cria uma nova janela para as estatísticas
        self.stats_window = toga.Window(title="Estatísticas dos Jogadores")
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20, alignment=CENTER, background_color="#e5e7eb"))

        # Caixa de filtros
        filter_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        user_escalao = self.user_info.get("escalao", "Todos")
        user_clube = self.user_info.get("clube", "Todos")

        # Configuração do filtro de Escalão
        escaloes = [
            "Petizes 1ºano(Sub-6)", "Petizes 2ºano(Sub-7)",
            "Traquinas 1ºano(Sub-8)", "Traquinas 2ºano(Sub-9)",
            "Benjamins 1ºano(Sub-10)", "Benjamins 2ºano(Sub-11)",
            "Infantis 1ºano(Sub-12)", "Infantis 2ºano(Sub-13)",
            "Iniciados 1ºano(Sub-14)", "Iniciados 2ºano(Sub-15)",
            "Juvenis 1ºano(Sub-16)", "Juvenis 2ºano(Sub-17)",
            "Juniores 1ºano(Sub-18)", "Juniores 2ºano(Sub-19)"
        ]
        if user_escalao != "Todos":
            escalao_items = [user_escalao]
            escalao_default = user_escalao
            escalao_disabled = True
        else:
            escalao_items = ["Todos"] + escaloes
            escalao_default = "Todos"
            escalao_disabled = False
        self.escalao_selection = toga.Selection(
            items=escalao_items,
            style=Pack(width=300, padding_bottom=10)
        )
        self.escalao_selection.value = escalao_default
        self.escalao_selection.enabled = not escalao_disabled

        filter_box.add(toga.Label("Filtrar por Escalão:", style=Pack(padding_bottom=5)))
        filter_box.add(self.escalao_selection)

        # Configuração do filtro de Clube
        if user_clube != "Todos":
            clube_items = [user_clube]
            clube_default = user_clube
            clube_disabled = True
        else:
            clube_items = ["Todos"]
            clube_default = "Todos"
            clube_disabled = False
        self.clube_selection = toga.Selection(
            items=clube_items,
            style=Pack(width=300, padding_bottom=10)
        )
        self.clube_selection.value = clube_default
        self.clube_selection.enabled = not clube_disabled

        filter_box.add(toga.Label("Filtrar por Clube:", style=Pack(padding_bottom=5)))
        filter_box.add(self.clube_selection)

        # Botão para atualizar a tabela conforme os filtros
        refresh_button = toga.Button("Aplicar Filtro", on_press=self.refresh_stats, style=Pack(padding_bottom=10))
        filter_box.add(refresh_button)
        main_box.add(filter_box)

        # Tabela para exibir as estatísticas
        # As colunas serão: Foto, Número, Nome, Jogos, Golos, Assistências, CA, CV, TTU
        self.stats_table = toga.Table(
            headings=["Foto", "Número", "Nome", "Jogos", "Golos", "Assistências", "CA", "CV", "TTU"],
            data=[],
            style=Pack(flex=1)
        )
        main_box.add(self.stats_table)

        # Botão para exportar para CSV
        export_button = toga.Button("Exportar CSV", on_press=self.export_stats_csv, style=Pack(padding_top=10))
        main_box.add(export_button)

        self.stats_window.content = main_box
        self.stats_window.show()

        # Carrega os jogadores a partir da API e atualiza os filtros (no caso de utilizador com "Todos" no clube)
        self.load_players_stats()

    def load_players_stats(self):
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            response = requests.get(f"{self.api_url}/api/jogadores", headers=headers)
            if response.status_code == 200:
                self.all_players = response.json()  # Armazena todos os jogadores com estatísticas
                # Se o clube do utilizador for "Todos", atualiza o widget com os clubes encontrados
                if self.user_info.get("clube", "Todos") == "Todos":
                    clubs = sorted(list({ player.get("clube", "") for player in self.all_players }))
                    clubs = ["Todos"] + clubs
                    self.clube_selection.items = clubs
                    self.clube_selection.value = "Todos"
                # Atualiza a tabela com os dados filtrados
                self.refresh_stats(None)
            else:
                self.main_window.error_dialog("Erro", "Não foi possível carregar as estatísticas dos jogadores.")
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    def refresh_stats(self, widget):
        # Aplica os filtros de escalão e clube e atualiza a tabela de estatísticas
        selected_escalao = self.escalao_selection.value
        selected_clube = self.clube_selection.value
        filtered = []
        for p in self.all_players:
            match_escalao = (selected_escalao == "Todos") or (p.get("escalao") == selected_escalao)
            match_clube = (selected_clube == "Todos") or (p.get("clube") == selected_clube)
            if match_escalao and match_clube:
                foto = "Foto" if p.get("foto") else "Sem foto"
                row = [
                    foto,
                    str(p.get("numero", "")),
                    p.get("nome", ""),
                    str(p.get("jogosParticipados", 0)),
                    str(p.get("golosMarcados", 0)),
                    str(p.get("assistencias", 0)),
                    str(p.get("CA", 0)),
                    str(p.get("CV", 0)),
                    str(p.get("TTU", 0))
                ]
                filtered.append(row)
        self.stats_table.data = filtered

    def export_stats_csv(self, widget):
        # Gera uma string CSV com os dados exibidos na tabela (exceto a coluna "Foto")
        header = ["Número", "Nome", "Jogos", "Golos", "Assistências", "CA", "CV", "TTU"]
        csv_lines = [",".join(header)]
        for row in self.stats_table.data:
            csv_lines.append(",".join(row[1:]))  # ignora a primeira coluna (foto)
        csv_content = "\n".join(csv_lines)
        try:
            with open("estatisticas_jogadores.csv", "w", encoding="utf-8") as f:
                f.write(csv_content)
            self.stats_window.info_dialog("Exportação CSV", "Arquivo CSV exportado com sucesso: estatisticas_jogadores.csv")
        except Exception as e:
            self.stats_window.error_dialog("Erro", str(e))
    def show_jogo_planeado(self, jogo):
        """
        Abre a janela para o jogo planeado, mostrando os detalhes do jogo e
        as duas listas de jogadores: Disponíveis e Convocados.
        """
        self.jogo_selecionado = jogo

        # Cria a nova janela
        self.jogo_planeado_window = toga.Window(title="Jogo Planeado")
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=20))

        detalhes_text = (
            f"Data: {jogo.get('data')}\n"
            f"Adversário: {jogo.get('adversario')}\n"
            f"Escalão: {jogo.get('escalao')}\n"
            f"Clube: {jogo.get('clube')}\n"
            f"Estado: {jogo.get('estado')}"
        )
        detalhes_label = toga.Label(detalhes_text, style=Pack(padding_bottom=10))
        main_box.add(detalhes_label)

        # Define as tabelas com ordem: [Foto, Num, Nome, Posição]
        # Ajustamos a largura total para acomodar melhor os campos Nome e Posição,
        # mas vamos "reduzir" visualmente Foto e Num.
        self.available_table = toga.Table(
            headings=["Foto", "Num", "Nome", "Posição"],
            data=[],
            on_select=self.on_select_available,
            style=Pack(width=700, flex=1)
        )
        self.convoked_table = toga.Table(
            headings=["Foto", "Num", "Nome", "Posição"],
            data=[],
            on_select=self.on_select_convoked,
            style=Pack(width=700, flex=1)
        )

        # Insere as tabelas num ScrollContainer para permitir visualizar muitas linhas
        available_scroll = toga.ScrollContainer(
            content=self.available_table,
            style=Pack(height=300, flex=1, padding_right=10)
        )
        convoked_scroll = toga.ScrollContainer(
            content=self.convoked_table,
            style=Pack(height=300, flex=1, padding_left=10)
        )

        tables_box = toga.Box(style=Pack(direction=ROW, padding=10, alignment=CENTER))
        tables_box.add(available_scroll)
        tables_box.add(convoked_scroll)
        main_box.add(tables_box)

        # Botões para transferir jogadores
        buttons_box = toga.Box(style=Pack(direction=ROW, alignment=CENTER, padding_top=10))
        add_btn = toga.Button("➡️ Adicionar", on_press=self.add_convoked, style=Pack(padding=5))
        remove_btn = toga.Button("⬅️ Remover", on_press=self.remove_convoked, style=Pack(padding=5))
        buttons_box.add(add_btn)
        buttons_box.add(remove_btn)
        main_box.add(buttons_box)

        confirm_btn = toga.Button("Avançar (Confirmar Convocatória)", on_press=self.confirm_convocation, style=Pack(padding_top=10))
        main_box.add(confirm_btn)

        self.jogo_planeado_window.content = main_box
        self.jogo_planeado_window.show()

        self.load_jogo_planeado_players(jogo)


    def refresh_jogo_planeado_tables(self):
        """
        Atualiza as tabelas exibindo os jogadores disponíveis e os já convocados.
        Ordem: [Foto, Num, Nome, Posição]
        """
        available_rows = []
        for p in self.available_players:
            foto_str = "Foto" if p.foto else "Sem foto"
            available_rows.append([foto_str, str(p.numero), p.nome, p.posicao])
        self.available_table.data = available_rows

        convoked_rows = []
        for p in self.convoked_players:
            foto_str = "Foto" if p.foto else "Sem foto"
            convoked_rows.append([foto_str, str(p.numero), p.nome, p.posicao])
        self.convoked_table.data = convoked_rows


    def on_select_available(self, widget):
        """
        Callback para seleção na tabela de disponíveis.
        Usa a abordagem semelhante ao método on_select_player que funciona bem.
        """
        selected = widget.selection
        if not selected:
            print("Nenhuma linha selecionada na tabela de disponíveis.")
            self.selected_available = None
            return
        row = selected[0] if isinstance(selected, list) else selected
        print("Linha selecionada (Disponíveis):", row)
        try:
            numero_str = getattr(row, "num", None) or getattr(row, "número", None) or getattr(row, "numero", None)
            nome_str = getattr(row, "nome", None)
            if not numero_str or not nome_str:
                if hasattr(row, "cells") and row.cells:
                    cells = row.cells
                    if len(cells) >= 3:
                        numero_str = str(cells[1])
                        nome_str = str(cells[2])
                    else:
                        print("Células insuficientes na tabela de disponíveis.")
                        return
                else:
                    print("Não foi possível extrair 'num' ou 'nome' da linha de disponíveis.")
                    return
            self.selected_available = None
            for player in self.available_players:
                if str(player.numero) == str(numero_str) and player.nome == nome_str:
                    self.selected_available = player
                    print("Jogador selecionado (Disponíveis):", player)
                    break
            if self.selected_available is None:
                print("Nenhum jogador correspondente encontrado na tabela de disponíveis para Num:", numero_str, "Nome:", nome_str)
        except Exception as e:
            print("Erro ao processar a seleção (Disponíveis):", e)
            self.selected_available = None


    def on_select_convoked(self, widget):
        """
        Callback para seleção na tabela de convocados.
        Usa a mesma lógica do método on_select_player.
        """
        selected = widget.selection
        if not selected:
            print("Nenhuma linha selecionada na tabela de convocados.")
            self.selected_convoked = None
            return
        row = selected[0] if isinstance(selected, list) else selected
        print("Linha selecionada (Convocados):", row)
        try:
            numero_str = getattr(row, "num", None) or getattr(row, "número", None) or getattr(row, "numero", None)
            nome_str = getattr(row, "nome", None)
            if not numero_str or not nome_str:
                if hasattr(row, "cells") and row.cells:
                    cells = row.cells
                    if len(cells) >= 3:
                        numero_str = str(cells[1])
                        nome_str = str(cells[2])
                    else:
                        print("Células insuficientes na tabela de convocados.")
                        return
                else:
                    print("Não foi possível extrair 'num' ou 'nome' da linha de convocados.")
                    return
            self.selected_convoked = None
            for player in self.convoked_players:
                if str(player.numero) == str(numero_str) and player.nome == nome_str:
                    self.selected_convoked = player
                    print("Jogador selecionado (Convocados):", player)
                    break
            if self.selected_convoked is None:
                print("Nenhum jogador correspondente encontrado na tabela de convocados para Num:", numero_str, "Nome:", nome_str)
        except Exception as e:
            print("Erro ao processar a seleção (Convocados):", e)
            self.selected_convoked = None

    def find_player_in_list(self, row, players_list):
        """
        Tenta identificar o objeto Player correspondente à linha selecionada,
        utilizando os dados (número e nome). Nesta nova ordem de colunas:
            índice 0 -> número
            índice 1 -> nome
        A função primeiro tenta obter os atributos 'num' e 'nome' do row,
        e se não encontrados, recorre a row.cells.
        """
        try:
            # Tenta extrair diretamente dos atributos do row
            numero_str = getattr(row, "num", None) or getattr(row, "número", None) or getattr(row, "numero", None)
            nome_str = getattr(row, "nome", None)
            if not numero_str or not nome_str:
                if hasattr(row, "cells") and row.cells:
                    cells = row.cells
                    if len(cells) >= 2:
                        numero_str = str(cells[0])
                        nome_str = str(cells[1])
                    else:
                        return None
                else:
                    return None
            for p in players_list:
                if str(p.numero) == str(numero_str) and p.nome == nome_str:
                    return p
            return None
        except Exception as e:
            print("Erro em find_player_in_list:", e)
            return None

    def load_jogo_planeado_players(self, jogo):
        """
        Carrega os jogadores do escalão e clube do jogo e os separa nas listas:
        - available_players: jogadores disponíveis (mesmo clube e escalão) que ainda não foram convocados.
        - convoked_players: jogadores já convocados para o jogo.
        Armazena também a lista original de convocados para comparações posteriores.
        """
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            # Busca jogadores pelo escalão (ajuste o endpoint se necessário)
            jogadores_response = requests.get(
                f"{self.api_url}/api/jogadores?escalao={jogo.get('escalao')}",
                headers=headers
            )
            if jogadores_response.status_code == 200:
                all_players_data = jogadores_response.json()
                # Filtra apenas jogadores do mesmo clube do jogo
                self.available_players = [Player(**p) for p in all_players_data if p.get("clube") == jogo.get("clube")]
            else:
                self.available_players = []

            # Busca os jogadores já convocados para o jogo
            conv_response = requests.get(
                f"{self.api_url}/api/convocados/detalhes/{jogo.get('id')}",
                headers=headers
            )
            if conv_response.status_code == 200:
                convoked_data = conv_response.json()
                self.convoked_players = [Player(**p) for p in convoked_data]
            else:
                self.convoked_players = []

            # Remove os jogadores já convocados da lista de disponíveis
            convoked_ids = {p.id for p in self.convoked_players}
            self.available_players = [p for p in self.available_players if p.id not in convoked_ids]

            # Armazena a lista original de convocados para comparar alterações na convocatória
            self.original_convoked_players = self.convoked_players.copy()

            self.refresh_jogo_planeado_tables()

        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    def refresh_jogo_planeado_tables(self):
        """
        Atualiza as tabelas exibindo os jogadores disponíveis e os já convocados.
        """
        available_rows = []
        for p in self.available_players:
            foto_str = "Foto" if p.foto else "Sem foto"
            available_rows.append([foto_str, str(p.numero), p.nome, p.posicao])
        self.available_table.data = available_rows

        convoked_rows = []
        for p in self.convoked_players:
            foto_str = "Foto" if p.foto else "Sem foto"
            convoked_rows.append([foto_str, str(p.numero), p.nome, p.posicao])
        self.convoked_table.data = convoked_rows


    def add_convoked(self, widget):
        """
        Move o jogador selecionado da lista de disponíveis para a lista de convocados.
        """
        if not hasattr(self, "selected_available") or self.selected_available is None:
            self.main_window.error_dialog("Erro", "Selecione um jogador na lista de disponíveis!")
            return
        player = self.selected_available
        self.available_players = [p for p in self.available_players if p.id != player.id]
        self.convoked_players.append(player)
        self.selected_available = None
        self.refresh_jogo_planeado_tables()

    def remove_convoked(self, widget):
        """
        Move o jogador selecionado da lista de convocados de volta para a lista de disponíveis.
        """
        if not hasattr(self, "selected_convoked") or self.selected_convoked is None:
            self.main_window.error_dialog("Erro", "Selecione um jogador na lista de convocados!")
            return
        player = self.selected_convoked
        self.convoked_players = [p for p in self.convoked_players if p.id != player.id]
        self.available_players.append(player)
        self.selected_convoked = None
        self.refresh_jogo_planeado_tables()

    def confirm_convocation(self, widget):
        """
        Compara as listas original e atual de convocados, identifica os jogadores adicionados e removidos,
        envia as chamadas à API correspondentes e atualiza o estado do jogo para "Em Curso".
        """
        try:
            headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
            jogo_id = self.jogo_selecionado.get("id")
            original_ids = {p.id for p in self.original_convoked_players} if hasattr(self, "original_convoked_players") else set()
            current_ids = {p.id for p in self.convoked_players}

            # Identifica jogadores adicionados e removidos
            added_ids = list(current_ids - original_ids)
            removed_ids = list(original_ids - current_ids)

            # Se houver jogadores removidos, envia DELETE em lote
            if removed_ids:
                del_payload = {"jogadores": removed_ids}
                del_url = f"{self.api_url}/api/convocados/remover-varios/{jogo_id}"
                del_response = requests.delete(del_url, json=del_payload, headers=headers)
                if del_response.status_code not in (200, 204):
                    self.main_window.error_dialog("Erro", "Falha ao remover alguns jogadores da convocatória.")
                    return

            # Se houver jogadores adicionados, envia POST
            if added_ids:
                add_payload = {"jogadores": added_ids}
                add_url = f"{self.api_url}/api/convocados/{jogo_id}"
                add_response = requests.post(add_url, json=add_payload, headers=headers)
                if add_response.status_code not in (200, 201):
                    self.main_window.error_dialog("Erro", "Falha ao adicionar alguns jogadores à convocatória.")
                    return

            # Atualiza o estado do jogo para "Em Curso" via PATCH
            patch_url = f"{self.api_url}/api/jogos/{jogo_id}/estado"
            new_status = "Em Curso"
            patch_response = requests.patch(patch_url, json=new_status, headers={"Content-Type": "application/json"})
            if patch_response.status_code in (200, 204):
                self.main_window.info_dialog("Sucesso", "Convocatória confirmada e jogo iniciado!")
                # Aqui você pode chamar o método para abrir a tela "Jogo Em Curso"
                # ex: self.show_jogo_em_curso(self.jogo_selecionado)
            else:
                self.main_window.error_dialog("Erro", "Falha ao atualizar o estado do jogo.")
        except Exception as e:
            self.main_window.error_dialog("Erro", str(e))

    # MÉTODOS DE VISUALIZAÇÃO DO JOGO

    def ver_jogo(self, widget):
        """
        Método final para "Ver Jogo". Verifica o estado do jogo selecionado e
        invoca a visualização correspondente:
          - Para jogo planeado: chama show_jogo_planeado
          - Para jogo em curso: chama show_jogo_em_curso (placeholder)
          - Para jogo terminado: chama show_jogo_terminado (placeholder)
        """
        if not self.jogo_selecionado:
            self.main_window.error_dialog("Erro", "Nenhum jogo selecionado!")
            return

        estado = self.jogo_selecionado.get("estado", "")

        if estado.startswith("Resultado:"):
            self.show_jogo_terminado(self.jogo_selecionado)
        elif estado == "Planeado":
            self.show_jogo_planeado(self.jogo_selecionado)
        elif estado == "Em Curso":
            self.show_jogo_em_curso(self.jogo_selecionado)
        else:
            self.main_window.error_dialog("Erro", "Estado do jogo desconhecido.")

    def show_jogo_em_curso(self, jogo):
        """
        Placeholder para a visualização de um jogo em curso.
        Futuramente, aqui serão implementadas as funcionalidades para gerenciar o cronómetro,
        registrar eventos, atualizar estatísticas, etc.
        """
        self.main_window.info_dialog("Jogo Em Curso", "Funcionalidade de jogo em curso em desenvolvimento.")

    def show_jogo_terminado(self, jogo):
        """
        Placeholder para a visualização dos detalhes de um jogo terminado.
        Futuramente, aqui serão exibidos o resultado final e as estatísticas do jogo.
        """
        self.main_window.info_dialog("Jogo Terminado", "Funcionalidade de jogo terminado em desenvolvimento.")

def main():
    return TeamTrackerMobile()

if __name__ == "__main__":
    app = main()
    app.main_loop()
