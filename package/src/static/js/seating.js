// Seating Configuration
const seatingConfig = {
    rows: 15,
    columns: 12,
    rowLabels: ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O'],
    vipRows: [9, 10, 11], // J, K, L (0-indexed)
    vipColumns: [2, 3, 4, 5, 6, 7, 8, 9], // 3-10 (0-indexed)
    accessibleSeats: [
        {row: 5, col: 0}, {row: 5, col: 1}, // F1, F2
        {row: 5, col: 10}, {row: 5, col: 11} // F11, F12
    ],
    discountRows: [0, 1], // A, B (0-indexed)
    aisleAfterColumn: 5 // Aisle after column 6 (0-indexed)
};

// Pricing
const pricing = {
    normal: 10.00,
    vip: 15.00,
    accessible: 10.00,
    discount: 7.50
};

// Seat Status
let seats = [];
let selectedSeats = [];
let userMode = true; // true for user mode, false for admin mode

// Initialize the seating layout
function initializeSeating() {
    seats = [];
    
    // Create seat data structure
    for (let i = 0; i < seatingConfig.rows; i++) {
        const row = [];
        for (let j = 0; j < seatingConfig.columns; j++) {
            // Determine seat type
            let type = 'normal';
            
            // Check if VIP
            if (seatingConfig.vipRows.includes(i) && seatingConfig.vipColumns.includes(j)) {
                type = 'vip';
            }
            
            // Check if accessible
            const isAccessible = seatingConfig.accessibleSeats.some(seat => 
                seat.row === i && seat.col === j
            );
            if (isAccessible) {
                type = 'accessible';
            }
            
            // Check if discount
            const isDiscount = seatingConfig.discountRows.includes(i);
            
            // Create seat object
            row.push({
                id: `${seatingConfig.rowLabels[i]}${j + 1}`,
                row: i,
                col: j,
                type: type,
                status: 'available',
                isDiscount: isDiscount,
                price: calculatePrice(type, isDiscount)
            });
        }
        seats.push(row);
    }
    
    renderSeating();
    updateStats();
}

// Calculate price based on seat type and discount
function calculatePrice(type, isDiscount) {
    if (isDiscount && type === 'normal') {
        return pricing.discount;
    }
    
    switch (type) {
        case 'vip':
            return pricing.vip;
        case 'accessible':
            return pricing.accessible;
        default:
            return pricing.normal;
    }
}

// Render the seating layout
function renderSeating() {
    const seatingLayout = document.getElementById('seating-layout');
    seatingLayout.innerHTML = '';
    
    for (let i = 0; i < seatingConfig.rows; i++) {
        const rowElement = document.createElement('div');
        rowElement.className = 'row';
        
        // Add row label
        const rowLabel = document.createElement('div');
        rowLabel.className = 'row-label';
        rowLabel.textContent = seatingConfig.rowLabels[i];
        rowElement.appendChild(rowLabel);
        
        for (let j = 0; j < seatingConfig.columns; j++) {
            // Add aisle
            if (j === seatingConfig.aisleAfterColumn) {
                const aisle = document.createElement('div');
                aisle.className = 'aisle';
                rowElement.appendChild(aisle);
            }
            
            const seat = seats[i][j];
            const seatElement = document.createElement('div');
            
            // Set seat classes
            let seatClasses = ['seat', seat.status];
            if (seat.type === 'vip') seatClasses.push('vip');
            if (seat.type === 'accessible') seatClasses.push('accessible');
            
            seatElement.className = seatClasses.join(' ');
            seatElement.textContent = j + 1;
            seatElement.dataset.row = i;
            seatElement.dataset.col = j;
            
            // Add click event
            seatElement.addEventListener('click', () => handleSeatClick(i, j));
            
            rowElement.appendChild(seatElement);
        }
        
        seatingLayout.appendChild(rowElement);
    }
}

// Handle seat click
function handleSeatClick(row, col) {
    const seat = seats[row][col];
    
    // Admin mode - change seat status based on selected option
    if (!userMode) {
        const statusSelect = document.getElementById('seat-status');
        const newStatus = statusSelect.value;
        
        seat.status = newStatus;
        renderSeating();
        updateStats();
        return;
    }
    
    // User mode - handle seat selection
    if (seat.status === 'booked' || seat.status === 'disabled') {
        return; // Can't select booked or disabled seats
    }
    
    // Toggle selection
    if (seat.status === 'selected') {
        seat.status = 'available';
        selectedSeats = selectedSeats.filter(s => !(s.row === row && s.col === col));
    } else {
        seat.status = 'selected';
        selectedSeats.push(seat);
    }
    
    renderSeating();
    updateSelectedSeats();
}

