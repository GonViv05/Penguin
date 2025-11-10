#include <iostream>
#include <vector>
#include <stack>
#include <queue>
#include <random>
#include <algorithm>
#include <chrono>
#include <thread>
#include <iomanip>

using namespace std;

// Definición de la estructura Point
struct Point {
    int x, y;
    
    Point() : x(0), y(0) {}
    Point(int _x, int _y) : x(_x), y(_y) {}
    
    bool operator==(const Point& other) const {
        return x == other.x && y == other.y;
    }
    
    bool operator!=(const Point& other) const {
        return !(*this == other);
    }
};

class Maze {
private:
    vector<vector<bool>> maze; // lista de lista de vectores, si tiene un true es una pared, si tiene un false es camino
    int rows, cols;  // dimensiones 
    Point start, end; // el inicio y el finaol del laberinto
    vector<Point> solution; // El camino que almacena el

    const vector<Point> directions = {{-1, 0}, {0, 1}, {1, 0}, {0, -1}}; // izquierda - arriba - derecha - abajo

    // Colores ANSI para la visualización
    const string RED = "\033[31m";
    const string GREEN = "\033[32m";
    const string YELLOW = "\033[33m";
    const string BLUE = "\033[34m";
    const string MAGENTA = "\033[35m";
    const string CYAN = "\033[36m";
    const string RESET = "\033[0m";

public:
    Maze(int r, int c, Point s, Point e) 
        : rows(r), cols(c), start(s), end(e) {
        maze = vector<vector<bool>>(rows, vector<bool>(cols, true));
    }

    void generateMaze() {
        vector<vector<bool>> visited(rows, vector<bool>(cols, false));
        stack<Point> stack;
        
        stack.push(start);
        visited[start.x][start.y] = true;
        maze[start.x][start.y] = false;

        random_device rd;
        mt19937 g(rd());

        while (!stack.empty()) {
            Point current = stack.top();
            vector<Point> neighbors;

            for (const auto& dir : directions) {
                int nx = current.x + dir.x * 2;
                int ny = current.y + dir.y * 2;

                if (isValid(nx, ny) && !visited[nx][ny]) {
                    neighbors.push_back(Point(nx, ny));
                }
            }

            if (!neighbors.empty()) {
                shuffle(neighbors.begin(), neighbors.end(), g);
                Point next = neighbors[0];

                int wallX = current.x + (next.x - current.x) / 2;
                int wallY = current.y + (next.y - current.y) / 2;
                maze[wallX][wallY] = false;

                maze[next.x][next.y] = false;
                visited[next.x][next.y] = true;
                stack.push(next);
            } else {
                stack.pop();
            }
        }

        maze[start.x][start.y] = false;
        maze[end.x][end.y] = false;
    }

    vector<Point> solveBFS(bool visualize = false, int delay_ms = 50) {
        vector<vector<bool>> visited(rows, vector<bool>(cols, false));
        vector<vector<Point>> parent(rows, vector<Point>(cols, Point(-1, -1)));
        queue<Point> q;

        q.push(start);
        visited[start.x][start.y] = true;
        parent[start.x][start.y] = Point(-1, -1);

        if (visualize) {
            clearScreen();
            cout << "=== BFS - BUSQUEDA EN ANCHURA ===" << endl;
            cout << "Explorando nivel por nivel..." << endl << endl;
        }

        int step = 0;
        while (!q.empty()) {
            Point current = q.front();
            q.pop();

            if (visualize) {
                printExploration(visited, current, "BFS", step++);
                this_thread::sleep_for(chrono::milliseconds(delay_ms));
            }

            if (current == end) {
                if (visualize) {
                    cout << YELLOW << "¡Meta encontrada! Reconstruyendo camino..." << RESET << endl;
                    this_thread::sleep_for(chrono::milliseconds(1000));
                }
                solution = reconstructPath(parent);
                return solution;
            }

            for (const auto& dir : directions) {
                int nx = current.x + dir.x;
                int ny = current.y + dir.y;

                if (isValid(nx, ny) && !maze[nx][ny] && !visited[nx][ny]) {
                    visited[nx][ny] = true;
                    parent[nx][ny] = current;
                    q.push(Point(nx, ny));
                }
            }
        }

        return {};
    }

