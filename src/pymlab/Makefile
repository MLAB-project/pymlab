CC = ../../../micropython/mpy-cross/mpy-cross

MOUNTPOINT = ~/mnt/pyb

SENSORS = altimet.py

SRC = sensors/iic.py \
	  sensors/__init__.py \
	  __init__.py \
	  config.py \
	  utils.py

OUTPUT = $(SRC:.py=.mpy) $(addprefix sensors/,$(SENSORS:.py=.mpy))

all: $(OUTPUT)

deploy: $(OUTPUT)
	@mkdir -p $(MOUNTPOINT)/pymlab
	@for f in $(OUTPUT); do \
		echo CP $$f; \
		mkdir -p $(MOUNTPOINT)/pymlab/$$(dirname $$f); \
		cp $$f $(MOUNTPOINT)/pymlab/$$(dirname $$f)/;\
	done;

clean:
	@echo RM $(OUTPUT)
	@rm -f $(OUTPUT)

%.mpy: %.py
	@echo CC $<
	@$(CC) $<

.PHONY clean all deploy