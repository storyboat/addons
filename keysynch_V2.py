bl_info = {
    "name": "Keyframe Synch",
    "description": "Synchronize Keyframe handles",
    "author": "Justin Mueller",
    "version": (0, 0, 1),
    "blender": (2, 80, 0),
    "location": "Graph Editor > F-Curve",
    "warning": "", # used for warning icon and text in addons panel
    "wiki_url": "",
    "tracker_url": "",
    "category": ""
}

import bpy
import numpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
                       
from bpy.types import (Panel,
                       Operator,
                       AddonPreferences,
                       PropertyGroup,
                       )



check_handle_action = False

def Correct_Aligned(x1 , y1 , input_key , input_side):
    
    x2 = input_key.get("Key_Frame")
    y2 = input_key.get("Key_Value")
    
    if input_side == 'L':
        
        x = input_key.get("Handle_R_Frame")
        
    elif input_side == 'R':
        
        x = input_key.get("Handle_L_Frame")
        
    y = (( y2 - y1 ) / ( x2 - x1 )) * ( x - x1 ) + y1

    return y

def Check_Handles_Valid_Input (KeyFrame_Data_Before , KeyFrame_Data_After ):

    i = 0
    NOF_Handles_Moved = 0
    
    #Check if Keyframes were added or deleted
    if len(KeyFrame_Data_Before) != len(KeyFrame_Data_After):
        return False
    
    
    for item in KeyFrame_Data_Before:

        #Check if Keyframe itself moved
        if item.get("Key_Value") != KeyFrame_Data_After[i].get("Key_Value") or \
        item.get("Key_Frame") != KeyFrame_Data_After[i].get("Key_Frame"):
            return False
        
        This_Curve_Size = len(bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points)
        
        
        
        if item.get("Handle_L_Value") != KeyFrame_Data_After[i].get("Handle_L_Value") and KeyFrame_Data_After[i].get("Handle_L_Selected") and item.get("Keyframe_Point") > 0:
            
            NOF_Handles_Moved += 1
            Index_Moved = i
            Moved_LR = 'L'
            Handle_Pre = KeyFrame_Data_Before[Index_Moved].get("Handle_L_Value")
            Handle_Aft = KeyFrame_Data_After[Index_Moved].get("Handle_L_Value")
            VCU = bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[Index_Moved].get("Curve")].keyframe_points[KeyFrame_Data_Before[Index_Moved].get("Keyframe_Point")-1].co[1]
            
        if item.get("Handle_R_Value") != KeyFrame_Data_After[i].get("Handle_R_Value") and KeyFrame_Data_After[i].get("Handle_R_Selected") and (KeyFrame_Data_Before[i].get("Keyframe_Point") < This_Curve_Size - 1) :
        
            NOF_Handles_Moved += 1
            Index_Moved = i
            Moved_LR = 'R'
            Handle_Pre = KeyFrame_Data_Before[Index_Moved].get("Handle_R_Value")
            Handle_Aft = KeyFrame_Data_After[Index_Moved].get("Handle_R_Value")
            VCU = bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[Index_Moved].get("Curve")].keyframe_points[KeyFrame_Data_Before[Index_Moved].get("Keyframe_Point")+1].co[1]
            
        i += 1
  
    #Calc Factor
    if NOF_Handles_Moved == 1:
        
        VDE = Handle_Aft - Handle_Pre
        
        VAF = KeyFrame_Data_Before[Index_Moved].get("Key_Value")
        
        Factor =  (VCU - VAF ) / VDE
      
        print ("Moved " , Moved_LR , " handle of: " , KeyFrame_Data_Before[Index_Moved].get("Axis") , "Keyframe No: " , KeyFrame_Data_Before[Index_Moved].get("Keyframe_Point"))   
        print ('VCU: ' , VCU)
        print ('VAF: ' , VAF)
        print ('Factor: ', Factor)

        #Move All Handles of same Frame
        i = 0
        
        for item in KeyFrame_Data_Before:
     
            if i != Index_Moved and KeyFrame_Data_Before[i].get("Key_Frame") == KeyFrame_Data_Before[Index_Moved].get("Key_Frame"):
      
                if Moved_LR == 'L':
                    VaCu =  bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i - 1].get("Keyframe_Point")].co[1]
                    VaAf = KeyFrame_Data_Before[i].get("Key_Value")
                    
                    Delta_Val = (VaCu - VaAf ) / Factor
                    #actual move
                    New_Pos = bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_left[1] + Delta_Val  
                    bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_left[1] = New_Pos
                    bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_left[0] = KeyFrame_Data_After[Index_Moved].get("Handle_L_Frame")  
                    
                    #correct right handle
                    if (KeyFrame_Data_Before[i].get("Handle_L_Type") == 'ALIGNED' and KeyFrame_Data_Before[i].get("Handle_R_Type") == 'ALIGNED') or ('AUTO' in KeyFrame_Data_Before[i].get("Handle_L_Type") and 'AUTO' in KeyFrame_Data_Before[i].get("Handle_R_Type")):

                        bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_right[1] = Correct_Aligned(KeyFrame_Data_After[Index_Moved].get("Handle_L_Frame"), bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_left[1] , KeyFrame_Data_Before[i] , 'L')
                        bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_left_type = 'ALIGNED'
                        bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_left_type = 'ALIGNED'
                        
                elif Moved_LR == 'R':
                
                    VaCu =  bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i + 1].get("Keyframe_Point")].co[1]
                    VaAf = KeyFrame_Data_Before[i].get("Key_Value")
                    
                    Delta_Val = (VaCu - VaAf ) / Factor
                    #actual move
                    New_Pos = bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_right[1] + Delta_Val  
                    bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_right[1] = New_Pos
                    bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_right[0] = KeyFrame_Data_After[Index_Moved].get("Handle_R_Frame")  
                    
                    #correct left handle
                    if (KeyFrame_Data_Before[i].get("Handle_R_Type") == 'ALIGNED' and KeyFrame_Data_Before[i].get("Handle_L_Type") == 'ALIGNED') or ('AUTO' in KeyFrame_Data_Before[i].get("Handle_R_Type") and 'AUTO' in KeyFrame_Data_Before[i].get("Handle_L_Type")):
                        
                        bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_left[1] = Correct_Aligned(KeyFrame_Data_After[Index_Moved].get("Handle_R_Frame"), bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_right[1] , KeyFrame_Data_Before[i] , 'R')
                        bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_left_type = 'ALIGNED'
                        bpy.context.active_object.animation_data.action.fcurves[KeyFrame_Data_Before[i].get("Curve")].keyframe_points[KeyFrame_Data_Before[i].get("Keyframe_Point")].handle_left_type = 'ALIGNED'
                        
                print ( KeyFrame_Data_Before[i].get("Axis") , "@Keyframe No: " , KeyFrame_Data_Before[i].get("Keyframe_Point")) 
                print ("VaCu: " , VaCu) 
                print ("VaAf: " , VaAf)
                print ("New Position: " , New_Pos)
                
            i += 1 
    else:
        return False

