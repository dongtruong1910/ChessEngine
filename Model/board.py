import pygame
import sys
from typing import Optional, Tuple, Dict, List
from Model.piece import Piece, Pawn, Rook, Knight, Bishop, Queen, King

class Board():
    def __init__(self):
        self.squares = {}  # Dictionary lưu trữ các quân cờ trên bàn
        self.current_turn = "white"  # Lượt đi hiện tại
        self.move_history = []  # Lịch sử các nước đi
        
        pygame.init()
        self.init_board()
        self.update_all_pieces_status()

    def init_board(self):
        """Khởi tạo bàn cờ với các quân cờ ở vị trí ban đầu"""
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
            
    def get_piece(self, position: Tuple[int, int]) -> Optional[Piece]:
        """Lấy quân cờ tại vị trí position"""
        return self.squares.get(position)

    def get_piece_data(self, position: Tuple[int, int]) -> Optional[dict]:
        """Lấy thông tin của quân cờ để hiển thị"""
        piece = self.get_piece(position)
        if piece:
            return {
                'type': type(piece).__name__.lower(),
                'color': piece.color,
                'position': position
            }
        return None

    def promote_pawn(self, position: Tuple[int, int], promotion_type: str) -> None:
        """
        Thực hiện phong cấp tốt tại vị trí position thành loại quân cờ mới

        Args:
            position: Vị trí của tốt (row, col)
            promotion_type: Loại quân cờ để phong cấp ("queen", "rook", "bishop", "knight")
        """
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

    def move_piece(self, start: Tuple[int, int], end: Tuple[int, int]):
        """Di chuyển quân cờ từ vị trí start đến vị trí end"""

        piece = self.squares.get(start)

        # Xử lý en passant
        if isinstance(piece, Pawn) and abs(end[1] - start[1]) == 1 and not self.get_piece(end):
            # Đây là nước đi en passant
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

    def is_valid_move(self, start: Tuple[int, int], end: Tuple[int, int]) -> bool:
        """Kiểm tra xem nước đi từ start đến end có hợp lệ không"""
        piece = self.squares.get(start)
        if not piece or piece.color != self.current_turn:
            return False

        # Kiểm tra nước đi có hợp lệ không
        if not piece.is_valid_move(self, end):
            return False

        # # Xử lý đặc biệt cho castling
        # is_castling = False
        # if isinstance(piece, King) and abs(end[1] - start[1]) == 2:
        #     is_castling = True
        #     # Kiểm tra vua không đang bị chiếu
        #     if self.is_check(piece.color):
        #         return False
        #
        #     # Kiểm tra các ô vua đi qua không bị tấn công
        #     col_direction = 1 if end[1] > start[1] else -1
        #     for col in range(start[1], end[1] + col_direction, col_direction):
        #         if self.is_square_under_attack((start[0], col), piece.color):
        #             return False

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
    
    def get_king(self, color: str) -> Optional[King]:
        """Lấy quân vua của màu color"""
        for piece in self.squares.values():
            if isinstance(piece, King) and piece.color == color:
                return piece
        return None
        
    def is_check(self, color: str) -> bool:
        """
        Kiểm tra xem vua của màu color có đang bị chiếu không.
        
        Args:
            color: Màu của vua cần kiểm tra ('white' hoặc 'black')
            
        Returns:
            True nếu vua đang bị chiếu, False nếu không
        """
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
    
    def is_square_under_attack(self, position: Tuple[int, int], color: str) -> bool:
        """Kiểm tra xem một ô có bị tấn công không"""
        for piece in self.squares.values():
            if piece.color != color:
                if piece.is_valid_move(self, position):
                    return True
        return False
    
    def update_all_pieces_status(self):
        """Cập nhật trạng thái của tất cả các quân cờ"""
        for piece in self.squares.values():
            piece.update_status(self)

    def get_valid_moves(self, position: Tuple[int, int]) -> List[Tuple[int, int]]:
        """Lấy danh sách các nước đi hợp lệ cho quân cờ tại vị trí position"""
        piece = self.squares.get(position)
        if not piece or piece.color != self.current_turn:
            return []

        valid_moves = []

        # Normal move checking first
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(position, (row, col)):
                    valid_moves.append((row, col))



        return valid_moves
    def get_all_pieces(self) -> List[dict]:
        """Lấy thông tin tất cả quân cờ trên bàn để hiển thị"""
        pieces = []
        for pos, piece in self.squares.items():
            pieces.append({
                'type': type(piece).__name__.lower(),
                'color': piece.color,
                'position': pos
            })
        return pieces

    def get_king(self, color: str) -> Optional[King]:
        """Lấy quân vua của màu color"""
        for piece in self.squares.values():
            if isinstance(piece, King) and piece.color == color:
                return piece
        return None

    def is_checkmate(self, color: str) -> bool:
        """Kiểm tra xem vua của màu color có bị chiếu tướng không"""
        # 1. Kiểm tra chiếu trước
        if not self.is_check(color):
            return False

        # 2. Tìm vua
        king = self.get_king(color)
        if not king:
            return False

        # 3. Kiểm tra tất cả các nước đi của quân cờ cùng màu
        # First, create a copy of the positions to iterate over
        positions = [(pos, piece) for pos, piece in self.squares.items() if piece.color == color]

        for piece_pos, piece in positions:
            # Skip if the piece has been captured during iteration
            if self.squares.get(piece_pos) != piece:
                continue

            valid_moves = []
            # Build the list of potential moves
            for row in range(8):
                for col in range(8):
                    if self.is_valid_move(piece_pos, (row, col)):
                        valid_moves.append((row, col))

            # If there's any valid move, it's not checkmate
            if valid_moves:
                return False

        # No valid moves to escape check
        return True
        
    def is_stalemate(self) -> bool:
        """Kiểm tra xem có phải là hòa do không còn nước đi hợp lệ không"""
        # 1. Kiểm tra xem vua có đang bị chiếu không
        if self.is_check(self.current_turn):
            return False
            
        # 2. Kiểm tra xem có quân nào có thể di chuyển không
        for piece in self.squares.values():
            if piece.color == self.current_turn:
                if piece.get_valid_moves(self):
                    return False
                    
        return True

    def undo_move(self):
        """Hoàn tác nước đi cuối cùng"""
        if self.move_history:
            start, end, piece = self.move_history.pop()

            # Check if this was a castling move
            was_castling = isinstance(piece, King) and abs(end[1] - start[1]) == 2

            # Restore the piece to its original position
            self.squares[start] = piece
            del self.squares[end]
            piece.position = start
            piece.has_moved = False  # Reset has_moved flag

            # Handle undoing rook movement for castling
            if was_castling:
                # Determine rook positions
                rook_row = start[0]
                new_rook_col = 5 if end[1] > start[1] else 3  # Where rook moved to
                old_rook_col = 7 if end[1] > start[1] else 0  # Original rook position

                # Get the rook and move it back
                rook = self.squares.get((rook_row, new_rook_col))
                if rook and isinstance(rook, Rook):
                    self.squares[(rook_row, old_rook_col)] = rook
                    del self.squares[(rook_row, new_rook_col)]
                    rook.position = (rook_row, old_rook_col)
                    rook.has_moved = False  # Reset has_moved flag

            # Update game state
            self.update_all_pieces_status()
            self.current_turn = "black" if self.current_turn == "white" else "white"