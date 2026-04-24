#include <Stepper.h>

// Define o número de passos por volta do motor (padrão para o 28BYJ-48)
const int stepsPerRevolution = 2048;  

// Inicializa a biblioteca nos pinos digitais 8, 10, 9 e 11
// (A ordem 8, 10, 9, 11 é necessária para o driver ULN2003AN funcionar certinho)
Stepper motor(stepsPerRevolution, 8, 10, 9, 11);

bool motorAtivo = false;

void setup() {
  Serial.begin(9600); // Inicia a comunicação com o Python
  motor.setSpeed(10); // Velocidade bem lenta e relaxante (10 RPM)
}

void loop() {
  // Verifica se o Python enviou alguma mensagem
  if (Serial.available() > 0) {
    char comando = Serial.read();
    
    if (comando == '1') {
      motorAtivo = true;  // Liga o modo relaxamento
    } 
    else if (comando == '0') {
      motorAtivo = false; // Desliga o motor
    }
  }

  // Se o modo estiver ativo, o motor gira suavemente
  if (motorAtivo) {
    motor.step(100); 
  }
}