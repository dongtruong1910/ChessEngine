import pygame
import sys
from typing import Optional, Tuple, Dict, List
from Model.piece import Piece, Pawn, Rook, Knight, Bishop, Queen, King

class Board():
    def __init__(self):
        self.squares = {}  # Dictionary lưu trữ các quân cờ trên bàn
        self.current_turn = "white"  # Lượt đi hiện tại, bắt đầu là white
        self.move_history = []  # Lịch sử các nước đi
        
        pygame.init()
        self.init_board()
        self.update_all_pieces_status()

    # Khởi tạo bàn cờ
    def init_board(self):
        # Khởi tạo quân trắng
        self.squares[(7, 0)] = Rook("white", (7, 0))
        self.squares[(7, 1)] = Knight("white", (7, 1))
        self.squares[(7, 2)] = Bishop("white", (7, 2))
        self.squares[(7, 3)] = Queen("white", (7, 3))
        self.squares[(7, 4)] = King("white", (7, 4))
        self.squares[(7, 5)] = Bishop("white", (7, 5))
        self.squares[(7, 6)] = Knight("white", (7, 6))
        self.squares[(7, 7)] = Rook("white", (7, 7))
        for col in range(8):
            self.squares[(6, col)] = Pawn("white", (6, col))


        # Khởi tạo quân đen
        self.squares[(0, 0)] = Rook("black", (0, 0))
        self.squares[(0, 1)] = Knight("black", (0, 1))
        self.squares[(0, 2)] = Bishop("black", (0, 2))
        self.squares[(0, 3)] = Queen("black", (0, 3))
        self.squares[(0, 4)] = King("black", (0, 4))
        self.squares[(0, 5)] = Bishop("black", (0, 5))
        self.squares[(0, 6)] = Knight("black", (0, 6))
        self.squares[(0, 7)] = Rook("black", (0, 7))
        for col in range(8):
            self.squares[(1, col)] = Pawn("black", (1, col))

    # Lấy quân cờ tại vị trí trên bàn cờ
    def get_piece(self, position: Tuple[int, int]) -> Optional[Piece]:
        return self.squares.get(position)

    # Lấy thông tin quân cờ tại vị trí trên bàn cờ
    def get_piece_data(self, position: Tuple[int, int]) -> Optional[dict]:
        piece = self.get_piece(position)
        if piece:
            return {
                'type': type(piece).__name__.lower(),
                'color': piece.color,
                'position': position
            }
        return None

    # Phong cấp tốt
    def promote_pawn(self, position: Tuple[int, int], promotion_type: str) -> None:
        piece = self.get_piece(position)
        if not piece or not isinstance(piece, Pawn):
            return

        color = piece.color

        # Tạo quân cờ mới theo loại đã chọn
        if promotion_type == "queen":
            new_piece = Queen(color, position)
        elif promotion_type == "rook":
            new_piece = Rook(color, position)
        elif promotion_type == "bishop":
            new_piece = Bishop(color, position)
        elif promotion_type == "knight":
            new_piece = Knight(color, position)
        else:
            # Mặc định phong cấp thành hậu
            new_piece = Queen(color, position)

        # Thay thế tốt bằng quân cờ mới
        self.squares[position] = new_piece

        # Cập nhật trạng thái quân cờ mới
        new_piece.update_status(self)

    # Di chuyển quân cờ
    def move_piece(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        piece = self.squares.get(start)

        # Xử lý bắt tốt qua đường
        if isinstance(piece, Pawn) and abs(end[1] - start[1]) == 1 and not self.get_piece(end):
            captured_pawn_pos = (start[0], end[1])  # Vị trí của tốt bị bắt
            del self.squares[captured_pawn_pos]  # Xóa tốt bị bắt

        if piece:
            # Lưu nước đi vào lịch sử
            self.move_history.append((start, end, piece))

            # Di chuyển quân cờ
            self.squares[end] = piece
            del self.squares[start]
            piece.move(end)  # Cập nhật vị trí và has_moved

            # Kiểm tra phong cấp cho tốt
            needs_promotion = False
            if isinstance(piece, Pawn):
                if (piece.color == "white" and end[0] == 0) or (piece.color == "black" and end[0] == 7):
                    needs_promotion = True


            # Xử lý nhập thành (nếu di chuyển vua 2 ô)
            if isinstance(piece, King) and abs(end[1] - start[1]) == 2:
                # Xác định vị trí của xe
                rook_col = 7 if end[1] > start[1] else 0
                rook_row = start[0]
                rook = self.squares.get((rook_row, rook_col))

                if rook and isinstance(rook, Rook):
                    # Xác định vị trí mới của xe
                    new_rook_col = 5 if end[1] > start[1] else 3

                    # Di chuyển xe
                    self.squares[(rook_row, new_rook_col)] = rook
                    del self.squares[(rook_row, rook_col)]
                    rook.move((rook_row, new_rook_col))

            # Cập nhật trạng thái các quân cờ
            self.update_all_pieces_status()

            # Đổi lượt
            self.current_turn = "black" if self.current_turn == "white" else "white"
            return needs_promotion

    # Kiểm tra xem nước đi có hợp lệ không
    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        piece = self.squares.get(start)
        if not piece or piece.color != self.current_turn:
            return False

        # Kiểm tra nước đi có hợp lệ không
        if not piece.is_valid_move(self, end):
            return False

        # Thử di chuyển và kiểm tra xem vua có bị chiếu không
        old_piece = self.squares.get(end)
        old_position = piece.position
        has_moved = piece.has_moved

        self.squares[end] = piece
        del self.squares[start]
        piece.position = end
        piece.has_moved = True

        # Kiểm tra xem vua có bị chiếu không
        is_check = self.is_check(piece.color)

        # Hoàn tác
        self.squares[start] = piece
        del self.squares[end]
        piece.position = old_position
        piece.has_moved = has_moved

        if old_piece:
            self.squares[end] = old_piece

        return not is_check

    # Lấy quân vua của màu color, trả về None nếu không tìm thấy
    def get_king(self, color: str) -> Optional[King]:
        for piece in self.squares.values():
            if isinstance(piece, King) and piece.color == color:
                return piece
        return None

    # Kiểm tra xem vua có bị chiếu không
    def is_check(self, color: str) -> bool:
        # Tìm vua của màu cần kiểm tra
        king = None
        for piece in self.squares.values():
            if isinstance(piece, King) and piece.color == color:
                king = piece
                break
        
        if not king:
            return False
            
        # Kiểm tra xem có quân cờ nào của đối phương đang tấn công vua không
        for piece in self.squares.values():
            if piece.color != color:
                if piece.is_valid_move(self, king.position):
                    return True
        
        return False

    # Kiểm tra xem ô có bị tấn công không (dùng để xác định xem vua có đi vào vị trí đó được không)
    def is_square_under_attack(self, position: Tuple[int, int], color: str) -> bool:
        for piece in self.squares.values():
            if piece.color != color:
                if isinstance(piece, King):
                    # Kiểm tra xem quân vua có thể bị tấn công ô đó không
                    king_pos = piece.position
                    row_diff = abs(king_pos[0] - position[0])
                    col_diff = abs(king_pos[1] - position[1])
                    if row_diff <= 1 and col_diff <= 1:
                        return True
                elif piece.is_valid_move(self, position):
                    return True
        return False

    # Cập nhật trạng thái của tất cả quân cờ
    def update_all_pieces_status(self):
        for piece in self.squares.values():
            piece.update_status(self)

    # Lấy tất cả các nước đi hợp lệ của quân cờ tại vị trí position
    def get_valid_moves(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        piece = self.squares.get(position)
        if not piece or piece.color != self.current_turn:
            return []

        valid_moves = []

        for row in range(8):
            for col in range(8):
                if self.is_valid_move(position, (row, col)):
                    valid_moves.append((row, col))

        return valid_moves

    # Lấy thông tin tất cả quân cờ trên bàn
    def get_all_pieces(self) -> List[dict]:
        pieces = []
        for pos, piece in self.squares.items():
            pieces.append({
                'type': type(piece).__name__.lower(),
                'color': piece.color,
                'position': pos
            })
        return pieces

    # Kiểm tra chiếu hết
    def is_checkmate(self, color: str) -> bool:

        # Kiểm tra xem vua có bị chiếu không
        if not self.is_check(color):
            return False

        # Tìm vua
        king = self.get_king(color)
        if not king:
            return False

        # Kiểm tra tất cả các nước đi của quân cờ cùng màu
        positions = [(pos, piece) for pos, piece in self.squares.items() if piece.color == color]

        for piece_pos, piece in positions:
            if self.squares.get(piece_pos) != piece:
                continue

            valid_moves = []
            # Lấy tất cả các nước đi hợp lệ của quân cờ cùng màu
            for row in range(8):
                for col in range(8):
                    if self.is_valid_move(piece_pos, (row, col)):
                        valid_moves.append((row, col))
            # Nếu có nước đi hợp lệ (có thể bảo vệ vua), thì không phải chiếu hết
            if valid_moves:
                return False

        # Nếu không có nước đi nào hợp lệ, thì là chiếu hết
        return True

    # Kiểm tra hòa cờ
    def is_stalemate(self) -> bool:
        # Nếu chỉ còn 2 quân cờ trên bàn (vua và vua), thì hòa
        if len(self.squares) == 2:
            return True

        # Kiểm tra xem vua có đang bị chiếu không
        if self.is_check(self.current_turn):
            return False
            
        # Kiểm tra xem có quân nào có thể di chuyển không
        for piece in self.squares.values():
            if piece.color == self.current_turn:
                if piece.get_valid_moves(self):
                    return False
        return True


    # Tạo 1 bản sao bàn cờ, dùng cho AI
    def clone(self):
        new_board = Board()
        # Khởi tạo bàn cờ mới, giống bàn cờ hiện tại
        new_board.squares = {} # Tạo một bản sao rỗng
        # Copy các quân cờ
        for pos, piece in self.squares.items():
            piece_type = type(piece)
            new_piece = piece_type(piece.color, pos)
            new_piece.has_moved = piece.has_moved
            new_board.squares[pos] = new_piece

        # Copy lượt đi hiện tại và lịch sử nước đi
        new_board.current_turn = self.current_turn
        new_board.move_history = self.move_history.copy()

        # Copy trạng thái của các quân cờ
        new_board.update_all_pieces_status()
        return new_board