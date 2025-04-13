from itertools import count
import pygame
import os
from typing import List, Tuple, Dict, Optional
from pygame import Color
from Model.piece import King


class BoardView:
    def __init__(self, board_size=640, margin=30, player_color=None):
        """
        board_size: kich thuoc ban co
        margin: le cua ban co
        """
        self.board_size = board_size
        self.square_size = board_size / 8
        self.margin = margin
        self.player_color = player_color  # Fix: properly store as instance attribute

        """
        mau sac cua ban co
        """
        self.LIGHT_SQUARE = Color('white')  # mau o sang
        self.DARK_SQUARE = Color('green')  # mau o toi
        self.HIGHLIGHT = (124, 192, 214, 170)  # mau goi y nuoc di
        self.SELECTED = (106, 168, 79, 200)  # mau o dang chon
        self.ACTIVE_PLAYER = (255, 255, 200, 128)  # Màu highlight người chơi đang đi

        """
        khoi tao man hinh
        """
        self.screen_width = board_size + 2 * margin + 200  # Thêm 200px cho phần hiển thị lịch sử
        self.screen_height = board_size + 2 * margin
        self.screen = None

        """
        tai hinh anh quan co va nguoi choi
        """
        self.piece_images = {}
        self.player_images = {}

        # luu vi tri o dc chon va nuoc di hop le
        self.selected_square = None
        self.valid_moves = []
        self.pieces_data = []  # Danh sách thông tin các quân cờ

        # Font hien thi
        self.coordinate_font = None
        self.clock_font = None

        # Thời gian cho mỗi người chơi (phút)
        self.white_time = 10 * 60  # 10 phút
        self.black_time = 10 * 60
        self.last_time_update = pygame.time.get_ticks()

        # Thêm biến lưu trữ lịch sử nước đi
        self.move_history = []

        # Thêm biến lưu trạng thái kết thúc game
        self.game_over = False
        self.winner = None

        # Khởi tạo board reference
        self.board = None

    def load_player_images(self):
        """Tải hình ảnh người chơi"""
        try:
            image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images')

            # Tạo placeholder nếu không tìm thấy ảnh
            for color in ['white', 'black']:
                file_name = f"player_{color}.png"
                file_path = os.path.join(image_path, file_name)

                if os.path.exists(file_path):
                    img = pygame.image.load(file_path)
                    img = pygame.transform.scale(img, (80, 80))  # Kích thước avatar
                    self.player_images[color] = img
                else:
                    # Tạo hình ảnh mặc định
                    surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                    pygame.draw.circle(surf, Color(color), (40, 40), 35)
                    pygame.draw.circle(surf, Color('black'), (40, 40), 35, 2)
                    self.player_images[color] = surf
                    print(f"Không tìm thấy hình ảnh {file_path}, đã tạo ảnh mặc định")
        except Exception as e:
            print(f"Lỗi khi tải hình ảnh người chơi: {e}")
            # Tạo hình ảnh mặc định trong trường hợp lỗi
            for color in ['white', 'black']:
                surf = pygame.Surface((80, 80), pygame.SRCALPHA)
                pygame.draw.circle(surf, Color(color), (40, 40), 35)
                pygame.draw.circle(surf, Color('black'), (40, 40), 35, 2)
                self.player_images[color] = surf

    def init_screen(self):
        """khoi tao man hinh pygame"""
        if self.screen is None:
            if pygame.display.get_surface() is None:
                pygame.init()
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
                pygame.display.set_caption("Chess Board")
            else:
                self.screen = pygame.display.get_surface()

            # khoi tao font
            pygame.font.init()
            self.coordinate_font = pygame.font.SysFont('Arial', 14)
            self.clock_font = pygame.font.SysFont('Arial', 24)

            # Tải hình ảnh sau khi pygame được khởi tạo
            self.load_piece_images()
            self.load_player_images()

    def load_piece_images(self):
        # duong dan den thu muc anh
        image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'assets', 'images')

        # hinh anh cho tung quan co
        piece_names = ['pawn', 'knight', 'bishop', 'rook', 'queen', 'king']
        colors = ['white', 'black']

        for color in colors:
            for piece in piece_names:
                file_name = f"{color}_{piece}.png"
                file_path = os.path.join(image_path, file_name)

                if os.path.exists(file_path):
                    img = pygame.image.load(file_path)
                    img = pygame.transform.scale(img, (int(self.square_size), int(self.square_size)))
                    self.piece_images[f"{color}_{piece}"] = img
                else:
                    print(f"Cảnh báo: Không tìm thấy hình ảnh {file_path}")

    def get_square_rect(self, row, col):
        """
        Lấy hình chữ nhật cho một ô bàn cờ, điều chỉnh theo hướng bàn cờ
        """
        if self.player_color == "black":
            # Lật tọa độ khi chơi quân đen
            row, col = 7 - row, 7 - col

        x = self.margin + col * self.square_size
        y = self.margin + row * self.square_size
        return pygame.Rect(x, y, self.square_size, self.square_size)

    def draw_board(self):
        """Vẽ bàn cờ"""
        if not self.screen:
            self.init_screen()

        self.screen.fill((240, 240, 240))

        # ve o vuong
        for row in range(8):
            for col in range(8):
                display_row, display_col = (7 - row, 7- col) if self.player_color == "black" else (row, col)

                x = self.margin + display_col * self.square_size
                y = self.margin + display_row * self.square_size

                # xan dinh mau o
                color = self.LIGHT_SQUARE if (row + col) % 2 == 0 else self.DARK_SQUARE

                # ve o vuong
                pygame.draw.rect(self.screen, color, (x, y, self.square_size, self.square_size))

                # ve toa do
                if display_row == 7:  # a-h
                    text = self.coordinate_font.render(chr(97 + col), True,
                                                       (0, 0, 0) if color == self.LIGHT_SQUARE else (255, 255, 255))
                    self.screen.blit(text, (x + self.square_size - 15, y + self.square_size - 15))

                if display_col == 0:  # 1-8
                    text = self.coordinate_font.render(str(8 - row), True,
                                                       (0, 0, 0) if color == self.LIGHT_SQUARE else (255, 255, 255))
                    self.screen.blit(text, (x + 5, y + 5))

    def draw_pieces(self):
        """Vẽ các quân cờ"""
        if not self.screen:
            return

        for piece_data in self.pieces_data:
            row, col = piece_data['position']
            rect = self.get_square_rect(row, col)

            image_key = f"{piece_data['color']}_{piece_data['type']}"
            if image_key in self.piece_images:
                self.screen.blit(self.piece_images[image_key], rect)

    def update(self, pieces_data=None, selected_square=None, valid_moves=None, player_time=None,
               ai_time=None, game_over=False, winner=None, move_history=None, board=None):
        """Cập nhật trạng thái hiển thị"""
        if not self.screen:
            self.init_screen()

        # Cập nhật dữ liệu
        if pieces_data is not None:
            self.pieces_data = pieces_data
        if selected_square is not None:
            self.selected_square = selected_square
        if valid_moves is not None:
            self.valid_moves = valid_moves
        if move_history is not None:
            self.move_history = move_history
        if board is not None:
            self.board = board



        # Cập nhật trạng thái game
        self.game_over = game_over
        self.winner = winner

        # Cập nhật thời gian
        if player_time is not None and ai_time is not None:
            self.update_time(player_time, ai_time)

        # Vẽ toàn bộ màn hình
        self.draw_all()

    def draw_all(self):
        """Vẽ toàn bộ giao diện game"""
        if not self.screen:
            return

        # Xóa màn hình
        self.screen.fill((240, 240, 240))

        # Vẽ bàn cờ
        self.draw_board()

        # Highlight ô được chọn
        if self.selected_square:
            self.highlight_selected_square(self.selected_square)

        # Highlight các nước đi hợp lệ
        if self.valid_moves:
            self.highlight_valid_moves(self.valid_moves)

        # Vẽ các quân cờ
        self.draw_pieces()

        # Vẽ người chơi và đồng hồ
        self.draw_players_and_clock()

        # Vẽ lịch sử nước đi
        self.draw_move_history()

        # Hiển thị thông báo kết thúc game nếu cần
        if self.game_over:
            self.show_game_over(self.winner)

        pygame.display.flip()

    def get_clicked_square(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Lấy tọa độ ô được click"""
        x, y = pos
        if (self.margin <= x < self.margin + self.board_size and
                self.margin <= y < self.margin + self.board_size):
            col = int((x - self.margin) // self.square_size)
            row = int((y - self.margin) // self.square_size)
            if self.player_color == "black":
                # Lật tọa độ khi chơi quân đen
                row, col = 7 - row, 7 - col
            return (row, col)
        return None

    def draw_players_and_clock(self):
        """Vẽ hình ảnh người chơi và đồng hồ"""
        if not self.screen:
            return

        # Vị trí hiển thị
        info_x = self.board_size + self.margin * 2
        white_player_y = self.margin
        black_player_y = self.margin + 130

        # Get current turn color
        current_turn = "white" if len(self.move_history) % 2 == 0 else "black"

        # Vẽ khung người chơi trắng
        white_rect = pygame.Rect(info_x, white_player_y, 180, 120)
        if current_turn == "white":
            # Highlight người chơi đang đi
            pygame.draw.rect(self.screen, self.ACTIVE_PLAYER, white_rect)
        pygame.draw.rect(self.screen, Color('black'), white_rect, 2)  # Viền

        # Vẽ hình ảnh người chơi trắng
        if 'white' in self.player_images:
            self.screen.blit(self.player_images['white'], (info_x + 10, white_player_y + 10))

        # Vẽ đồng hồ người chơi trắng
        white_time_str = self.format_time(self.white_time)
        white_time_text = self.clock_font.render(white_time_str, True, Color('black'))
        self.screen.blit(white_time_text, (info_x + 100, white_player_y + 40))

        # Vẽ khung người chơi đen
        black_rect = pygame.Rect(info_x, black_player_y, 180, 120)
        if current_turn == "black":
            # Highlight người chơi đang đi
            pygame.draw.rect(self.screen, self.ACTIVE_PLAYER, black_rect)
        pygame.draw.rect(self.screen, Color('black'), black_rect, 2)  # Viền

        # Vẽ hình ảnh người chơi đen
        if 'black' in self.player_images:
            self.screen.blit(self.player_images['black'], (info_x + 10, black_player_y + 10))

        # Vẽ đồng hồ người chơi đen
        black_time_str = self.format_time(self.black_time)
        black_time_text = self.clock_font.render(black_time_str, True, Color('black'))
        self.screen.blit(black_time_text, (info_x + 100, black_player_y + 40))

    def update_time(self, player_time: float, ai_time: float):
        """Cập nhật thời gian cho người chơi và AI"""
        self.white_time = player_time if self.player_color == 'white' else ai_time
        self.black_time = ai_time if self.player_color == 'white' else player_time

    def format_time(self, seconds: float) -> str:
        """Định dạng thời gian từ giây thành chuỗi phút:giây"""
        if seconds is None:
            return "00:00"

        minutes = int(seconds // 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"

    def draw_move_history(self):
        """Vẽ lịch sử các nước đi với khả năng cuộn"""
        if not self.screen or not self.move_history:
            return

        # Vị trí hiển thị
        history_x = self.board_size + self.margin * 2
        history_y = self.margin + 270

        # Vẽ tiêu đề
        title = self.clock_font.render("Move History", True, Color('black'))
        self.screen.blit(title, (history_x, history_y))

        # Vẽ khung cho phần lịch sử
        history_bg = pygame.Rect(history_x, history_y + 30, 180, 250)
        pygame.draw.rect(self.screen, Color(240, 240, 240), history_bg)
        pygame.draw.rect(self.screen, Color('black'), history_bg, 2)  # Viền

        # Vẽ nút cuộn lên/xuống
        scroll_up_rect = pygame.Rect(history_x + 155, history_y + 35, 20, 20)
        scroll_down_rect = pygame.Rect(history_x + 155, history_y + 255, 20, 20)
        pygame.draw.rect(self.screen, Color('lightgray'), scroll_up_rect)
        pygame.draw.rect(self.screen, Color('lightgray'), scroll_down_rect)
        pygame.draw.rect(self.screen, Color('black'), scroll_up_rect, 1)
        pygame.draw.rect(self.screen, Color('black'), scroll_down_rect, 1)

        # Vẽ mũi tên
        pygame.draw.polygon(self.screen, Color('black'), [
            (history_x + 165, history_y + 40),
            (history_x + 160, history_y + 50),
            (history_x + 170, history_y + 50)
        ])
        pygame.draw.polygon(self.screen, Color('black'), [
            (history_x + 165, history_y + 270),
            (history_x + 160, history_y + 260),
            (history_x + 170, history_y + 260)
        ])

        # Nếu không có thuộc tính scroll_offset, khởi tạo nó
        if not hasattr(self, 'scroll_offset'):
            self.scroll_offset = 0

        # Xác định vùng hiển thị (clipping)
        clip_rect = pygame.Rect(history_x + 5, history_y + 35, 145, 240)
        self.screen.set_clip(clip_rect)

        # Số dòng có thể hiển thị trong khung
        visible_lines = 9  # Số dòng có thể hiển thị với khoảng cách 12.5px

        # Tổng số nước đi hiển thị (mỗi nước chiếm 2 dòng)
        total_moves = len(self.move_history)
        total_lines = (total_moves + 1) // 2  # Làm tròn lên

        # Giới hạn scroll_offset
        max_offset = max(0, total_lines - visible_lines)
        self.scroll_offset = min(max_offset, self.scroll_offset)

        # Dịch chuyển vị trí bắt đầu dựa trên scroll_offset
        start_idx = self.scroll_offset * 2
        end_idx = min(start_idx + visible_lines * 2, total_moves)

        # Vẽ từng nước đi
        for i in range(start_idx, end_idx):
            try:
                move_idx = i
                if move_idx >= len(self.move_history):
                    break

                move = self.move_history[move_idx]

                # Trích xuất chỉ start và end, bỏ qua piece
                start, end = move[0], move[1]

                # Chuyển đổi tọa độ sang ký hiệu cờ vua
                start_pos = chr(97 + start[1]) + str(8 - start[0])
                end_pos = chr(97 + end[1]) + str(8 - end[0])

                # Tạo chuỗi nước đi
                move_number = move_idx // 2 + 1
                is_white_move = move_idx % 2 == 0

                if is_white_move:
                    # Nước đi của trắng (bên trái)
                    move_text = f"{move_number}. {start_pos}-{end_pos}"
                    y_pos = history_y + 45 + (move_idx // 2 - self.scroll_offset) * 25
                    self.screen.blit(self.coordinate_font.render(move_text, True, Color('black')),
                                     (history_x + 10, y_pos))
                else:
                    # Nước đi của đen (bên phải)
                    move_text = f"{start_pos}-{end_pos}"
                    y_pos = history_y + 45 + ((move_idx - 1) // 2 - self.scroll_offset) * 25
                    self.screen.blit(self.coordinate_font.render(move_text, True, Color(64, 64, 64)),
                                     (history_x + 100, y_pos))

            except Exception as e:
                print(f"Error displaying move {i}: {e}")



        # Khôi phục clipping
        self.screen.set_clip(None)

        # Lưu trữ thông tin về nút cuộn để xử lý sự kiện
        self.scroll_up_button = scroll_up_rect
        self.scroll_down_button = scroll_down_rect

    def show_game_over(self, winner: Optional[str] = None):
        """Hiển thị thông báo kết thúc game và tùy chọn tiếp tục"""
        if not self.screen:
            return

        # Create and show endgame view
        from View.endgame_view import EndgameView
        endgame_view = EndgameView(self.screen, winner)
        return endgame_view.draw()

    def highlight_selected_square(self, square: Tuple[int, int]):
        """Tô màu ô được chọn"""
        if not self.screen or not square:
            return

        rect = self.get_square_rect(*square)

        # Tạo surface với độ trong suốt
        highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        highlight_surface.fill(self.SELECTED)

        # Vẽ surface lên màn hình
        self.screen.blit(highlight_surface, rect)

    def get_square_center(self, square: Tuple[int, int]) -> Tuple[int, int]:
        """Tính toán tọa độ trung tâm của ô cờ"""
        row, col = square
        x = self.margin + col * self.square_size + self.square_size // 2
        y = self.margin + row * self.square_size + self.square_size // 2
        return (x, y)

    def highlight_valid_moves(self, valid_moves: List[Tuple[int, int]]):
        """Hiển thị các nước đi hợp lệ"""
        if not self.screen or not valid_moves:
            return

        for move in valid_moves:
            rect = self.get_square_rect(*move)

            # Tạo surface với độ trong suốt
            highlight_surface = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
            highlight_surface.fill(self.HIGHLIGHT)

            # Vẽ surface lên màn hình
            self.screen.blit(highlight_surface, rect)

    def handle_scroll(self, pos):
        """Xử lý sự kiện cuộn lịch sử nước đi"""
        if hasattr(self, 'scroll_up_button') and self.scroll_up_button.collidepoint(pos):
            # Cuộn lên
            print("Scroll up clicked!")
            if hasattr(self, 'scroll_offset'):
                self.scroll_offset = max(0, self.scroll_offset - 1)
                # Vẽ lại lịch sử nước đi ngay lập tức
                self.draw_move_history()
                pygame.display.update(pygame.Rect(
                    self.board_size + self.margin * 2,
                    self.margin + 270,
                    180, 280
                ))
            return True

        if hasattr(self, 'scroll_down_button') and self.scroll_down_button.collidepoint(pos):
            # Cuộn xuống
            print("Scroll down clicked!")
            if hasattr(self, 'scroll_offset'):
                # Giới hạn sẽ được kiểm tra trong draw_move_history
                self.scroll_offset += 1
                # Vẽ lại lịch sử nước đi ngay lập tức
                self.draw_move_history()
                pygame.display.update(pygame.Rect(
                    self.board_size + self.margin * 2,
                    self.margin + 270,
                    180, 280
                ))
            return True

        return False