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
  public static Dictionary<string, string?> LodMapping = new()
  {
    // ["LOD"] = "higher_res",
    ["harry_whiphat"] = "icon_sling",
    ["harry_ice_pick_128"] = "icon_pickaxe",
    ["tex1_16x16_ccface591a847a86_14"] = "gen_native_pouch",
    ["s_jm_snow"] = "iceland_jm_snow bank",

    // Technically the same texture 128x128 vs 256x256, but keep the lower res version for the blurry ice floor effect!
    // ["s_jm_ice hard_see through"] = "s_jm_ice_see through_maze"
  };

  // Textures that we know for certain are unused on GameCube/Wii
  public static HashSet<string> UnusedTextures = new()
  {
    // Unused icons
    "icon_emptyslot",
    // Xbox
    "legal_screen_xbox_english",
    // PS2
    "insert_controller",
    "legal_screen_ps2_english",
    // Demo
    "a05",
    "a50",
    "b15",
    "c02",
    "s14",
    "opmcontrolscreen",
    "opmexitscreenall",
    // Early dev
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
  };
}