    vector<Point> solveDFS(bool visualize = false, int delay_ms = 100) {
        vector<vector<bool>> visited(rows, vector<bool>(cols, false));
        solution.clear();
        
        if (visualize) {
            clearScreen();
            cout << "=== DFS - BUSQUEDA EN PROFUNDIDAD ===" << endl;
            cout << "Explorando caminos hasta el fondo..." << endl << endl;
        }

        if (dfsRecursive(start.x, start.y, visited, visualize, delay_ms, 0)) {
            return solution;
        }
        
        return {};
    }

private:
    bool dfsRecursive(int x, int y, vector<vector<bool>>& visited, 
                     bool visualize, int delay_ms, int depth) {
        if (!isValid(x, y) || maze[x][y] || visited[x][y]) {
            return false;
        }

        visited[x][y] = true;
        solution.push_back(Point(x, y));

        if (visualize) {
            printExploration(visited, Point(x, y), "DFS", depth);
            this_thread::sleep_for(chrono::milliseconds(delay_ms));
        }

        if (Point(x, y) == end) {
            return true;
        }

        // Mezclar direcciones para exploración aleatoria
        vector<Point> shuffledDirs = directions;
        random_device rd;
        shuffle(shuffledDirs.begin(), shuffledDirs.end(), mt19937(rd()));

        for (const auto& dir : shuffledDirs) {
            int nx = x + dir.x;
            int ny = y + dir.y;
            
            if (dfsRecursive(nx, ny, visited, visualize, delay_ms, depth + 1)) {
                return true;
            }
        }

        // Backtrack - visualizar el retroceso
        if (visualize && !solution.empty()) {
            solution.pop_back();
            printExploration(visited, Point(x, y), "DFS-BACK", depth);
            this_thread::sleep_for(chrono::milliseconds(delay_ms / 2));
        } else {
            solution.pop_back();
        }

        return false;
    }

    void printExploration(const vector<vector<bool>>& visited, 
                         Point current, const string& algorithm, int step) {
        clearScreen();
        
        cout << "=== " << algorithm << " - PASO " << step << " ===" << endl;
        cout << "Posicion actual: (" << current.x << ", " << current.y << ")" << endl;
        cout << "Leyenda: S=Inicio, E=Fin, #=Pared, O=Camino, .=Visitado, @=Actual" << endl << endl;

        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                Point p(i, j);
                
                if (p == start) {
                    cout << GREEN << "S " << RESET;
                } else if (p == end) {
                    cout << RED << "E " << RESET;
                } else if (p == current) {
                    cout << MAGENTA << "@ " << RESET;
                } else if (find(solution.begin(), solution.end(), p) != solution.end()) {
                    cout << YELLOW << "O " << RESET;
                } else if (visited[i][j] && !maze[i][j]) {
                    cout << BLUE << ". " << RESET;
                } else if (maze[i][j]) {
                    cout << "# ";
                } else {
                    cout << "  ";
                }
            }
            cout << endl;
        }
        
        cout << endl << "Presiona Ctrl+C para detener..." << endl;
    }

    vector<Point> reconstructPath(const vector<vector<Point>>& parent) {
        vector<Point> path;
        Point current = end;

        while (current != Point(-1, -1)) {
            path.push_back(current);
            current = parent[current.x][current.y];
        }

        reverse(path.begin(), path.end());
        return path;
    }

    void clearScreen() {
        // Limpiar pantalla
        cout << "\033[2J\033[1;1H";
    }

    bool isValid(int x, int y) {
        return x >= 0 && x < rows && y >= 0 && y < cols;
    }

