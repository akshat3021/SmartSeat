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
vector<Student> students;
vector<vector<string>> roomMap; // Stores which branch is in which seat

// --- CHECKING FOR CONFLICTS ---
// This function checks if it's safe to place a student of 'branch' at (r, c)
bool isSafe(int r, int c, string branch) {
    // Check Top
    if (r > 0 && roomMap[r - 1][c] == branch) return false;
    // Check Bottom
    if (r < ROWS - 1 && roomMap[r + 1][c] == branch) return false;
    // Check Left
    if (c > 0 && roomMap[r][c - 1] == branch) return false;
    // Check Right
    if (c < COLS - 1 && roomMap[r][c + 1] == branch) return false;

    // STRICT MODE: Check Diagonals (Optional - currently enabled)
    if (r > 0 && c > 0 && roomMap[r - 1][c - 1] == branch) return false; // Top-Left
    if (r > 0 && c < COLS - 1 && roomMap[r - 1][c + 1] == branch) return false; // Top-Right

    return true;
}

// --- THE BACKTRACKING ALGORITHM (The Brain) ---
bool solve(int studentIdx) {
    // Base Case: If we have placed all students, we are done!
    if (studentIdx == students.size()) {
        return true;
    }

    string currentBranch = students[studentIdx].branch;

    // Try to find a seat for this student
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

    // 2. READ ROOM DIMENSIONS
    inFile >> ROWS >> COLS;
    
    // Initialize the room map with "EMPTY"
    roomMap.resize(ROWS, vector<string>(COLS, "EMPTY"));

    // 3. READ STUDENTS
    int id;
    string branch;
    while (inFile >> id >> branch) {
        students.push_back({id, branch});
    }
    inFile.close();

    // 4. RUN THE ALGORITHM
    if (solve(0)) {
        // 5. WRITE OUTPUT FILE (For Python to read)
        ofstream outFile("output.txt");
        for (const auto& s : students) {
            outFile << s.id << " " << s.branch << " " << s.row << " " << s.col << endl;
        }
        outFile.close();
        cout << "Success: Arrangement Generated." << endl;
    } else {
        cout << "Failure: Cannot fit students strictly." << endl;
    }

    return 0;
}