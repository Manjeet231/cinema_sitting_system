import unittest
import sys
import os
import json
from copy import deepcopy

# Add the src directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

# Import the seating module
from routes.seating import find_best_seats_for_group, find_consecutive_available_seats
from models.seating import SeatingModel

class TestSeatingAlgorithm(unittest.TestCase):
    """Test suite for the cinema seating algorithm"""

    def setUp(self):
        """Set up test fixtures before each test method"""
        # Define a test seating configuration
        self.config = {
            "rows": 15,
            "columns": 12,
            "rowLabels": ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O'],
            "vipRows": [9, 10, 11],  # J, K, L (0-indexed)
            "vipColumns": [2, 3, 4, 5, 6, 7, 8, 9],  # 3-10 (0-indexed)
            "accessibleSeats": [
                {"row": 5, "col": 0}, {"row": 5, "col": 1},  # F1, F2
                {"row": 5, "col": 10}, {"row": 5, "col": 11}  # F11, F12
            ],
            "discountRows": [0, 1],  # A, B (0-indexed)
            "aisleAfterColumn": 5  # Aisle after column 6 (0-indexed)
        }
        
        # Create an empty theater with all seats available
        self.seats = []
        for i in range(self.config["rows"]):
            row = []
            for j in range(self.config["columns"]):
                # Determine seat type
                seat_type = 'normal'
                
                # Check if VIP
                if i in self.config["vipRows"] and j in self.config["vipColumns"]:
                    seat_type = 'vip'
                
                # Check if accessible
                is_accessible = any(seat["row"] == i and seat["col"] == j for seat in self.config["accessibleSeats"])
                if is_accessible:
                    seat_type = 'accessible'
                
                # Check if discount
                is_discount = i in self.config["discountRows"]
                
                # Create seat object
                row.append({
                    "id": f"{self.config['rowLabels'][i]}{j + 1}",
                    "row": i,
                    "col": j,
                    "type": seat_type,
                    "status": "available",
                    "isDiscount": is_discount,
                    "price": SeatingModel.calculate_price(seat_type, is_discount)
                })
            self.seats.append(row)

    def test_find_best_seats_for_small_group(self):
        """Test finding best seats for a small group (2 people)"""
        # Find best seats for a group of 2
        best_seats = find_best_seats_for_group(self.seats, self.config, 2, "any")
        
        # Verify that 2 seats were found
        self.assertEqual(len(best_seats), 2, "Should find exactly 2 seats")
        
        # Verify that seats are in the same row
        self.assertEqual(best_seats[0]["row"], best_seats[1]["row"], "Seats should be in the same row")
        
        # Verify that seats are adjacent
        self.assertEqual(best_seats[0]["col"] + 1, best_seats[1]["col"], "Seats should be adjacent")
        
        # Verify that seats are in a middle row (close to row H)
        middle_row = self.config["rows"] // 2  # Row H (7) in 0-indexed
        self.assertTrue(abs(best_seats[0]["row"] - middle_row) <= 2, 
                        "Seats should be in or close to middle rows")

    def test_find_best_seats_for_large_group(self):
        """Test finding best seats for a large group (7 people)"""
        # Find best seats for a group of 7
        best_seats = find_best_seats_for_group(self.seats, self.config, 7, "any")
        
        # Verify that 7 seats were found
        self.assertEqual(len(best_seats), 7, "Should find exactly 7 seats")
        
        # Verify that seats are in the same row
        first_row = best_seats[0]["row"]
        for seat in best_seats:
            self.assertEqual(seat["row"], first_row, "All seats should be in the same row")
        
        # Verify that seats are consecutive (accounting for aisle)
        sorted_seats = sorted(best_seats, key=lambda s: s["col"])
        for i in range(1, len(sorted_seats)):
            diff = sorted_seats[i]["col"] - sorted_seats[i-1]["col"]
            # Either adjacent or separated by aisle
            self.assertTrue(diff == 1 or (sorted_seats[i-1]["col"] == 5 and sorted_seats[i]["col"] == 6),
                           f"Seats should be consecutive, found gap of {diff} columns")

    def test_find_vip_seats(self):
        """Test finding VIP seats"""
        # Find best VIP seats for a group of 4
        best_seats = find_best_seats_for_group(self.seats, self.config, 4, "vip")
        
        # Verify that 4 seats were found
        self.assertEqual(len(best_seats), 4, "Should find exactly 4 seats")
        
        # Verify that all seats are VIP
        for seat in best_seats:
            self.assertEqual(seat["type"], "vip", "All seats should be VIP")
            
        # Verify that seats are in VIP rows
        for seat in best_seats:
            self.assertTrue(seat["row"] in self.config["vipRows"], 
                           f"Seat should be in VIP rows, found row {seat['row']}")
            
        # Verify that seats are in VIP columns
        for seat in best_seats:
            self.assertTrue(seat["col"] in self.config["vipColumns"], 
                           f"Seat should be in VIP columns, found column {seat['col']}")

    def test_find_accessible_seats(self):
        """Test finding accessible seats"""
        # Find best accessible seats for a group of 2
        best_seats = find_best_seats_for_group(self.seats, self.config, 2, "accessible")
        
        # Verify that 2 seats were found
        self.assertEqual(len(best_seats), 2, "Should find exactly 2 seats")
        
        # Verify that all seats are accessible
        for seat in best_seats:
            self.assertEqual(seat["type"], "accessible", "All seats should be accessible")
            
        # Verify that seats are in accessible positions
        accessible_positions = [(seat["row"], seat["col"]) for seat in self.config["accessibleSeats"]]
        for seat in best_seats:
            self.assertTrue((seat["row"], seat["col"]) in accessible_positions, 
                           f"Seat should be in accessible positions, found {seat['row']}, {seat['col']}")

    def test_no_single_seat_gaps(self):
        """Test that the algorithm prevents single seat gaps"""
        # Book some seats to create a potential gap scenario
        # Book seats in row H (middle row), columns 3-5
        middle_row = self.config["rows"] // 2  # Row H (7) in 0-indexed
        for j in range(3, 6):
            self.seats[middle_row][j]["status"] = "booked"
            
        # Book seats in row H, columns 7-9
        for j in range(7, 10):
            self.seats[middle_row][j]["status"] = "booked"
            
        # This leaves column 6 open, which would create a single-seat gap
        # Verify that the validation would detect this
        would_create_gap, gap_col = SeatingModel.would_create_single_gap(
            self.seats, middle_row, [{"row": middle_row, "col": 2}])
        
        self.assertTrue(would_create_gap, "Should detect potential single-seat gap")
        self.assertEqual(gap_col, 6, "Gap should be detected at column 6")
        
        # Test that the algorithm won't recommend seats that create single gaps
        # Find best seats for a group of 2 in row H
        # The algorithm should avoid creating a situation where column 6 is isolated
        best_seats = find_consecutive_available_seats(self.seats[middle_row], self.config, 2, "any")
        
        # Check if any of the recommended seat groups would create a single gap
        for group in best_seats:
            # Create a temporary booking
            temp_seats = deepcopy(self.seats)
            for seat in group:
                row = seat["row"]
                col = seat["col"]
                temp_seats[row][col]["status"] = "booked"
                
            # Check if this creates a single gap
            would_create_gap, _ = SeatingModel.would_create_single_gap(
                temp_seats, middle_row, group)
            
            self.assertFalse(would_create_gap, 
                            "Algorithm should not recommend seats that create single gaps")

    def test_center_preference(self):
        """Test that the algorithm prefers center seats"""
        # Find best seats for a group of 4
        best_seats = find_best_seats_for_group(self.seats, self.config, 4, "any")
        
        # Calculate the average column position
        avg_col = sum(seat["col"] for seat in best_seats) / len(best_seats)
        
        # Center column should be around 5.5 (between columns 5 and 6)
        center_col = (self.config["columns"] - 1) / 2  # 5.5 for 12 columns
        
        # Verify that the average column is close to the center
        self.assertTrue(abs(avg_col - center_col) <= 2, 
                       f"Seats should be centered, average column was {avg_col}")

    def test_row_priority(self):
        """Test that the algorithm prioritizes middle rows"""
        # Book all seats in the middle row (H)
        middle_row = self.config["rows"] // 2  # Row H (7) in 0-indexed
        for j in range(self.config["columns"]):
            self.seats[middle_row][j]["status"] = "booked"
            
        # Find best seats for a group of 4
        best_seats = find_best_seats_for_group(self.seats, self.config, 4, "any")
        
        # Verify that seats are in rows adjacent to the middle (G or I)
        for seat in best_seats:
            self.assertTrue(seat["row"] == middle_row - 1 or seat["row"] == middle_row + 1,
                           f"Seats should be in rows adjacent to middle, found row {seat['row']}")

    def test_fallback_to_any_seats(self):
        """Test that the algorithm falls back to any available seats when specific type is unavailable"""
        # Book all VIP seats
        for i in self.config["vipRows"]:
            for j in self.config["vipColumns"]:
                self.seats[i][j]["status"] = "booked"
                
        # Try to find VIP seats for a group of 2
        best_seats = find_best_seats_for_group(self.seats, self.config, 2, "vip")
        
        # Verify that seats were found (fallback to any available)
        self.assertTrue(len(best_seats) > 0, "Should find seats even when VIP is unavailable")
        
        # Verify that seats are not VIP (since all VIP are booked)
        for seat in best_seats:
            self.assertNotEqual(seat["type"], "vip", "Seats should not be VIP")

    def test_near_capacity_scenario(self):
        """Test the algorithm's behavior in a near-capacity scenario"""
        # Book most seats, leaving only scattered seats
        for i in range(self.config["rows"]):
            for j in range(self.config["columns"]):
                # Leave only one seat available in each row
                if j != 3:  # Leave column 3 available
                    self.seats[i][j]["status"] = "booked"
        
        # Try to find seats for a group of 2
        best_seats = find_best_seats_for_group(self.seats, self.config, 2, "any")
        
        # In this scenario, it's impossible to seat 2 people together
        # The algorithm should return an empty list
        self.assertEqual(len(best_seats), 0, 
                        "Should return empty list when unable to seat group together")
        
        # Try to find seats for a group of 1
        best_seats = find_best_seats_for_group(self.seats, self.config, 1, "any")
        
        # Verify that a single seat was found
        self.assertEqual(len(best_seats), 1, "Should find exactly 1 seat")
        
        # Verify that the seat is in column 3 (the only available column)
        self.assertEqual(best_seats[0]["col"], 3, "Seat should be in column 3")

    def test_validation_of_seat_selection(self):
        """Test validation of seat selection"""
        # Select a group of 3 adjacent seats
        middle_row = self.config["rows"] // 2  # Row H (7) in 0-indexed
        selected_seats = [
            {"row": middle_row, "col": 4},
            {"row": middle_row, "col": 5},
            {"row": middle_row, "col": 6}
        ]
        
        # Validate the selection
        is_valid, message = SeatingModel.validate_seat_selection(self.seats, selected_seats)
        
        # Verify that the selection is valid
        self.assertTrue(is_valid, f"Selection should be valid, got: {message}")
        
        # Test invalid selection: non-adjacent seats
        invalid_seats = [
            {"row": middle_row, "col": 2},
            {"row": middle_row, "col": 4},
            {"row": middle_row, "col": 6}
        ]
        
        # Validate the invalid selection
        is_valid, message = SeatingModel.validate_seat_selection(self.seats, invalid_seats)
        
        # Verify that the selection is invalid
        self.assertFalse(is_valid, "Non-adjacent seats should be invalid")
        
        # Test invalid selection: seats in different rows
        invalid_seats = [
            {"row": middle_row, "col": 4},
            {"row": middle_row + 1, "col": 4}
        ]
        
        # Validate the invalid selection
        is_valid, message = SeatingModel.validate_seat_selection(self.seats, invalid_seats)
        
        # Verify that the selection is invalid
        self.assertFalse(is_valid, "Seats in different rows should be invalid for groups")

if __name__ == '__main__':
    unittest.main()
