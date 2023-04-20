using System.Diagnostics;

namespace PCTexturePackGeneratorConsole;

public class Utils
{
  public static string GetDefaultOutputLocation()
  {
    var myDocuments = Environment.GetFolderPath(Environment.SpecialFolder.MyDocuments) + "\\Dolphin Emulator";
    if (Directory.Exists(myDocuments)) return myDocuments;

    var appDataRoaming = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData) + "\\Dolphin Emulator";
    return Directory.Exists(appDataRoaming) ? appDataRoaming : Directory.GetCurrentDirectory();
  }

  public static (string, string) ParseArguments(string[] args)
  {
    var defaultPcArcFolder = "C:\\Program Files (x86)\\Aspyr\\PITFALL The Lost Expedition\\Game\\data";
    string pcArcFolder;
    if (args.Length > 0)
    {
      pcArcFolder = args[0];
    }
    else
    {
      Console.WriteLine($"Folder containing textures.arc and index.ind: ({defaultPcArcFolder})");
      pcArcFolder = Console.ReadLine() ?? "";
      if (pcArcFolder == "")
      {
        pcArcFolder = defaultPcArcFolder;
      }
    }

    var defaultoutputLocation = GetDefaultOutputLocation() + "\\Load\\Textures";
    string outputLocation;
    if (args.Length > 1)
    {
      outputLocation = args[1];
    }
    else
    {
      Console.WriteLine($"Texture pack output location: ({defaultoutputLocation})");
      outputLocation = Console.ReadLine() ?? "";
      if (outputLocation == "")
      {
        outputLocation = defaultoutputLocation;
      }
    }

    return (pcArcFolder, outputLocation);
  }

  public static int Execute(string fileName, string arguments)
  {
    Console.WriteLine($"\nCommand: {fileName} {arguments}\n");
    var psi = new ProcessStartInfo
    {
      FileName = fileName,
      Arguments = arguments,
    };
    var process = Process.Start(psi);
    process?.WaitForExit();
    return process?.ExitCode ?? -1;
  }

  // Map the Level of Details textures to their higher resolution equivalents.
  public static Dictionary<string, string> LodMapping = new()
  {
    // ["LOD"] = "higher_res",
    ["tucotuco_rotisserie"] = "tucotuco",
    ["kh_steelwire"] = "jm_steelwire03p",
    ["harry_whiphat"] = "icon_sling",
    ["torch-01"] = "icon_torch",
    ["supai_eye_glow"] = "jungle_rt_light_beam_spot_01",
    ["c00_ws_rockwall"] = "small_c00_ws_rockwall", // Not a mistake, "small" is bigger
    ["harry_ice_pick_128"] = "icon_pickaxe",
    ["a_kg_vistaa"] = "a_kg_vistaa_256",
    ["a_kg_vistab"] = "a_kg_vistab_256",
    ["a_figleaf3_lod"] = "a_figleaf3",
    ["a_kg_palm_leaf03_lod"] = "a_kg_palm_leaf03",
    ["bernard_legs_lod"] = "bernard_legs",
    ["bernard_head_lod"] = "bernard_head",
    ["croc_head_lod"] = "croc_head",
    ["explorerlegs_type2_lod"] = "explorerlegs_type2",
    ["explorerhead_lod"] = "explorerhead",
    ["explorerhead_type2_lod"] = "explorerhead_type2",
    ["croc3_body_lod"] = "croc3_body",
    ["eel_lod"] = "eel",
    ["croc3_tail_lod"] = "croc3_tail",
    ["explorerlegs_lod"] = "explorerlegs",
    ["henchman_body_lod"] = "henchman_body",
    ["henchman_head_lod"] = "henchman_head",
    ["howler_lod"] = "howler",
    ["gen_native_legs_lod"] = "gen_native_legs",
    ["gen_native_pouch_lod"] = "gen_native_pouch",
    ["gen_native_torso_lod"] = "gen_native_torso",
    ["jungle_jj_planta_lod"] = "jungle_jj_planta",
    ["leech_body_lod"] = "leech_body",
    ["leech_head_lod"] = "leech_head",
    ["monkey2_lod"] = "monkey2",
    ["native_mask_lod"] = "native_mask",
    ["monkeybaby_texturecloth_lod"] = "monkeybaby_texturecloth",
    ["monkeymom_texture_lod"] = "monkeymom_texture",
    ["renegade_native_torso_lod"] = "renegade_native_torso",
    ["shaman_native_torso_lod"] = "shaman_native_torso",
    ["penguin_map_lod"] = "penguin_map",
    ["porcu_texture_lod"] = "porcu_texture",
    ["micay_legs_lod"] = "micay_legs",
    ["snblowler_legs_lod"] = "snblowler_legs",
    ["micay_torso_lod"] = "micay_torso",
    ["snbowler_ball_lod"] = "snbowler_ball",
    ["noxious_lod"] = "noxious",
    ["snbowler_mask_lod"] = "snbowler_mask",
    ["snbowler_torso_lod"] = "snbowler_torso",
    ["renegade_native_legs_lod"] = "renegade_native_legs",
    ["scarab_lod"] = "scarab",
    ["renegade_native_mask_lod"] = "renegade_native_mask",
    ["spinja_legs_lod"] = "spinja_legs",
    ["spinja_mask_lod"] = "spinja_mask",
    ["spinja_torso_lod"] = "spinja_torso",
    ["shaman_native_legs_lod"] = "shaman_native_legs",
    ["shaman_native_mask_lod"] = "shaman_native_mask",
    ["tucotuco_body_lod"] = "tucotuco_body",
  };

  // Textures that we know for certain are unused on GameCube/Wii
  public static HashSet<string> UnusedTextures = new()
  {
    // Unused icons
    "icon_emptyslot",
    "icon_inv_pogostilt",
    "heroic",
    // TODO: Validate!
    //"icon_emptyhand",
    //"icon_pickaxe",
    //"icon_torch",
    //"icon_save_shaman",
    //"icon_save_idol",
    //"icon_sling",
    //"harry_whiphat",
    // Xbox
    "legal_screen_xbox_english",
    "book_page_options_controls_remap_xbox",
    "button_xbx_a",
    "button_xbx_analog_left_down",
    "button_xbx_analog_left_left",
    "button_xbx_analog_left_leftright",
    "button_xbx_analog_left_none",
    "button_xbx_analog_left_right",
    "button_xbx_analog_left_up",
    "button_xbx_analog_left_updown",
    "button_xbx_analog_right_down",
    "button_xbx_analog_right_left",
    "button_xbx_analog_right_leftright",
    "button_xbx_analog_right_none",
    "button_xbx_analog_right_right",
    "button_xbx_analog_right_up",
    "button_xbx_b",
    "button_xbx_black",
    "button_xbx_dpad_down",
    "button_xbx_dpad_left",
    "button_xbx_dpad_right",
    "button_xbx_dpad_up",
    "button_xbx_l",
    "button_xbx_r",
    "button_xbx_start",
    "button_xbx_white",
    "button_xbx_x",
    "button_xbx_y",
    // PS2
    "insert_controller",
    "legal_screen_ps2_english",
    "book_page_options_controls_remap_ps2",
    "button_ps2_analog_left_down",
    "button_ps2_analog_left_left",
    "button_ps2_analog_left_leftright",
    "button_ps2_analog_left_none",
    "button_ps2_analog_left_right",
    "button_ps2_analog_left_up",
    "button_ps2_analog_left_updown",
    "button_ps2_analog_right_down",
    "button_ps2_analog_right_left",
    "button_ps2_analog_right_leftright",
    "button_ps2_analog_right_none",
    "button_ps2_analog_right_right",
    "button_ps2_analog_right_up",
    "button_ps2_analog_right_updown",
    "button_ps2_circle",
    "button_ps2_dpad_down",
    "button_ps2_dpad_left",
    "button_ps2_dpad_right",
    "button_ps2_dpad_up",
    "button_ps2_l1",
    "button_ps2_l2",
    "button_ps2_r1",
    "button_ps2_r2",
    "button_ps2_square",
    "button_ps2_start",
    "button_ps2_triangle",
    "button_ps2_x",
    // Demo
    "a05",
    "a50",
    "b15",
    "c02",
    "s14",
    "book_page_opm_controls",
    "opmcontrolscreen",
    "opmexitscreenall",
    "opmexitscreennotall",
    "opmlegalscreen",
    "opmtitlescreen",
    // Early dev
    "font_systemfont_s12_p0",
    "legal_screen_bad",
    "lifepiplevel1",
    "lifepiplevel2",
    "lifepiplevel3",
    "lifepiplevel4",
    "lifepipoff",
    "lifepipon",
    "screendeveloper",
    "screenpublisher",
    "a28",
    "a29",
    "a30",
    "a31",
    "a32",
    "c07",
    "b09",
    // TODO: Book overlays and inserts!
    // TODO: Supai
  };
}