// Update selected seats display
function updateSelectedSeats() {
    const selectedSeatsList = document.getElementById('selected-seats-list');
    const totalPriceElement = document.getElementById('total-price');
    
    if (selectedSeats.length === 0) {
        selectedSeatsList.textContent = 'None';
        totalPriceElement.textContent = '0.00';
        return;
    }
    
    // Sort selected seats by row and column
    selectedSeats.sort((a, b) => {
        if (a.row !== b.row) return a.row - b.row;
        return a.col - b.col;
    });
    
    // Display selected seats
    selectedSeatsList.textContent = selectedSeats.map(seat => seat.id).join(', ');
    
    // Calculate total price
    const totalPrice = selectedSeats.reduce((sum, seat) => sum + seat.price, 0);
    totalPriceElement.textContent = totalPrice.toFixed(2);
}

// Update statistics
function updateStats() {
    const totalSeatsElement = document.getElementById('total-seats');
    const availableSeatsElement = document.getElementById('available-seats');
    const bookedSeatsElement = document.getElementById('booked-seats');
    const occupancyRateElement = document.getElementById('occupancy-rate');
    
    let totalSeats = 0;
    let availableSeats = 0;
    let bookedSeats = 0;
    
    // Count seats by status
    seats.forEach(row => {
        row.forEach(seat => {
            totalSeats++;
            if (seat.status === 'available' || seat.status === 'selected') {
                availableSeats++;
            } else if (seat.status === 'booked') {
                bookedSeats++;
            }
        });
    });
    
    // Update elements
    totalSeatsElement.textContent = totalSeats;
    availableSeatsElement.textContent = availableSeats;
    bookedSeatsElement.textContent = bookedSeats;
    
    // Calculate occupancy rate
    const occupancyRate = (bookedSeats / totalSeats) * 100;
    occupancyRateElement.textContent = `${occupancyRate.toFixed(1)}%`;
}

// Auto-select best seats for a group
function autoSelectBestSeats() {
    // Clear current selection
    selectedSeats.forEach(seat => {
        seats[seat.row][seat.col].status = 'available';
    });
    selectedSeats = [];
    
    const groupSize = parseInt(document.getElementById('group-size').value);
    const seatType = document.getElementById('seat-type').value;
    
    // Find best seats based on group size and seat type
    const bestSeats = findBestSeats(groupSize, seatType);
    
    if (bestSeats.length > 0) {
        // Select the seats
        bestSeats.forEach(seat => {
            const { row, col } = seat;
            seats[row][col].status = 'selected';
            selectedSeats.push(seats[row][col]);
        });
        
        renderSeating();
        updateSelectedSeats();
    } else {
        alert('Could not find suitable seats for your group. Please try a different seat type or group size.');
    }
}

// Find best seats for a group
function findBestSeats(groupSize, seatType) {
    // Priority: middle rows, consecutive seats, centered
    const middleRow = Math.floor(seatingConfig.rows / 2);
    const rowPriority = Array.from({ length: seatingConfig.rows }, (_, i) => 
        Math.abs(middleRow - i)
    ).map((distance, index) => ({ index, distance }))
    .sort((a, b) => a.distance - b.distance)
    .map(item => item.index);
    
    // Check each row for consecutive available seats
    for (const rowIndex of rowPriority) {
        const row = seats[rowIndex];
        
        // Skip if we're looking for specific seat types that don't match this row
        if (seatType === 'vip' && !seatingConfig.vipRows.includes(rowIndex)) continue;
        if (seatType === 'accessible' && !seatingConfig.accessibleSeats.some(seat => seat.row === rowIndex)) continue;
        
        // Find consecutive available seats in this row
        const availableGroups = findConsecutiveAvailableSeats(row, groupSize, seatType);
        
        if (availableGroups.length > 0) {
            // Sort groups by distance from center
            const centerCol = Math.floor(seatingConfig.columns / 2);
            availableGroups.sort((a, b) => {
                const aCenter = a.reduce((sum, seat) => sum + seat.col, 0) / a.length;
                const bCenter = b.reduce((sum, seat) => sum + seat.col, 0) / b.length;
                return Math.abs(aCenter - centerCol) - Math.abs(bCenter - centerCol);
            });
            
            // Return the best group (closest to center)
            return availableGroups[0];
        }
    }
    
    // If no consecutive seats found, try to find any available seats
    if (seatType !== 'any') {
        return findBestSeats(groupSize, 'any');
    }
    
    // If still no seats found, return empty array
    return [];
}

