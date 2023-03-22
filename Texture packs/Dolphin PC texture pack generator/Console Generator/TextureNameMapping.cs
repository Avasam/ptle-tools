using System.Diagnostics;

namespace PCTexturePackGeneratorConsole
{
  public class Utils
  {
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

      string outputLocation;
      if (args.Length > 1)
      {
        outputLocation = args[1];
      }
      else
      {
        Console.WriteLine("Texture pack output location: ");
        outputLocation = Console.ReadLine() ?? "";
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

    public static Dictionary<string, string?> TextureNameMapping = new()
    {

      ["some texture name"] = "tex1_something_something",
      ["some texture name 2"] = "tex1_something_something_2",
      ["no equivalent yet"] = null,
    };
  }
}
