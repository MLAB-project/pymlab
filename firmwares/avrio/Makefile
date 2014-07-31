twi.hex: slave_I2C.hex
	cp slave_I2C.hex twi.hex
slave_I2C.hex: slave_I2C.elf
	avr-objcopy -R .eeprom -O ihex slave_I2C.elf slave_I2C.hex
slave_I2C.elf: slave_I2C.o TWI.o
	avr-gcc -g -Os -mmcu=atmega8 slave_I2C.o TWI.o -o slave_I2C.elf
slave_I2C.o: slave_I2C.c
	avr-gcc -g -c -Os -mmcu=atmega8 slave_I2C.c -o slave_I2C.o
TWI.o: TWI.c
	avr-gcc -g -c -Os -mmcu=atmega8 TWI.c -o TWI.o
