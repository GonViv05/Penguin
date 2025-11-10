#include <iostream>
#include <cmath>
#include <cstring>
#include <cstdio>

// --- Declaración anticipada (Prototipo) ---
// Esto le dice al compilador que la función existe, ya sea la versión de Windows o la de Unix.
void usleep(__int64 usec);

// Bloque de manejo de usleep
#ifdef _WIN32 // Si estamos en Windows
#include <windows.h>

void usleep(__int64 usec){
	HANDLE timer;
	// Corregido: LARGE_INREGER -> LARGE_INTEGER
	LARGE_INTEGER ft; 
	
	ft.QuadPart = -(10 * usec);
	
	timer = CreateWaitableTimer(NULL, TRUE, NULL);
	SetWaitableTimer(timer, &ft, 0, NULL, NULL, 0);
	WaitForSingleObject(timer, INFINITE);
	CloseHandle(timer);
}

#else // Si NO estamos en Windows (Unix/Linux/macOS)
#include <unistd.h>

// En Unix/Linux/macOS, usleep ya está declarado en <unistd.h>
void usleep(__int64 usec) {
    ::usleep(usec); // Llama a la función del sistema, asegurando que el prototipo coincida.
}

#endif 

// Variables Globales
float A = 0.0f, B = 0.0f, C = 0.0f;
float cubeWidth = 20.0f; 
int width = 160, height = 44; 
float zBuffer[160 * 44];
char buffer[160 * 44]; // Corregido: Faltaba el punto y coma
int backgroundASCIICode = '.';
int distanceFromCam = 100;
float horizontalOffset;
float K1 = 40; 

float incrementSpeed = 0.5f;

float x, y, z;
float ooz;
int xp, yp;
int idx;

float calculateX(float i, float j, float k){
	return j * sin(A) * sin(B) * cos(C) - k * cos(A) * sin(B) * cos(C) + j * cos(A) * sin(C) + k * sin(A) * sin(C) + i * cos(B) * cos(C); 
}

float calculateY(float i, float j, float k){
	// Fórmula corregida
	return j * cos(A) * cos(C) + k * sin(A) * cos(C) - j * sin(A) * sin(B) * sin(C) + k * cos(A) * sin(B) * sin(C) - i * cos(B) * sin(C);
}

float calculateZ(float i, float j, float k){
	return k * cos(A) * cos(B) - j * sin(A) * cos(B) + i * sin(B);
}

void calculateForSurface(float cubeX, float cubeY, float cubeZ, int ch){
	x = calculateX(cubeX, cubeY, cubeZ);
	y = calculateY(cubeX, cubeY, cubeZ);
	z = calculateZ(cubeX, cubeY, cubeZ) + distanceFromCam; 
	
	if (z == 0) return;
	
	ooz = 1.0f / z;
	
	xp = (int)(width / 2 + horizontalOffset + K1 * ooz * x * 2);
	yp = (int)(height / 2 + K1 * ooz * y);
	
	idx = xp + yp * width;
	

	if (idx >= 0 && idx < width * height && ooz > zBuffer[idx]) {
		zBuffer[idx] = ooz; 
		buffer[idx] = ch; 
	}
}

int main(){

	std::cout << "\x1b[2J"; 
	
	while (1) {
		// Corregido: 'zbuffer' a 'zBuffer'
		std::memset(buffer, backgroundASCIICode, width * height);
		std::memset(zBuffer, 0, width * height * sizeof(float)); 
		
		horizontalOffset = -2 * cubeWidth;
		
		// Itera sobre las superficies del cubo
		for (float cubeX = -cubeWidth; cubeX <= cubeWidth; cubeX += incrementSpeed){
			for(float cubeY = -cubeWidth; cubeY <= cubeWidth; cubeY += incrementSpeed){
				
				calculateForSurface(cubeX, cubeY, -cubeWidth, '@');
				
				calculateForSurface(cubeWidth, cubeY, cubeX, '$');
				
				calculateForSurface(-cubeWidth, cubeY, -cubeX, '~');
				
				calculateForSurface(-cubeX, cubeY, cubeWidth, '#');
				
				calculateForSurface(cubeX, -cubeWidth, -cubeY, '!');
			
				calculateForSurface(cubeX, cubeWidth, -cubeY, '+');
			}
		}
		
		// Mueve el cursor a la esquina superior izquierda
		std::cout << "\x1b[H";
		for (int k = 0; k < width * height; k++) {
			std::putchar(k % width ? buffer[k] : '\n'); 
		}
		
		// Incremento de los ángulos de rotación
		A += 0.05f;
		B += 0.05f;
		C += 0.01f;
		
		usleep(5000 * 2);
	}
	
	return 0; 
}






