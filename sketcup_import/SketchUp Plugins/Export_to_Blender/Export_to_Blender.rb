require 'sketchup'
require 'sketchup.rb'
require 'extensions.rb'
require 'langhandler.rb'

module Export_to_Blender
  unless file_loaded?(__FILE__)




    # # تحميل مكتبة SketchUp Ruby API
    # # دالة للتحقق من المادة وتطبيقها على السطح
    # def self.apply_material_to_surface(surface, material)
    #   model = Sketchup.active_model
    #   model.start_operation('Apply Material', true)
    #   surface.material = material
    #   model.commit_operation
    # end

    # # دالة لعكس الوجه وإصدار رسالة
    # def self.reverse_face(face)
    #   model = Sketchup.active_model
    #   model.start_operation('Reverse Face', true)
    #   face.reverse!
    #   model.commit_operation
    #   #UI.messagebox('Reverse Face Done')
    # end

    # def self.apply_back_material_to_front(entities)
    #   entities.each do |entity|
    #     if entity.is_a?(Sketchup::Group) || entity.is_a?(Sketchup::ComponentInstance)
    #       # التحقق مما إذا كان الكائن يحتوي على مكونات (أسطح) قبل تطبيق المادة الخلفية
    #       if entity.respond_to?(:definition)
    #         apply_back_material_to_front(entity.definition.entities)
    #       else
    #         # إذا لم يكن للكائن تعريف (definition)، قم بتطبيق المادة الخلفية مباشرة عليه
    #         apply_back_material_to_front(entity.entities)
    #       end
    #     elsif entity.is_a?(Sketchup::Face)
    #       if entity.back_material && !entity.back_material.display_name.to_s.include?("Default")
    #         reverse_face(entity)
    #         #if entity.material.nil? || entity.material.display_name.to_s.include?("Default")
    #         if (entity.material != entity.back_material) || entity.material.nil? || entity.material.display_name.to_s.include?("Default")
    #           apply_material_to_surface(entity, entity.back_material)
    #           reverse_face(entity)
    #         end
    #       end
    #     end
    #   end
    # end

    # # الوظيفة الرئيسية لبدء عملية التحقق والتطبيق على الكائنات بالمشهد
    # def self.main_apply_back_material_to_front
    #   model = Sketchup.active_model
    #   # استخراج جميع الكائنات الأساسية (الأسطح والكمبوننتات والجروبات)
    #   entities = model.entities
    #   # تطبيق المادة الخلفية على الأمامية لجميع الكائنات
    #   apply_back_material_to_front(entities)
    # end


    # def self.explode_inner_groups_and_components(entities)
    #   groups_and_components_to_explode = []

    #   # ابحث عن القروبات والكومبوننتات الداخلية
    #   entities.each do |entity|
    #     next unless entity.is_a?(Sketchup::Group) || entity.is_a?(Sketchup::ComponentInstance)

    #     inner_entities = find_inner_entities(entity)
    #     groups_and_components_to_explode.concat(inner_entities)
    #   end

    #   # تفجير القروبات والكومبوننتات الداخلية
    #   groups_and_components_to_explode.each do |entity|
    #     begin
    #       explode_entity(entity)
    #     rescue TypeError => e
    #       puts "خطأ: #{e}"
    #       next
    #     end
    #   end

    #   # تحديث العرض
    #   Sketchup.active_model.active_view.invalidate
    # end

    # def self.find_inner_entities(entity)
    #   inner_entities = []

    #   entity.definition.entities.each do |sub_entity|
    #     if sub_entity.is_a?(Sketchup::Group) || sub_entity.is_a?(Sketchup::ComponentInstance)
    #       inner_entities << sub_entity
    #       inner_entities.concat(find_inner_entities(sub_entity))
    #     end
    #   end

    #   inner_entities
    # end

    # def self.explode_entity(entity)
    #   entities = entity.definition.entities.to_a
    #   entity.explode

    #   # إنشاء قروب أو كومبوننت جديد
    #   new_entity = entity.parent.entities.add_instance(entity.definition, entity.transformation)

    #   # تحديث المكون
    #   new_entity.make_unique
    # end

    #  #create_materials////////////////////////////////////////////////////////////////////////////////////////////////////////

    #  def self.create_materials(model)
    #   # Define the colors
    #   color_h = 220
    #   color_s = 220
    #   color_l = 220

    #   # Create the color
    #   color = Sketchup::Color.new(color_h, color_s, color_l)

    #   # Define the default material and the replacement materials
    #   default_material_name = 'Default'
    #   replacement_material_names = ['Color_001', 'Color_M01']

    #   # Iterate through the replacement material names
    #   replacement_material_names.each do |replacement_material_name|
    #     # Check if the replacement material already exists
    #     replacement_material = model.materials[replacement_material_name]

    #     # If the replacement material doesn't exist, create it
    #     unless replacement_material
    #       replacement_material = model.materials.add(replacement_material_name)
    #       # Set the color to the material
    #       replacement_material.color = color
    #     end
    #   end
    # end

    # def self.replace_materials(entity)
    #   # Define the default material and the replacement materials
    #   default_material_name = 'Default'
    #   replacement_material_names = ['Color_001', 'Color_M01']

    #   # Check if the entity is a face
    #   if entity.is_a?(Sketchup::Face)
    #     # Get the material of the face
    #     material = entity.material

    #     # If the face has no material or its material is 'Default'
    #     if material.nil? || material.name == default_material_name
    #       # Iterate through replacement materials
    #       replacement_material_names.each do |replacement_material_name|
    #         # Check if the replacement material exists in the model
    #         replacement_material = entity.model.materials[replacement_material_name]

    #         # If the replacement material exists, apply it to the face
    #         if replacement_material
    #           entity.material = replacement_material
    #           break # Exit the loop after applying the first replacement material
    #         end
    #       end
    #     end
    #   end

    #   # If the entity is a group or component instance, recursively apply the script to its entities
    #   if entity.respond_to?(:definition)
    #     entity.definition.entities.each do |sub_entity|
    #       replace_materials(sub_entity)
    #     end
    #   elsif entity.is_a?(Sketchup::Group)
    #     entity.entities.each do |sub_entity|
    #       replace_materials(sub_entity)
    #     end
    #   end
    # end

    # # تحميل مكتبة SketchUp Ruby API
    # # دالة للتحقق من المادة وتطبيقها على السطح
    # def self.apply_material_to_surface(surface, material)
    #   model = Sketchup.active_model
    #   model.start_operation('Apply Material', true)
    #   surface.material = material
    #   model.commit_operation
    # end

    # # دالة للبحث عن الأسطح وتطبيق المادة الخلفية على المادة الأمامية وعكس الوجه إذا لزم الأمر
    # def self.apply_back_material_to_front(entities)
    #   entities.each do |entity|
    #     # فحص إذا كان الكائن جروب أو كمبوننت
    #     if entity.is_a?(Sketchup::Group) || entity.is_a?(Sketchup::ComponentInstance)
    #       # استكشاف الأسطح داخل الجروب أو الكمبوننت باستدعاء الدالة نفسها مرة أخرى
    #       apply_back_material_to_front(entity.definition.entities)
    #     elsif entity.is_a?(Sketchup::Face)
    #       # التحقق مما إذا كان للوجه مادة خلفية وليست مادة افتراضية
    #       if entity.back_material && !entity.back_material.display_name.start_with?("Default")
    #         # التحقق من أن المادة الأمامية فارغة أو مادة افتراضية
    #         #if entity.material.nil? || entity.material.display_name.start_with?("Default")
    #         if (entity.material != entity.back_material) || entity.material.nil? || entity.material.display_name.start_with?("Default")

    #           # تطبيق المادة الخلفية على المادة الأمامية
    #           apply_material_to_surface(entity, entity.back_material)
    #           # عكس الوجه
    #           reverse_face(entity)
    #         end
    #       end
    #     end
    #   end
    # end
    # selection = Sketchup.active_model.selection
    # # الوظيفة الرئيسية لبدء عملية التحقق والتطبيق على الكائنات بالمشهد
    # def self.main_apply_back_material_to_front
    #   model = Sketchup.active_model
    #   # استخراج جميع الكائنات الأساسية (الأسطح والكمبوننتات والجروبات)
    #   entities = model.entities
    #   # تطبيق المادة الخلفية على الأمامية لجميع الكائنات
    #   apply_back_material_to_front(entities)
    # end




    #create_materials////////////////////////////////////////////////////////////////////////////////////////////////////////



    # الاوامر ///////////////////////////////////////////////////////////////////////

    cmd1 = UI::Command.new("Export to Blender") {
      model_path = Sketchup.active_model.path
      saved = !model_path.nil? && !model_path.empty?
      if saved
        modified = Sketchup.active_model.modified?
      end

      if !saved || modified
        UI.messagebox("يجب حفظ الملف أولاً / Save the file first")
        Sketchup.active_model.save
      end

      user_documents_dir = File.join(ENV['HOMEDRIVE'], ENV['HOMEPATH'], 'Documents')
      folder_path = File.expand_path(user_documents_dir)
      file_name = "sketchup_script.py"
      file_path = File.join(folder_path, file_name)
      file = File.open(file_path, "w")

      script_code = <<-SCRIPT
import bpy
import os

# استيراد نوافذ التقدم من KH-Tools
try:
    from sketcup_import.progress_window import show_confirm, start_import_progress, get_current_progress, close_progress
    use_progress_window = True
except:
    use_progress_window = False

folder_path = r"#{model_path}"
file_name = "#{File.basename(model_path)}"
file_base, file_ext = os.path.splitext(file_name)
blender_file_name = file_base + ".blend"
file_path = os.path.join(folder_path)

# تحديد مسار ملف .blend
parts = folder_path.split('\\\\')
new_name = parts[-1]
NEW_folder_path = folder_path.replace(new_name, '')

folder_path1 = os.path.join(NEW_folder_path, file_base)
folder_path2 = folder_path1 + ".blend"

# التأكد من أن الاسم فريد
count = 1
while os.path.exists(os.path.join(NEW_folder_path, blender_file_name)):
    blender_file_name = f"{file_base}_{count}.blend"
    count += 1

# نافذة تأكيد الاستيراد
if use_progress_window:
    import_confirmation = show_confirm("Import SketchUp", f"Do you want to import the file:\\n{file_name}?")
else:
    import ctypes
    import_confirmation = ctypes.windll.user32.MessageBoxW(0, f"Do you want to Import the File: {file_name}?", "Import Sketchup", 1) == 1

if import_confirmation:
    # نافذة تأكيد الحفظ
    if use_progress_window:
        save_confirmation = show_confirm("Save After Import", f"Do you want to save the file after import?\\n\\nPath: {NEW_folder_path}\\nFile: {blender_file_name}")
    else:
        import ctypes
        save_confirmation = ctypes.windll.user32.MessageBoxW(0, f"Do you want to Save the File After Import?\\nFolder Path: {NEW_folder_path}\\nFile Name: {blender_file_name}", "Save After Import", 1) == 1
    
    bpy.ops.import_scene.skp_k(filepath=file_path)
    bpy.ops.object.skp_addonn()
    if save_confirmation:
        bpy.ops.wm.save_mainfile(filepath=os.path.join(NEW_folder_path, blender_file_name))

      SCRIPT
      UI.messagebox("Export Blender Done.")
      file.write(script_code)
      file.close
    }

