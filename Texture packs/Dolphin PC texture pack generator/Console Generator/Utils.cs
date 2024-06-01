using System.Diagnostics;

namespace PCTexturePackGeneratorConsole;

public class Utils
{
  internal struct Manifest
  {
    public string name { get; set; }
    public string id { get; set; }
    public string version { get; set; }
    public string description { get; set; }
    public string[] authors { get; set; }
    public string website { get; set; }
    public bool compressed { get; set; }
  };

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

    var defaultoutputLocation = GetDefaultOutputLocation() + "\\ResourcePacks";
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
}
