using System.Reflection;
using System.Text.Json;
using PCTexturePackGeneratorConsole;

(var pcArcFolder, var outputLocation) = Utils.ParseArguments(args);
var workingPath = Path.GetDirectoryName(Assembly.GetExecutingAssembly().Location);
var tempDirectory = Path.Combine(Path.GetTempPath(), Path.GetRandomFileName());
var extractedTexturesFolder = $"{tempDirectory}/textures";
var convertedTexturesFolder = $"{tempDirectory}/textures_converted";
Directory.CreateDirectory(tempDirectory);

// PitfallARCTool.Program.Main(new string[]{ "-x", $"{pcArcFolder}/textures.arc", "-o", extractedTexturesFolder });
var exitCode = Utils.Execute($"{workingPath}\\PitfallARCTool.exe", $"-x \"{pcArcFolder}/textures.arc\" -o \"{extractedTexturesFolder}\" -e LE");
if (exitCode != 0) return exitCode;

// TexConvert.TexConvert.Main(new string[] { extractedTexturesFolder, convertedTexturesFolder });
exitCode = Utils.Execute(
  $"{workingPath}\\TexConvert.exe",
  $"--input {extractedTexturesFolder} --output {convertedTexturesFolder} --format png --vflip false"
  );
Console.WriteLine("");
if (exitCode != 0) return exitCode;


foreach (var textureFileInfo in new DirectoryInfo(convertedTexturesFolder).GetFiles())
{
  //var newName = Utils.TextureNameMapping.GetValueOrDefault(textureFileInfo.Name);
  //var newName = textureFileInfo.Name;

  var dteTextureMap = JsonSerializer.Deserialize<Dictionary<string, string[]>>(File.ReadAllText("./DTETextureMap.json"));
  if (dteTextureMap == null) throw new NullReferenceException(nameof(dteTextureMap) + " is null.");

  var textureFileName = textureFileInfo.Name[..^textureFileInfo.Extension.Length];
  var newNames = dteTextureMap.GetValueOrDefault(textureFileName);

  // PC has some extra files
  // Two Palettes textures aren't supported by this generator yet.
  if (newNames?.Length != 1)
  {
    var reason = newNames?.Length > 2 ? "it's a TwoPalettes format" : "it does not exist on GameCube";
    Console.WriteLine($"Ignoring {textureFileName} because {reason}");
    File.Delete(textureFileInfo.FullName);
    continue;
  }

  var newName = newNames[0];
  var destinationFolder = $"{outputLocation}/GPHE52/";
  if (!File.Exists(destinationFolder))
  {
    Directory.CreateDirectory(destinationFolder);
  }
  File.Move(textureFileInfo.FullName, destinationFolder + newName + textureFileInfo.Extension);
}

return 0;