public:
    void printStatic() const {
        cout << "=== LABERINTO GENERADO ===" << endl;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                if (Point(i, j) == start) cout << GREEN << "S " << RESET;
                else if (Point(i, j) == end) cout << RED << "E " << RESET;
                else cout << (maze[i][j] ? "# " : "  ");
            }
            cout << endl;
        }
    }

    void printFinalSolution() const {
        cout << "=== SOLUCION FINAL ===" << endl;
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                Point p(i, j);
                if (p == start) {
                    cout << GREEN << "S " << RESET;
                } else if (p == end) {
                    cout << RED << "E " << RESET;
                } else if (find(solution.begin(), solution.end(), p) != solution.end()) {
                    cout << YELLOW << "O " << RESET;
                } else if (maze[i][j]) {
                    cout << "# ";
                } else {
                    cout << "  ";
                }
            }
            cout << endl;
        }
    }

    void animateSolution(int delay_ms = 100) {
        if (solution.empty()) {
            cout << "No hay solucion para animar" << endl;
            return;
        }

        clearScreen();
        cout << "=== ANIMACION DEL CAMINO SOLUCION ===" << endl;
        cout << "Presiona Enter para comenzar...";
        cin.ignore();
        cin.get();

        for (size_t i = 0; i < solution.size(); i++) {
            clearScreen();
            cout << "Paso " << i + 1 << " de " << solution.size() << endl;
            
            for (int y = 0; y < rows; y++) {
                for (int x = 0; x < cols; x++) {
                    Point p(y, x);
                    if (p == start) {
                        cout << GREEN << "S " << RESET;
                    } else if (p == end) {
                        cout << RED << "E " << RESET;
                    } else if (p == solution[i]) {
                        cout << MAGENTA << "@ " << RESET;
                    } else if (find(solution.begin(), solution.begin() + i + 1, p) != solution.begin() + i + 1) {
                        cout << YELLOW << "O " << RESET;
                    } else if (maze[y][x]) {
                        cout << "# ";
                    } else {
                        cout << "  ";
                    }
                }
                cout << endl;
            }
            this_thread::sleep_for(chrono::milliseconds(delay_ms));
        }
        
        cout << endl << "Animacion completada. Presiona Enter para continuar...";
        cin.ignore();
        cin.get();
    }
};

// Función principal con menú interactivo
int main() {
    int rows = 15, cols = 15;
    Point start(1, 1);
    Point end(rows - 2, cols - 2);

    Maze maze(rows, cols, start, end);
    
    cout << "Generando laberinto..." << endl;
    maze.generateMaze();
    maze.printStatic();
    
    cout << endl << "¿Que algoritmo quieres visualizar?" << endl;
    cout << "1. BFS (Busqueda en Anchura)" << endl;
    cout << "2. DFS (Busqueda en Profundidad)" << endl;
    cout << "3. Ambos" << endl;
    cout << "Opcion: ";
    
    int option;
    cin >> option;

    if (option == 1 || option == 3) {
        cout << "Iniciando BFS..." << endl;
        this_thread::sleep_for(chrono::milliseconds(1000));
        vector<Point> bfsSolution = maze.solveBFS(true, 80);
        
        if (!bfsSolution.empty()) {
            cout << "BFS completado. Mostrando solucion final..." << endl;
            this_thread::sleep_for(chrono::milliseconds(2000));
            maze.printFinalSolution();
            cout << endl << "Presiona Enter para ver animacion...";
            cin.ignore();
            cin.get();
            maze.animateSolution(100);
        }
    }

    if (option == 2 || option == 3) {
        if (option == 3) {
            cout << "Presiona Enter para continuar con DFS...";
            cin.ignore();
            cin.get();
        }
        
        cout << "Iniciando DFS..." << endl;
        this_thread::sleep_for(chrono::milliseconds(1000));
        vector<Point> dfsSolution = maze.solveDFS(true, 100);
        
        if (!dfsSolution.empty()) {
            cout << "DFS completado. Mostrando solucion final..." << endl;
            this_thread::sleep_for(chrono::milliseconds(2000));
            maze.printFinalSolution();
            cout << endl << "Presiona Enter para ver animacion...";
            cin.ignore();
            cin.get();
            maze.animateSolution(100);
        }
    }
    
    cout << "Programa terminado. Presiona Enter para salir...";
    cin.ignore();
    cin.get();

    return 0;
}