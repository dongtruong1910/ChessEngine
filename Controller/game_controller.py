import threading

from Model.board import Board
from View.board_view import BoardView
from Model.chess_ai import ChessAI
from typing import Tuple, Optional
import pygame

from View.pawn_promotion_view import PawnPromotionView


class GameController:
    def __init__(self, player_color= None, time_limit=None):
        # Thông tin người chơi và thời gian
        self.player_color = player_color
        self.time_limit = time_limit * 60  # Chuyển đổi phút thành giây

        # Khởi tạo model
        self.board = Board()
        
        # Khởi tạo AI
        self.ai = ChessAI("black" if player_color == "white" else "white")
        
        # Khởi tạo view
        self.board_view = None

        # Lịch sử nước đi
        self.move_history = []

        # Thời gian còn lại của mỗi người chơi (giây)
        self.player_remaining_time = self.time_limit
        self.ai_remaining_time = self.time_limit
        
        # Thời gian bắt đầu lượt đi hiện tại
        self.current_turn_start_time = None
        
        # Trạng thái game
        self.selected_piece = None
        self.valid_moves = []
        self.game_over = False
        self.winner = None  # "white", "black" hoặc None nếu hòa

        # AI đi trước nếu người chơi chọn quân đen
        if self.player_color == "black" and self.board.current_turn == "white":
            self.make_ai_move()

        # Trạng thái suy nghĩ của AI
        self.ai_thinking = False

    def init_view(self, board_size=640, margin=30):
        self.board_view = BoardView(board_size, margin, self.player_color)
        self.board_view.init_screen()
        self.update_view()
        
    def check_win(self):
        # Kiểm tra chiếu tướng
        if self.board.is_checkmate("white"):
            self.game_over = True
            self.winner = "black"
            return True
        elif self.board.is_checkmate("black"):
            self.game_over = True
            self.winner = "white"
            return True
            
        # Kiểm tra hết thời gian
        if self.player_remaining_time <= 0:
            self.game_over = True
            self.winner = "black" if self.player_color == "white" else "white"
            return True
        elif self.ai_remaining_time <= 0:
            self.game_over = True
            self.winner = "white" if self.player_color == "white" else "black"
            return True
            
        # Kiểm tra hòa
        if self.board.is_stalemate():
            self.game_over = True
            self.winner = None
            return True
            
        return False

    # Xử lý click chuột
    def handle_click(self, pos: Tuple[int, int]):

        if self.game_over:
            return
            
        # Nếu là lượt của AI, không xử lý click, nhưng vẫn xử lý click để cuộn lịch sử nước đi
        if self.board.current_turn != self.player_color:
            if self.board_view:
                self.board_view.handle_scroll(pos)
                self.update_view()
            return

        # Xử lý cuộn lịch sử nước đi
        if self.board_view:
            if self.board_view.handle_scroll(pos):
                self.update_view()
                return

        # Lấy ô vuông được click
        clicked_square = self.board_view.get_clicked_square(pos)
        if clicked_square is None:
            return

        if self.selected_piece is None:
            # Chọn quân cờ
            piece_data = self.board.get_piece_data(clicked_square)
            if piece_data and piece_data['color'] == self.board.current_turn:
                self.selected_piece = clicked_square
                self.valid_moves = self.board.get_valid_moves(clicked_square)
                self.update_view()
        else:
            # Di chuyển quân cờ
            if clicked_square in self.valid_moves:
                needs_promotion = self.board.move_piece(self.selected_piece, clicked_square)
                if needs_promotion:
                    # Lấy màu của quân cờ cần phong cấp
                    piece_color = "black" if self.board.current_turn == "white" else "white"

                    # Hiển thị giao diện phong cấp
                    promotion_view = PawnPromotionView(self.board_view.screen, self.board_view.square_size)
                    chosen_piece = promotion_view.get_pawn_promotion_choice(piece_color, clicked_square[1])

                    # Thực hiện phong cấp
                    self.board.promote_pawn(clicked_square, chosen_piece)

                # Cập nhật thời gian sau khi di chuyển
                self.update_time()
                # Kiểm tra chiến thắng sau mỗi nước đi
                self.check_win()
                
                # Nếu chưa kết thúc game, cho AI đi
                if not self.game_over and self.board.current_turn != self.player_color:
                    self.make_ai_move()
            
            # Bỏ chọn quân cờ
            self.selected_piece = None
            self.valid_moves = []
            self.update_view()

    # Cho AI thực hiện nước đi
    def make_ai_move(self):


        # Đánh dấu là AI đang suy nghĩ
        self.ai_thinking = True

        # Tạo thread cho AI suy nghĩ
        ai_thread = threading.Thread(target=self._ai_thinking_process)
        ai_thread.daemon = True
        ai_thread.start()

    # Thời gian suy nghĩ của AI, chạy trong một thread riêng
    def _ai_thinking_process(self):
        best_move = self.ai.get_best_move(self.board)

        # Kết thúc suy nghĩ
        self.ai_thinking = False

        if best_move:
            start, end = best_move
            # Thực hiện nước đi
            needs_promotion = self.board.move_piece(start, end)
            if not needs_promotion:
                self.board.move_piece(start, end)
            else:
                self.board.promote_pawn(end, "queen")  # Mặc định phong cấp thành hậu

            # Reset thời gian bắt đầu lượt mới
            self.current_turn_start_time = pygame.time.get_ticks()

            # Kiểm tra chiến thắng
            self.check_win()

    # Cập nhật thời gian còn lại
    def update_time(self):

        if self.current_turn_start_time is None:
            self.current_turn_start_time = pygame.time.get_ticks()
            return
            
        current_time = pygame.time.get_ticks()
        elapsed_time = (current_time - self.current_turn_start_time) / 1000  # Chuyển sang giây
        
        # Cập nhật thời gian còn lại cho người chơi hiện tại
        if self.board.current_turn == self.player_color:
            self.player_remaining_time -= elapsed_time
        else:
            self.ai_remaining_time -= elapsed_time
            
        # Reset thời gian bắt đầu lượt mới
        self.current_turn_start_time = current_time
        
        # Kiểm tra chiến thắng
        self.check_win()

    # Cập nhật view
    def update_view(self):
        if self.board_view:
            # Lấy thông tin từ model để truyền cho view
            pieces_data = self.board.get_all_pieces()
            move_history = self.board.move_history
            self.board_view.update(
                pieces_data=pieces_data,
                selected_square=self.selected_piece,
                valid_moves=self.valid_moves,
                player_time=self.player_remaining_time,
                ai_time=self.ai_remaining_time,
                game_over=self.game_over,
                winner=self.winner,
                move_history = move_history
            )

    def run(self):
        # Cập nhật thời gian nếu chưa có thời gian bắt đầu lượt
        if self.current_turn_start_time is None:
            self.current_turn_start_time = pygame.time.get_ticks()
            
        # Cập nhật thời gian liên tục
        current_time = pygame.time.get_ticks()
        if self.current_turn_start_time is not None:
            elapsed_time = (current_time - self.current_turn_start_time) / 1000
            if self.ai_thinking:
                self.ai_remaining_time -= elapsed_time
            if self.board.current_turn == self.player_color:
                self.player_remaining_time -= elapsed_time
            else:
                self.ai_remaining_time -= elapsed_time
            self.current_turn_start_time = current_time


        # Kiểm tra chiến thắng
        self.check_win()
        self.update_view()
