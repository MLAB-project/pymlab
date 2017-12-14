CC = ../../../micropython/mpy-cross/mpy-cross

TARGET = ~/mnt/pyb/pymlab

SENSORS = altimet.py \
		  light.py \
		  sht.py

SRC = sensors/iic.py \
	  sensors/__init__.py \
	  __init__.py \
	  config.py \
	  utils.py

OUTPUT = $(SRC:.py=.mpy) $(addprefix sensors/,$(SENSORS:.py=.mpy))

all: $(OUTPUT)

deploy: $(addprefix $(TARGET)/,$(OUTPUT))

clean:
	@echo RM $(OUTPUT)
	@rm -f $(OUTPUT)

%.mpy: %.py
	@echo CC $<
	@$(CC) $<

$(TARGET)/%.mpy: %.mpy
	@echo CP $<
	@mkdir -p $$(dirname $@)
	@cp $< $@

.PHONY: clean all deploy