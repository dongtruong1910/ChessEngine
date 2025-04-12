from typing import Tuple, List, Optional
from Model.board import Board
from Model.piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King

class ChessAI:
    def __init__(self, color: str, depth: int = 3):
        self.color = color  # Màu quân của AI
        self.depth = depth  # Độ sâu tìm kiếm
        
        # Giá trị của từng loại quân
        self.piece_values = {
            Pawn: 100,    # Tốt
            Knight: 320,  # Mã
            Bishop: 330,  # Tượng
            Rook: 500,    # Xe
            Queen: 900,   # Hậu
            King: 20000   # Vua
        }
        
        # Bảng giá trị vị trí cho từng loại quân
        self.position_values = {
            Pawn: [  # Bảng giá trị vị trí cho quân tốt
                [0,  0,  0,  0,  0,  0,  0,  0],
                [50, 50, 50, 50, 50, 50, 50, 50],
                [10, 10, 20, 30, 30, 20, 10, 10],
                [5,  5, 10, 25, 25, 10,  5,  5],
                [0,  0,  0, 20, 20,  0,  0,  0],
                [5, -5,-10,  0,  0,-10, -5,  5],
                [5, 10, 10,-20,-20, 10, 10,  5],
                [0,  0,  0,  0,  0,  0,  0,  0]
            ],
            Knight: [  # Bảng giá trị vị trí cho quân mã
                [-50,-40,-30,-30,-30,-30,-40,-50],
                [-40,-20,  0,  0,  0,  0,-20,-40],
                [-30,  0, 10, 15, 15, 10,  0,-30],
                [-30,  5, 15, 20, 20, 15,  5,-30],
                [-30,  0, 15, 20, 20, 15,  0,-30],
                [-30,  5, 10, 15, 15, 10,  5,-30],
                [-40,-20,  0,  5,  5,  0,-20,-40],
                [-50,-40,-30,-30,-30,-30,-40,-50]
            ],
            Bishop: [  # Bảng giá trị vị trí cho quân tượng
                [-20,-10,-10,-10,-10,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5, 10, 10,  5,  0,-10],
                [-10,  5,  5, 10, 10,  5,  5,-10],
                [-10,  0, 10, 10, 10, 10,  0,-10],
                [-10, 10, 10, 10, 10, 10, 10,-10],
                [-10,  5,  0,  0,  0,  0,  5,-10],
                [-20,-10,-10,-10,-10,-10,-10,-20]
            ],
            Rook: [  # Bảng giá trị vị trí cho quân xe
                [0,  0,  0,  0,  0,  0,  0,  0],
                [5, 10, 10, 10, 10, 10, 10,  5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [-5,  0,  0,  0,  0,  0,  0, -5],
                [0,  0,  0,  5,  5,  0,  0,  0]
            ],
            Queen: [  # Bảng giá trị vị trí cho quân hậu
                [-20,-10,-10, -5, -5,-10,-10,-20],
                [-10,  0,  0,  0,  0,  0,  0,-10],
                [-10,  0,  5,  5,  5,  5,  0,-10],
                [-5,  0,  5,  5,  5,  5,  0, -5],
                [0,  0,  5,  5,  5,  5,  0, -5],
                [-10,  5,  5,  5,  5,  5,  0,-10],
                [-10,  0,  5,  0,  0,  0,  0,-10],
                [-20,-10,-10, -5, -5,-10,-10,-20]
            ],
            King: [  # Bảng giá trị vị trí cho quân vua
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-30,-40,-40,-50,-50,-40,-40,-30],
                [-20,-30,-30,-40,-40,-30,-30,-20],
                [-10,-20,-20,-20,-20,-20,-20,-10],
                [20, 20,  0,  0,  0,  0, 20, 20],
                [20, 30, 10,  0,  0, 10, 30, 20]
            ]
        }

    def evaluate_board(self, board: Board) -> int:
        """
        Đánh giá thế cờ hiện tại.
        Giá trị dương nghĩa là bên trắng có lợi thế, âm là bên đen có lợi thế.
        """
        score = 0
        
        # Duyệt qua tất cả các ô trên bàn cờ
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece:
                    # Lấy giá trị cơ bản của quân cờ
                    piece_value = self.piece_values[type(piece)]
                    
                    # Lấy giá trị vị trí của quân cờ
                    position_value = self.position_values[type(piece)][row][col]
                    if piece.color == "black":
                        # Đảo ngược bảng giá trị vị trí cho quân đen
                        position_value = self.position_values[type(piece)][7-row][col]
                    
                    # Tính tổng giá trị
                    value = piece_value + position_value
                    
                    # Cộng hoặc trừ vào tổng điểm tùy theo màu quân
                    if piece.color == "white":
                        score += value
                    else:
                        score -= value
                        
        # Điều chỉnh điểm theo góc nhìn của AI
        return score if self.color == "white" else -score

    def minimax(self, board: Board, depth: int, is_maximizing: bool) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Thuật toán minimax cơ bản.
        Trả về (điểm đánh giá, nước đi tốt nhất)
        """
        if depth == 0:
            return self.evaluate_board(board), None
            
        # TODO: Thêm logic kiểm tra chiếu tướng, hết cờ
        
        best_move = None
        if is_maximizing:
            max_eval = float('-inf')
            # Duyệt qua tất cả các nước đi có thể
            for move in self.get_all_possible_moves(board, self.color):
                # Thử nước đi
                board.move_piece(move[0], move[1])
                eval = self.minimax(board, depth - 1, False)[0]
                # Hoàn tác nước đi
                board.undo_move()
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
            return max_eval, best_move
        else:
            min_eval = float('inf')
            opponent_color = "black" if self.color == "white" else "white"
            # Duyệt qua tất cả các nước đi có thể
            for move in self.get_all_possible_moves(board, opponent_color):
                # Thử nước đi
                board.move_piece(move[0], move[1])
                eval = self.minimax(board, depth - 1, True)[0]
                # Hoàn tác nước đi
                board.undo_move()
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
            return min_eval, best_move

    def alpha_beta(self, board: Board, depth: int, alpha: float, beta: float, 
                  is_maximizing: bool) -> Tuple[int, Optional[Tuple[Tuple[int, int], Tuple[int, int]]]]:
        """
        Thuật toán alpha-beta pruning.
        Trả về (điểm đánh giá, nước đi tốt nhất)
        """
        if depth == 0:
            return self.evaluate_board(board), None
            
        # TODO: Thêm logic kiểm tra chiếu tướng, hết cờ
        
        best_move = None
        if is_maximizing:
            max_eval = float('-inf')
            # Duyệt qua tất cả các nước đi có thể
            for move in self.get_all_possible_moves(board, self.color):
                # Thử nước đi
                board.move_piece(move[0], move[1])
                eval = self.alpha_beta(board, depth - 1, alpha, beta, False)[0]
                # Hoàn tác nước đi
                board.undo_move()
                
                if eval > max_eval:
                    max_eval = eval
                    best_move = move
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # Cắt tỉa beta
            return max_eval, best_move
        else:
            min_eval = float('inf')
            opponent_color = "black" if self.color == "white" else "white"
            # Duyệt qua tất cả các nước đi có thể
            for move in self.get_all_possible_moves(board, opponent_color):
                # Thử nước đi
                board.move_piece(move[0], move[1])
                eval = self.alpha_beta(board, depth - 1, alpha, beta, True)[0]
                # Hoàn tác nước đi
                board.undo_move()
                
                if eval < min_eval:
                    min_eval = eval
                    best_move = move
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # Cắt tỉa alpha
            return min_eval, best_move

    def get_best_move(self, board: Board, use_alpha_beta: bool = True) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Tìm nước đi tốt nhất cho AI sử dụng minimax hoặc alpha-beta
        """
        if use_alpha_beta:
            _, best_move = self.alpha_beta(board, self.depth, float('-inf'), float('inf'), True)
        else:
            _, best_move = self.minimax(board, self.depth, True)
        return best_move

    def get_all_possible_moves(self, board: Board, color: str) -> List[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Lấy tất cả các nước đi có thể cho một bên
        """
        moves = []
        for row in range(8):
            for col in range(8):
                piece = board.get_piece((row, col))
                if piece and piece.color == color:
                    valid_moves = board.get_valid_moves((row, col))
                    for move in valid_moves:
                        moves.append(((row, col), move))
        return moves