#/Update to Blender///////////////////////////////////////////////////////////////////////////////////////////////
    cmd2 = UI::Command.new("Update to Blender") {
      model_path = Sketchup.active_model.path
      saved = !model_path.nil? && !model_path.empty?
      if saved
        modified = Sketchup.active_model.modified?
      end
      if !saved || modified
        UI.messagebox("يجب حفظ الملف أولاً / Save the file first")
        Sketchup.active_model.save
      end
      user_documents_dir = File.join(ENV['HOMEDRIVE'], ENV['HOMEPATH'], 'Documents')
      folder_path = File.expand_path(user_documents_dir)
      file_name = "update_script.py"
      file_path = File.join(folder_path, file_name)
      file = File.open(file_path, "w")

      script_code = <<-SCRIPT
import bpy
import os

# استيراد نوافذ التقدم من KH-Tools
try:
    from sketcup_import.progress_window import show_confirm, start_import_progress, get_current_progress, close_progress
    use_progress_window = True
except:
    use_progress_window = False

folder_path = r"#{Sketchup.active_model.path}"
file_name = "#{File.basename(Sketchup.active_model.path)}"
file_path = os.path.join(folder_path)

# نافذة تأكيد التحديث
if use_progress_window:
    import_confirmation = show_confirm("Update SketchUp", f"Do you want to update the file:\\n{file_name}?")
else:
    import ctypes
    import_confirmation = ctypes.windll.user32.MessageBoxW(0, f"Do you want to Update: {file_name}?", "Update Sketchup", 1) == 1

# إذا كانت الإجابة نعم
if import_confirmation:
    bpy.ops.import_scene_update.skp(filepath=file_path)
    bpy.ops.object.skp_update_file()
      SCRIPT

      file.write(script_code)
      file.close
      UI.messagebox("Update Done")
    }

    # Search /////////////////////////////////////////////////////////////////////////////////////////////////
    cmd3 = UI::Command.new("Search for back-face materials") {
      find_surfaces_with_different_materials
      select_components_with_different_back_material
      UI.messagebox('Search for back-face materials Done')
    }

    def self.find_surfaces_with_different_materials
      model = Sketchup.active_model
      return unless model
      selection = model.selection

      def self.find_surfaces_in_entities(entities, selection)
        entities.each do |entity|
          if entity.respond_to?(:definition)
              find_surfaces_in_entities(entity.definition.entities, selection)
          elsif entity.is_a?(Sketchup::Group)
              find_surfaces_in_entities(entity.entities, selection)
          elsif entity.is_a?(Sketchup::Face)
            if entity.back_material && entity.material != entity.back_material
              selection.add(entity)
            end
          end
        end
      end
      self.find_surfaces_in_entities(model.entities, selection)
    end

    def self.select_components_with_different_back_material
      model = Sketchup.active_model
      definitions = model.definitions
      components_with_different_back_material = []

      definitions.each do |definition|
        next unless definition.instances.any? # تأكد من وجود نسخ للكائن

        definition.instances.each do |instance|
          next unless instance.is_a?(Sketchup::ComponentInstance)

          instance.definition.entities.each do |entity|
            if entity.is_a?(Sketchup::Face)
              if entity.material && entity.back_material && entity.material != entity.back_material
                components_with_different_back_material << instance
                break # توقف عن البحث بمجرد العثور على اختلاف
              end
            end
          end
        end
      end

      model.selection.add(components_with_different_back_material)
    end

    # Material Converter /////////////////////////////////////////////////////////////////////////////////////////////////
    cmd4 = UI::Command.new("Reverse Face & Material Converter") {
      model = Sketchup.active_model
      selection = model.selection
      if selection.empty?
        UI.messagebox('Please select first')
      else
        switch_materials_with_face_reversal
      end
      # main_apply_back_material_to_front
    }

    # تعريف الوظيفة لتبديل المواد بين الباك فيس و الفرونت فيس مع عكس الوجوه
    def self.switch_materials_with_face_reversal
      model = Sketchup.active_model
      selection = model.selection
      if selection.empty?
        UI.messagebox('Please select first')
      else
        model.start_operation('Switch Materials with Face Reversal', true)

        # جمع جميع الأسطح المحددة في مجموعة واحدة
        entities_with_back_materials = []
        selection.each do |entity|
          collect_entities(entity, entities_with_back_materials)
        end

        # تبديل المواد بين الباك فيس و الفرونت فيس
        entities_with_back_materials.each do |entity|
          if entity.is_a?(Sketchup::Face)
            back_material = entity.back_material
            front_material = entity.material
            entity.material = back_material
            entity.back_material = front_material
          end
        end
        # تبديل المواد بين الباك فيس و الفرونت فيس مع عكس الوجوه
        reverse_face(entities_with_back_materials)

        model.commit_operation
        UI.messagebox("#{entities_with_back_materials.length} surfaces have their materials switched with face reversal.")
      end
    end

    # وظيفة لجمع الأسطح والمكونات والقروبات التي تحتوي على مادة في الباك فيس
    def self.collect_entities(entity, entities_with_back_materials)
      if entity.is_a?(Sketchup::Group)
        entity.entities.each do |sub_entity|
          collect_entities(sub_entity, entities_with_back_materials)
        end

      elsif entity.is_a?(Sketchup::ComponentInstance)
        entity.definition.entities.each do |sub_entity|
          collect_entities(sub_entity, entities_with_back_materials)
        end
      elsif entity.is_a?(Sketchup::Face) && entity.back_material
        entities_with_back_materials << entity
      end
    end

    # دالة لعكس الوجوه وإصدار رسالة
    def self.reverse_face(entities)
      model = Sketchup.active_model
      model.start_operation('Reverse Faces', true)
      entities.each do |entity|
        if entity.is_a?(Sketchup::Face)
          entity.reverse!
        elsif entity.is_a?(Sketchup::Group) || entity.is_a?(Sketchup::ComponentInstance)
          entity.definition.entities.each do |sub_entity|
            sub_entity.reverse! if sub_entity.is_a?(Sketchup::Face)
          end
        end
      end
      model.commit_operation
    end


    # Default Meterial/////////////////////////////////////////////////////////////////////////////////////////////////

    cmd5 = UI::Command.new("Default Material") {
      find_surfaces_with_different_materials1
      select_surfaces_without_material1
    }

    def self.find_surfaces_with_different_materials1
      model = Sketchup.active_model
      return unless model
      selection = model.selection
      def self.find_surfaces_in_entities(entities, selection)
        entities.each do |entity|
          if entity.respond_to?(:definition)
              find_surfaces_in_entities(entity.definition.entities, selection) if entity.material.nil?
          elsif entity.is_a?(Sketchup::Group)
              find_surfaces_in_entities(entity.entities, selection) if entity.material.nil?
          elsif entity.is_a?(Sketchup::Face)

            if entity.material.nil?
              selection.add(entity)
            end
          end
        end
      end
      self.find_surfaces_in_entities(model.entities, selection)
    end

    def self.select_surfaces_without_material1
      model = Sketchup.active_model
      entities = model.active_entities
      surfaces_without_material = []
      entities.each do |entity|
        if entity.is_a?(Sketchup::Group) && entity.material.nil?
            surfaces_without_material << entity
        end
        if entity.is_a?(Sketchup::ComponentInstance) && entity.material.nil?
            surfaces_without_material << entity
        end
      end
      model.selection.add(surfaces_without_material)
    end

    # Explode /////////////////////////////////////////////////////////////////////////////////////////////////

    cmd6 = UI::Command.new("Explode Groups & Components") {
      # تشغيل السكربت
      model = Sketchup.active_model
      selection = model.selection
      if selection.empty?
        UI.messagebox('Please select groups or components first')
      else
       # explode_inner_groups_and_components
        explode_inner_groups_and_components(selection)
        UI.messagebox('Explode Done')
      end

    }

    def self.explode_inner_groups_and_components(entities)
      entities.each do |entity|
        next unless entity.is_a?(Sketchup::Group) || entity.is_a?(Sketchup::ComponentInstance)
        # Check if the entity has inner groups or components
        has_inner_entities = entity.is_a?(Sketchup::Group) ? entity.entities.any? { |e| e.is_a?(Sketchup::Group) || e.is_a?(Sketchup::ComponentInstance) } : entity.definition.entities.any? { |e| e.is_a?(Sketchup::Group) || e.is_a?(Sketchup::ComponentInstance) }
        # If it has inner entities, explode them
        explode_entity_recursive(entity) if has_inner_entities
      end
      Sketchup.active_model.active_view.invalidate
    end

    def self.explode_entity_recursive(entity)
      return unless entity.is_a?(Sketchup::Group) || entity.is_a?(Sketchup::ComponentInstance)
      entities = entity.is_a?(Sketchup::Group) ? entity.entities.to_a : entity.definition.entities.to_a
      entities.each do |sub_entity|
        explode_entity_recursive(sub_entity)
      end

      entities.each { |e| e.make_unique if e.is_a?(Sketchup::Group) || e.is_a?(Sketchup::ComponentInstance) }
      entity.explode

      if entity.is_a?(Sketchup::Group)
        entity.parent.entities.add_group(entities)
      elsif entity.is_a?(Sketchup::ComponentInstance)
        entity.parent.entities.add_instance(entity.definition, entity.transformation)
      end
    rescue TypeError => e
      puts "خطأ: #{e}"
    end

    # Fence Group" /////////////////////////////////////////////////////////////////////////////////////////////////

    cmd7 = UI::Command.new("Fence Group") {
      self.rename_groups
    }

    def self.rename_groups
      model = Sketchup.active_model
      all_groups = model.entities.grep(Sketchup::Group)

      group_names = all_groups.map { |group| group.name ? group.name.upcase : '' }

      group_options = {
        "F" => "F - أمامي",
        "R" => "R - يمين",
        "L" => "L - يسار",
        "B" => "B - خلفي"
      }

      preferred_order = ["F", "R", "L", "B"]
      available_letters = preferred_order.reject { |letter| group_names.include?(letter) }

      selection = model.selection
      if selection.empty? || selection.length != 1 || !(selection.first.is_a?(Sketchup::Group) || selection.first.is_a?(Sketchup::ComponentInstance))
        UI.messagebox('يرجى اختيار جروب أو كمبوننت واحد فقط.')
        return
      end

      entity = selection.first
      final_name = nil

      if available_letters.any?
        descriptions = available_letters.map { |key| group_options[key] }
        prompts = ['أدخل الاسم يدوياً (يُستخدم إذا كان غير فارغ):', 'اختر نوع الفنس:']
        defaults = ['', descriptions.first]
        lists = ['', descriptions.join('|')]

        results = UI.inputbox(prompts, defaults, lists)
        return unless results

        manual_input = results[0]
        selection_desc = results[1]

        if manual_input && !manual_input.strip.empty?
          final_name = manual_input.strip
        elsif selection_desc && !selection_desc.empty?
          chosen_letter = group_options.find { |k, v| v == selection_desc }
          final_name = chosen_letter.first if chosen_letter
        end
      else
        manual_input = UI.inputbox(['أدخل الاسم يدوياً:'], [''], [''])
        return unless manual_input
        manual_input = manual_input[0]
        return if manual_input.nil? || manual_input.strip.empty?
        final_name = manual_input.strip
      end

      model.start_operation('Fence Group', true)
      rename_entity_recursive(entity, final_name)
      model.commit_operation
      UI.messagebox("تم التسمية بنجاح: '#{final_name}'")
    end

    def self.rename_entity_recursive(entity, prefix)
      return unless entity && entity.valid?

      if entity.is_a?(Sketchup::Group)
        entity.name = prefix
        children = entity.entities.to_a.select { |e|
          e.is_a?(Sketchup::Group) || e.is_a?(Sketchup::ComponentInstance)
        }
        index = 1
        children.each do |child|
          rename_entity_recursive(child, "#{prefix} #{index}")
          index += 1
        end

      elsif entity.is_a?(Sketchup::ComponentInstance)
        entity.make_unique
        entity.name = prefix
        entity.definition.name = prefix

        children = entity.definition.entities.to_a.select { |e|
          e.is_a?(Sketchup::Group) || e.is_a?(Sketchup::ComponentInstance)
        }
        index = 1
        children.each do |child|
          rename_entity_recursive(child, "#{prefix} #{index}")
          index += 1
        end
      end
    end

    # تعريف الأيقونات
    plugin_dir = File.expand_path(File.dirname(__FILE__))
    icon_path1 = File.join(plugin_dir, "B.png")
    icon_path2 = File.join(plugin_dir, "U.png")
    icon_path3 = File.join(plugin_dir, "S.png")
    icon_path4 = File.join(plugin_dir, "C.png")
    icon_path5 = File.join(plugin_dir, "M.png")
    icon_path6 = File.join(plugin_dir, "G.png")
    icon_path7 = File.join(plugin_dir, "F.png")

    cmd1.small_icon = icon_path1
    cmd1.large_icon = icon_path1

    cmd2.small_icon = icon_path2
    cmd2.large_icon = icon_path2

    cmd3.small_icon = icon_path3
    cmd3.large_icon = icon_path3

    cmd4.small_icon = icon_path4
    cmd4.large_icon = icon_path4

    cmd5.small_icon = icon_path5
    cmd5.large_icon = icon_path5

    cmd6.small_icon = icon_path6
    cmd6.large_icon = icon_path6

    cmd7.small_icon = icon_path7
    cmd7.large_icon = icon_path7

    # إنشاء شريط الأدوات وإضافة الأوامر إليه
    toolbar = UI::Toolbar.new "Export to Blender"
    toolbar.add_item cmd1
    toolbar.add_item cmd2
    toolbar.add_item cmd3
    toolbar.add_item cmd4
    toolbar.add_item cmd5
    toolbar.add_item cmd6
    toolbar.add_item cmd7

    toolbar.show

    # تحديث حالة التحميل
    file_loaded(__FILE__)
  end
end
