from abc import ABC, abstractmethod
from typing import List, Tuple, Optional

class Piece(ABC):
    """
    Lớp cơ sở trừu tượng cho tất cả các quân cờ.
    """
    def __init__(self, color: str, position: Tuple[int, int]):
        """
        Khởi tạo quân cờ.
        
        Args:
            color: Màu của quân cờ ('white' hoặc 'black')
            position: Vị trí của quân cờ dưới dạng (row, col), bắt đầu từ (0,0)
        """
        self.color = color
        self.position = position
        self.has_moved = False
        self.value = 0
    
    @abstractmethod
    def is_valid_move(self, board, target_position: Tuple[int, int]) -> bool:
        """Kiểm tra xem một nước đi có hợp lệ không"""
        pass
    
    def get_valid_moves(self, board) -> List[Tuple[int, int]]:
        """Lấy danh sách các nước đi hợp lệ"""
        valid_moves = []
        for row in range(8):
            for col in range(8):
                if self.is_valid_move(board, (row, col)):
                    valid_moves.append((row, col))
        return valid_moves
    
    def move(self, target_position: Tuple[int, int]):
        """
        Di chuyển quân cờ đến vị trí mới.
        
        Args:
            target_position: Vị trí đích dưới dạng (row, col)
        """
        self.position = target_position
        self.has_moved = True  # Đánh dấu quân cờ đã di chuyển
    
    def get_symbol(self) -> str:
        """
        Trả về biểu tượng của quân cờ để hiển thị.
        
        Returns:
            Chuỗi ký tự đại diện cho quân cờ
        """
        return ""
        
    def get_color(self) -> str:
        """
        Trả về màu của quân cờ.
        
        Returns:
            'white' hoặc 'black'
        """
        return self.color
    
    def is_opponent(self, other_piece) -> bool:
        """
        Kiểm tra xem quân cờ khác có phải là đối thủ không.
        
        Args:
            other_piece: Quân cờ khác cần kiểm tra
            
        Returns:
            True nếu other_piece là đối thủ, False nếu không
        """
        if other_piece is None:
            return False
        return self.color != other_piece.color

    def update_status(self, board):
        pass

    def can_promote(self):
        """
        Kiểm tra xem quân cờ có thể phong cấp không.

        Returns:
            True nếu quân cờ có thể phong cấp, False nếu không
        """
        return False



class Pawn(Piece):
    """
    Quân tốt (Pawn).
    """
    def __init__(self, color: str, position: Tuple[int, int]):
        super().__init__(color, position)
        self.value = 1
        self.start_row = 6 if color == "white" else 1  # Vị trí ban đầu của quân tốt
    
    def get_symbol(self) -> str:
        return "P" if self.color == "white" else "p"
    
    def is_valid_move(self, board, target_position: Tuple[int, int]) -> bool:
        # Kiểm tra vị trí đích có nằm trong bàn cờ không
        if not (0 <= target_position[0] < 8 and 0 <= target_position[1] < 8):
            return False
            
        # Kiểm tra vị trí đích có quân cờ cùng màu không
        target_piece = board.get_piece(target_position)
        if target_piece and target_piece.color == self.color:
            return False
            
        # Xác định hướng di chuyển
        direction = -1 if self.color == "white" else 1
        
        # Di chuyển thẳng
        if target_position[1] == self.position[1]:
            # Di chuyển 1 ô
            if target_position[0] == self.position[0] + direction and not target_piece:
                return True
                
            # Di chuyển 2 ô từ vị trí ban đầu
            if (self.position[0] == self.start_row and 
                target_position[0] == self.position[0] + 2 * direction and 
                not target_piece and
                not board.get_piece((self.position[0] + direction, self.position[1]))):
                return True
                    
        # Ăn chéo
        elif abs(target_position[1] - self.position[1]) == 1:
            if target_position[0] == self.position[0] + direction:
                # Kiểm tra có quân đối phương để ăn không
                if target_piece and target_piece.color != self.color:
                    return True
                # Kiểm tra nước đi en passant
                if not target_piece and board.move_history:
                    last_move = board.move_history[-1]
                    last_piece = last_move[2]

                    # Kiểm tra nếu quân cờ vừa di chuyển là tốt đối phương
                    if (isinstance(last_piece, Pawn) and
                        last_piece.color != self.color and
                        abs(last_move[0][0] - last_move[1][0]) == 2 and  # Di chuyển 2 ô
                        last_move[1][0] == self.position[0] and  # Cùng hàng với tốt hiện tại
                        last_move[1][1] == target_position[1]):  # Cùng cột với vị trí đích
                        return True
        return False
    def can_promote(self):
        """
        Kiểm tra xem quân tốt có thể phong cấp không.

        Returns:
            True nếu quân tốt có thể phong cấp, False nếu không
        """
        if self.color == "white" and self.position[0] == 0:
            return True
        elif self.color == "black" and self.position[0] == 7:
            return True
        return False


