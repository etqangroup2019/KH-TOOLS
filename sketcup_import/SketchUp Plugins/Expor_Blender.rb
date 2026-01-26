

require 'extensions.rb'
require 'langhandler.rb'

module D5Converter
  # Clear expired files
  expired_file=File.join(File.dirname(__FILE__),"Export_to_Blender.rb")
  File.delete(expired_file) if File.exist?(expired_file)

  NAME = "Export_to_Blender"


  VERSION = "1.3"
  ENVIRONMENT = 1


  EXTENSION = SketchupExtension.new(NAME, "Export_to_Blender/Export_to_Blender")

  EXTENSION.description="A plugin to export SketchUp file to Blender."

  EXTENSION.version = VERSION
  EXTENSION.creator = "Blender."
  EXTENSION.copyright = "2008, Blender."

  Sketchup.register_extension EXTENSION,true

end # module D5Converter
