#include <iostream>
#include <fstream>
#include <vector>
#include <string>
#include <sstream>

using namespace std;

// --- STRUCTURES ---
struct Student {
    int id;
    string branch;
    int row = -1;
    int col = -1;
};

// --- GLOBAL VARIABLES ---
int ROWS, COLS;
int STRICT_MODE = 0; // 0 = Normal (4 directions), 1 = Strict (8 directions + diagonals)
vector<Student> students;
vector<vector<string> > roomMap; // Stores which branch is in which seat

// --- CHECKING FOR CONFLICTS ---
// This function checks if it's safe to place a student of 'branch' at (r, c)
// NORMAL MODE  (STRICT_MODE=0): checks 4 neighbours (Top, Bottom, Left, Right)
// STRICT MODE  (STRICT_MODE=1): checks all 8 neighbours (4 sides + 4 diagonals)
bool isSafe(int r, int c, string branch) {
<<<<<<< HEAD
    // Check Top
    if (r > 0 && roomMap[r - 1][c] == branch) return false; 
    // Check Bottom
    if (r < ROWS - 1 && roomMap[r + 1][c] == branch) return false;
    // Check Left
    if (c > 0 && roomMap[r][c - 1] == branch) return false;
    // Check Right
    if (c < COLS - 1 && roomMap[r][c + 1] == branch) return false;
=======
    // Always check 4 cardinal directions
    if (r > 0          && roomMap[r - 1][c] == branch) return false; // Top
    if (r < ROWS - 1   && roomMap[r + 1][c] == branch) return false; // Bottom
    if (c > 0          && roomMap[r][c - 1] == branch) return false; // Left
    if (c < COLS - 1   && roomMap[r][c + 1] == branch) return false; // Right
>>>>>>> 9137a56 (Login / Authentication System Implimented)

    // Only check diagonals in STRICT MODE
    if (STRICT_MODE == 1) {
        if (r > 0        && c > 0        && roomMap[r-1][c-1] == branch) return false; // Top-Left
        if (r > 0        && c < COLS - 1 && roomMap[r-1][c+1] == branch) return false; // Top-Right
        if (r < ROWS - 1 && c > 0        && roomMap[r+1][c-1] == branch) return false; // Bottom-Left
        if (r < ROWS - 1 && c < COLS - 1 && roomMap[r+1][c+1] == branch) return false; // Bottom-Right
    }

    return true;
}

// --- THE BACKTRACKING ALGORITHM (The Brain) ---
bool solve(int studentIdx) {
    // Base Case: If we have placed all students, we are done!
    if (studentIdx == (int)students.size()) {
        return true;
    }

    string currentBranch = students[studentIdx].branch;

    // Try to find a seat for this student
    // At starting [empty(0,0) , empty , ...., empty]
    //             .   .   .   .   .   .    .    .
    //             [empty , empty , ...., empty(R-1,C-1)]
    for (int i = 0; i < ROWS; i++) {
        for (int j = 0; j < COLS; j++) {
            
            // If seat is empty AND it is safe (no cheating possible)
            if (roomMap[i][j] == "EMPTY" && isSafe(i, j, currentBranch)) {
                
                // 1. PLACE THE STUDENT
                roomMap[i][j] = currentBranch;
                students[studentIdx].row = i;
                students[studentIdx].col = j;

                // 2. RECURSE (Try to place the NEXT student)
                if (solve(studentIdx + 1)) {
                    return true; // Success!
                }

                // 3. BACKTRACK (If it didn't work, remove student and try next seat)
                roomMap[i][j] = "EMPTY";
                students[studentIdx].row = -1;
                students[studentIdx].col = -1;
            }
        }
    }

    return false; // Could not place this student anywhere
}

// --- MAIN FUNCTION ---
int main() {

    // 1. OPEN INPUT FILE (Sent by Python)
    ifstream inFile("input.txt");
    if (!inFile) {
        cerr << "Error: Cannot open input.txt" << endl;
        return 1;
    }

    // 2. READ ROOM DIMENSIONS + MODE
    // input.txt line 1 format:  ROWS COLS MODE
    // MODE: 0 = Normal (4 directions), 1 = Strict (8 directions)
    inFile >> ROWS >> COLS >> STRICT_MODE;
    
    // Initialize the room map with "EMPTY"
    roomMap.resize(ROWS, vector<string>(COLS, "EMPTY"));

    // 3. READ STUDENTS
    int id;
    string branch;
    while (inFile >> id >> branch) {
        Student s;
        s.id = id;
        s.branch = branch;
        s.row = -1;
        s.col = -1;
        students.push_back(s);
    }
    inFile.close();

    // 4. RUN THE ALGORITHM
    if (solve(0)) {
        // 5. WRITE OUTPUT FILE (For Python to read)
        ofstream outFile("output.txt");
        for (int i = 0; i < (int)students.size(); i++) {
            outFile << students[i].id << " " << students[i].branch << " " << students[i].row << " " << students[i].col << endl;
        }
        outFile.close();
        cout << "Success: Arrangement Generated. Mode=" << STRICT_MODE << endl;
    } else {
        cout << "Failure: Cannot fit students strictly." << endl;
    }

    return 0;
}