class Knight(Piece):
    """
    Quân mã (Knight).
    """
    def __init__(self, color: str, position: Tuple[int, int]):
        super().__init__(color, position)
        self.value = 3
    
    def get_symbol(self) -> str:
        return "N" if self.color == "white" else "n"
    
    def is_valid_move(self, board, target_position: Tuple[int, int]) -> bool:
        # Kiểm tra vị trí đích có nằm trong bàn cờ không
        if not (0 <= target_position[0] < 8 and 0 <= target_position[1] < 8):
            return False
            
        # Kiểm tra vị trí đích có quân cờ cùng màu không
        target_piece = board.get_piece(target_position)
        if target_piece and target_piece.color == self.color:
            return False
            
        # Kiểm tra nước đi hình chữ L
        row_diff = abs(target_position[0] - self.position[0])
        col_diff = abs(target_position[1] - self.position[1])
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)


class Bishop(Piece):
    """
    Quân tượng (Bishop).
    """
    def __init__(self, color: str, position: Tuple[int, int]):
        super().__init__(color, position)
        self.value = 3
    
    def get_symbol(self) -> str:
        return "B" if self.color == "white" else "b"
    
    def is_valid_move(self, board, target_position: Tuple[int, int]) -> bool:
        # Kiểm tra vị trí đích có nằm trong bàn cờ không
        if not (0 <= target_position[0] < 8 and 0 <= target_position[1] < 8):
            return False
            
        # Kiểm tra vị trí đích có quân cờ cùng màu không
        target_piece = board.get_piece(target_position)
        if target_piece and target_piece.color == self.color:
            return False
            
        # Kiểm tra di chuyển theo đường chéo
        if abs(target_position[0] - self.position[0]) != abs(target_position[1] - self.position[1]):
            return False
            
        # Kiểm tra có quân cờ nào chặn đường không
        row_direction = 1 if target_position[0] > self.position[0] else -1
        col_direction = 1 if target_position[1] > self.position[1] else -1
        current_row = self.position[0] + row_direction
        current_col = self.position[1] + col_direction
        
        while current_row != target_position[0]:
            if board.get_piece((current_row, current_col)):
                return False
            current_row += row_direction
            current_col += col_direction
            
        return True


