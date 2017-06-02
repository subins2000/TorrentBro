# Build resources into python files

###### EDIT #####################
#Directory with ui and resource files
RESOURCE_DIR = resources

#Directory for compiled resources
COMPILED_DIR = ui

#UI files to compile
UI_FILES = Home.ui
#Qt resource files to compile
RESOURCES =

#pyuic4 and pyrcc4 binaries
PYUIC = pyuic5
PYRCC = pyrcc5

#################################
# DO NOT EDIT FOLLOWING

COMPILED_UI = $(UI_FILES:%.ui=$(COMPILED_DIR)/ui_%.py)
COMPILED_RESOURCES = $(RESOURCES:%.qrc=$(COMPILED_DIR)/%_rc.py)

all : resources ui

resources : $(COMPILED_RESOURCES)

ui : $(COMPILED_UI)

$(COMPILED_DIR)/ui_%.py : $(RESOURCE_DIR)/%.ui
	$(PYUIC) $< -o $@

$(COMPILED_DIR)/%_rc.py : $(RESOURCE_DIR)/%.qrc
	$(PYRCC) $< -o $@

clean :
	$(RM) $(COMPILED_UI) $(COMPILED_RESOURCES) $(COMPILED_UI:.py=.pyc) $(COMPILED_RESOURCES:.py=.pyc)
