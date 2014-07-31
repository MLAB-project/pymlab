//
// slave_I2C.c
//
#define F_CPU 16000000UL

#include <avr/io.h>
#include <avr/interrupt.h>
#include <avr/pgmspace.h>
#include <util/delay.h>
#include <stdbool.h>
#include <stdlib.h>
#include <ctype.h>
 
#include "TWI.h"

// settings for I2C
uint8_t I2C_buffer[25];
#define I2C_SLAVE_ADDRESS 0x10
void handle_I2C_interrupt(volatile uint8_t status);
 
// --------------------------------------------------------------------------------------------------------
int main() {
DDRD = 0xFF;
DDRB |= 0x04;
DDRC = 0x00;
PORTC |= 0xFF;

    // Initialize I2C
    TWI_init(   F_CPU,                      // clock frequency
                100000L,                    // desired TWI/IC2 bitrate
                I2C_buffer,                 // pointer to comm buffer
                sizeof(I2C_buffer),         // size of comm buffer
                &handle_I2C_interrupt       // pointer to callback function
                );
 
    // Enable interrupts
    sei();
 
    // give our slave address and enable I2C
    TWI_enable_slave_mode(  I2C_SLAVE_ADDRESS,      // device address of slave
                            0,                      // enable general call
                            &handle_I2C_interrupt   // pointer to callback function
                        );
 
    // received data is processed in the callback
    // nothing else to do here
unsigned long i = 1000000;
    while(true){
	if(i == 0)
	{
	      PORTD ^= 0x40;
		i=1000000;
	}
	i--;
    }
}
// --------------------------------------------------------------------------------------------------------
//
void handle_I2C_interrupt(volatile uint8_t status){
	PORTD ^= 0x20;
    if(status==TWI_success){
	PORTD ^= 0x80;
	PORTB = I2C_buffer[0];
        // increment the integer in the buffer
        // and it will be returned during the read cycle
        //(*(int*)I2C_buffer)++;
    }
} 