// Find consecutive available seats in a row
function findConsecutiveAvailableSeats(row, groupSize, seatType) {
    const groups = [];
    let currentGroup = [];
    
    // Account for aisle
    const rowWithAisle = [...row];
    rowWithAisle.splice(seatingConfig.aisleAfterColumn + 1, 0, null);
    
    for (let i = 0; i < rowWithAisle.length; i++) {
        const seat = rowWithAisle[i];
        
        // Skip aisle
        if (seat === null) {
            if (currentGroup.length >= groupSize) {
                groups.push([...currentGroup]);
            }
            currentGroup = [];
            continue;
        }
        
        const isAvailable = seat.status === 'available';
        const matchesType = seatType === 'any' || seat.type === seatType;
        
        if (isAvailable && matchesType) {
            currentGroup.push(seat);
        } else {
            if (currentGroup.length >= groupSize) {
                groups.push([...currentGroup]);
            }
            currentGroup = [];
        }
    }
    
    // Check the last group
    if (currentGroup.length >= groupSize) {
        groups.push([...currentGroup]);
    }
    
    // For each group, take exactly the number of seats needed
    return groups.map(group => {
        // If group is larger than needed, take seats from the middle
        if (group.length > groupSize) {
            const startIndex = Math.floor((group.length - groupSize) / 2);
            return group.slice(startIndex, startIndex + groupSize);
        }
        return group;
    });
}

// Confirm booking
function confirmBooking() {
    if (selectedSeats.length === 0) {
        alert('Please select at least one seat.');
        return;
    }
    
    // Change status to booked
    selectedSeats.forEach(seat => {
        seats[seat.row][seat.col].status = 'booked';
    });
    
    selectedSeats = [];
    renderSeating();
    updateSelectedSeats();
    updateStats();
    
    alert('Booking confirmed! Thank you for your purchase.');
}

// Clear selection
function clearSelection() {
    selectedSeats.forEach(seat => {
        seats[seat.row][seat.col].status = 'available';
    });
    
    selectedSeats = [];
    renderSeating();
    updateSelectedSeats();
}

// Reset all seats (admin function)
function resetAllSeats() {
    if (confirm('Are you sure you want to reset all seats to available?')) {
        seats.forEach(row => {
            row.forEach(seat => {
                seat.status = 'available';
            });
        });
        
        selectedSeats = [];
        renderSeating();
        updateSelectedSeats();
        updateStats();
    }
}

// Toggle between user and admin modes
function toggleMode(mode) {
    userMode = mode === 'user';
    
    // Update UI
    document.getElementById('user-mode').classList.toggle('active', userMode);
    document.getElementById('admin-mode').classList.toggle('active', !userMode);
    
    document.querySelector('.booking-form').style.display = userMode ? 'block' : 'none';
    document.querySelector('.admin-panel').style.display = userMode ? 'none' : 'block';
    
    // Clear selection when switching modes
    clearSelection();
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initialize seating
    initializeSeating();
    
    // Mode toggle
    document.getElementById('user-mode').addEventListener('click', () => toggleMode('user'));
    document.getElementById('admin-mode').addEventListener('click', () => toggleMode('admin'));
    
    // Booking form buttons
    document.getElementById('auto-select').addEventListener('click', autoSelectBestSeats);
    document.getElementById('confirm-booking').addEventListener('click', confirmBooking);
    document.getElementById('clear-selection').addEventListener('click', clearSelection);
    
    // Admin panel buttons
    document.getElementById('reset-all').addEventListener('click', resetAllSeats);
    document.getElementById('apply-status').addEventListener('click', () => {
        if (selectedSeats.length === 0) {
            alert('Please select at least one seat to change status.');
            return;
        }
        
        const newStatus = document.getElementById('seat-status').value;
        selectedSeats.forEach(seat => {
            seats[seat.row][seat.col].status = newStatus;
        });
        
        selectedSeats = [];
        renderSeating();
        updateSelectedSeats();
        updateStats();
    });
});