def Get_Info(clear_info):
    
    win = bpy.context.window_manager.windows[0]
    area = win.screen.areas[0]
    area_type = area.type
    area.type = "INFO"
    override = bpy.context.copy()
    override['window'] = win
    override['screen'] = win.screen
    override['area'] = win.screen.areas[0]
    
    bpy.ops.info.select_all(override, action='SELECT')
    
    if clear_info:
    
        bpy.ops.info.report_delete(override)
        
    else:
    
        bpy.ops.info.report_copy(override)
        area.type = area_type
        clipboard = bpy.context.window_manager.clipboard
        CP = clipboard

        if len(CP) > 0:
            if 'bpy.ops.transform.' in CP or 'object.handle' in CP:
                return 'Fetched Transform'
            else:
                return 'Fetched Else'

    
def Get_Key_Frame_Data(): 
    
    active_object_fcurves = bpy.context.active_object.animation_data.action.fcurves
    keyframe_data = []
    
    curve_index = 0
    
    for curve in active_object_fcurves:
        
        keyframepoint_index = 0
        
        for keyframe in curve.keyframe_points:
            
            Key_Detail = {
                "Curve": curve_index,
                "Keyframe_Point": keyframepoint_index,
                "Axis": curve.data_path,
                "Key_Frame": keyframe.co[0],
                "Key_Value": keyframe.co[1],
                "Handle_L_Selected": keyframe.select_left_handle,
                "Handle_L_Frame": keyframe.handle_left[0],
                "Handle_L_Value": keyframe.handle_left[1],
                "Handle_L_Type": keyframe.handle_left_type,
                "Handle_R_Selected": keyframe.select_right_handle,
                "Handle_R_Frame": keyframe.handle_right[0],
                "Handle_R_Value": keyframe.handle_right[1],
                "Handle_R_Type": keyframe.handle_right_type
            }
            
            keyframe_data.append(Key_Detail)
            keyframepoint_index += 1
            
        curve_index += 1  
                   
    return keyframe_data 

def keysynch_switch_update(self, context):

    from bpy.utils import register_class, unregister_class

    if self.keysynch_switch == False:
        unregister_class(modalks)
    else:
        register_class(modalks)
        bpy.ops.wm.modalks()
    
class MySettings(PropertyGroup):
        
        
    keysynch_switch : BoolProperty(
        name="Enable or Disable",
        description="A bool property",
        default = False,
        update = keysynch_switch_update
        )

class UV_PT_my_panel(Panel):
    bl_label = "Key Synch"
    bl_idname = "OBJECT_PT_Key_Synch_Panel"
    bl_space_type = "GRAPH_EDITOR"   
    bl_region_type = "UI"
    bl_category = "F-Curve"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        mytool = scene.my_tool

        layout.prop(mytool, "keysynch_switch", text="Key Synch Active")

            
class modalks(bpy.types.Operator):
    bl_idname = "wm.modalks"
    bl_label = "Modal KS"
    
    def modal(self, context, event):
        global check_handle_action
        global KeyFrame_Data_Before
        global KeyFrame_Data_After
        
    
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE'}:
            if event.value == 'PRESS':
            
                Get_Info(True)
                if bpy.context.active_object:
                    KeyFrame_Data_Before = Get_Key_Frame_Data()
                    check_handle_action = True
                
            elif event.value == 'RELEASE':
            
                check_handle_action = False

        
        if event.type == 'MOUSEMOVE' and check_handle_action == True:
            
            Fetched_Info = Get_Info(False)
            
            if Fetched_Info == 'Fetched Transform':
                check_handle_action = False
                
                if bpy.context.active_object:
                
                    KeyFrame_Data_After = Get_Key_Frame_Data()
                    
                    if KeyFrame_Data_Before != KeyFrame_Data_After:

                        Check_Handles_Valid_Input(KeyFrame_Data_Before , KeyFrame_Data_After)

            elif Fetched_Info == 'Fetched Else':
                check_handle_action = False  
            
        return {'PASS_THROUGH'}

    def execute(self, context):
        wm = context.window_manager
        wm.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        wm = context.window_manager


# ------------------------------------------------------------------------
#     Registration
# ------------------------------------------------------------------------

classes = (
    MySettings,
    UV_PT_my_panel
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.my_tool


if __name__ == "__main__":
    register()
    




