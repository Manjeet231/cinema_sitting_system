class SeatingModel:
    """Model for seating data"""
    
    @staticmethod
    def calculate_price(seat_type, is_discount):
        """Calculate price based on seat type and discount"""
        pricing = {
            "normal": 10.00,
            "vip": 15.00,
            "accessible": 10.00,
            "discount": 7.50
        }
        
        if is_discount and seat_type == 'normal':
            return pricing["discount"]
        
        return pricing.get(seat_type, pricing["normal"])
    
    @staticmethod
    def validate_seat_selection(seats, selected_seats):
        """Validate seat selection for booking"""
        # Check if all selected seats are available
        for seat in selected_seats:
            row = seat.get("row")
            col = seat.get("col")
            
            if row is None or col is None:
                return False, "Invalid seat selection"
            
            if row < 0 or row >= len(seats) or col < 0 or col >= len(seats[0]):
                return False, "Seat out of range"
            
            if seats[row][col]["status"] != "available":
                return False, "One or more selected seats are not available"
        
        # Check if selected seats are adjacent (for groups)
        if len(selected_seats) > 1:
            # Sort by row and column
            sorted_seats = sorted(selected_seats, key=lambda s: (s["row"], s["col"]))
            
            # Check if all seats are in the same row
            first_row = sorted_seats[0]["row"]
            if not all(seat["row"] == first_row for seat in sorted_seats):
                return False, "Group seats must be in the same row"
            
            # Check if seats are consecutive
            for i in range(1, len(sorted_seats)):
                if sorted_seats[i]["col"] != sorted_seats[i-1]["col"] + 1:
                    # Check if there's an aisle between them (column 5 and 6)
                    if not (sorted_seats[i-1]["col"] == 5 and sorted_seats[i]["col"] == 6):
                        return False, "Group seats must be adjacent"
        
        return True, "Valid selection"
    
    @staticmethod
    def would_create_single_gap(seats, row_index, selected_seats):
        """Check if booking would create a single seat gap"""
        # Get all columns in this row
        row = seats[row_index]
        
        # Create a temporary status array for this row
        status_array = [seat["status"] for seat in row]
        
        # Mark selected seats as booked
        for seat in selected_seats:
            if seat["row"] == row_index:
                status_array[seat["col"]] = "booked"
        
        # Check for single seat gaps
        for i in range(1, len(status_array) - 1):
            # Skip the aisle
            if i == 5:
                continue
                
            # Check if this creates a single available seat between booked seats
            if (status_array[i] == "available" and 
                status_array[i-1] in ["booked", "disabled"] and 
                status_array[i+1] in ["booked", "disabled"]):
                return True, i
        
        return False, -1