class Rook(Piece):
    """
    Quân xe (Rook).
    """
    def __init__(self, color: str, position: Tuple[int, int]):
        super().__init__(color, position)
        self.value = 5
    
    def get_symbol(self) -> str:
        return "R" if self.color == "white" else "r"
    
    def is_valid_move(self, board, target_position: Tuple[int, int]) -> bool:
        # Kiểm tra vị trí đích có nằm trong bàn cờ không
        if not (0 <= target_position[0] < 8 and 0 <= target_position[1] < 8):
            return False
            
        # Kiểm tra vị trí đích có quân cờ cùng màu không
        target_piece = board.get_piece(target_position)
        if target_piece and target_piece.color == self.color:
            return False
            
        # Kiểm tra di chuyển theo hàng hoặc cột
        if target_position[0] != self.position[0] and target_position[1] != self.position[1]:
            return False
            
        # Kiểm tra có quân cờ nào chặn đường không
        if target_position[0] == self.position[0]:  # Di chuyển ngang
            start = min(self.position[1], target_position[1]) + 1
            end = max(self.position[1], target_position[1])
            for col in range(start, end):
                if board.get_piece((self.position[0], col)):
                    return False
        else:  # Di chuyển dọc
            start = min(self.position[0], target_position[0]) + 1
            end = max(self.position[0], target_position[0])
            for row in range(start, end):
                if board.get_piece((row, self.position[1])):
                    return False
                    
        return True


class Queen(Piece):
    """
    Quân hậu (Queen).
    """
    def __init__(self, color: str, position: Tuple[int, int]):
        super().__init__(color, position)
        self.value = 9
    
    def get_symbol(self) -> str:
        return "Q" if self.color == "white" else "q"
    
    def is_valid_move(self, board, target_position: Tuple[int, int]) -> bool:
        # Kiểm tra vị trí đích có nằm trong bàn cờ không
        if not (0 <= target_position[0] < 8 and 0 <= target_position[1] < 8):
            return False
            
        # Kiểm tra vị trí đích có quân cờ cùng màu không
        target_piece = board.get_piece(target_position)
        if target_piece and target_piece.color == self.color:
            return False
            
        # Hậu có thể di chuyển như xe hoặc tượng
        # Tạo tạm thời một quân xe và tượng để kiểm tra
        temp_rook = Rook(self.color, self.position)
        temp_bishop = Bishop(self.color, self.position)
        return (temp_rook.is_valid_move(board, target_position) or 
                temp_bishop.is_valid_move(board, target_position))


class King(Piece):
    """
    Quân vua (King).
    """
    def __init__(self, color: str, position: Tuple[int, int]):
        super().__init__(color, position)
        self.value = 0  # Vua không có giá trị vì không thể bị ăn
    
    def get_symbol(self) -> str:
        return "K" if self.color == "white" else "k"
    
    def is_valid_move(self, board, target_position: Tuple[int, int]) -> bool:
        # Kiểm tra vị trí đích có nằm trong bàn cờ không
        if not (0 <= target_position[0] < 8 and 0 <= target_position[1] < 8):
            return False
            
        # Kiểm tra vị trí đích có quân cờ cùng màu không
        target_piece = board.get_piece(target_position)
        if target_piece and target_piece.color == self.color:
            return False
            
        # Kiểm tra khoảng cách di chuyển
        row_diff = abs(target_position[0] - self.position[0])
        col_diff = abs(target_position[1] - self.position[1])
        
        # Di chuyển thông thường
        if row_diff <= 1 and col_diff <= 1:
            # Kiểm tra xem vị trí đích có bị tấn công không
            return not board.is_square_under_attack(target_position, self.color)

        # Nhập thành
        if not self.has_moved and row_diff == 0 and col_diff == 2:
            # Kiểm tra xe có ở đúng vị trí không
            rook_col = 7 if target_position[1] > self.position[1] else 0
            rook = board.get_piece((self.position[0], rook_col))
            if not (isinstance(rook, Rook) and not rook.has_moved):
                return False

            # Kiểm tra có quân cờ nào chặn đường không
            direction = 1 if target_position[1] > self.position[1] else -1
            for col in range(self.position[1] + direction, target_position[1], direction):
                if board.get_piece((self.position[0], col)):
                    return False

            # Kiểm tra vua và các ô đi qua có bị tấn công không
            if board.is_check(self.color):
                return False

            # Kiểm tra các ô vua đi qua có bị tấn công không
            for col in range(self.position[1], target_position[1] + direction, direction):
                if board.is_square_under_attack((self.position[0], col), self.color):
                    return False

            return True
            
        return False